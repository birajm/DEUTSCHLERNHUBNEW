/**
 * Audio JavaScript for DeutschLernHub
 * Handles audio playback for language learning
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all audio players on the page
    initializeAudioPlayers();
});

/**
 * Initialize all audio players on the page
 */
function initializeAudioPlayers() {
    const audioPlayers = document.querySelectorAll('.audio-player');
    
    audioPlayers.forEach(player => {
        // Find elements
        const playButton = player.querySelector('.play-button');
        const progressBar = player.querySelector('.progress-bar');
        const audioElement = player.querySelector('audio');
        
        if (playButton && progressBar && audioElement) {
            setupAudioPlayer(playButton, progressBar, audioElement);
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
    // Play/pause button functionality
    playButton.addEventListener('click', function() {
        if (audioElement.paused) {
            // Pause any other playing audio first
            pauseAllAudio();
            
            // Play this audio
            audioElement.play();
            playButton.innerHTML = '<i class="fas fa-pause"></i>';
            playButton.setAttribute('aria-label', 'Pause');
        } else {
            audioElement.pause();
            playButton.innerHTML = '<i class="fas fa-play"></i>';
            playButton.setAttribute('aria-label', 'Play');
        }
    });
    
    // Update progress bar as audio plays
    audioElement.addEventListener('timeupdate', function() {
        const progress = (audioElement.currentTime / audioElement.duration) * 100;
        progressBar.style.width = progress + '%';
    });
    
    // Reset when audio ends
    audioElement.addEventListener('ended', function() {
        playButton.innerHTML = '<i class="fas fa-play"></i>';
        playButton.setAttribute('aria-label', 'Play');
        progressBar.style.width = '0%';
    });
    
    // Handle progress bar clicks to seek
    const progressContainer = progressBar.parentElement;
    progressContainer.addEventListener('click', function(e) {
        const rect = progressContainer.getBoundingClientRect();
        const position = (e.clientX - rect.left) / rect.width;
        
        audioElement.currentTime = position * audioElement.duration;
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
    
    if (container) {
        // Create audio player structure
        const playerDiv = document.createElement('div');
        playerDiv.className = 'audio-player';
        
        // Create audio element
        const audio = document.createElement('audio');
        audio.src = audioSrc;
        audio.preload = 'none';
        
        // Create play button
        const playButton = document.createElement('button');
        playButton.className = 'play-button';
        playButton.setAttribute('aria-label', `Play pronunciation of ${word}`);
        playButton.innerHTML = '<i class="fas fa-play"></i>';
        
        // Create progress container and bar
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress-container';
        
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        
        // Assemble the player
        progressContainer.appendChild(progressBar);
        playerDiv.appendChild(playButton);
        playerDiv.appendChild(progressContainer);
        playerDiv.appendChild(audio);
        
        // Add to container
        container.appendChild(playerDiv);
        
        // Set up event listeners
        setupAudioPlayer(playButton, progressBar, audio);
    }
}

/**
 * Pause all audio elements on the page
 * Used when starting a new audio to prevent multiple audios playing at once
 */
function pauseAllAudio() {
    const allAudio = document.querySelectorAll('audio');
    const allPlayButtons = document.querySelectorAll('.play-button');
    
    allAudio.forEach(audio => {
        audio.pause();
    });
    
    allPlayButtons.forEach(button => {
        button.innerHTML = '<i class="fas fa-play"></i>';
        button.setAttribute('aria-label', 'Play');
    });
}

/**
 * Load audio for a pronunciation example
 * Can be called directly from HTML onclick events
 * @param {string} word - The German word to pronounce
 * @param {HTMLElement} element - The triggering element
 */
function pronounce(word, element) {
    // Format the word for the file name (lowercase, remove special chars)
    const formattedWord = word.toLowerCase().replace(/[^\w]/g, '');
    const audioSrc = `/static/audio/words/${formattedWord}.mp3`;
    
    // Create a temporary audio element
    const audio = new Audio(audioSrc);
    
    // Add loading indicator
    element.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    // Play when loaded
    audio.addEventListener('canplaythrough', function() {
        // Pause any other playing audio first
        pauseAllAudio();
        
        // Reset the button text
        element.innerHTML = '<i class="fas fa-volume-up"></i>';
        
        // Play the audio
        audio.play();
    });
    
    // Handle errors
    audio.addEventListener('error', function() {
        console.error('Error loading audio for word:', word);
        element.innerHTML = '<i class="fas fa-volume-mute"></i>';
        
        // Reset after a delay
        setTimeout(() => {
            element.innerHTML = '<i class="fas fa-volume-up"></i>';
        }, 2000);
    });
    
    // Reset when done
    audio.addEventListener('ended', function() {
        element.innerHTML = '<i class="fas fa-volume-up"></i>';
    });
    
    // Attempt to load the audio
    audio.load();
}
