/**
 * Audio JavaScript for DeutschLernHub
 * Handles audio playback for language learning
 */

// Audio player state
let currentAudio = null;
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

// Initialize audio functionality
function initializeAudio() {
  const audioButtons = document.querySelectorAll('.play-audio');
  audioButtons.forEach(button => {
    button.addEventListener('click', function() {
      const word = this.dataset.word;
      playWordAudio(word, this);
    });
  });
}

// Play word pronunciation
async function playWordAudio(word, button) {
  try {
    if (currentAudio) {
      currentAudio.pause();
    }

    const audioPath = `/static/audio/vocabulary/${word.toLowerCase()}.mp3`;
    const response = await fetch(audioPath);

    if (!response.ok) {
      throw new Error('Audio file not found');
    }

    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);

    currentAudio = source;
    source.start(0);

    // Update button state
    button.innerHTML = '<i class="fas fa-volume-up fa-spin"></i>';
    source.onended = () => {
      button.innerHTML = '<i class="fas fa-volume-up"></i>';
    };
  } catch (error) {
    console.error('Error playing audio:', error);
    button.innerHTML = '<i class="fas fa-volume-mute"></i>';
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializeAudio);