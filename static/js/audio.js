
// Audio context and cache for better performance
let audioContext = null;
let audioCache = new Map();

// Initialize audio context
function initAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioContext;
}

// Play audio with progress tracking
async function playAudio(button, audioPath) {
  try {
    // Initialize context
    const context = initAudioContext();
    
    // Update button state
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    // Check cache first
    let audioBuffer = audioCache.get(audioPath);
    
    if (!audioBuffer) {
      const response = await fetch(audioPath);
      if (!response.ok) {
        throw new Error(`Failed to load audio: ${response.status}`);
      }
      const arrayBuffer = await response.arrayBuffer();
      audioBuffer = await context.decodeAudioData(arrayBuffer);
      audioCache.set(audioPath, audioBuffer);
    }
    
    const source = context.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(context.destination);
    
    // Update UI
    button.innerHTML = '<i class="fas fa-volume-up"></i>';
    
    // Handle completion
    source.onended = () => {
      button.innerHTML = '<i class="fas fa-play"></i>';
    };
    
    source.start(0);
  } catch (error) {
    console.error('Error playing audio:', error);
    button.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
  }
}

// Main function to handle pronunciation
function pronounce(word) {
  const button = document.querySelector(`[data-word="${word}"]`);
  if (!button) {
    console.error('Button not found for word:', word);
    return;
  }
  
  const audioPath = `/static/audio/vocabulary/${word.toLowerCase()}.mp3`;
  playAudio(button, audioPath);
}

// Initialize audio buttons
document.addEventListener('DOMContentLoaded', function() {
  // Handle vocabulary pronunciation buttons
  document.querySelectorAll('.play-audio[data-word]').forEach(button => {
    button.addEventListener('click', function() {
      const word = this.dataset.word;
      if (word) {
        pronounce(word);
      }
    });
  });
  
  // Handle conversation audio buttons
  document.querySelectorAll('.play-audio[data-type="conversation"]').forEach(button => {
    button.addEventListener('click', function() {
      const conversationId = this.dataset.word;
      if (conversationId) {
        const audioPath = `/static/audio/conversations/${conversationId}.mp3`;
        playAudio(this, audioPath);
      }
    });
  });
});
