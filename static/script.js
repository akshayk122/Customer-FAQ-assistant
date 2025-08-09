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
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

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
        isListening = false;
        micButton.textContent = '🎤';
        if (liveTranscript.textContent.trim()) {
            sendTextQuery(liveTranscript.textContent.trim(), true);
            liveTranscript.textContent = '';
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        isListening = false;
        micButton.textContent = '🎤';
    };
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
    if (!recognition) setupRecognition();

    // Stop bot speech before listening
    if (botAudio && !botAudio.paused) {
        botAudio.pause();
        botAudio.currentTime = 0;
    }

    if (!isListening) {
        isListening = true;
        micButton.textContent = '🔴';
        liveTranscript.textContent = 'Listening...';
        recognition.start();
    } else {
        recognition.stop();
    }
});

// Enter key to submit
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendButton.click();
});
