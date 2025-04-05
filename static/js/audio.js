
// Audio context and cache
let audioContext = null;
let audioCache = new Map();

// Initialize audio context on user interaction
function initAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioContext;
}

// Function to play audio
async function playAudio(button, audioPath) {
  try {
    const context = initAudioContext();
    
    // Show loading state
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    // Try to get from cache first
    let audioBuffer = audioCache.get(audioPath);
    
    if (!audioBuffer) {
      const response = await fetch(audioPath);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const arrayBuffer = await response.arrayBuffer();
      audioBuffer = await context.decodeAudioData(arrayBuffer);
      audioCache.set(audioPath, audioBuffer);
    }
    
    const source = context.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(context.destination);
    
    // Update button state
    button.innerHTML = '<i class="fas fa-volume-up"></i>';
    
    source.onended = () => {
      button.innerHTML = '<i class="fas fa-play"></i>';
    };
    
    source.start(0);
  } catch (error) {
    console.error('Error playing audio:', error);
    button.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
  }
}

// Main click handler for audio buttons
function handleAudioClick(button) {
  const word = button.dataset.word;
  const type = button.dataset.type || 'vocabulary';
  
  if (!word) {
    console.error('No word specified for audio button');
    return;
  }
  
  const path = type === 'conversation' 
    ? `/static/audio/conversations/${word}.mp3`
    : `/static/audio/vocabulary/${word.toLowerCase()}.mp3`;
    
  playAudio(button, path);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.play-audio').forEach(button => {
    button.addEventListener('click', () => handleAudioClick(button));
  });
});
