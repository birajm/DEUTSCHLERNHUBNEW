
// Audio context for better browser compatibility
let audioContext = null;

// Initialize audio context on user interaction
function initAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
}

// Function to handle pronunciation
function pronounce(word) {
  initAudioContext();
  
  const audioPath = `/static/audio/vocabulary/${word.toLowerCase()}.mp3`;
  const audio = new Audio(audioPath);
  
  audio.onerror = function() {
    console.error('Error loading audio file:', audioPath);
    // Change button icon to show error
    const button = document.querySelector(`button[onclick="pronounce('${word}')"]`);
    if (button) {
      button.innerHTML = '<i class="fas fa-volume-mute"></i>';
    }
  };

  audio.onplay = function() {
    const button = document.querySelector(`button[onclick="pronounce('${word}')"]`);
    if (button) {
      button.innerHTML = '<i class="fas fa-volume-up fa-spin"></i>';
    }
  };

  audio.onended = function() {
    const button = document.querySelector(`button[onclick="pronounce('${word}')"]`);
    if (button) {
      button.innerHTML = '<i class="fas fa-volume-up"></i>';
    }
  };

  audio.play().catch(function(error) {
    console.error('Error playing audio:', error);
  });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  // Add click listeners to all audio buttons
  document.querySelectorAll('.play-audio').forEach(button => {
    button.addEventListener('click', function() {
      const word = this.dataset.word;
      if (word) {
        pronounce(word);
      }
    });
  });
});
