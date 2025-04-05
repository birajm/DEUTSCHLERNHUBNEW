/**
 * Audio JavaScript for DeutschLernHub
 * Handles audio playback for language learning
 */

// Keep track of all audio elements on the page
let audioElements = [];

/**
 * Initialize all audio players on the page
 */
function initializeAudioPlayers() {
    const playButtons = document.querySelectorAll('.audio-play-btn');
    
    playButtons.forEach(playButton => {
        const container = playButton.closest('.audio-player');
        const progressBar = container.querySelector('.audio-progress');
        const audioElement = container.querySelector('audio');
        
        if (playButton && progressBar && audioElement) {
            setupAudioPlayer(playButton, progressBar, audioElement);
            audioElements.push(audioElement);
        }
    });
}

/**
 * Set up a single audio player with event listeners
 * @param {HTMLElement} playButton - The play/pause button
 * @param {HTMLElement} progressBar - The progress bar element
 * @param {HTMLAudioElement} audioElement - The audio element
 */
function setupAudioPlayer(playButton, progressBar, audioElement) {
    // Play/pause button click
    playButton.addEventListener('click', function() {
        if (audioElement.paused) {
            pauseAllAudio(); // Pause any other playing audio
            audioElement.play();
            playButton.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
            audioElement.pause();
            playButton.innerHTML = '<i class="fas fa-play"></i>';
        }
    });
    
    // Update progress bar as audio plays
    audioElement.addEventListener('timeupdate', function() {
        const progress = (audioElement.currentTime / audioElement.duration) * 100;
        progressBar.style.width = progress + '%';
    });
    
    // Reset button when audio ends
    audioElement.addEventListener('ended', function() {
        playButton.innerHTML = '<i class="fas fa-play"></i>';
        progressBar.style.width = '0%';
    });
}

/**
 * Create and attach a new audio player for a pronunciation example
 * @param {string} audioSrc - The audio file source
 * @param {string} containerId - The ID of the container to attach the player to
 * @param {string} word - The German word being pronounced (for accessibility)
 */
function createAudioPlayer(audioSrc, containerId, word) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Create player HTML
    const playerHTML = `
        <div class="audio-player">
            <audio src="${audioSrc}" preload="none" aria-label="Pronunciation of ${word}"></audio>
            <button class="btn btn-sm btn-primary audio-play-btn" aria-label="Play pronunciation">
                <i class="fas fa-play"></i>
            </button>
            <div class="audio-progress-container">
                <div class="audio-progress" style="width: 0%"></div>
            </div>
        </div>
    `;
    
    // Add to container
    container.innerHTML = playerHTML;
    
    // Initialize this player
    const playButton = container.querySelector('.audio-play-btn');
    const progressBar = container.querySelector('.audio-progress');
    const audioElement = container.querySelector('audio');
    
    if (playButton && progressBar && audioElement) {
        setupAudioPlayer(playButton, progressBar, audioElement);
        audioElements.push(audioElement);
    }
}

/**
 * Pause all audio elements on the page
 * Used when starting a new audio to prevent multiple audios playing at once
 */
function pauseAllAudio() {
    audioElements.forEach(audio => {
        if (!audio.paused) {
            audio.pause();
            const container = audio.closest('.audio-player');
            if (container) {
                const playButton = container.querySelector('.audio-play-btn');
                if (playButton) {
                    playButton.innerHTML = '<i class="fas fa-play"></i>';
                }
            }
        }
    });
    
    // Also pause any currently playing pronunciation audio
    const pronunciationAudio = document.getElementById('pronunciation-audio');
    if (pronunciationAudio && !pronunciationAudio.paused) {
        pronunciationAudio.pause();
    }
}

/**
 * Load audio for a pronunciation example
 * Can be called directly from HTML onclick events
 * @param {string} word - The German word to pronounce
 * @param {HTMLElement} element - The triggering element
 */
function pronounce(word, element) {
    // Create or get the audio element
    let pronunciationAudio = document.getElementById('pronunciation-audio');
    
    if (!pronunciationAudio) {
        pronunciationAudio = document.createElement('audio');
        pronunciationAudio.id = 'pronunciation-audio';
        document.body.appendChild(pronunciationAudio);
    }
    
    // Set loading state on button
    if (element) {
        const originalHTML = element.innerHTML;
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        element.disabled = true;
        
        // Reset button after audio finishes or fails
        const resetButton = () => {
            element.innerHTML = originalHTML;
            element.disabled = false;
        };
        
        pronunciationAudio.onended = resetButton;
        pronunciationAudio.onerror = resetButton;
    }
    
    // Pause any other audio
    pauseAllAudio();
    
    // Try to load from our own audio files first
    const audioPath = `/static/audio/vocabulary/${word.toLowerCase()}.mp3`;
    
    // Set the src and play
    pronunciationAudio.src = audioPath;
    pronunciationAudio.play().catch(error => {
        console.error('Error playing audio:', error);
        if (element) {
            element.innerHTML = originalHTML;
            element.disabled = false;
        }
        
        // If we can't play our own audio file, could fallback to a text-to-speech API
        alert('Audio pronunciation not available for this word.');
    });
}

// Initialize audio players when DOM content loaded
document.addEventListener('DOMContentLoaded', initializeAudioPlayers);

// Function to play audio for quiz questions
function playAudio(audioFile, button) {
    if (!audioFile) return;
    
    // Create or get the audio element
    let audioElement = document.getElementById('quiz-audio');
    
    if (!audioElement) {
        audioElement = document.createElement('audio');
        audioElement.id = 'quiz-audio';
        document.body.appendChild(audioElement);
    }
    
    // Update button state
    if (button) {
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        button.disabled = true;
        
        // Reset button after audio finishes or fails
        const resetButton = () => {
            button.innerHTML = originalHTML;
            button.disabled = false;
        };
        
        audioElement.onended = resetButton;
        audioElement.onerror = resetButton;
    }
    
    // Pause any other audio
    pauseAllAudio();
    
    // Set the src and play
    const audioPath = `/static/audio/${audioFile}`;
    audioElement.src = audioPath;
    audioElement.play().catch(error => {
        console.error('Error playing audio:', error);
        if (button) {
            button.innerHTML = originalHTML;
            button.disabled = false;
        }
        alert('Audio playback failed.');
    });
}