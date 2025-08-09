let recognition;
let isListening = false;
let finalTranscript = '';
let interim = '';
let botAudio = null;  // Track current bot audio

const micButton = document.getElementById('mic-button');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const liveTranscript = document.getElementById('live-transcript');
const chatBox = document.getElementById('chat-box');

function setupRecognition() {
    // Check if speech recognition is supported
    if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
        console.error('Speech recognition not supported');
        micButton.disabled = true;
        micButton.title = 'Speech recognition not supported in this browser';
        return false;
    }

    try {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        
        // Try more compatible settings first
        recognition.continuous = false; // Start with non-continuous for better compatibility
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        recognition.maxAlternatives = 1;
        
        // Add some additional settings for better compatibility
        if ('serviceURI' in recognition) {
            recognition.serviceURI = 'wss://www.google.com/speech-api/full-duplex/v1/up';
        }
        
        console.log('Speech recognition initialized with settings:', {
            continuous: recognition.continuous,
            interimResults: recognition.interimResults,
            lang: recognition.lang,
            maxAlternatives: recognition.maxAlternatives
        });
        
    } catch (e) {
        console.error('Failed to create speech recognition:', e);
        micButton.disabled = true;
        micButton.title = 'Speech recognition failed to initialize';
        return false;
    }

    recognition.onresult = (event) => {
        finalTranscript = '';
        interim = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript = transcript;
                interim = '';
            } else {
                interim = transcript;
            }
        }
        liveTranscript.textContent = finalTranscript + interim;
    };

    recognition.onend = () => {
        console.log('Recognition ended. isListening:', isListening, 'finalTranscript:', finalTranscript);
        
        if (isListening) {
            // Recognition stopped automatically, restart it after a short delay
            setTimeout(() => {
                if (isListening) { // Check again in case user stopped it
                    try {
                        console.log('Attempting to restart recognition...');
                        recognition.start();
                    } catch (e) {
                        console.log('Recognition restart failed:', e);
                        isListening = false;
                        micButton.innerHTML = '<i class="fas fa-microphone"></i>';
                        micButton.classList.remove('recording');
                        liveTranscript.textContent = 'Speech recognition stopped. Click microphone to try again.';
                        setTimeout(() => {
                            liveTranscript.textContent = 'Live transcript will appear here...';
                        }, 3000);
                    }
                }
            }, 100);
        } else {
            // User manually stopped, process the transcript
            micButton.innerHTML = '<i class="fas fa-microphone"></i>';
            micButton.classList.remove('recording');
            if (finalTranscript.trim()) {
                console.log('Processing final transcript:', finalTranscript);
                sendTextQuery(finalTranscript.trim(), true);
                liveTranscript.textContent = '';
                finalTranscript = '';
                interim = '';
            } else {
                liveTranscript.textContent = 'No speech detected. Try speaking again.';
                setTimeout(() => {
                    liveTranscript.textContent = 'Live transcript will appear here...';
                }, 2000);
            }
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error details:', {
            error: event.error,
            type: event.type,
            timeStamp: event.timeStamp,
            userAgent: navigator.userAgent,
            protocol: window.location.protocol,
            isSecure: window.isSecureContext
        });
        
        isListening = false;
        micButton.innerHTML = '<i class="fas fa-microphone"></i>';
        micButton.classList.remove('recording');
        
        let errorMessage = '';
        let shouldShowTroubleshooting = false;
        
        switch (event.error) {
            case 'not-allowed':
            case 'service-not-allowed':
                errorMessage = 'Microphone access denied. Please allow microphone access in your browser settings.';
                break;
            case 'network':
                errorMessage = 'Network error. Speech recognition requires internet connection.';
                shouldShowTroubleshooting = true;
                break;
            case 'no-speech':
                errorMessage = 'No speech detected. Please speak clearly into your microphone.';
                break;
            case 'audio-capture':
                errorMessage = 'Microphone not found. Please check your microphone connection.';
                break;
            case 'language-not-supported':
                errorMessage = 'Language not supported. Trying with default settings...';
                break;
            case 'aborted':
                errorMessage = 'Speech recognition was stopped.';
                break;
            default:
                errorMessage = `Speech recognition error: ${event.error}`;
                shouldShowTroubleshooting = true;
        }
        
        liveTranscript.textContent = errorMessage;
        
        if (shouldShowTroubleshooting) {
            setTimeout(() => {
                if (!window.isSecureContext) {
                    liveTranscript.textContent = 'Try using HTTPS instead of HTTP for better speech recognition support.';
                } else {
                    liveTranscript.textContent = 'Try refreshing the page or using Chrome browser for better support.';
                }
            }, 2000);
        }
        
        setTimeout(() => {
            liveTranscript.textContent = 'Live transcript will appear here...';
        }, 5000);
    };
    
    return true;
}

function addMessage(message, sender) {
    const msg = document.createElement('div');
    msg.className = sender;
    msg.textContent = `${sender === 'user' ? 'You' : 'Bot'}: ${message}`;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendTextQuery(query, useTTS = false) {
    addMessage(query, 'user');
    userInput.value = '';
    liveTranscript.textContent = 'Thinking...';

    const textRes = await fetch('/api/ask-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: query })
    });
    const data = await textRes.json();
    addMessage(data.answer, 'bot');

    if (useTTS) {
        const ttsRes = await fetch('/api/ask-tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: data.answer })
        });

        if (!ttsRes.ok) {
            console.error('TTS error:', await ttsRes.text());
            return;
        }

        const blob = await ttsRes.blob();
        const audioUrl = URL.createObjectURL(blob);

        // Stop any currently playing bot audio before playing new
        if (botAudio) {
            botAudio.pause();
            botAudio.currentTime = 0;
        }

        botAudio = new Audio(audioUrl);
        botAudio.play();
    }
}

async function dummyAudioUpload() {
    const dummyBlob = new Blob([new Uint8Array([1])], { type: "audio/webm" });
    const formData = new FormData();
    const file = new File([dummyBlob], "dummy.webm", { type: "audio/webm" });
    formData.append("file", file);
    return formData;
}

// Send button click
sendButton.addEventListener('click', () => {
    const input = userInput.value.trim();
    if (input) sendTextQuery(input, false);
});

// Mic button click
micButton.addEventListener('click', () => {
    if (!recognition) {
        if (!setupRecognition()) {
            liveTranscript.textContent = 'Speech recognition is not available in this browser.';
            setTimeout(() => {
                liveTranscript.textContent = 'Live transcript will appear here...';
            }, 3000);
            return;
        }
    }

    // Stop bot speech before listening
    if (botAudio && !botAudio.paused) {
        botAudio.pause();
        botAudio.currentTime = 0;
    }

    if (!isListening) {
        isListening = true;
        micButton.innerHTML = 'Listening';
        micButton.classList.add('recording');
        liveTranscript.textContent = 'Listening...';
        finalTranscript = '';
        interim = '';
        
        try {
            recognition.start();
        } catch (e) {
            console.error('Failed to start recognition:', e);
            isListening = false;
            micButton.innerHTML = '<i class="fas fa-microphone"></i>';
            micButton.classList.remove('recording');
            liveTranscript.textContent = 'Live transcript will appear here...';
        }
    } else {
        isListening = false;
        recognition.stop();
        liveTranscript.textContent = 'Processing...';
    }
});

// Enter key to submit
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendButton.click();
});
