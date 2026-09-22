"""
Video Processing Service (services/video_processor.py)
Handles traffic sign detection on uploaded driving videos, drawing bounding boxes,
extracting frame timestamps, and generating annotated video outputs.
"""

import os
import cv2
import time
import logging
from pathlib import Path
from services.detector import TrafficSignDetector
from sign_info import get_sign_info

logger = logging.getLogger("VideoProcessor")

# Risk Color Palette (BGR for OpenCV)
RISK_COLORS = {
    "Critical": (0, 0, 220),     # Red
    "High": (0, 120, 255),       # Orange
    "Medium": (0, 195, 255),     # Yellow
    "Low": (50, 180, 50),        # Green
    "Default": (255, 140, 0)
}

class VideoProcessor:
    def __init__(self, detector: TrafficSignDetector = None):
        self.detector = detector if detector else TrafficSignDetector()

    def process_video(self, input_path: str, output_dir: str = None, frame_stride: int = 2) -> dict:
        """
        Processes driving video file:
        - Extracts frames and runs YOLO inference
        - Annotates bounding boxes and sign metrics
        - Writes annotated output video using OpenCV VideoWriter
        - Generates timestamped detection log
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Video file not found: {input_path}")

        if output_dir is None:
            output_dir = input_path.parent.parent / "static" / "processed"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_filename = f"proc_vid_{int(time.time())}.mp4"
        output_path = output_dir / output_filename

        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise ValueError(f"OpenCV could not open video file: {input_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Setup VideoWriter with mp4v codec
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        frame_idx = 0
        frame_logs = []
        unique_signs_detected = set()

        logger.info(f"Processing video: {input_path.name} ({total_frames} frames @ {fps:.1f} FPS)")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process detection every Nth frame for efficiency
            if frame_idx % frame_stride == 0:
                raw_detections = self.detector.detect(frame, conf_thresh=0.25)
            else:
                raw_detections = []

            # Current timestamp calculation
            current_time_sec = frame_idx / fps
            mins = int(current_time_sec // 60)
            secs = int(current_time_sec % 60)
            millis = int((current_time_sec - int(current_time_sec)) * 10)
            timestamp_str = f"{mins:02d}:{secs:02d}.{millis}"

            # Annotate frame
            annotated_frame = frame.copy()
            
            for det in raw_detections:
                class_name = det["class_name"]
                conf = det["confidence"]
                box = det["box"]  # [x1, y1, x2, y2]

                info = get_sign_info(class_name)
                risk = info.get("risk", "Medium")
                display_name = info.get("name", class_name)
                action = info.get("action", "")
                meaning = info.get("meaning", "")

                unique_signs_detected.add(display_name)

                color = RISK_COLORS.get(risk, RISK_COLORS["Default"])
                x1, y1, x2, y2 = box

                # Draw bounding box
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)

                # Draw header label with timestamp badge
                label_text = f"{display_name} ({int(conf * 100)}%)"
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(annotated_frame, label_text, (x1, max(20, y1 - 10)), font, 0.6, color, 2, cv2.LINE_AA)

                # Append log record
                frame_logs.append({
                    "frame": frame_idx,
                    "timestamp": round(current_time_sec, 2),
                    "timestamp_str": timestamp_str,
                    "sign_name": display_name,
                    "class_name": class_name,
                    "confidence": conf,
                    "confidence_pct": f"{int(conf * 100)}%",
                    "risk": risk,
                    "meaning": meaning,
                    "action": action
                })

            # Overlay timestamp on video corner
            cv2.putText(
                annotated_frame,
                f"TIME: {timestamp_str}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            out.write(annotated_frame)
            frame_idx += 1

        cap.release()
        out.release()

        logger.info(f"Video processing finished. Output saved to {output_path}")

        # Filter duplicate consecutive detections for summary table
        summarized_logs = []
        last_sign = None
        for log in frame_logs:
            sign_key = (log["sign_name"], int(log["timestamp"]))
            if sign_key != last_sign:
                summarized_logs.append(log)
                last_sign = sign_key

        return {
            "status": "success",
            "media_type": "video",
            "filename": output_filename,
            "processed_url": f"/static/processed/{output_filename}",
            "total_frames": frame_idx,
            "duration_sec": round(frame_idx / fps, 2),
            "total_detections": len(unique_signs_detected),
            "frame_logs": summarized_logs[:50]  # Cap top 50 log events
        }
