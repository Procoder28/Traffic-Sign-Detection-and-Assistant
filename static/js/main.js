/**
 * AI-Powered Traffic Sign Assistant (static/js/main.js)
 * Interactive JS logic for uploads, dropzones, previews, and spinners.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const tabBtns = document.querySelectorAll('.tab-btn');
    const imageSection = document.getElementById('image-upload-section');
    const videoSection = document.getElementById('video-upload-section');
    const spinnerOverlay = document.getElementById('spinner-overlay');
    const spinnerText = document.getElementById('spinner-text');

    // Tab Switcher Logic
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const tab = btn.getAttribute('data-tab');
            if (tab === 'image') {
                imageSection.style.display = 'block';
                videoSection.style.display = 'none';
            } else {
                imageSection.style.display = 'none';
                videoSection.style.display = 'block';
            }
        });
    });

    // Setup Dropzone for Image
    setupDropzone({
        dropzoneId: 'image-dropzone',
        inputId: 'image-file-input',
        previewContainerId: 'image-preview-container',
        previewMediaId: 'image-preview-element',
        submitBtnId: 'image-submit-btn',
        formId: 'image-upload-form',
        isVideo: false,
        spinnerText: 'Running YOLOv8 Traffic Sign Detection on Image...'
    });

    // Setup Dropzone for Video
    setupDropzone({
        dropzoneId: 'video-dropzone',
        inputId: 'video-file-input',
        previewContainerId: 'video-preview-container',
        previewMediaId: 'video-preview-element',
        submitBtnId: 'video-submit-btn',
        formId: 'video-upload-form',
        isVideo: true,
        spinnerText: 'Extracting Frames & Processing Video with YOLOv8...'
    });

    function setupDropzone(config) {
        const dropzone = document.getElementById(config.dropzoneId);
        const fileInput = document.getElementById(config.inputId);
        const previewContainer = document.getElementById(config.previewContainerId);
        const previewMedia = document.getElementById(config.previewMediaId);
        const submitBtn = document.getElementById(config.submitBtnId);
        const form = document.getElementById(config.formId);

        if (!dropzone || !fileInput) return;

        dropzone.addEventListener('click', () => fileInput.click());

        // Dragover styling
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (fileInput.files.length > 0) {
                handleFileSelect(fileInput.files[0]);
            }
        });

        function handleFileSelect(file) {
            if (submitBtn) submitBtn.style.display = 'inline-flex';
            if (previewContainer && previewMedia) {
                const url = URL.createObjectURL(file);
                previewMedia.src = url;
                previewContainer.style.display = 'block';
            }
        }

        if (form) {
            form.addEventListener('submit', () => {
                if (spinnerOverlay) {
                    if (spinnerText) spinnerText.textContent = config.spinnerText;
                    spinnerOverlay.style.display = 'flex';
                }
            });
        }
    }
});
