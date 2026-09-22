"""
Image Processing Service (services/image_processor.py)
Annotates uploaded images with bounding boxes, risk badges, confidence labels, and metadata.
"""

import os
import cv2
import time
import numpy as np
from pathlib import Path
from services.detector import TrafficSignDetector
from sign_info import get_sign_info

# Risk Color Palette (BGR for OpenCV)
RISK_COLORS = {
    "Critical": (0, 0, 220),     # Bright Red
    "High": (0, 120, 255),       # Orange
    "Medium": (0, 195, 255),     # Yellow / Gold
    "Low": (50, 180, 50),        # Emerald Green
    "Default": (255, 140, 0)     # Blue
}

class ImageProcessor:
    def __init__(self, detector: TrafficSignDetector = None):
        self.detector = detector if detector else TrafficSignDetector()

    def process_image(self, input_path: str, output_dir: str = None) -> dict:
        """
        Processes image at input_path:
        - Runs YOLO detection
        - Draws formatted bounding boxes & risk labels
        - Saves result image to static/processed/
        - Retrieves sign knowledge base information
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Image not found: {input_path}")

        # Setup output location
        if output_dir is None:
            output_dir = input_path.parent.parent / "static" / "processed"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"proc_{int(time.time())}_{input_path.name}"
        output_path = output_dir / filename

        # Read original image
        image = cv2.imread(str(input_path))
        if image is None:
            raise ValueError(f"Could not load image using OpenCV: {input_path}")

        # Run detection
        raw_detections = self.detector.detect(str(input_path), conf_thresh=0.25)
        
        annotated_image = image.copy()
        processed_detections = []

        # Annotate Detections
        for idx, det in enumerate(raw_detections):
            class_name = det["class_name"]
            conf = det["confidence"]
            box = det["box"]  # [x1, y1, x2, y2]
            
            # Lookup knowledge base info
            info = get_sign_info(class_name)
            risk = info.get("risk", "Medium")
            action = info.get("action", "")
            meaning = info.get("meaning", "")
            display_name = info.get("name", class_name)

            color = RISK_COLORS.get(risk, RISK_COLORS["Default"])
            x1, y1, x2, y2 = box

            # Draw outer bounding box with rounded corners / thick border
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 3)

            # Draw filled header box for label
            label_text = f"{display_name} ({int(conf * 100)}%)"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2
            
            (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
            
            # Label background banner
            banner_y1 = max(0, y1 - text_h - 12)
            banner_y2 = y1
            banner_x2 = min(annotated_image.shape[1], x1 + text_w + 12)

            cv2.rectangle(annotated_image, (x1, banner_y1), (banner_x2, banner_y2), color, cv2.FILLED)

            # Draw Label text (White text over colored banner)
            cv2.putText(
                annotated_image,
                label_text,
                (x1 + 6, banner_y2 - 6),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA
            )

            # Record detection data structure
            processed_detections.append({
                "id": idx + 1,
                "class_name": class_name,
                "display_name": display_name,
                "confidence": conf,
                "confidence_pct": f"{int(conf * 100)}%",
                "box": box,
                "risk": risk,
                "meaning": meaning,
                "action": action,
                "category": info.get("category", "General")
            })

        # Save annotated image
        cv2.imwrite(str(output_path), annotated_image)

        # Return metadata summary
        return {
            "status": "success",
            "media_type": "image",
            "filename": filename,
            "processed_url": f"/static/processed/{filename}",
            "total_signs": len(processed_detections),
            "detections": processed_detections
        }
