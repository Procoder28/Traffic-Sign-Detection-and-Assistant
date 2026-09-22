"""
AI-Powered Traffic Sign Assistant (Flask Application app.py)
Phase 1 & Phase 2 Complete Implementation
"""

import os
import logging
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

from services.detector import TrafficSignDetector
from services.image_processor import ImageProcessor
from services.video_processor import VideoProcessor

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TrafficSignApp")

# Paths Configuration
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "static" / "processed"
RESULTS_DIR = BASE_DIR / "results"

for folder in [UPLOAD_DIR, PROCESSED_DIR, RESULTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Allowed File Extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "traffic_sign_assistant_secret_key_2026"
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max upload limit

# Lazy load AI services
detector = None
image_processor = None
video_processor = None

def get_services():
    global detector, image_processor, video_processor
    if detector is None:
        logger.info("Initializing YOLOv8 Detector and Services...")
        detector = TrafficSignDetector()
        image_processor = ImageProcessor(detector=detector)
        video_processor = VideoProcessor(detector=detector)
    return image_processor, video_processor

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/')
def index():
    """Renders main upload dashboard."""
    return render_template('index.html')


@app.route('/upload_image', methods=['POST'])
def upload_image():
    """Handles image upload and triggers YOLOv8 traffic sign analysis."""
    if 'image_file' not in request.files:
        flash("No file part provided in request.", "danger")
        return redirect(url_for('index'))

    file = request.files['image_file']
    if file.filename == '':
        flash("No image selected for upload.", "warning")
        return redirect(url_for('index'))

    if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        filename = secure_filename(file.filename)
        input_path = UPLOAD_DIR / filename
        file.save(str(input_path))
        logger.info(f"Image uploaded successfully: {input_path}")

        try:
            img_proc, _ = get_services()
            result_data = img_proc.process_image(str(input_path))
            return render_template('result.html', data=result_data)
        except Exception as e:
            logger.error(f"Error processing image: {e}", exc_info=True)
            flash(f"Failed to process image: {str(e)}", "danger")
            return redirect(url_for('index'))
    else:
        flash("Invalid image file format. Supported formats: JPG, PNG, WEBP, BMP.", "warning")
        return redirect(url_for('index'))


@app.route('/upload_video', methods=['POST'])
def upload_video():
    """Handles driving video upload and triggers frame-by-frame YOLO analysis."""
    if 'video_file' not in request.files:
        flash("No video file provided.", "danger")
        return redirect(url_for('index'))

    file = request.files['video_file']
    if file.filename == '':
        flash("No video selected for upload.", "warning")
        return redirect(url_for('index'))

    if file and allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        filename = secure_filename(file.filename)
        input_path = UPLOAD_DIR / filename
        file.save(str(input_path))
        logger.info(f"Video uploaded successfully: {input_path}")

        try:
            _, vid_proc = get_services()
            result_data = vid_proc.process_video(str(input_path))
            return render_template('result.html', data=result_data)
        except Exception as e:
            logger.error(f"Error processing video: {e}", exc_info=True)
            flash(f"Failed to process video: {str(e)}", "danger")
            return redirect(url_for('index'))
    else:
        flash("Invalid video file format. Supported formats: MP4, AVI, MOV, MKV.", "warning")
        return redirect(url_for('index'))


@app.route('/api/health')
def health_check():
    """Service health API endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "AI Traffic Sign Assistant",
        "model": "YOLOv8 Pretrained (36 Classes)",
        "phase": "Phase 1 & Phase 2 Active"
    })


if __name__ == '__main__':
    logger.info("Starting AI Traffic Sign Assistant Flask Server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
