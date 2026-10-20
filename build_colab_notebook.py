"""
Builds the complete Google Colab training notebook:
train_indian_traffic_signs_colab.ipynb
"""
import json
from pathlib import Path

notebook = {
    "cells": [],
    "metadata": {
        "accelerator": "GPU",
        "colab": {
            "gpuType": "T4",
            "provenance": []
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 0
}

def add_md(text):
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().split("\n")]
    })

def add_code(code):
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.strip().split("\n")]
    })

# ==================== CELL 1: Header ====================
add_md("""
# 🚦 AI Traffic Sign Assistant: Indian Road Signs Fine-Tuning Pipeline
**Project**: AI-Based Traffic Sign Detection and Recognition System with Indian Traffic Information Chatbot  
**Target**: Fine-tune YOLOv8s on the **Indian Traffic Signboards Dataset (56 Classes)**  
**Hardware Environment**: Google Colab with NVIDIA Tesla T4 GPU (Free Tier)  
**Estimated Runtime**: ~1 to 1.25 hours (25–30 epochs with early stopping)  

### 📋 Overview of this Notebook:
1. **GPU & Environment Setup**: Verifies CUDA acceleration and installs Ultralytics YOLOv8.
2. **Dataset Acquisition**: Flexible download via Roboflow, Kaggle, Google Drive, or direct upload.
3. **COCO to YOLO Conversion**: Converts `_annotations.coco.json` into normalized coordinates with contiguous zero-indexed class IDs.
4. **Baseline Evaluation ("Before")**: Tests your baseline `best.pt` on real Indian road scenes to document the domain gap.
5. **YOLOv8s Fine-Tuning**: Trains on Indian road scenes using mixed precision (FP16), early stopping, and data augmentations.
6. **Comprehensive Metrics ("After")**: Measures Precision, Recall, mAP50, and mAP50-95 on the unseen test set.
7. **Side-by-Side Visual Comparison**: Displays real road scene detections before vs. after fine-tuning.
8. **Export**: Automatically packages `best_indian.pt` (~22 MB) for download to your local Flask app.
""")

# ==================== CELL 2: GPU Check ====================
add_code("""
# Cell 1: Verify GPU Environment & Install Dependencies
import os
import torch

print("=" * 60)
print("🔍 SYSTEM & ACCELERATOR CHECK")
print("=" * 60)
print(f"PyTorch Version: {torch.__version__}")
cuda_avail = torch.cuda.is_available()
print(f"CUDA Available: {cuda_avail}")

if cuda_avail:
    gpu_name = torch.cuda.get_device_name(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
    print(f"Active GPU: {gpu_name} ({vram_gb:.2f} GB VRAM)")
    print("✅ Hardware accelerator is configured correctly!")
else:
    print("⚠️ WARNING: GPU is not active!")
    print("Please go to Menu: Runtime -> Change runtime type -> Select 'T4 GPU' -> Save.")

# Install Ultralytics and dependencies
!nvidia-smi
!pip install -q "ultralytics>=8.0.0" roboflow opencv-python matplotlib pyyaml
print("✅ Ultralytics & dependencies installed successfully!")
""")

# ==================== CELL 3: Step 1 Markdown ====================
add_md("""
---
## 📦 Step 1: Obtain the Indian Traffic Signboards Dataset (v2)
The dataset contains **7,833 images** annotated across 56 Indian traffic sign classes.

Choose **ONE** of the convenient options below to load the dataset into Colab:
- **Option A (Roboflow Public Download)**: If you have your Roboflow project download snippet, paste it in the designated section.
- **Option B (Kaggle Dataset)**: Download directly using `kaggle datasets download -d hemanthande24/custom-indian-traffic-sign-dataset-coco`.
- **Option C (Direct Zip Upload / Google Drive)**: Upload your dataset zip to `/content/` or mount Google Drive.
""")

# ==================== CELL 4: Step 1 Code ====================
add_code("""
# Cell 2: Dataset Acquisition & Extraction
import os
import zipfile
import shutil
from pathlib import Path

RAW_DATA_DIR = Path("/content/raw_dataset")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# OPTION A: Download directly from Kaggle (Recommended if you have kaggle.json)
# -------------------------------------------------------------
# If you have your kaggle.json, uncomment the lines below:
# !pip install -q kaggle
# !mkdir -p ~/.kaggle && cp /content/kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
# !kaggle datasets download -d hemanthande24/custom-indian-traffic-sign-dataset-coco -p /content/

# -------------------------------------------------------------
# OPTION B: Download via Roboflow API (if using Roboflow Universe)
# -------------------------------------------------------------
# from roboflow import Roboflow
# rf = Roboflow(api_key="YOUR_ROBOFLOW_API_KEY")
# project = rf.workspace("hemanth-dtwzo").project("indian-traffic-signboards-zcmku-pug8l")
# version = project.version(2).download("coco", location=str(RAW_DATA_DIR))

# -------------------------------------------------------------
# OPTION C: Automatic Detection of any uploaded .zip in /content
# -------------------------------------------------------------
print("Scanning /content for dataset archives...")
zip_candidates = [f for f in Path("/content").glob("*.zip") if "yolo" not in f.name.lower()]

if zip_candidates:
    selected_zip = zip_candidates[0]
    print(f"📦 Found archive: {selected_zip.name}. Extracting to {RAW_DATA_DIR}...")
    with zipfile.ZipFile(selected_zip, 'r') as zip_ref:
        zip_ref.extractall(RAW_DATA_DIR)
    print("✅ Extraction complete!")
else:
    # Check if files already extracted
    subdirs = [p for p in RAW_DATA_DIR.iterdir() if p.is_dir()]
    if subdirs:
        print(f"✅ Found existing extracted dataset directories in {RAW_DATA_DIR}: {[d.name for d in subdirs]}")
    else:
        print("ℹ️ No zip archive found automatically.")
        print("👉 Please upload your dataset zip file to '/content/' in the Colab file browser on the left, then re-run this cell.")

# List discovered folders
print("\nDirectory contents of /content/raw_dataset:")
for item in RAW_DATA_DIR.iterdir():
    print(f" - {item.name} ({'Dir' if item.is_dir() else 'File'})")
""")

# ==================== CELL 5: Step 2 Markdown ====================
add_md("""
---
## 🔄 Step 2: Accurate COCO to YOLO Format Conversion
COCO and YOLO format differences:
1. **Coordinates**:
   - COCO bounding boxes: `[x_min, y_min, width, height]` in absolute pixel coordinates.
   - YOLO bounding boxes: `[x_center, y_center, width, height]` normalized between `0.0` and `1.0`.
2. **Category IDs**:
   - COCO `category_id` values can be 1-indexed or non-contiguous (e.g. 1, 2, 5...).
   - YOLO strictly requires **contiguous zero-indexed class IDs** `[0, 1, 2, ..., N-1]`.
3. **Directory Structure**:
   - Formats into standard YOLO layout:
     ```
     /content/yolo_dataset/
       ├── images/ (train, val, test)
       ├── labels/ (train, val, test)
       └── indian_traffic_signs.yaml
     ```
""")

# ==================== CELL 6: Step 2 Code ====================
add_code("""
# Cell 3: COCO to Contiguous YOLO Format Converter
import json
import shutil
from pathlib import Path
import yaml

YOLO_ROOT = Path("/content/yolo_dataset")
for split in ["train", "val", "test"]:
    (YOLO_ROOT / "images" / split).mkdir(parents=True, exist_ok=True)
    (YOLO_ROOT / "labels" / split).mkdir(parents=True, exist_ok=True)

# Find COCO annotation files across possible split names
split_aliases = {
    "train": ["train", "Training"],
    "val": ["valid", "val", "validation"],
    "test": ["test", "testing"]
}

# Recursively locate split directories
def find_split_dir(base_path, aliases):
    for alias in aliases:
        for p in base_path.rglob(alias):
            if p.is_dir():
                return p
    return None

print("=" * 60)
print("⚙️ STARTING COCO TO CONTIGUOUS YOLO CONVERSION")
print("=" * 60)

# Step 2.1: Discover unified categories across all splits
unified_categories = {}
category_mapping = {}  # coco_id -> zero_indexed_id

# Look for all coco json files
json_files = list(RAW_DATA_DIR.rglob("*.json"))
print(f"Discovered {len(json_files)} annotation file(s): {[f.name for f in json_files]}")

# Collect all unique categories
for jf in json_files:
    try:
        with open(jf, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if "categories" in data and data["categories"]:
            for cat in data["categories"]:
                cat_id = cat["id"]
                cat_name = cat["name"].strip()
                if cat_id not in unified_categories:
                    unified_categories[cat_id] = cat_name
    except Exception as e:
        print(f"Warning reading {jf.name}: {e}")

# Sort categories by ID to generate deterministic zero-indexed mapping
sorted_coco_ids = sorted(unified_categories.keys())
category_mapping = {coco_id: idx for idx, coco_id in enumerate(sorted_coco_ids)}
yolo_names = {idx: unified_categories[coco_id] for coco_id, idx in category_mapping.items()}

print(f"Total Unique Classes Identified: {len(yolo_names)}")
print("Sample class mappings:")
for i in range(min(5, len(yolo_names))):
    print(f"  YOLO ID {i}: '{yolo_names[i]}'")

# Step 2.2: Convert Each Split
conversion_stats = {"train": 0, "val": 0, "test": 0}

for target_split, aliases in split_aliases.items():
    split_dir = find_split_dir(RAW_DATA_DIR, aliases)
    if not split_dir:
        print(f"⚠️ Split directory for '{target_split}' not found. Checking root...")
        continue

    # Find annotation file in split_dir
    ann_files = list(split_dir.glob("*.json")) or list(split_dir.glob("_annotations*.json"))
    if not ann_files:
        print(f"⚠️ No JSON annotation found in {split_dir}")
        continue

    ann_path = ann_files[0]
    print(f"Processing split '{target_split}' from {split_dir.name} using {ann_path.name}...")

    with open(ann_path, 'r', encoding='utf-8') as f:
        coco = json.load(f)

    # Index images
    image_dict = {img["id"]: img for img in coco.get("images", [])}
    
    # Group annotations by image_id
    img_to_anns = {}
    for ann in coco.get("annotations", []):
        img_id = ann["image_id"]
        img_to_anns.setdefault(img_id, []).append(ann)

    # Convert annotations and copy images
    for img_id, img_info in image_dict.items():
        file_name = img_info["file_name"]
        img_w = float(img_info["width"])
        img_h = float(img_info["height"])

        # Source image path
        src_img = split_dir / file_name
        if not src_img.exists():
            # Sometimes file_name includes subpaths
            src_img = split_dir / Path(file_name).name
        
        if not src_img.exists():
            continue

        # Destination paths
        dst_img = YOLO_ROOT / "images" / target_split / src_img.name
        dst_lbl = YOLO_ROOT / "labels" / target_split / f"{src_img.stem}.txt"

        # Copy image (using copy2 to preserve metadata)
        if not dst_img.exists():
            shutil.copy2(src_img, dst_img)

        # Build YOLO label entries
        yolo_lines = []
        for ann in img_to_anns.get(img_id, []):
            coco_cat_id = ann.get("category_id")
            if coco_cat_id not in category_mapping:
                continue

            yolo_cls = category_mapping[coco_cat_id]
            bbox = ann.get("bbox", [])
            if len(bbox) != 4:
                continue

            x_min, y_min, w, h = bbox
            # Avoid invalid boxes
            if w <= 0 or h <= 0 or img_w <= 0 or img_h <= 0:
                continue

            # Normalized YOLO coordinates
            x_center = (x_min + w / 2.0) / img_w
            y_center = (y_min + h / 2.0) / img_h
            w_norm = w / img_w
            h_norm = h / img_h

            # Clamp between 0.0 and 1.0 to guard against boundary rounding
            x_center = max(0.0, min(1.0, x_center))
            y_center = max(0.0, min(1.0, y_center))
            w_norm = max(0.0, min(1.0, w_norm))
            h_norm = max(0.0, min(1.0, h_norm))

            yolo_lines.append(f"{yolo_cls} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")

        # Write label file (even if empty to act as background negative)
        with open(dst_lbl, 'w', encoding='utf-8') as lf:
            lf.write("\\n".join(yolo_lines))

        conversion_stats[target_split] += 1

print("\n" + "=" * 60)
print("📊 CONVERSION COMPLETED SUCCESSFULLY")
print("=" * 60)
for s, count in conversion_stats.items():
    print(f" - {s.upper()} Split: {count} images processed")

# Step 2.3: Write dataset.yaml configuration file
yaml_config = {
    "path": str(YOLO_ROOT),
    "train": "images/train",
    "val": "images/val",
    "test": "images/test",
    "names": yolo_names
}

yaml_path = YOLO_ROOT / "indian_traffic_signs.yaml"
with open(yaml_path, 'w', encoding='utf-8') as yf:
    yaml.dump(yaml_config, yf, default_flow_style=False, sort_keys=False)

print(f"\n✅ YOLO Configuration saved to: {yaml_path}")
""")

# ==================== CELL 7: Step 3 Markdown ====================
add_md("""
---
## 🧠 Step 3: Load Checkpoint for Transfer Learning
To preserve the feature representations from your existing `best.pt` model:
- If you uploaded `best.pt` to `/content/best.pt`, it will load weights from your previous model.
- If not uploaded, it automatically initializes from official `yolov8s.pt`.
""")

# ==================== CELL 8: Step 3 Code ====================
add_code("""
# Cell 4: Initialize YOLOv8 Model Checkpoint
from ultralytics import YOLO
from pathlib import Path

local_best = Path("/content/best.pt")

if local_best.exists() and local_best.stat().st_size > 1000000:
    print(f"✅ Found uploaded baseline checkpoint: {local_best} ({local_best.stat().st_size / (1024*1024):.2f} MB)")
    print("Loading weights from 'best.pt' for transfer learning...")
    model = YOLO(str(local_best))
else:
    print("ℹ️ No local 'best.pt' uploaded in /content. Initializing from standard 'yolov8s.pt'...")
    model = YOLO("yolov8s.pt")

print("✅ Model initialized and ready for training!")
""")

# ==================== CELL 9: Step 4 Markdown ====================
add_md("""
---
## 🧪 Step 4: Baseline ("Before") Evaluation on Indian Road Scenes
Before fine-tuning, let's test how the baseline model performs on sample Indian road scenes.
This establishes empirical proof of the domain gap for your college project report.
""")

# ==================== CELL 10: Step 4 Code ====================
add_code("""
# Cell 5: Baseline Model Evaluation on Indian Test Images
import cv2
import matplotlib.pyplot as plt
from pathlib import Path

test_images = list((YOLO_ROOT / "images" / "test").glob("*.*")) or list((YOLO_ROOT / "images" / "val").glob("*.*"))

if test_images:
    sample_img_path = str(test_images[0])
    print(f"Testing baseline model on sample Indian road scene: {Path(sample_img_path).name}")
    
    baseline_results = model.predict(source=sample_img_path, conf=0.25, verbose=False)
    boxes = baseline_results[0].boxes
    
    print(f"Total signs detected by baseline model: {len(boxes) if boxes is not None else 0}")
    
    # Render baseline detection
    res_plotted = baseline_results[0].plot()
    plt.figure(figsize=(9, 6))
    plt.imshow(cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB))
    plt.title(f"Baseline Model Detection Result (Signs Found: {len(boxes) if boxes is not None else 0})")
    plt.axis("off")
    plt.show()
else:
    print("No test images available yet.")
""")

# ==================== CELL 11: Step 5 Markdown ====================
add_md("""
---
## 🚀 Step 5: Fine-Tune YOLOv8s on Indian Traffic Signs
### Hyperparameters:
- **Epochs**: `30` (with early stopping `patience=10`)
- **Batch Size**: `16` (optimal for Tesla T4 16GB VRAM)
- **Image Size**: `512` (matches dataset native resolution, high speed)
- **Mixed Precision**: `amp=True` (FP16 automatic mixed precision for maximum throughput)
- **Augmentation**: Default YOLO mosaic, HSV jitter, and flips enabled for robust real-world generalization
""")

# ==================== CELL 12: Step 5 Code ====================
add_code("""
# Cell 6: Fine-Tuning Execution
import time

yaml_file = "/content/yolo_dataset/indian_traffic_signs.yaml"
project_dir = "/content/training_runs"
run_name = "indian_traffic_yolov8s"

print("=" * 60)
print("🚀 LAUNCHING YOLOV8s FINE-TUNING")
print("=" * 60)
start_time = time.time()

train_results = model.train(
    data=yaml_file,
    epochs=30,
    patience=10,
    batch=16,
    imgsz=512,
    workers=2,
    project=project_dir,
    name=run_name,
    exist_ok=True,
    pretrained=True,
    optimizer="auto",
    amp=True,
    verbose=True,
    plots=True
)

elapsed_min = (time.time() - start_time) / 60.0
print("=" * 60)
print(f"🎉 TRAINING COMPLETED IN {elapsed_min:.2f} MINUTES!")
print("=" * 60)
""")

# ==================== CELL 13: Step 6 Markdown ====================
add_md("""
---
## 📈 Step 6: Test Set Validation & Comparative Metrics
Evaluate the fine-tuned model on the unseen `test` split:
- **Precision (P)**
- **Recall (R)**
- **mAP50** (Mean Average Precision at IoU 0.50)
- **mAP50-95** (Standard COCO benchmark metric)
""")

# ==================== CELL 14: Step 6 Code ====================
add_code("""
# Cell 7: Final Test Set Evaluation & Metrics
from ultralytics import YOLO
import matplotlib.pyplot as plt
import cv2
from pathlib import Path

best_weights = Path("/content/training_runs/indian_traffic_yolov8s/weights/best.pt")

if best_weights.exists():
    print(f"Loading trained weights: {best_weights}")
    improved_model = YOLO(str(best_weights))
    
    print("\nRunning comprehensive evaluation on TEST split...")
    val_results = improved_model.val(
        data="/content/yolo_dataset/indian_traffic_signs.yaml",
        split="test",
        batch=16,
        imgsz=512
    )

    p = val_results.box.mp
    r = val_results.box.mr
    map50 = val_results.box.map50
    map50_95 = val_results.box.map

    print("\n" + "=" * 60)
    print("🏆 MEASURED BENCHMARK EVALUATION RESULTS")
    print("=" * 60)
    print(f"  Precision (P):       {p * 100:.2f}%")
    print(f"  Recall (R):          {r * 100:.2f}%")
    print(f"  mAP@0.50:            {map50 * 100:.2f}%")
    print(f"  mAP@0.50:0.95:       {map50_95 * 100:.2f}%")
    print("=" * 60)

    # Display generated training curves
    run_dir = Path("/content/training_runs/indian_traffic_yolov8s")
    for chart_name in ["results.png", "confusion_matrix.png"]:
        chart_path = run_dir / chart_name
        if chart_path.exists():
            img = cv2.imread(str(chart_path))
            plt.figure(figsize=(12, 6))
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            plt.title(chart_name)
            plt.axis("off")
            plt.show()
else:
    print(f"Checkpoint not found at: {best_weights}")
""")

# ==================== CELL 15: Step 7 Markdown ====================
add_md("""
---
## 🔍 Step 7: Side-by-Side Visual Comparison (Before vs. After)
Let's see how the baseline model and the improved model perform on the same real Indian road scene test images!
""")

# ==================== CELL 16: Step 7 Code ====================
add_code("""
# Cell 8: Visual Comparison (Before vs After)
import cv2
import matplotlib.pyplot as plt

test_images = list((YOLO_ROOT / "images" / "test").glob("*.*"))

if test_images and best_weights.exists():
    sample_images = test_images[:min(3, len(test_images))]

    for idx, test_img_path in enumerate(sample_images):
        test_path_str = str(test_img_path)
        
        # 1. Baseline prediction
        res_baseline = model.predict(test_path_str, conf=0.25, verbose=False)[0]
        plot_baseline = res_baseline.plot()

        # 2. Improved prediction
        res_improved = improved_model.predict(test_path_str, conf=0.25, verbose=False)[0]
        plot_improved = res_improved.plot()

        # Display side-by-side
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        axes[0].imshow(cv2.cvtColor(plot_baseline, cv2.COLOR_BGR2RGB))
        axes[0].set_title(f"BEFORE: Baseline Model ({len(res_baseline.boxes)} signs detected)")
        axes[0].axis("off")

        axes[1].imshow(cv2.cvtColor(plot_improved, cv2.COLOR_BGR2RGB))
        axes[1].set_title(f"AFTER: Fine-Tuned Indian Model ({len(res_improved.boxes)} signs detected)")
        axes[1].axis("off")

        plt.suptitle(f"Test Scene #{idx+1}: {test_img_path.name}", fontsize=14, weight="bold")
        plt.tight_layout()
        plt.show()
""")

# ==================== CELL 17: Step 8 Markdown ====================
add_md("""
---
## 💾 Step 8: Export `best_indian.pt` for your Flask App
We copy the best weights and package them with the YAML configuration for easy download to your local project.
""")

# ==================== CELL 18: Step 8 Code ====================
add_code("""
# Cell 9: Package & Download Model Weights
import shutil
from pathlib import Path
from google.colab import files

OUTPUT_DIR = Path("/content/indian_model_export")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Copy trained weights as best_indian.pt
src_weights = Path("/content/training_runs/indian_traffic_yolov8s/weights/best.pt")
dst_weights = OUTPUT_DIR / "best_indian.pt"

if src_weights.exists():
    shutil.copy2(src_weights, dst_weights)
    print(f"✅ Saved weights as: {dst_weights} ({dst_weights.stat().st_size / (1024*1024):.2f} MB)")

# 2. Copy dataset yaml
shutil.copy2("/content/yolo_dataset/indian_traffic_signs.yaml", OUTPUT_DIR / "indian_traffic_signs.yaml")

# 3. Create zip bundle
zip_path = "/content/indian_traffic_model_bundle.zip"
shutil.make_archive("/content/indian_traffic_model_bundle", 'zip', OUTPUT_DIR)
print(f"✅ Bundle ready: {zip_path}")

print("\\n" + "=" * 60)
print("📥 DOWNLOAD INSTRUCTIONS")
print("=" * 60)
print("1. Download 'best_indian.pt' or 'indian_traffic_model_bundle.zip'.")
print("2. Place 'best_indian.pt' into your project's 'traffic-sign-assistant/models/' folder.")
print("3. Your existing 'best.pt' remains intact as a baseline comparator!")
print("=" * 60)

# Trigger automatic browser download
files.download(str(dst_weights))
""")

# Save notebook to disk
target_file = Path("d:/Traffic Sign Assisstant Mini project/traffic-sign-assistant/train_indian_traffic_signs_colab.ipynb")
with open(target_file, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print(f"Successfully created Google Colab notebook at: {target_file}")
