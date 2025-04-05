from flask import render_template, url_for, flash, redirect, request, jsonify, send_file
from app import app, db
from models import User, Vocabulary, Progress
from forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
import os
from werkzeug.utils import secure_filename
from resource_utils import get_resources_by_category, get_resources_by_level, get_resources_by_topic
from vocabulary_utils import get_vocabulary_stats
import json

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile')

@app.route('/grammar')
def grammar():
    return render_template('grammar.html')

@app.route('/vocabulary')
def vocabulary():
    return render_template('vocabulary/index.html')

@app.route('/resources')
def resources():
    return render_template('resources/index.html')

@app.route('/resources/category/<category>')
def resources_by_category(category):
    resources = get_resources_by_category(category)
    return render_template('resources/category.html', category=category, resources=resources)

@app.route('/resources/level/<level>')
def resources_by_level(level):
    resources = get_resources_by_level(level)
    return render_template('resources/level.html', level=level, resources=resources)

@app.route('/resources/topic/<topic>')
def resources_by_topic(topic):
    resources = get_resources_by_topic(topic)
    return render_template('resources/topic.html', topic=topic, resources=resources)

@app.route('/vocabulary/stats')
@login_required
def vocabulary_stats():
    stats = get_vocabulary_stats(current_user.id)
    return render_template('vocabulary/stats.html', stats=stats)

@app.route('/vocabulary/review')
@login_required
def vocabulary_review():
    return render_template('vocabulary/review.html')

@app.route('/vocabulary/saved')
@login_required
def saved_vocabulary():
    vocabulary = Vocabulary.query.filter_by(user_id=current_user.id).all()
    return render_template('vocabulary/saved.html', vocabulary=vocabulary)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/listening')
def listening():
    return render_template('listening/index.html')

@app.route('/reading')
def reading():
    return render_template('reading/index.html')

# A1 routes
@app.route('/a1')
def a1_level():
    return render_template('a1/index.html')

# A2 routes
@app.route('/a2')
def a2_level():
    return render_template('a2/index.html')

# B1 routes
@app.route('/b1')
def b1_level():
    return render_template('b1/index.html')

# Quiz routes
@app.route('/quiz/<level>/<topic>')
def quiz(level, topic):
    try:
        with open(f'static/data/quizzes/{level}/{topic}.json', 'r') as f:
            quiz_data = json.load(f)
        return render_template('quiz.html', quiz=quiz_data)
    except FileNotFoundError:
        flash('Quiz not found', 'error')
        return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500