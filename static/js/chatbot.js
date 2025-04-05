/**
 * Chatbot JavaScript for DeutschLernHub
 * Handles the interactive German practice chatbot functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the chat functionality
    initializeChat();
});

/**
 * Initialize the chat interface and event listeners
 */
function initializeChat() {
    const chatForm = document.getElementById('chat-form');
    const userMessageInput = document.getElementById('user-message');
    const chatMessages = document.getElementById('chat-messages');
    
    if (chatForm && userMessageInput && chatMessages) {
        // Handle form submission
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const userMessage = userMessageInput.value.trim();
            if (userMessage) {
                // Add user message to chat
                addUserMessage(userMessage);
                
                // Clear input field
                userMessageInput.value = '';
                
                // Get bot response
                getBotResponse(userMessage);
            }
        });
        
        // Focus on input field
        userMessageInput.focus();
        
        // Scroll to bottom of chat messages
        scrollToBottom();
    }
}

/**
 * Add a user message to the chat interface
 * @param {string} message - The user's message text
 */
function addUserMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    
    const messageElement = document.createElement('div');
    messageElement.className = 'message user-message';
    
    messageElement.innerHTML = `
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
        </div>
        <div class="message-info">
            <small class="text-muted">You</small>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

/**
 * Add a bot message to the chat interface
 * @param {string} message - The bot's response text
 */
function addBotMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    
    const messageElement = document.createElement('div');
    messageElement.className = 'message bot-message';
    
    // Add typing indicator first
    messageElement.innerHTML = `
        <div class="message-content">
            <p>
                <span class="typing-indicator">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </span>
            </p>
        </div>
        <div class="message-info">
            <small class="text-muted">DeutschBot</small>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
    
    // After a short delay, replace typing indicator with actual message
    setTimeout(() => {
        messageElement.querySelector('.message-content').innerHTML = `<p>${message}</p>`;
        scrollToBottom();
    }, 1000);
}

/**
 * Get a response from the chatbot API
 * @param {string} userMessage - The user's message
 */
function getBotResponse(userMessage) {
    fetch('/api/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Add bot response to chat
        addBotMessage(data.response);
    })
    .catch(error => {
        console.error('Error getting chatbot response:', error);
        addBotMessage('Entschuldigung, ich habe ein technisches Problem. Kannst du es noch einmal versuchen?');
    });
}

/**
 * Send a suggestion chip message to the chatbot
 * @param {string} suggestion - The suggested message text
 */
function sendSuggestion(suggestion) {
    // Add suggestion to input field
    const userMessageInput = document.getElementById('user-message');
    userMessageInput.value = suggestion;
    
    // Focus on input field
    userMessageInput.focus();
}

/**
 * Scroll the chat messages container to the bottom
 */
function scrollToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Escape HTML to prevent XSS
 * @param {string} unsafe - The unsafe string
 * @returns {string} Escaped HTML string
 */
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
