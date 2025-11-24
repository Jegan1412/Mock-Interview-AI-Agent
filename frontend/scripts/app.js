class InterviewApp {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.currentMode = 'text'; // Start with text mode for reliability
        this.apiBaseUrl = ''; // Empty string for same-origin requests
        
        this.initializeElements();
        this.attachEventListeners();
    }

    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    initializeElements() {
        // Sections
        this.setupSection = document.getElementById('setup-section');
        this.interviewSection = document.getElementById('interview-section');
        this.feedbackSection = document.getElementById('feedback-section');

        // Setup elements
        this.roleSelect = document.getElementById('role-select');
        this.resumeUpload = document.getElementById('resume-upload');
        this.modeRadios = document.querySelectorAll('input[name="mode"]');
        this.startInterviewBtn = document.getElementById('start-interview');

        // Interview elements
        this.currentRoleSpan = document.getElementById('current-role');
        this.endInterviewBtn = document.getElementById('end-interview');
        this.conversationDiv = document.getElementById('conversation');
        this.voiceControls = document.getElementById('voice-controls');
        this.textInput = document.getElementById('text-input');
        this.recordBtn = document.getElementById('record-btn');
        this.recordingStatus = document.getElementById('recording-status');
        this.answerInput = document.getElementById('answer-input');
        this.submitAnswerBtn = document.getElementById('submit-answer');

        // Feedback elements
        this.feedbackContent = document.getElementById('feedback-content');
        this.newInterviewBtn = document.getElementById('new-interview');
    }

    attachEventListeners() {
        this.startInterviewBtn.addEventListener('click', () => this.startInterview());
        this.endInterviewBtn.addEventListener('click', () => this.endInterview());
        this.recordBtn.addEventListener('click', () => this.toggleRecording());
        this.submitAnswerBtn.addEventListener('click', () => this.submitTextAnswer());
        this.newInterviewBtn.addEventListener('click', () => this.resetApp());

        // Enter key for text input
        this.answerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.submitTextAnswer();
            }
        });

        // Mode change
        this.modeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentMode = e.target.value;
                this.updateInputMode();
            });
        });
    }

    async startInterview() {
        console.log('🎯 Starting interview...');
        
        const role = this.roleSelect.value;
        this.currentRoleSpan.textContent = `Role: ${role}`;

        // Show loading state
        this.startInterviewBtn.textContent = 'Starting Interview...';
        this.startInterviewBtn.disabled = true;

        try {
            // Upload resume if provided
            if (this.resumeUpload.files.length > 0) {
                await this.uploadResume();
            }

            // Start interview session
            const response = await this.apiCall('/api/start_interview', {
                session_id: this.sessionId,
                role: role
            });

            console.log('✅ Interview started:', response);

            if (response.success) {
                this.showSection(this.interviewSection);
                this.conversationDiv.innerHTML = ''; // Clear welcome message
                this.addMessage(response.question, 'question');
                this.updateInputMode();
            }
        } catch (error) {
            console.error('❌ Error starting interview:', error);
            this.showError('Failed to start interview. Please make sure the server is running. Error: ' + error.message);
        } finally {
            // Reset button state
            this.startInterviewBtn.textContent = 'Start Mock Interview';
            this.startInterviewBtn.disabled = false;
        }
    }

    updateInputMode() {
        if (this.currentMode === 'voice') {
            this.voiceControls.classList.remove('hidden');
            this.textInput.classList.add('hidden');
            this.recordingStatus.textContent = 'Voice mode: Click microphone to record';
        } else {
            this.voiceControls.classList.add('hidden');
            this.textInput.classList.remove('hidden');
            this.answerInput.focus();
        }
    }

    async toggleRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            this.stopRecording();
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: true
            });
            
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                await this.processVoiceAnswer(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.recordBtn.textContent = '⏹️ Stop Recording';
            this.recordBtn.classList.add('recording');
            this.recordingStatus.textContent = '🎤 Recording... Speak now!';

        } catch (error) {
            this.showError('Microphone access denied. Please allow microphone access.');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.recordBtn.textContent = '🎤 Start Recording';
            this.recordBtn.classList.remove('recording');
            this.recordingStatus.textContent = '🔄 Processing...';
        }
    }

    async processVoiceAnswer(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('session_id', this.sessionId);

            const response = await fetch('/api/process-voice-answer', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                this.addMessage(data.answer_text, 'answer');
                this.addMessage(data.next_question, 'question');
                await this.speakText(data.next_question);
                this.recordingStatus.textContent = '✅ Answer recorded!';
            } else {
                throw new Error(data.error);
            }

        } catch (error) {
            this.showError('Voice processing error: ' + error.message);
            this.recordingStatus.textContent = '❌ Processing failed';
        }
    }

    async submitTextAnswer() {
        const answer = this.answerInput.value.trim();
        if (!answer) {
            this.showError('Please enter your answer');
            return;
        }

        this.answerInput.value = '';
        await this.submitAnswer(answer);
    }

    async submitAnswer(answer) {
        this.addMessage(answer, 'answer');
        this.disableInput(true);

        try {
            const response = await this.apiCall('/api/submit_answer', {
                session_id: this.sessionId,
                answer: answer
            });

            if (response.success) {
                this.addMessage(response.question, 'question');
                if (this.currentMode === 'voice') {
                    await this.speakText(response.question);
                }
            }
        } catch (error) {
            this.showError('Failed to submit answer: ' + error.message);
        } finally {
            this.disableInput(false);
        }
    }

    disableInput(disabled) {
        if (this.currentMode === 'voice') {
            this.recordBtn.disabled = disabled;
        } else {
            this.submitAnswerBtn.disabled = disabled;
            this.answerInput.disabled = disabled;
            this.submitAnswerBtn.textContent = disabled ? 'Processing...' : 'Submit Answer';
        }
    }

    async endInterview() {
        this.disableInput(true);

        try {
            const response = await this.apiCall('/api/end_interview', {
                session_id: this.sessionId
            });

            if (response.success) {
                this.showFeedback(response.feedback);
            }
        } catch (error) {
            this.showError('Failed to end interview: ' + error.message);
        } finally {
            this.disableInput(false);
        }
    }

    showFeedback(feedback) {
        this.feedbackContent.textContent = feedback;
        this.showSection(this.feedbackSection);
    }

    async uploadResume() {
        const formData = new FormData();
        formData.append('resume', this.resumeUpload.files[0]);
        formData.append('session_id', this.sessionId);

        try {
            await fetch('/api/upload_resume', {
                method: 'POST',
                body: formData
            });
        } catch (error) {
            console.warn('Resume upload failed:', error);
        }
    }

    async speakText(text) {
        try {
            const response = await this.apiCall('/api/text-to-speech', {
                text: text
            });

            if (response.success && response.audio) {
                const audio = new Audio('data:audio/wav;base64,' + response.audio);
                await audio.play();
            }
        } catch (error) {
            console.warn('Text-to-speech failed:', error);
        }
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = content;
        this.conversationDiv.appendChild(messageDiv);
        this.conversationDiv.scrollTop = this.conversationDiv.scrollHeight;
    }

    showSection(section) {
        document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
        section.classList.remove('hidden');
    }

    resetApp() {
        this.sessionId = this.generateSessionId();
        this.conversationDiv.innerHTML = '<div class="message question">Welcome to your mock interview!</div>';
        this.answerInput.value = '';
        this.resumeUpload.value = '';
        this.showSection(this.setupSection);
    }

    async apiCall(endpoint, data) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    showError(message) {
        alert('❌ Error: ' + message);
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new InterviewApp();
});