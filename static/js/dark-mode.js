/**
 * Dark Mode JavaScript for DeutschLernHub
 * Handles theme toggling and persistence
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode toggle
    initializeDarkMode();
});

/**
 * Initialize dark mode functionality
 */
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    
    if (darkModeToggle) {
        // Check if user previously enabled dark mode
        const darkModeEnabled = localStorage.getItem('darkModeEnabled') === 'true';
        
        // Apply dark mode if it was previously enabled
        if (darkModeEnabled) {
            enableDarkMode();
        }
        
        // Set up toggle button event listener
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }
}

/**
 * Toggle dark mode on/off
 */
function toggleDarkMode() {
    const body = document.body;
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const darkModeIcon = darkModeToggle.querySelector('i');
    
    if (body.classList.contains('dark-mode')) {
        // Disable dark mode
        disableDarkMode();
    } else {
        // Enable dark mode
        enableDarkMode();
    }
}

/**
 * Enable dark mode
 */
function enableDarkMode() {
    const body = document.body;
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const darkModeIcon = darkModeToggle.querySelector('i');
    
    // Add dark mode class to body
    body.classList.add('dark-mode');
    
    // Update the toggle button
    darkModeIcon.classList.remove('fa-moon');
    darkModeIcon.classList.add('fa-sun');
    darkModeToggle.innerHTML = darkModeIcon.outerHTML + ' Light Mode';
    
    // Save preference to localStorage
    localStorage.setItem('darkModeEnabled', 'true');
}

/**
 * Disable dark mode
 */
function disableDarkMode() {
    const body = document.body;
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const darkModeIcon = darkModeToggle.querySelector('i');
    
    // Remove dark mode class from body
    body.classList.remove('dark-mode');
    
    // Update the toggle button
    darkModeIcon.classList.remove('fa-sun');
    darkModeIcon.classList.add('fa-moon');
    darkModeToggle.innerHTML = darkModeIcon.outerHTML + ' Dark Mode';
    
    // Save preference to localStorage
    localStorage.setItem('darkModeEnabled', 'false');
}

/**
 * Check if the user's system prefers dark mode
 * @returns {boolean} True if the system prefers dark mode
 */
function systemPrefersDarkMode() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
}

/**
 * Listen for system theme changes
 */
if (window.matchMedia) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Add change listener if supported
    if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', event => {
            // Only apply system preference if user hasn't manually set a preference
            if (localStorage.getItem('darkModeEnabled') === null) {
                if (event.matches) {
                    enableDarkMode();
                } else {
                    disableDarkMode();
                }
            }
        });
    }
}
