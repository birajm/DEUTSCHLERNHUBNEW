/**
 * Quiz JavaScript for DeutschLernHub
 * Handles quiz loading, submission, and scoring
 */

// Quiz state variables
let quizData = [];
let currentScore = 0;
let totalQuestions = 0;
let userAnswers = {};
let quizTimer = null;
let timeLeft = 0;

document.addEventListener('DOMContentLoaded', function() {
    const quizContainer = document.getElementById('quiz-container');
    
    if (quizContainer) {
        // Extract level and topic from the page URL
        const pathParts = window.location.pathname.split('/');
        const level = pathParts[pathParts.length - 2];
        const topic = pathParts[pathParts.length - 1];
        
        // Load quiz data
        loadQuiz(level, topic);
        
        // Initialize event listeners
        const quizForm = document.getElementById('quiz-form');
        if (quizForm) {
            quizForm.addEventListener('submit', submitQuiz);
        }
    }
});

/**
 * Load quiz data from the server
 * @param {string} level - Quiz level (a1, a2, b1)
 * @param {string} topic - Quiz topic
 */
function loadQuiz(level, topic) {
    const loadingElement = document.getElementById('quiz-loading');
    const quizContent = document.getElementById('quiz-content');
    
    loadingElement.style.display = 'block';
    quizContent.style.display = 'none';
    
    fetch(`/api/quiz/${level}/${topic}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            quizData = data.questions;
            totalQuestions = quizData.length;
            timeLeft = data.timeLimit || 15 * 60; // Default to 15 minutes if not specified
            
            // Render the quiz
            renderQuiz();
            
            // Start the timer
            startTimer();
            
            // Hide loading and show content
            loadingElement.style.display = 'none';
            quizContent.style.display = 'block';
        })
        .catch(error => {
            console.error('Error loading quiz:', error);
            document.getElementById('quiz-error').textContent = 
                'Sorry, we could not load this quiz. Please try again later.';
            document.getElementById('quiz-error').style.display = 'block';
            loadingElement.style.display = 'none';
        });
}

/**
 * Render quiz questions in the container
 */
function renderQuiz() {
    const questionsContainer = document.getElementById('quiz-questions');
    questionsContainer.innerHTML = '';
    
    quizData.forEach((question, index) => {
        const questionNumber = index + 1;
        const questionElement = document.createElement('div');
        questionElement.className = 'quiz-question';
        questionElement.id = `question-${questionNumber}`;
        
        let questionContent = `
            <div class="question-number">Question ${questionNumber} of ${totalQuestions}</div>
            <h5>${question.text}</h5>
        `;
        
        // Add audio if available
        if (question.audio) {
            questionContent += `
                <div class="audio-player mt-2 mb-3">
                    <button type="button" onclick="playAudio('${question.audio}', this)">
                        <i class="fas fa-play"></i>
                    </button>
                    <div class="progress-container">
                        <div class="progress-bar" id="progress-${questionNumber}"></div>
                    </div>
                </div>
            `;
        }
        
        // Add options based on question type
        questionContent += `<div class="quiz-options mt-3">`;
        
        if (question.type === 'multiple-choice') {
            question.options.forEach((option, optionIndex) => {
                const optionId = `q${questionNumber}_option${optionIndex}`;
                questionContent += `
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="radio" name="question_${questionNumber}" 
                            id="${optionId}" value="${optionIndex}" 
                            onchange="saveAnswer(${questionNumber}, ${optionIndex})">
                        <label class="form-check-label" for="${optionId}">
                            ${option}
                        </label>
                    </div>
                `;
            });
        } else if (question.type === 'fill-in') {
            questionContent += `
                <div class="mb-3">
                    <input type="text" class="form-control" name="question_${questionNumber}" 
                        placeholder="Type your answer here..." 
                        onchange="saveAnswer(${questionNumber}, this.value)">
                </div>
            `;
        }
        
        questionContent += `</div>`;
        questionElement.innerHTML = questionContent;
        questionsContainer.appendChild(questionElement);
    });
    
    // Update quiz info
    document.getElementById('quiz-total-questions').textContent = totalQuestions;
}

/**
 * Save user answer to track progress
 * @param {number} questionNumber - The question number
 * @param {any} answer - The user's answer
 */
function saveAnswer(questionNumber, answer) {
    userAnswers[questionNumber] = answer;
    
    // Update progress indicator
    const answeredQuestions = Object.keys(userAnswers).length;
    const progressPercent = (answeredQuestions / totalQuestions) * 100;
    
    const progressBar = document.getElementById('quiz-progress-bar');
    if (progressBar) {
        progressBar.style.width = `${progressPercent}%`;
        progressBar.setAttribute('aria-valuenow', progressPercent);
    }
    
    document.getElementById('quiz-answered-questions').textContent = answeredQuestions;
}

/**
 * Start the quiz timer
 */
function startTimer() {
    const timerElement = document.getElementById('quiz-timer-value');
    
    if (timerElement) {
        updateTimerDisplay();
        
        quizTimer = setInterval(() => {
            timeLeft--;
            updateTimerDisplay();
            
            if (timeLeft <= 0) {
                clearInterval(quizTimer);
                submitQuiz(null, true);
            }
        }, 1000);
    }
}

/**
 * Update the timer display with formatted time
 */
function updateTimerDisplay() {
    const timerElement = document.getElementById('quiz-timer-value');
    
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    
    timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Change color when time is running low
    if (timeLeft < 60) {
        timerElement.classList.add('text-danger');
    } else if (timeLeft < 120) {
        timerElement.classList.add('text-warning');
    }
}

/**
 * Submit the quiz and calculate score
 * @param {Event} event - Form submission event
 * @param {boolean} timeUp - Whether submission is due to time expiration
 */
function submitQuiz(event, timeUp = false) {
    if (event) {
        event.preventDefault();
    }
    
    // Show immediate feedback for each question
    quizData.forEach((question, index) => {
        const questionNumber = index + 1;
        const userAnswer = userAnswers[questionNumber];
        const questionElement = document.getElementById(`question-${questionNumber}`);
        
        if (userAnswer !== undefined) {
            const feedbackElement = document.createElement('div');
            feedbackElement.className = 'feedback-container mt-2';
            
            if ((question.type === 'multiple-choice' && userAnswer === question.correctAnswer) ||
                (question.type === 'fill-in' && question.correctAnswer.includes(userAnswer.trim().toLowerCase()))) {
                feedbackElement.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i> Richtig! (Correct!)
                        <p class="mt-2 mb-0"><strong>Explanation:</strong> ${question.explanation || 'Good job!'}</p>
                    </div>`;
            } else {
                feedbackElement.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-times-circle"></i> Nicht ganz richtig. (Not quite right.)
                        <p class="mt-2 mb-0"><strong>Correct answer:</strong> ${question.correctAnswer}</p>
                        <p class="mb-0"><strong>Explanation:</strong> ${question.explanation || 'Keep practicing!'}</p>
                    </div>`;
            }
            
            questionElement.appendChild(feedbackElement);
        }
    });
    
    // Stop the timer
    if (quizTimer) {
        clearInterval(quizTimer);
    }
    
    // Calculate score
    currentScore = 0;
    
    quizData.forEach((question, index) => {
        const questionNumber = index + 1;
        const userAnswer = userAnswers[questionNumber];
        
        if (userAnswer !== undefined) {
            if (question.type === 'multiple-choice' && userAnswer === question.correctAnswer) {
                currentScore++;
            } else if (question.type === 'fill-in') {
                // For fill-in questions, do case-insensitive comparison and trim spaces
                const correctAnswers = Array.isArray(question.correctAnswer) 
                    ? question.correctAnswer 
                    : [question.correctAnswer];
                
                const normalizedUserAnswer = userAnswer.trim().toLowerCase();
                
                if (correctAnswers.some(answer => 
                    answer.trim().toLowerCase() === normalizedUserAnswer)) {
                    currentScore++;
                }
            }
        }
    });
    
    // Calculate percentage
    const scorePercent = (currentScore / totalQuestions) * 100;
    
    // Display results
    const quizContent = document.getElementById('quiz-content');
    const quizResults = document.getElementById('quiz-results');
    
    document.getElementById('quiz-score').textContent = currentScore;
    document.getElementById('quiz-max-score').textContent = totalQuestions;
    document.getElementById('quiz-percentage').textContent = Math.round(scorePercent);
    
    // Set appropriate message based on score
    let resultMessage = '';
    let resultClass = '';
    
    if (scorePercent >= 90) {
        resultMessage = 'Hervorragend! (Excellent!) You have an outstanding grasp of this material.';
        resultClass = 'text-success';
    } else if (scorePercent >= 75) {
        resultMessage = 'Sehr gut! (Very good!) You have a strong understanding of this material.';
        resultClass = 'text-success';
    } else if (scorePercent >= 60) {
        resultMessage = 'Gut! (Good!) You have a good understanding, but there's room for improvement.';
        resultClass = 'text-primary';
    } else if (scorePercent >= 40) {
        resultMessage = 'Befriedigend. (Satisfactory.) You should review this material again.';
        resultClass = 'text-warning';
    } else {
        resultMessage = 'Noch einmal versuchen. (Try again.) You need more practice with this material.';
        resultClass = 'text-danger';
    }
    
    if (timeUp) {
        resultMessage = 'Zeit ist um! (Time\'s up!) ' + resultMessage;
    }
    
    document.getElementById('quiz-message').textContent = resultMessage;
    document.getElementById('quiz-message').className = resultClass;
    
    // Hide quiz content and show results
    quizContent.style.display = 'none';
    quizResults.style.display = 'block';
    
    // Save quiz result to server if user is logged in
    saveQuizResult();
    
    // Scroll to top
    window.scrollTo(0, 0);
}

/**
 * Save quiz result to the server
 */
function saveQuizResult() {
    // Extract level and topic from the page URL
    const pathParts = window.location.pathname.split('/');
    const level = pathParts[pathParts.length - 2];
    const topic = pathParts[pathParts.length - 1];
    
    fetch('/api/quiz/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            level: level,
            topic: topic,
            score: currentScore,
            max_score: totalQuestions
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Quiz result saved successfully:', data);
    })
    .catch(error => {
        console.error('Error saving quiz result:', error);
    });
}

/**
 * Play audio for a quiz question
 * @param {string} audioFile - The audio file path
 * @param {HTMLButtonElement} button - The play button element
 */
function playAudio(audioFile, button) {
    const audio = new Audio(`/static/audio/${audioFile}`);
    const progressBar = button.nextElementSibling.querySelector('.progress-bar');
    
    // Update UI
    button.innerHTML = '<i class="fas fa-pause"></i>';
    
    // Play audio
    audio.play();
    
    // Update progress bar
    audio.addEventListener('timeupdate', () => {
        const progress = (audio.currentTime / audio.duration) * 100;
        progressBar.style.width = `${progress}%`;
    });
    
    // Handle audio completion
    audio.addEventListener('ended', () => {
        button.innerHTML = '<i class="fas fa-play"></i>';
        progressBar.style.width = '0%';
    });
    
    // Handle pause/play toggle
    button.onclick = function() {
        if (audio.paused) {
            audio.play();
            button.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
            audio.pause();
            button.innerHTML = '<i class="fas fa-play"></i>';
        }
    };
}
