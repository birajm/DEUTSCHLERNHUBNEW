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

// Play audio with fallback to AI voice
async function playAudio(button, word) {
  try {
    const audioPath = `/static/audio/vocabulary/${word.toLowerCase()}.mp3`;
    const context = initAudioContext();

    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    try {
      let audioBuffer = audioCache.get(audioPath);

      if (!audioBuffer) {
        const response = await fetch(audioPath);
        if (!response.ok) throw new Error('Audio file not found');
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
  document.querySelectorAll('.play-audio, [onclick*="pronounce"]').forEach(button => {
    const word = button.dataset.word || button.getAttribute('onclick')?.match(/pronounce\(['"](.+?)['"]\)/)?.[1];

    if (word) {
      // Remove old onclick handler and add new one
      button.removeAttribute('onclick');
      button.addEventListener('click', function() {
        playAudio(this, word);
      });
    }
  });
});

//The functions below are removed because they are not used anymore.
/*
// Extract text from audio path
function getTextFromPath(path) {
  const filename = path.split('/').pop();
  return filename.replace('.mp3', '').replace(/_/g, ' ');
}

//This whole block is removed because the functionality is replaced by the new event listener above
document.addEventListener('DOMContentLoaded', function() {
  // Handle all play-audio buttons
  document.querySelectorAll('.play-audio').forEach(button => {
    button.addEventListener('click', function() {
      const word = this.dataset.word;
      if (!word) return;
      const audioPath = `/static/audio/vocabulary/${word.toLowerCase()}.mp3`;
      playAudio(this, audioPath, word);
    });
  });
});

//This whole block is removed because the functionality is replaced by the new event listener above
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
      const text = this.dataset.text || '';
      if (conversationId) {
        const audioPath = `/static/audio/conversations/${conversationId}.mp3`;
        playAudio(this, audioPath, text);
      }
    });
  });
});
*/