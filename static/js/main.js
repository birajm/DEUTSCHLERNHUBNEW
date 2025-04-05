/**
 * Main JavaScript for DeutschLernHub
 * Handles common functionality across the site
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize progress tracking
    initializeProgressTracking();

    // Handle card animations
    initializeCardAnimations();
    
    // Automatic Flash Message Dismissal
    setTimeout(function() {
        const flashMessages = document.querySelectorAll('.alert-dismissible');
        flashMessages.forEach(message => {
            const bsAlert = new bootstrap.Alert(message);
            bsAlert.close();
        });
    }, 5000);
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

/**
 * Initialize progress tracking for lesson completion
 * Sends AJAX requests to update user progress when lessons are completed
 */
function initializeProgressTracking() {
    // Look for lesson completion buttons
    const completionButtons = document.querySelectorAll('.mark-complete-btn');
    
    completionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const level = this.dataset.level;
            const section = this.dataset.section;
            const lesson = this.dataset.lesson;
            
            // Update progress via AJAX
            updateProgress(level, section, lesson, true);
            
            // Update UI
            this.innerHTML = '<i class="fas fa-check"></i> Completed';
            this.classList.remove('btn-outline-primary');
            this.classList.add('btn-success');
            this.disabled = true;
        });
    });
}

/**
 * Update user progress in the database
 * @param {string} level - A1, A2, or B1
 * @param {string} section - Section name
 * @param {string} lesson - Lesson name
 * @param {boolean} completed - Whether the lesson is completed
 */
function updateProgress(level, section, lesson, completed) {
    fetch('/api/progress/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            level: level,
            section: section,
            lesson: lesson,
            completed: completed
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Progress updated successfully:', data);
    })
    .catch(error => {
        console.error('Error updating progress:', error);
    });
}

/**
 * Initialize card animations for better user experience
 */
function initializeCardAnimations() {
    const cards = document.querySelectorAll('.level-card, .feature-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.05)';
        });
    });
}

/**
 * Get cookie by name (used for CSRF token)
 * @param {string} name - Cookie name
 * @returns {string|null} Cookie value or null if not found
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}
