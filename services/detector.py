"""
YOLOv8 Traffic Sign Detector Service (services/detector.py)
Handles loading fine-tuned YOLOv8 model weights and running object detection.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger("TrafficSignDetector")

class TrafficSignDetector:
    def __init__(self, model_path: str = None):
        """
        Initializes the YOLOv8 model detector.
        If model_path is not specified, resolves to 'models/best.pt'.
        """
        if model_path is None:
            project_root = Path(__file__).parent.parent
            indian_model_path = project_root / "models" / "best_indian.pt"
            baseline_model_path = project_root / "models" / "best.pt"

            if indian_model_path.exists() and indian_model_path.stat().st_size > 1000000:
                logger.info(f"Discovered fine-tuned Indian Traffic Sign Model: {indian_model_path}")
                model_path = indian_model_path
            elif baseline_model_path.exists() and baseline_model_path.stat().st_size > 1000000:
                logger.info(f"Loading baseline traffic sign model: {baseline_model_path}")
                model_path = baseline_model_path
            else:
                # Auto-trigger download if model file missing
                logger.info("Model file missing. Running automatic downloader...")
                try:
                    from download_model import download_pretrained_model
                    model_path = download_pretrained_model()
                except Exception as err:
                    logger.warning(f"Download failed: {err}. Fallback to standard 'yolov8n.pt'")
                    model_path = "yolov8n.pt"

        self.model_path = str(model_path)
        logger.info(f"Loading YOLOv8 Traffic Sign Model from: {self.model_path}")

        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            logger.info("YOLOv8 Traffic Sign Model initialized successfully.")
        except Exception as e:
            logger.error(f"Error loading YOLO model ({e}). Attempting baseline initialization...")
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")

    def detect(self, source, conf_thresh: float = 0.25):
        """
        Runs object detection on image file path, URL, PIL image, or NumPy array.
        Returns list of dicts:
        [
            {
                "class_id": int,
                "class_name": str,
                "confidence": float,
                "box": [x1, y1, x2, y2]
            }, ...
        ]
        """
        results = self.model.predict(source=source, conf=conf_thresh, verbose=False)
        detections = []

        if not results:
            return detections

        first_result = results[0]
        boxes = first_result.boxes

        if boxes is None or len(boxes) == 0:
            return detections

        names = self.model.names if hasattr(self.model, 'names') else {}

        for box in boxes:
            # Coordinates
            xyxy = box.xyxy[0].cpu().numpy().tolist()
            x1, y1, x2, y2 = [int(val) for val in xyxy]

            # Confidence & Class
            conf = float(box.conf[0].cpu().numpy())
            cls_id = int(box.cls[0].cpu().numpy())
            
            # Lookup class name
            cls_name = names.get(cls_id, f"sign_{cls_id}")

            detections.append({
                "class_id": cls_id,
                "class_name": cls_name,
                "confidence": round(conf, 4),
                "box": [x1, y1, x2, y2]
            })

        return detections
