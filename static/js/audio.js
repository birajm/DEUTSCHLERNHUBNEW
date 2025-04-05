// Audio context and cache for better performance
let audioContext = null;
let audioCache = new Map();
let audioElements = new Map();

// Initialize audio context
function initAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioContext;
}

// Function to play audio in listening exercises
function playListeningAudio(audioPath, button) {
  if (!button) return;

  const existingAudio = audioElements.get(audioPath);
  if (existingAudio) {
    existingAudio.pause();
    existingAudio.currentTime = 0;
    audioElements.delete(audioPath);
    button.innerHTML = '<i class="fas fa-play"></i>';
    return;
  }

  const audio = new Audio(audioPath);
  audioElements.set(audioPath, audio);

  button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

  audio.addEventListener('canplay', () => {
    button.innerHTML = '<i class="fas fa-pause"></i>';
    audio.play();
  });

  audio.addEventListener('ended', () => {
    button.innerHTML = '<i class="fas fa-play"></i>';
    audioElements.delete(audioPath);
  });

  audio.addEventListener('error', () => {
    console.error('Error playing audio:', audioPath);
    button.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
    audioElements.delete(audioPath);
  });
}

// Global pronounce function for legacy onclick handlers
window.pronounce = function(word) {
  const button = event.currentTarget;
  const audioPath = `/static/audio/vocabulary/${word.toLowerCase()}.mp3`;
  playListeningAudio(audioPath, button);
};


// Text-to-speech function
function speakText(text) {
  if (synth.speaking) {
    synth.cancel();
  }

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'de-DE';
  utterance.rate = 0.9;
  synth.speak(utterance);
}

// Initialize when document loads
document.addEventListener('DOMContentLoaded', function() {
  // Handle all audio buttons
  document.querySelectorAll('.play-audio').forEach(button => {
    const audioPath = button.dataset.audio;
    if (audioPath) {
      button.addEventListener('click', function() {
        playListeningAudio(audioPath, this);
      });
    }
  });

  // Handle vocabulary pronunciation buttons
  document.querySelectorAll('.pronounce-word').forEach(button => {
    const word = button.dataset.word;
    if (word) {
      button.addEventListener('click', function() {
        const audioPath = `/static/audio/vocabulary/${word.toLowerCase()}.mp3`;
        playListeningAudio(audioPath, this);
      });
    }
  });
});