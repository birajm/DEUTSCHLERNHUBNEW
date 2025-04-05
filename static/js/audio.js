// Audio context and cache for better performance
let audioContext = null;
let audioCache = new Map();
let synth = window.speechSynthesis;

// Initialize audio context
function initAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioContext;
}

// Global pronounce function for legacy onclick handlers
window.pronounce = function(word) {
  const button = event.currentTarget;
  playAudio(button, word);
};

// Play audio with fallback to AI voice
async function playAudio(button, word) {
  try {
    if (!button) {
      console.error("Button not found for word:", word);
      return;
    }

    const audioPath = `/static/audio/vocabulary/${word.toLowerCase()}.mp3`;
    const context = initAudioContext();

    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    try {
      const response = await fetch(audioPath);
      if (!response.ok) {
        throw new Error('Audio file not found');
      }

      let audioBuffer = audioCache.get(audioPath);
      if (!audioBuffer) {
        const arrayBuffer = await response.arrayBuffer();
        audioBuffer = await context.decodeAudioData(arrayBuffer);
        audioCache.set(audioPath, audioBuffer);
      }

      const source = context.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(context.destination);

      button.innerHTML = '<i class="fas fa-volume-up"></i>';

      source.onended = () => {
        button.innerHTML = '<i class="fas fa-play"></i>';
      };

      source.start(0);
    } catch (error) {
      console.log("Falling back to AI voice synthesis");
      speakText(word);
      button.innerHTML = '<i class="fas fa-play"></i>';
    }
  } catch (error) {
    console.error('Error playing audio:', error);
    button.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
  }
}

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
    const word = button.dataset.word;
    if (word) {
      button.addEventListener('click', function() {
        playAudio(this, word);
      });
    }
  });
});