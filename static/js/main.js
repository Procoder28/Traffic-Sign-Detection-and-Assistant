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

    // Initialize AI Traffic Rules Chatbot
    setupChatbot();
});

function setupChatbot() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatConv = document.getElementById('chat-conversation');
    const clearBtn = document.getElementById('chat-clear-btn');
    const chips = document.querySelectorAll('.suggestion-chips .chip');

    if (!chatForm || !chatInput || !chatConv) return;

    let chatHistory = [];
    let chatContext = {};

    // Extract detection context if available on result page
    const contextScript = document.getElementById('detection-context-data');
    if (contextScript) {
        try {
            const data = JSON.parse(contextScript.textContent);
            if (data && data.detections && data.detections.length > 0) {
                const primarySign = data.detections[0];
                chatContext = {
                    detected_sign: primarySign.display_name,
                    class_name: primarySign.class_name,
                    confidence: primarySign.confidence,
                    confidence_pct: primarySign.confidence_pct,
                    category: primarySign.category,
                    risk: primarySign.risk,
                    media_type: data.media_type,
                    all_detections: data.detections.map(d => ({
                        name: d.display_name,
                        confidence: d.confidence_pct,
                        risk: d.risk
                    }))
                };
            } else if (data && data.media_type === 'video') {
                chatContext = {
                    media_type: 'video',
                    total_frames: data.total_frames,
                    frame_logs_count: (data.frame_logs || []).length
                };
            }
        } catch (e) {
            console.warn("Could not parse detection context data:", e);
        }
    }

    // Chip Click Handler
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.getAttribute('data-prompt');
            if (prompt) {
                chatInput.value = prompt;
                submitChatMessage(prompt);
            }
        });
    });

    // Clear Chat Handler
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            chatHistory = [];
            const isDetected = chatContext && chatContext.detected_sign;
            chatConv.innerHTML = `
                <div class="chat-bubble-row assistant">
                    <div class="chat-avatar assistant">AI</div>
                    <div class="chat-bubble assistant">
                        ${isDetected ? 
                            `<p>Conversation reset. I'm ready to answer any questions about <strong>${chatContext.detected_sign}</strong> (${chatContext.confidence_pct} confidence) or Indian traffic laws.</p>` :
                            `<p>Conversation reset. How can I help you with Indian traffic signs, road rules, and Motor Vehicles Act penalties?</p>`
                        }
                    </div>
                </div>
            `;
        });
    }

    // Form Submit Handler
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (text) {
            submitChatMessage(text);
        }
    });

    function submitChatMessage(messageText) {
        // Clear input field
        chatInput.value = '';

        // Append User Bubble
        appendBubble('user', messageText);

        // Append Typing Indicator
        const typingIndicator = appendTypingIndicator();

        // Disable input while generating
        const sendBtn = document.getElementById('chat-send-btn');
        if (sendBtn) sendBtn.disabled = true;

        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: messageText,
                history: chatHistory,
                context: chatContext
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            removeTypingIndicator(typingIndicator);
            if (sendBtn) sendBtn.disabled = false;

            if (data.status === 'success') {
                appendBubble('assistant', data.response, data.source);
                // Track in history
                chatHistory.push({ role: 'user', content: messageText });
                chatHistory.push({ role: 'assistant', content: data.response });
            } else {
                appendBubble('assistant', `⚠️ **Error**: ${data.error || 'Failed to process request.'}`);
            }
        })
        .catch(err => {
            removeTypingIndicator(typingIndicator);
            if (sendBtn) sendBtn.disabled = false;
            appendBubble('assistant', `⚠️ **Network / Server Error**: Could not connect to the traffic rules assistant. (${err.message})`);
        });
    }

    function appendBubble(role, content, source) {
        const row = document.createElement('div');
        row.className = `chat-bubble-row ${role}`;

        const avatar = document.createElement('div');
        avatar.className = `chat-avatar ${role}`;
        avatar.textContent = role === 'user' ? 'You' : 'AI';

        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${role}`;

        if (role === 'user') {
            bubble.textContent = content;
        } else {
            bubble.innerHTML = formatMarkdown(content);
            if (source) {
                const sourceBadge = document.createElement('div');
                sourceBadge.className = 'chat-source-tag';
                sourceBadge.textContent = source === 'gemini' ? '⚡ Powered by Gemini AI' : '📚 Verified Statutory Knowledge Base';
                bubble.appendChild(sourceBadge);
            }
        }

        row.appendChild(avatar);
        row.appendChild(bubble);
        chatConv.appendChild(row);
        scrollToBottom();
    }

    function appendTypingIndicator() {
        const row = document.createElement('div');
        row.className = 'chat-bubble-row assistant typing-indicator-row';
        row.innerHTML = `
            <div class="chat-avatar assistant">AI</div>
            <div class="typing-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
        `;
        chatConv.appendChild(row);
        scrollToBottom();
        return row;
    }

    function removeTypingIndicator(element) {
        if (element && element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }

    function scrollToBottom() {
        chatConv.scrollTop = chatConv.scrollHeight;
    }

    function formatMarkdown(text) {
        if (!text) return '';
        let escaped = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // Code blocks
        escaped = escaped.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        // Inline code
        escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');
        // Headers
        escaped = escaped.replace(/^### (.*$)/gim, '<h4>$1</h4>');
        escaped = escaped.replace(/^## (.*$)/gim, '<h3>$1</h3>');
        escaped = escaped.replace(/^# (.*$)/gim, '<h2>$1</h2>');
        // Bold & italics
        escaped = escaped.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        escaped = escaped.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        // Blockquotes
        escaped = escaped.replace(/^\&gt;\s*(.*$)/gim, '<blockquote>$1</blockquote>');
        // Links: [Text](URL)
        escaped = escaped.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
        // Lists
        escaped = escaped.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
        // Wrap consecutive <li> into <ul>
        escaped = escaped.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>');
        // Paragraphs
        escaped = escaped.replace(/\n\n+/g, '</p><p>');
        escaped = escaped.replace(/\n/g, '<br>');

        return '<p>' + escaped + '</p>';
    }
}
