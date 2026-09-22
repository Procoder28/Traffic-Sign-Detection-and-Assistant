import os
import sys
import logging
import urllib.request
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ModelDownloader")

MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "best.pt"
DIRECT_URL = "https://huggingface.co/ankitjha07/Traffic-Sign-Detection-YOLOv8/resolve/main/best.pt"
REPO_ID = "ankitjha07/Traffic-Sign-Detection-YOLOv8"
FILENAME = "best.pt"


def download_pretrained_model():
    """
    Downloads pretrained YOLOv8 model weights from Hugging Face or creates fallback weights.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 0:
        logger.info(f"Model already exists at: {MODEL_PATH} ({MODEL_PATH.stat().st_size / (1024*1024):.2f} MB)")
        return str(MODEL_PATH)

    logger.info(f"Downloading pretrained model weights to '{MODEL_PATH}'...")

    # Method 1: Try direct urllib download
    try:
        logger.info(f"Fetching weights directly from HuggingFace URL: {DIRECT_URL}")
        req = urllib.request.Request(
            DIRECT_URL,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response, open(MODEL_PATH, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        
        if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 1000:
            logger.info(f"Successfully downloaded best.pt ({MODEL_PATH.stat().st_size / (1024*1024):.2f} MB)")
            return str(MODEL_PATH)
    except Exception as urllib_err:
        logger.warning(f"Direct download via urllib failed ({urllib_err}).")

    # Method 2: Try huggingface_hub package if available
    try:
        from huggingface_hub import hf_hub_download
        downloaded_file = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            local_dir=str(MODEL_DIR),
            local_dir_use_symlinks=False
        )
        logger.info(f"Successfully downloaded model to: {downloaded_file}")
        return downloaded_file
    except Exception as hf_err:
        logger.warning(f"huggingface_hub download failed ({hf_err}).")

    # Method 3: Try Ultralytics fallback
    try:
        from ultralytics import YOLO
        logger.info("Initializing fallback YOLOv8 pretrained model...")
        fallback_model = YOLO("yolov8n.pt")
        fallback_model.save(str(MODEL_PATH))
        logger.info(f"Fallback model successfully generated at: {MODEL_PATH}")
        return str(MODEL_PATH)
    except Exception as fallback_err:
        logger.info("Ultralytics not yet installed. Please run 'pip install -r requirements.txt'")
        logger.info(f"Or place your fine-tuned 'best.pt' file into: {MODEL_PATH}")
        return str(MODEL_PATH)


if __name__ == "__main__":
    download_pretrained_model()
