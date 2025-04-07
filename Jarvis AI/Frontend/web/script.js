// Global variables
let isListening = false;
let isRecording = false;
let isVoiceActive = false;
let messages = [];
let jarvis3d = null;

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const micButton = document.getElementById('micButton');
const statusIndicator = document.getElementById('statusIndicator');
const jarvisGif = document.getElementById('jarvisGif');
const voiceBtn = document.getElementById('voiceBtn');
const searchBtn = document.getElementById('searchBtn');
const youtubeBtn = document.getElementById('youtubeBtn');
const searchModal = document.getElementById('searchModal');
const youtubeModal = document.getElementById('youtubeModal');
const searchInput = document.getElementById('searchInput');
const youtubeInput = document.getElementById('youtubeInput');
const searchSubmit = document.getElementById('searchSubmit');
const youtubeSubmit = document.getElementById('youtubeSubmit');

// Environment variables
const env = {
    AssistantName: 'Jarvis',
    InitialPath: '../Files',
    TempDirPath: '../Temp',
    GraphicsDirPath: '../Graphics'
};

// Utility functions
function AnswerModifier(answer) {
    const lines = answer.split('\n');
    const nonEmptyLines = lines.filter(line => line.trim());
    return nonEmptyLines.join('\n');
}

function QueryModifier(query) {
    const newQuery = query.toLowerCase().trim();
    const queryWords = newQuery.split(' ');
    const questionWords = ["what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how"];
    
    if (questionWords.some(word => newQuery.includes(word + ' '))) {
        if (queryWords[queryWords.length - 1].endsWith(['.', '?', '!'])) {
            return newQuery.slice(0, -1) + '?';
        }
        return newQuery + '?';
    }
    
    if (queryWords[queryWords.length - 1].endsWith(['.', '?', '!'])) {
        return newQuery.slice(0, -1) + '.';
    }
    return newQuery + '.';
}

function SetMicrophoneStatus(command) {
    localStorage.setItem('micStatus', command);
    updateStatusIndicator();
}

function GetMicrophoneStatus() {
    return localStorage.getItem('micStatus') || 'False';
}

function SetAssistantStatus(status) {
    localStorage.setItem('assistantStatus', status);
    updateJarvisAnimation(status);
}

function GetAssistantStatus() {
    return localStorage.getItem('assistantStatus') || 'Idle';
}

function ShowTextToScreen(text) {
    localStorage.setItem('responses', text);
    addMessage('assistant', text);
}

// Chat functions
function addMessage(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Speech recognition
let recognition = null;

function initSpeechRecognition() {
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            addMessage('user', transcript);
            sendToBackend(transcript);
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            MicButtonClosed();
        };
    } else {
        console.error('Speech recognition not supported');
    }
}

// Backend communication
async function sendToBackend(query) {
    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        ShowTextToScreen(data.response);
    } catch (error) {
        console.error('Error communicating with backend:', error);
    }
}

// 3D Animation functions
function init3DAnimations() {
    jarvis3d = document.querySelector('.jarvis-3d');
    
    // Add mouse movement tracking for 3D effect
    document.addEventListener('mousemove', (e) => {
        const { clientX, clientY } = e;
        const { innerWidth, innerHeight } = window;
        
        const x = (clientX / innerWidth - 0.5) * 20;
        const y = (clientY / innerHeight - 0.5) * 20;
        
        jarvis3d.style.transform = `rotateX(${y}deg) rotateY(${x}deg)`;
    });
}

function updateStatusIndicator() {
    const status = GetMicrophoneStatus();
    statusIndicator.classList.toggle('active', status === 'True');
}

function updateJarvisAnimation(status) {
    const gif = document.getElementById('jarvisGif');
    const lights = document.querySelector('.jarvis-lights');
    
    switch(status) {
        case 'Listening':
            gif.style.animation = 'pulse 1s infinite';
            lights.style.animation = 'blink 0.5s infinite';
            break;
        case 'Processing':
            gif.style.animation = 'pulse 0.5s infinite';
            lights.style.animation = 'blink 0.2s infinite';
            break;
        default:
            gif.style.animation = 'pulse 2s infinite';
            lights.style.animation = 'blink 2s infinite';
    }
}

// Event listeners
micButton.addEventListener('click', () => {
    if (!isListening) {
        MicButtonInitiated();
        recognition.start();
        micButton.classList.add('active');
        statusIndicator.classList.add('active');
    } else {
        MicButtonClosed();
        recognition.stop();
        micButton.classList.remove('active');
        statusIndicator.classList.remove('active');
    }
    isListening = !isListening;
});

voiceBtn.addEventListener('click', () => {
    isVoiceActive = !isVoiceActive;
    voiceBtn.classList.toggle('active', isVoiceActive);
    if (isVoiceActive) {
        SetAssistantStatus('Listening');
        recognition.start();
    } else {
        recognition.stop();
        SetAssistantStatus('Idle');
    }
});

searchBtn.addEventListener('click', () => {
    searchModal.style.display = 'block';
});

youtubeBtn.addEventListener('click', () => {
    youtubeModal.style.display = 'block';
});

searchSubmit.addEventListener('click', async () => {
    const query = searchInput.value;
    if (query) {
        try {
            const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
            const data = await response.json();
            ShowTextToScreen(data.results);
        } catch (error) {
            console.error('Error searching:', error);
            ShowTextToScreen('Error occurred while searching');
        }
        searchModal.style.display = 'none';
        searchInput.value = '';
    }
});

youtubeSubmit.addEventListener('click', async () => {
    const query = youtubeInput.value;
    if (query) {
        try {
            const response = await fetch(`/api/youtube?query=${encodeURIComponent(query)}`);
            const data = await response.json();
            ShowTextToScreen(data.results);
            window.open(data.url, '_blank');
        } catch (error) {
            console.error('Error searching YouTube:', error);
            ShowTextToScreen('Error occurred while searching YouTube');
        }
        youtubeModal.style.display = 'none';
        youtubeInput.value = '';
    }
});

document.querySelectorAll('.close-modal').forEach(button => {
    button.addEventListener('click', () => {
        const modal = button.closest('.modal');
        modal.style.display = 'none';
    });
});

// Initialize app
function initApp() {
    initSpeechRecognition();
    init3DAnimations();
    
    // Load saved messages
    const savedMessages = localStorage.getItem('messages');
    if (savedMessages) {
        messages = JSON.parse(savedMessages);
        messages.forEach(msg => addMessage(msg.sender, msg.content));
    }
    
    // Load saved status
    const savedStatus = localStorage.getItem('assistantStatus');
    if (savedStatus) {
        SetAssistantStatus(savedStatus);
    }
    
    // Load saved mic status
    const savedMicStatus = localStorage.getItem('micStatus');
    if (savedMicStatus) {
        SetMicrophoneStatus(savedMicStatus);
    }
}

// Start the app
initApp();