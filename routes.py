from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Progress, QuizResult
from forms import LoginForm, RegistrationForm, QuizForm
from chatbot import get_chatbot_response
from db_utils import get_user_progress, save_progress, save_quiz_result
import os
import json

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
    return render_template('grammar.html')

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

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500
