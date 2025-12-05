class VoiceRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.stream = null;
    }

    async initialize() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });

            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                this.handleRecordingStop();
            };

            return true;
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Could not access microphone. Please grant permission and try again.');
            return false;
        }
    }

    async startRecording() {
        if (!this.mediaRecorder) {
            const initialized = await this.initialize();
            if (!initialized) return false;
        }

        this.audioChunks = [];
        this.mediaRecorder.start();
        this.isRecording = true;

        return true;
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;

            // Stop all tracks
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }
        }
    }

    handleRecordingStop() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });

        // Create audio player
        const audioUrl = URL.createObjectURL(audioBlob);
        this.displayAudioPlayer(audioUrl);

        // Prepare for upload
        this.prepareUpload(audioBlob);
    }

    displayAudioPlayer(audioUrl) {
        const playerContainer = document.getElementById('audio-player-container');

        if (playerContainer) {
            playerContainer.innerHTML = `
                <div class="bg-white p-4 rounded-lg shadow-md mt-4">
                    <p class="text-sm text-gray-600 mb-2">Recording Preview:</p>
                    <audio controls class="w-full">
                        <source src="${audioUrl}" type="audio/webm">
                        Your browser does not support the audio element.
                    </audio>
                    <button id="upload-voice-btn" class="mt-3 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition duration-300">
                        <i class="fas fa-upload mr-2"></i> Save Voice Message
                    </button>
                </div>
            `;

            // Add upload handler
            const uploadBtn = document.getElementById('upload-voice-btn');
            if (uploadBtn) {
                uploadBtn.addEventListener('click', () => {
                    this.uploadRecording();
                });
            }
        }
    }

    prepareUpload(audioBlob) {
        this.recordingBlob = audioBlob;
    }

    async uploadRecording() {
        if (!this.recordingBlob) {
            alert('No recording to upload');
            return;
        }

        const formData = new FormData();
        formData.append('voice_recording', this.recordingBlob, 'voice_message.webm');

        // Get wish ID if available
        const wishIdInput = document.getElementById('wish-id');
        if (wishIdInput) {
            formData.append('wish_id', wishIdInput.value);
        }

        try {
            const response = await fetch('/save-voice/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                alert('Voice message saved successfully!');
                // Optionally redirect or update UI
            } else {
                alert('Error saving voice message: ' + data.message);
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Error uploading voice message');
        }
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    updateRecordingTimer(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}

// Initialize voice recorder when document is ready
document.addEventListener('DOMContentLoaded', function() {
    const startRecordBtn = document.getElementById('start-record-btn');
    const stopRecordBtn = document.getElementById('stop-record-btn');
    const recordingIndicator = document.getElementById('recording-indicator');
    const recordingTimer = document.getElementById('recording-timer');

    if (startRecordBtn && stopRecordBtn) {
        const recorder = new VoiceRecorder();
        let timerInterval = null;
        let seconds = 0;

        startRecordBtn.addEventListener('click', async function() {
            const started = await recorder.startRecording();

            if (started) {
                startRecordBtn.classList.add('hidden');
                stopRecordBtn.classList.remove('hidden');

                if (recordingIndicator) {
                    recordingIndicator.classList.remove('hidden');
                }

                // Start timer
                seconds = 0;
                timerInterval = setInterval(() => {
                    seconds++;
                    if (recordingTimer) {
                        recordingTimer.textContent = recorder.updateRecordingTimer(seconds);
                    }
                }, 1000);
            }
        });

        stopRecordBtn.addEventListener('click', function() {
            recorder.stopRecording();

            startRecordBtn.classList.remove('hidden');
            stopRecordBtn.classList.add('hidden');

            if (recordingIndicator) {
                recordingIndicator.classList.add('hidden');
            }

            // Stop timer
            if (timerInterval) {
                clearInterval(timerInterval);
            }
        });
    }
});
