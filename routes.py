from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Progress, QuizResult, Vocabulary, Theme, Badge, UserBadge
from forms import LoginForm, RegistrationForm, QuizForm, ChatbotForm
from chatbot import get_chatbot_response
from db_utils import get_user_progress, save_progress, save_quiz_result, get_user_stats, get_leaderboard
from vocabulary_utils import (get_vocabulary_by_level, get_vocabulary_by_theme, 
                             search_vocabulary, add_vocabulary_to_user, 
                             remove_vocabulary_from_user, get_user_vocabulary,
                             get_user_vocabulary_due_for_review, 
                             update_vocabulary_familiarity, get_themes,
                             get_user_vocabulary_stats)
from badge_utils import check_badge_eligibility, create_initial_badges
import os
import json
from datetime import datetime

# Main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('profile'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    progress = get_user_progress(current_user.id)
    quiz_results = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.completed_at.desc()).all()
    
    a1_progress = sum(1 for p in progress if p.level == 'A1' and p.completed) / max(1, sum(1 for p in progress if p.level == 'A1'))
    a2_progress = sum(1 for p in progress if p.level == 'A2' and p.completed) / max(1, sum(1 for p in progress if p.level == 'A2'))
    b1_progress = sum(1 for p in progress if p.level == 'B1' and p.completed) / max(1, sum(1 for p in progress if p.level == 'B1'))
    
    return render_template('profile.html', 
                          user=current_user, 
                          progress=progress, 
                          quiz_results=quiz_results, 
                          a1_progress=a1_progress*100, 
                          a2_progress=a2_progress*100, 
                          b1_progress=b1_progress*100)

# Learning levels routes
@app.route('/a1')
def a1_index():
    return render_template('a1/index.html')

@app.route('/a2')
def a2_index():
    return render_template('a2/index.html')

@app.route('/b1')
def b1_index():
    return render_template('b1/index.html')

# Grammar reference section
@app.route('/grammar')
def grammar():
    return render_template('grammar/index.html')

@app.route('/grammar/a1')
def grammar_a1():
    return render_template('grammar/a1.html')

@app.route('/grammar/a2')
def grammar_a2():
    return render_template('grammar/a2.html')

@app.route('/grammar/b1')
def grammar_b1():
    return render_template('grammar/b1.html')

@app.route('/grammar/practice')
def grammar_practice():
    return render_template('grammar/practice.html')

# Listening comprehension exercises
@app.route('/listening')
@app.route('/listening/<string:level>')
@app.route('/listening/<string:type>')
def listening(level=None, type=None):
    selected_level = level
    selected_type = type
    
    return render_template('listening/index.html', 
                          selected_level=selected_level,
                          selected_type=selected_type)

# Reading practice
@app.route('/reading')
@app.route('/reading/<string:level>')
@app.route('/reading/<string:category>')
def reading(level=None, category=None):
    selected_level = level
    selected_category = category
    
    return render_template('reading/index.html', 
                          selected_level=selected_level,
                          selected_category=selected_category)

# Chatbot route
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    response = get_chatbot_response(data['message'])
    return jsonify({'response': response})

# Quiz routes
@app.route('/quiz/<level>/<topic>')
def quiz(level, topic):
    form = QuizForm()
    return render_template('quiz.html', level=level, topic=topic, form=form)

@app.route('/api/quiz/<level>/<topic>', methods=['GET'])
def get_quiz(level, topic):
    # Load quiz questions from JSON files organized by level and topic
    try:
        with open(f'static/data/quizzes/{level}/{topic}.json', 'r') as f:
            quiz_data = json.load(f)
            return jsonify(quiz_data)
    except FileNotFoundError:
        return jsonify({'error': 'Quiz not found'}), 404

@app.route('/api/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    data = request.get_json()
    if not data or 'level' not in data or 'topic' not in data or 'score' not in data or 'max_score' not in data:
        return jsonify({'error': 'Invalid quiz submission'}), 400
    
    # Save quiz result to database
    save_quiz_result(current_user.id, data['level'], data['topic'], data['score'], data['max_score'])
    
    return jsonify({'success': True})

# Progress tracking routes
@app.route('/api/progress/update', methods=['POST'])
@login_required
def update_progress():
    data = request.get_json()
    if not data or 'level' not in data or 'section' not in data or 'lesson' not in data or 'completed' not in data:
        return jsonify({'error': 'Invalid progress update'}), 400
    
    # Save progress to database
    save_progress(current_user.id, data['level'], data['section'], data['lesson'], data['completed'])
    
    return jsonify({'success': True})

# Static files routes
@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

@app.route('/static/downloads/<path:filename>')
def serve_downloads(filename):
    return send_from_directory('static/downloads', filename)

# Vocabulary routes
@app.route('/vocabulary')
def vocabulary():
    # Get query parameters
    search = request.args.get('search', '')
    level = request.args.get('level', '')
    theme_name = request.args.get('theme', '')
    
    # Get themes for navigation
    themes = get_themes()
    
    # Get vocabulary based on filters
    if search:
        vocabulary = search_vocabulary(search, level)
    elif level and theme_name:
        level_vocab = get_vocabulary_by_level(level)
        vocabulary = [word for word in level_vocab if word.theme == theme_name]
    elif level:
        vocabulary = get_vocabulary_by_level(level)
    elif theme_name:
        vocabulary = get_vocabulary_by_theme(theme_name)
    else:
        # Get all vocabulary, limited to 100 items for performance
        vocabulary = Vocabulary.query.limit(100).all()
    
    # Get user's saved vocabulary if authenticated
    user_vocabulary = []
    stats = {'total': 0, 'mastered': 0, 'learning': 0, 'new': 0}
    review_count = 0
    
    if current_user.is_authenticated:
        user_vocabulary = get_user_vocabulary(current_user.id)
        stats = get_user_vocabulary_stats(current_user.id)
        review_words = get_user_vocabulary_due_for_review(current_user.id)
        review_count = len(review_words)
    
    return render_template('vocabulary/index.html',
                          vocabulary=vocabulary,
                          user_vocabulary=user_vocabulary,
                          themes=themes,
                          stats=stats,
                          review_count=review_count,
                          search=search,
                          selected_level=level,
                          selected_theme=theme_name)

@app.route('/vocabulary/review')
@login_required
def vocabulary_review():
    # Get words due for review
    words = get_user_vocabulary_due_for_review(current_user.id)
    
    return render_template('vocabulary/review.html', words=words)

@app.route('/vocabulary/saved')
@login_required
def vocabulary_saved():
    # Get user's saved vocabulary
    vocabulary = get_user_vocabulary(current_user.id)
    
    # Get themes for filtering
    themes = get_themes()
    
    # Get stats
    stats = get_user_vocabulary_stats(current_user.id)
    
    return render_template('vocabulary/saved.html',
                          vocabulary=vocabulary,
                          themes=themes,
                          stats=stats)

@app.route('/vocabulary/stats')
@login_required
def vocabulary_stats():
    # Get user's vocabulary stats
    stats = get_user_vocabulary_stats(current_user.id)
    
    # Get level-specific vocabulary
    a1_words = get_user_vocabulary(current_user.id, level='a1')
    a2_words = get_user_vocabulary(current_user.id, level='a2')
    b1_words = get_user_vocabulary(current_user.id, level='b1')
    
    # Get themes for chart
    themes = get_themes()
    theme_counts = {}
    
    for theme in themes:
        theme_words = get_user_vocabulary(current_user.id, theme=theme.name)
        theme_counts[theme.name] = len(theme_words)
    
    return render_template('vocabulary/stats.html',
                          stats=stats,
                          a1_words=a1_words,
                          a2_words=a2_words,
                          b1_words=b1_words,
                          theme_counts=theme_counts)

@app.route('/vocabulary/add', methods=['POST'])
@login_required
def add_vocabulary():
    data = request.get_json()
    if not data or 'vocab_id' not in data:
        return jsonify({'success': False, 'message': 'Invalid request'}), 400
    
    vocab_id = data['vocab_id']
    result = add_vocabulary_to_user(current_user.id, vocab_id)
    
    return jsonify({'success': result})

@app.route('/vocabulary/remove', methods=['POST'])
@login_required
def remove_vocabulary():
    data = request.get_json()
    if not data or 'vocab_id' not in data:
        return jsonify({'success': False, 'message': 'Invalid request'}), 400
    
    vocab_id = data['vocab_id']
    result = remove_vocabulary_from_user(current_user.id, vocab_id)
    
    return jsonify({'success': result})

@app.route('/vocabulary/update-familiarity', methods=['POST'])
@login_required
def update_familiarity():
    data = request.get_json()
    if not data or 'vocab_id' not in data or 'known' not in data:
        return jsonify({'success': False, 'message': 'Invalid request'}), 400
    
    vocab_id = data['vocab_id']
    known = data['known']
    result = update_vocabulary_familiarity(current_user.id, vocab_id, known)
    
    return jsonify({'success': result})

# Initialize system data
# Using with app.app_context() to replace the deprecated before_first_request
# Note: This will run when the application starts up
with app.app_context():
    try:
        # Create initial badges
        create_initial_badges()
        
        # Create some initial themes if none exist
        if Theme.query.count() == 0:
            themes = [
                {'name': 'Food', 'description': 'Food and drinks vocabulary', 'icon': 'fa-utensils'},
                {'name': 'Travel', 'description': 'Travel and transportation vocabulary', 'icon': 'fa-plane'},
                {'name': 'Family', 'description': 'Family and relationships vocabulary', 'icon': 'fa-users'},
                {'name': 'Home', 'description': 'Home and furniture vocabulary', 'icon': 'fa-home'},
                {'name': 'Work', 'description': 'Work and career vocabulary', 'icon': 'fa-briefcase'},
                {'name': 'Health', 'description': 'Health and medical vocabulary', 'icon': 'fa-heartbeat'},
                {'name': 'Hobbies', 'description': 'Hobbies and interests vocabulary', 'icon': 'fa-gamepad'},
                {'name': 'Weather', 'description': 'Weather and seasons vocabulary', 'icon': 'fa-cloud-sun'}
            ]
            
            for theme_data in themes:
                theme = Theme(**theme_data)
                db.session.add(theme)
            
            db.session.commit()
    except Exception as e:
        print(f"Error initializing system data: {e}")
        # Don't let initialization errors prevent app startup

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500
