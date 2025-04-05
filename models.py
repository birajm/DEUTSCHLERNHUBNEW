from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# User-Vocabulary relationship table (for saving words to user's collection)
user_vocabulary = db.Table('user_vocabulary',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('vocabulary_id', db.Integer, db.ForeignKey('vocabulary.id'), primary_key=True),
    db.Column('familiarity_level', db.Integer, default=0),  # 0-5 scale, 0=unfamiliar, 5=mastered
    db.Column('next_review', db.DateTime, default=datetime.utcnow),
    db.Column('saved_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    streak_days = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Integer, default=0)
    
    # Relationships
    progress = db.relationship('Progress', backref='user', lazy='dynamic')
    quiz_results = db.relationship('QuizResult', backref='user', lazy='dynamic')
    vocabulary_items = db.relationship('Vocabulary', secondary=user_vocabulary, 
                                      backref=db.backref('users', lazy='dynamic'))
    badges = db.relationship('UserBadge', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_points(self, points):
        self.points += points
        
    def update_streak(self):
        from datetime import timedelta
        # If last activity was yesterday, continue streak
        if (datetime.utcnow().date() - self.last_activity.date()) == timedelta(days=1):
            self.streak_days += 1
        # If last activity was today, no change
        elif (datetime.utcnow().date() - self.last_activity.date()) == timedelta(days=0):
            pass
        # If more than one day has passed, reset streak
        else:
            self.streak_days = 1
        
        self.last_activity = datetime.utcnow()
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level = db.Column(db.String(2), nullable=False)  # A1, A2, or B1
    section = db.Column(db.String(50), nullable=False)
    lesson = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Progress User:{self.user_id} Level:{self.level} Section:{self.section} Lesson:{self.lesson}>'

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level = db.Column(db.String(2), nullable=False)  # A1, A2, or B1
    topic = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<QuizResult User:{self.user_id} Level:{self.level} Topic:{self.topic} Score:{self.score}/{self.max_score}>'

class Vocabulary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    german = db.Column(db.String(100), nullable=False)
    english = db.Column(db.String(100), nullable=False)
    part_of_speech = db.Column(db.String(20))  # noun, verb, adjective, etc.
    level = db.Column(db.String(2), nullable=False)  # A1, A2, B1
    theme = db.Column(db.String(50))  # e.g., food, travel, family
    example_sentence = db.Column(db.Text)
    audio_filename = db.Column(db.String(100))  # Path to audio file for pronunciation
    image_filename = db.Column(db.String(100))  # Optional image for visualization
    
    def __repr__(self):
        return f'<Vocabulary {self.german} ({self.english})>'

class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # FontAwesome icon name
    
    def __repr__(self):
        return f'<Theme {self.name}>'

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False)  # FontAwesome icon or image path
    requirements = db.Column(db.Text, nullable=False)  # JSON string with requirements
    
    def __repr__(self):
        return f'<Badge {self.name}>'

class UserBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to the badge
    badge = db.relationship('Badge')
    
    def __repr__(self):
        return f'<UserBadge User:{self.user_id} Badge:{self.badge_id}>'
