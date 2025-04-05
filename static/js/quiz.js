
/**
 * Quiz JavaScript for DeutschLernHub
 * Handles quiz loading, submission, and scoring
 */

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
            quizForm.addEventListener('submit', function(e) {
                e.preventDefault();
                submitQuiz();
            });
        }
    }
});

function loadQuiz(level, topic) {
    const loadingElement = document.getElementById('quiz-loading');
    const quizContent = document.getElementById('quiz-content');
    
    if (loadingElement) loadingElement.style.display = 'block';
    if (quizContent) quizContent.style.display = 'none';
    
    fetch(`/api/quiz/${level}/${topic}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            quizData = data.questions || [];
            totalQuestions = quizData.length;
            timeLeft = data.timeLimit || 15 * 60;
            
            renderQuiz();
            startTimer();
            
            if (loadingElement) loadingElement.style.display = 'none';
            if (quizContent) quizContent.style.display = 'block';
        })
        .catch(error => {
            console.error('Error loading quiz:', error);
            const errorElement = document.getElementById('quiz-error');
            if (errorElement) {
                errorElement.textContent = 'Sorry, we could not load this quiz. Please try again later.';
                errorElement.style.display = 'block';
            }
            if (loadingElement) loadingElement.style.display = 'none';
        });
}

function renderQuiz() {
    const questionsContainer = document.getElementById('quiz-questions');
    if (!questionsContainer) return;
    
    questionsContainer.innerHTML = '';
    
    quizData.forEach((question, index) => {
        const questionNumber = index + 1;
        const questionElement = document.createElement('div');
        questionElement.className = 'quiz-question mb-4';
        questionElement.id = `question-${questionNumber}`;
        
        let questionContent = `
            <div class="question-header mb-3">
                <span class="badge bg-primary">Question ${questionNumber} of ${totalQuestions}</span>
            </div>
            <div class="question-text mb-3">
                <h5>${question.text}</h5>
            </div>
        `;
        
        if (question.audio) {
            questionContent += `
                <div class="audio-player mb-3">
                    <button type="button" class="btn btn-outline-primary btn-sm" onclick="playAudio('${question.audio}', this)">
                        <i class="fas fa-play"></i>
                    </button>
                    <div class="progress" style="height: 5px;">
                        <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                    </div>
                </div>
            `;
        }
        
        questionContent += '<div class="options-container">';
        
        if (question.type === 'multiple-choice') {
            question.options.forEach((option, optionIndex) => {
                const optionId = `q${questionNumber}_option${optionIndex}`;
                questionContent += `
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="radio" 
                            name="question_${questionNumber}" 
                            id="${optionId}" 
                            value="${optionIndex}"
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
                    <input type="text" class="form-control" 
                        name="question_${questionNumber}"
                        placeholder="Type your answer here..."
                        onchange="saveAnswer(${questionNumber}, this.value)">
                </div>
            `;
        }
        
        questionContent += '</div>';
        questionElement.innerHTML = questionContent;
        questionsContainer.appendChild(questionElement);
    });
    
    updateProgress();
}

function saveAnswer(questionNumber, answer) {
    userAnswers[questionNumber] = answer;
    updateProgress();
}

function updateProgress() {
    const answeredQuestions = Object.keys(userAnswers).length;
    const progressPercent = (answeredQuestions / totalQuestions) * 100;
    
    const progressBar = document.getElementById('quiz-progress-bar');
    const answeredElement = document.getElementById('quiz-answered-questions');
    const totalElement = document.getElementById('quiz-total-questions');
    
    if (progressBar) {
        progressBar.style.width = `${progressPercent}%`;
        progressBar.setAttribute('aria-valuenow', progressPercent);
    }
    
    if (answeredElement) {
        answeredElement.textContent = answeredQuestions;
    }
    
    if (totalElement) {
        totalElement.textContent = totalQuestions;
    }
}

function startTimer() {
    const timerElement = document.getElementById('quiz-timer-value');
    if (!timerElement) return;
    
    updateTimerDisplay();
    
    quizTimer = setInterval(() => {
        timeLeft--;
        updateTimerDisplay();
        
        if (timeLeft <= 0) {
            clearInterval(quizTimer);
            submitQuiz(true);
        }
    }, 1000);
}

function updateTimerDisplay() {
    const timerElement = document.getElementById('quiz-timer-value');
    if (!timerElement) return;
    
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    
    timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    timerElement.className = 'quiz-timer';
    if (timeLeft < 60) {
        timerElement.classList.add('text-danger');
    } else if (timeLeft < 120) {
        timerElement.classList.add('text-warning');
    }
}

function submitQuiz(timeUp = false) {
    if (quizTimer) {
        clearInterval(quizTimer);
    }
    
    currentScore = 0;
    
    quizData.forEach((question, index) => {
        const questionNumber = index + 1;
        const userAnswer = userAnswers[questionNumber];
        const questionElement = document.getElementById(`question-${questionNumber}`);
        
        if (!questionElement) return;
        
        // Remove any existing feedback
        const existingFeedback = questionElement.querySelector('.feedback-container');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        const feedbackElement = document.createElement('div');
        feedbackElement.className = 'feedback-container mt-3';
        
        if (userAnswer !== undefined) {
            let isCorrect = false;
            
            if (question.type === 'multiple-choice') {
                isCorrect = parseInt(userAnswer) === question.correctAnswer;
            } else if (question.type === 'fill-in') {
                const correctAnswers = Array.isArray(question.correctAnswer) 
                    ? question.correctAnswer 
                    : [question.correctAnswer];
                isCorrect = correctAnswers.some(answer => 
                    answer.toLowerCase().trim() === userAnswer.toLowerCase().trim()
                );
            }
            
            if (isCorrect) {
                currentScore++;
                feedbackElement.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i> Richtig! (Correct!)
                        <p class="mt-2 mb-0">${question.explanation || 'Good job!'}</p>
                    </div>
                `;
            } else {
                feedbackElement.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-times-circle"></i> Nicht ganz richtig. (Not quite right.)
                        <p class="mt-2 mb-0">
                            <strong>Correct answer:</strong> ${Array.isArray(question.correctAnswer) ? question.correctAnswer[0] : question.correctAnswer}
                            ${question.explanation ? `<br><strong>Explanation:</strong> ${question.explanation}` : ''}
                        </p>
                    </div>
                `;
            }
            
            questionElement.appendChild(feedbackElement);
        }
    });
    
    const scorePercent = (currentScore / totalQuestions) * 100;
    
    // Update UI elements
    const quizContent = document.getElementById('quiz-content');
    const quizResults = document.getElementById('quiz-results');
    const quizScore = document.getElementById('quiz-score');
    const quizMaxScore = document.getElementById('quiz-max-score');
    const quizPercentage = document.getElementById('quiz-percentage');
    const quizMessage = document.getElementById('quiz-message');
    
    if (quizScore) quizScore.textContent = currentScore;
    if (quizMaxScore) quizMaxScore.textContent = totalQuestions;
    if (quizPercentage) quizPercentage.textContent = Math.round(scorePercent);
    
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
    
    if (quizMessage) {
        quizMessage.textContent = resultMessage;
        quizMessage.className = resultClass;
    }
    
    if (quizContent) quizContent.style.display = 'none';
    if (quizResults) quizResults.style.display = 'block';
    
    // Save results if logged in
    saveQuizResult();
    
    // Scroll to top
    window.scrollTo(0, 0);
}

function saveQuizResult() {
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
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        console.log('Quiz result saved successfully');
    })
    .catch(error => {
        console.error('Error saving quiz result:', error);
    });
}

function playAudio(audioFile, button) {
    const audio = new Audio(`/static/audio/${audioFile}`);
    const progressBar = button.nextElementSibling.querySelector('.progress-bar');
    
    button.innerHTML = '<i class="fas fa-pause"></i>';
    
    audio.play();
    
    audio.addEventListener('timeupdate', () => {
        const progress = (audio.currentTime / audio.duration) * 100;
        progressBar.style.width = `${progress}%`;
    });
    
    audio.addEventListener('ended', () => {
        button.innerHTML = '<i class="fas fa-play"></i>';
        progressBar.style.width = '0%';
    });
    
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
