from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Progress, QuizResult, Vocabulary, Theme, Badge, UserBadge, Resource
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
from resource_utils import (get_resources_by_level, get_resources_by_category,
                           get_resources_by_topic, get_free_resources, get_all_resources,
                           get_resource_by_id, search_resources, create_initial_resources,
                           get_resource_categories, get_resource_topics, get_resource_levels,
                           get_resource_categories_by_level, get_resource_topics_by_level)
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

# A1 Lesson routes
@app.route('/a1/basics/alphabet')
def a1_basics_alphabet():
    return render_template('lessons/basics/alphabet.html')

@app.route('/a1/basics/greetings')
def a1_basics_greetings():
    return render_template('lessons/basics/greetings.html')

@app.route('/a1/basics/numbers')
def a1_basics_numbers():
    return render_template('lessons/basics/numbers.html')

@app.route('/a1/basics/phrases')
def a1_basics_phrases():
    return render_template('lessons/basics/phrases.html')

@app.route('/a1/grammar/articles')
def a1_grammar_articles():
    return render_template('lessons/grammar/articles.html')

@app.route('/a1/grammar/present-tense')
def a1_grammar_present_tense():
    return render_template('lessons/grammar/present_tense.html')

@app.route('/a1/grammar/pronouns')
def a1_grammar_pronouns():
    return render_template('lessons/grammar/pronouns.html')

@app.route('/a1/grammar/sentences')
def a1_grammar_sentences():
    return render_template('lessons/grammar/sentences.html')

@app.route('/a1/vocabulary/family')
def a1_vocabulary_family():
    return render_template('lessons/vocabulary/family.html')

@app.route('/a1/vocabulary/colors')
def a1_vocabulary_colors():
    return render_template('lessons/vocabulary/colors.html')

@app.route('/a1/vocabulary/dates')
def a1_vocabulary_dates():
    return render_template('lessons/vocabulary/dates.html')

@app.route('/a1/vocabulary/food')
def a1_vocabulary_food():
    return render_template('lessons/vocabulary/food.html')

@app.route('/a1/practice/listening')
def a1_practice_listening():
    return render_template('lessons/practice/listening.html')

@app.route('/a1/practice/reading')
def a1_practice_reading():
    return render_template('lessons/practice/reading.html')

@app.route('/a1/practice/writing')
def a1_practice_writing():
    return render_template('lessons/practice/writing.html')

@app.route('/a1/quizzes/phrases')
def a1_quiz_phrases():
    return render_template('lessons/quizzes/phrases.html')

@app.route('/a1/quizzes/articles')
def a1_quiz_articles():
    return render_template('lessons/quizzes/articles.html')

@app.route('/a1/quizzes/present-tense')
def a1_quiz_present_tense():
    return render_template('lessons/quizzes/present_tense.html')

@app.route('/a1/quizzes/comprehensive')
def a1_quiz_comprehensive():
    return render_template('lessons/quizzes/comprehensive.html')

@app.route('/a2')
def a2_index():
    return render_template('a2/index.html')

# A2 Lesson routes
@app.route('/a2/expanded-basics/small-talk')
def a2_basics_small_talk():
    return render_template('lessons/a2/expanded_basics/small_talk.html')

@app.route('/a2/expanded-basics/asking-information')
def a2_basics_asking_information():
    return render_template('lessons/a2/expanded_basics/asking_information.html')

@app.route('/a2/expanded-basics/shopping-services')
def a2_basics_shopping_services():
    return render_template('lessons/a2/expanded_basics/shopping_services.html')

@app.route('/a2/expanded-basics/directions-transportation')
def a2_basics_directions_transportation():
    return render_template('lessons/a2/expanded_basics/directions_transportation.html')

@app.route('/a2/grammar/past-tense')
def a2_grammar_past_tense():
    return render_template('lessons/a2/grammar/past_tense.html')

@app.route('/a2/grammar/modal-verbs')
def a2_grammar_modal_verbs():
    return render_template('lessons/a2/grammar/modal_verbs.html')

@app.route('/a2/grammar/prepositions')
def a2_grammar_prepositions():
    return render_template('lessons/a2/grammar/prepositions.html')

@app.route('/a2/grammar/conjunctions')
def a2_grammar_conjunctions():
    return render_template('lessons/a2/grammar/conjunctions.html')

@app.route('/a2/vocabulary/health-body')
def a2_vocabulary_health_body():
    return render_template('lessons/a2/vocabulary/health_body.html')

@app.route('/a2/vocabulary/work-education')
def a2_vocabulary_work_education():
    return render_template('lessons/a2/vocabulary/work_education.html')

@app.route('/a2/expanded-basics/expressing-opinions')
def a2_basics_expressing_opinions():
    return render_template('lessons/a2/expanded_basics/expressing_opinions.html')

@app.route('/a2/expanded-basics/telling-stories')
def a2_basics_telling_stories():
    return render_template('lessons/a2/expanded_basics/telling_stories.html')

@app.route('/b1')
def b1_index():
    return render_template('b1/index.html')

# B1 Lesson routes
@app.route('/b1/communication/complex-ideas')
def b1_communication_complex_ideas():
    return render_template('lessons/b1/communication/complex_ideas.html')

@app.route('/b1/communication/describing-experiences')
def b1_communication_describing_experiences():
    return render_template('lessons/b1/communication/describing_experiences.html')

@app.route('/b1/communication/debating-persuading')
def b1_communication_debating_persuading():
    return render_template('lessons/b1/communication/debating_persuading.html')

@app.route('/b1/communication/cultural-nuances')
def b1_communication_cultural_nuances():
    return render_template('lessons/b1/communication/cultural_nuances.html')

@app.route('/b1/practice/listening')
def b1_practice_listening():
    return render_template('lessons/practice/listening.html')

@app.route('/b1/practice/reading') 
def b1_practice_reading():
    return render_template('lessons/practice/reading.html')

@app.route('/b1/practice/writing')
def b1_practice_writing():
    return render_template('lessons/practice/writing.html')

@app.route('/b1/quizzes/subjunctive')
def b1_quiz_subjunctive():
    return render_template('lessons/quizzes/subjunctive.html')

@app.route('/b1/quizzes/vocabulary')
def b1_quiz_vocabulary():
    return render_template('lessons/quizzes/vocabulary.html')

@app.route('/b1/quizzes/complex-grammar') 
def b1_quiz_complex_grammar():
    return render_template('lessons/quizzes/complex_grammar.html')

@app.route('/b1/quizzes/comprehensive')
def b1_quiz_comprehensive():
    return render_template('lessons/quizzes/comprehensive.html')

# B1 Grammar routes
@app.route('/b1/grammar/passive-voice')
def b1_grammar_passive_voice():
    return render_template('lessons/b1/grammar/passive_voice.html')

@app.route('/b1/grammar/subjunctive')
def b1_grammar_subjunctive():
    return render_template('lessons/b1/grammar/subjunctive.html')

@app.route('/b1/grammar/advanced-tenses')
def b1_grammar_advanced_tenses():
    return render_template('lessons/b1/grammar/advanced_tenses.html')

@app.route('/b1/grammar/complex-sentences')
def b1_grammar_complex_sentences():
    return render_template('lessons/b1/grammar/complex_sentences.html')

# B1 Vocabulary routes
@app.route('/b1/vocabulary/work-career')
def b1_vocabulary_work_career():
    return render_template('lessons/b1/vocabulary/work_career.html')

@app.route('/b1/vocabulary/current-events')
def b1_vocabulary_current_events():
    return render_template('lessons/b1/vocabulary/current_events.html')

@app.route('/b1/vocabulary/environment-nature')
def b1_vocabulary_environment_nature():
    return render_template('lessons/b1/vocabulary/environment_nature.html')

@app.route('/b1/vocabulary/art-culture')
def b1_vocabulary_art_culture():
    return render_template('lessons/b1/vocabulary/art_culture.html')

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
            
        # Create initial learning resources
        create_initial_resources()
    except Exception as e:
        print(f"Error initializing system data: {e}")
        # Don't let initialization errors prevent app startup

# Resources routes
@app.route('/resources')
def resources():
    """Main resources page with all resources"""
    # Get query parameters
    search = request.args.get('search', '')
    level = request.args.get('level', '')
    category = request.args.get('category', '')
    resource_type = request.args.get('type', '')
    free_only = request.args.get('free_only') == 'true'
    
    # Filter resources based on parameters
    if search:
        resources = search_resources(search, level)
    elif level and category:
        resources = get_resources_by_category(category, level)
    elif level:
        resources = get_resources_by_level(level)
    elif category:
        resources = get_resources_by_category(category)
    else:
        # Get all resources
        resources = get_all_resources()
    
    # Filter by resource type if specified
    if resource_type and resources:
        resources = [r for r in resources if r.resource_type == resource_type]
    
    # Filter by free only if specified
    if free_only and resources:
        resources = [r for r in resources if r.is_free]
    
    # Get unique categories and resource types for filter options
    categories = get_resource_categories()
    
    # Get unique resource types
    resource_types = set(r.resource_type for r in get_all_resources())
    
    return render_template('resources/index.html',
                           resources=resources,
                           categories=categories,
                           resource_types=resource_types,
                           selected_level=level,
                           selected_category=category,
                           selected_type=resource_type,
                           free_only=free_only,
                           search=search)

@app.route('/resources/<string:level>')
def resources_by_level(level):
    """Show resources filtered by level"""
    resources = get_resources_by_level(level)
    
    # Get unique categories and topics for this level
    categories = get_resource_categories_by_level(level)
    topics = get_resource_topics_by_level(level)
    
    return render_template('resources/level.html', 
                           resources=resources,
                           level=level,
                           categories=categories,
                           topics=topics)

@app.route('/resources/category/<string:category>')
def resources_by_category(category):
    """Show resources filtered by category"""
    level = request.args.get('level', '')
    
    if level:
        resources = get_resources_by_category(category, level)
    else:
        resources = get_resources_by_category(category)
    
    return render_template('resources/category.html',
                           resources=resources,
                           category=category,
                           selected_level=level)

@app.route('/resources/topic/<string:topic>')
def resources_by_topic(topic):
    """Show resources for a specific topic"""
    level = request.args.get('level', '')
    
    if level:
        resources = get_resources_by_topic(topic, level)
    else:
        resources = get_resources_by_topic(topic)
    
    return render_template('resources/topic.html',
                           resources=resources,
                           topic=topic,
                           selected_level=level)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500
@app.route('/reading/content/<int:reading_id>')
def reading_content(reading_id):
    # Sample reading data - In production, this would come from a database
    readings = {
        1: {
            'title': 'Meine Familie',
            'subtitle': 'My Family',
            'level': 'A1',
            'category': 'Short Story',
            'content': '''
                <p>Hallo! Ich möchte euch meine Familie vorstellen. Ich heiße Thomas und bin 25 Jahre alt. 
                Meine Familie ist nicht sehr groß, aber ich liebe sie sehr.</p>
                
                <p>Mein Vater heißt Michael und ist 50 Jahre alt. Er ist Lehrer von Beruf. 
                Meine Mutter heißt Anna und ist 48 Jahre alt. Sie arbeitet als Krankenschwester.</p>
                
                <p>Ich habe eine Schwester. Sie heißt Laura und ist 20 Jahre alt. 
                Sie studiert Medizin an der Universität. Wir haben auch eine Katze. 
                Sie heißt Luna und ist 3 Jahre alt.</p>
            ''',
            'vocabulary': [
                {'german': 'Familie', 'english': 'family'},
                {'german': 'Vater', 'english': 'father'},
                {'german': 'Mutter', 'english': 'mother'},
                {'german': 'Schwester', 'english': 'sister'},
                {'german': 'Katze', 'english': 'cat'},
                {'german': 'Lehrer', 'english': 'teacher'},
                {'german': 'Krankenschwester', 'english': 'nurse'}
            ],
            'questions': [
                {
                    'text': 'Wie alt ist Thomas?',
                    'options': ['20 Jahre alt', '25 Jahre alt', '48 Jahre alt', '50 Jahre alt'],
                    'correct': 1
                },
                {
                    'text': 'Was ist der Beruf von Thomas Vater?',
                    'options': ['Arzt', 'Lehrer', 'Krankenpfleger', 'Student'],
                    'correct': 1
                },
                {
                    'text': 'Was studiert Laura?',
                    'options': ['Medizin', 'Deutsch', 'Mathematik', 'Geschichte'],
                    'correct': 0
                }
            ],
            'word_count': 150,
            'estimated_time': 5
        }
        # Add more readings here
    }
    
    reading = readings.get(reading_id)
    if not reading:
        abort(404)
    
    return render_template('reading/content.html', reading=reading)
