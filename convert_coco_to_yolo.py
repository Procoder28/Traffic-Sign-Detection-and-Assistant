"""
COCO to Contiguous YOLO Format Converter (convert_coco_to_yolo.py)
Converts Indian Traffic Signboards COCO annotations into YOLO format:
- Maps arbitrary/non-contiguous COCO category_ids into contiguous zero-indexed IDs [0 .. N-1].
- Normalizes bounding boxes [x_min, y_min, w, h] to [x_center, y_center, w, h] in range [0.0, 1.0].
- Generates indian_traffic_signs.yaml for YOLOv8 training.
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
import yaml

SPLIT_ALIASES = {
    "train": ["train", "Training"],
    "val": ["valid", "val", "validation"],
    "test": ["test", "testing"]
}


def find_split_dir(base_path: Path, aliases: list):
    for alias in aliases:
        for p in base_path.rglob(alias):
            if p.is_dir():
                return p
    return None


def convert_coco_dataset(raw_dir: str, output_dir: str):
    raw_path = Path(raw_dir)
    out_path = Path(output_dir)

    if not raw_path.exists():
        raise FileNotFoundError(f"Source dataset directory not found: {raw_path}")

    # Create destination YOLO structure
    for split in ["train", "val", "test"]:
        (out_path / "images" / split).mkdir(parents=True, exist_ok=True)
        (out_path / "labels" / split).mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print(f"Converting COCO Dataset: {raw_path} -> {out_path}")
    print("=" * 65)

    # 1. Discover unified categories
    json_files = list(raw_path.rglob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON annotation files found in {raw_path}")

    unified_categories = {}
    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "categories" in data:
                for cat in data["categories"]:
                    cat_id = cat["id"]
                    cat_name = cat["name"].strip()
                    if cat_id not in unified_categories:
                        unified_categories[cat_id] = cat_name
        except Exception as err:
            print(f"Warning reading {jf.name}: {err}")

    # Deterministic zero-indexed mapping
    sorted_coco_ids = sorted(unified_categories.keys())
    category_mapping = {coco_id: idx for idx, coco_id in enumerate(sorted_coco_ids)}
    yolo_names = {idx: unified_categories[coco_id] for coco_id, idx in category_mapping.items()}

    print(f"Discovered {len(yolo_names)} unique traffic sign classes:")
    for idx, name in sorted(yolo_names.items()):
        print(f"  [{idx:02d}] {name}")

    # 2. Process each split
    stats = {"train": 0, "val": 0, "test": 0}

    for target_split, aliases in SPLIT_ALIASES.items():
        split_dir = find_split_dir(raw_path, aliases)
        if not split_dir:
            print(f"Split directory for '{target_split}' not found. Skipping...")
            continue

        ann_files = list(split_dir.glob("*.json")) or list(split_dir.glob("_annotations*.json"))
        if not ann_files:
            print(f"No JSON annotation found in {split_dir}. Skipping...")
            continue

        ann_path = ann_files[0]
        print(f"\nProcessing '{target_split}' from {split_dir.name} using {ann_path.name}...")

        with open(ann_path, "r", encoding="utf-8") as f:
            coco = json.load(f)

        image_dict = {img["id"]: img for img in coco.get("images", [])}
        img_to_anns = {}
        for ann in coco.get("annotations", []):
            img_to_anns.setdefault(ann["image_id"], []).append(ann)

        for img_id, img_info in image_dict.items():
            file_name = img_info["file_name"]
            img_w = float(img_info["width"])
            img_h = float(img_info["height"])

            src_img = split_dir / file_name
            if not src_img.exists():
                src_img = split_dir / Path(file_name).name
            if not src_img.exists():
                continue

            dst_img = out_path / "images" / target_split / src_img.name
            dst_lbl = out_path / "labels" / target_split / f"{src_img.stem}.txt"

            if not dst_img.exists():
                shutil.copy2(src_img, dst_img)

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
                if w <= 0 or h <= 0 or img_w <= 0 or img_h <= 0:
                    continue

                # Normalization
                x_center = max(0.0, min(1.0, (x_min + w / 2.0) / img_w))
                y_center = max(0.0, min(1.0, (y_min + h / 2.0) / img_h))
                w_norm = max(0.0, min(1.0, w / img_w))
                h_norm = max(0.0, min(1.0, h / img_h))

                yolo_lines.append(f"{yolo_cls} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")

            with open(dst_lbl, "w", encoding="utf-8") as lf:
                lf.write("\n".join(yolo_lines))

            stats[target_split] += 1

    # 3. Generate dataset.yaml
    yaml_config = {
        "path": str(out_path.resolve()),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "names": yolo_names
    }

    yaml_path = out_path / "indian_traffic_signs.yaml"
    with open(yaml_path, "w", encoding="utf-8") as yf:
        yaml.dump(yaml_config, yf, default_flow_style=False, sort_keys=False)

    print("\n" + "=" * 65)
    print("CONVERSION SUMMARY:")
    for s, count in stats.items():
        print(f"  - {s.upper():5s}: {count} images and labels")
    print(f"Generated YAML config: {yaml_path}")
    print("=" * 65)
    return str(yaml_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert COCO traffic sign annotations to contiguous YOLO format.")
    parser.add_argument("--coco_dir", type=str, default="raw_dataset", help="Path to raw COCO dataset directory")
    parser.add_argument("--output_dir", type=str, default="yolo_dataset", help="Output path for YOLO formatted dataset")
    args = parser.parse_args()

    convert_coco_dataset(args.coco_dir, args.output_dir)
