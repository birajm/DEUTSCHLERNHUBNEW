
// Audio context and cache for better performance
let audioContext = null;
let audioElements = new Map();

// Initialize audio context
function initAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioContext;
}

// Function to play audio in listening exercises
function playListeningAudio(audioButton) {
  const audioPath = audioButton.dataset.audio;
  if (!audioPath) {
    console.error('No audio path specified');
    return;
  }

  // Stop any currently playing audio
  audioElements.forEach((audio) => {
    audio.pause();
    audio.currentTime = 0;
  });
  audioElements.clear();

  const audio = new Audio(audioPath);
  audioElements.set(audioPath, audio);
  
  const progressBar = audioButton.closest('.audio-player').querySelector('.progress-bar');
  const timeDisplay = audioButton.closest('.audio-player').querySelector('.time-display');
  
  audioButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

  audio.addEventListener('loadedmetadata', () => {
    updateTimeDisplay(timeDisplay, 0, audio.duration);
  });

  audio.addEventListener('timeupdate', () => {
    const progress = (audio.currentTime / audio.duration) * 100;
    progressBar.style.width = `${progress}%`;
    updateTimeDisplay(timeDisplay, audio.currentTime, audio.duration);
  });

  audio.addEventListener('canplay', () => {
    audioButton.innerHTML = '<i class="fas fa-pause"></i>';
    audio.play().catch(error => {
      console.error('Error playing audio:', error);
      audioButton.innerHTML = '<i class="fas fa-play"></i>';
    });
  });

  audio.addEventListener('ended', () => {
    audioButton.innerHTML = '<i class="fas fa-play"></i>';
    progressBar.style.width = '0%';
    audioElements.delete(audioPath);
  });

  audio.addEventListener('error', (e) => {
    console.error('Error loading audio file:', audioPath);
    audioButton.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
    audioElements.delete(audioPath);
  });
}

function updateTimeDisplay(element, currentTime, duration) {
  if (!element) return;
  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };
  element.textContent = `${formatTime(currentTime)} / ${formatTime(duration)}`;
}

// Initialize when document loads
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.audio-play-btn').forEach(button => {
    button.addEventListener('click', () => playListeningAudio(button));
  });
});
