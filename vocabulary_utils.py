"""
Vocabulary utilities for DeutschLernHub
Handles vocabulary operations such as adding, retrieving and reviewing vocabulary items
"""

import json
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from models import Vocabulary, user_vocabulary, User, Theme

def get_vocabulary_by_level(level):
    """Get all vocabulary items for a specific level (A1, A2, B1)"""
    return Vocabulary.query.filter_by(level=level).all()

def get_vocabulary_by_theme(theme):
    """Get all vocabulary items for a specific theme"""
    return Vocabulary.query.filter_by(theme=theme).all()

def get_vocabulary_by_id(vocab_id):
    """Get a vocabulary item by its ID"""
    return Vocabulary.query.get(vocab_id)

def search_vocabulary(query, level=None):
    """Search vocabulary items by German or English text"""
    search = f"%{query}%"
    if level:
        return Vocabulary.query.filter(
            (Vocabulary.german.ilike(search) | Vocabulary.english.ilike(search)) &
            (Vocabulary.level == level)
        ).all()
    else:
        return Vocabulary.query.filter(
            Vocabulary.german.ilike(search) | Vocabulary.english.ilike(search)
        ).all()

def add_vocabulary_to_user(user_id, vocab_id):
    """Add a vocabulary item to a user's collection"""
    # Check if already exists
    exists = db.session.query(user_vocabulary).filter_by(
        user_id=user_id, vocabulary_id=vocab_id
    ).first()
    
    if not exists:
        stmt = user_vocabulary.insert().values(
            user_id=user_id,
            vocabulary_id=vocab_id,
            familiarity_level=0,
            next_review=datetime.utcnow(),
            saved_at=datetime.utcnow()
        )
        db.session.execute(stmt)
        db.session.commit()
        return True
    return False

def remove_vocabulary_from_user(user_id, vocab_id):
    """Remove a vocabulary item from a user's collection"""
    stmt = user_vocabulary.delete().where(
        (user_vocabulary.c.user_id == user_id) & 
        (user_vocabulary.c.vocabulary_id == vocab_id)
    )
    db.session.execute(stmt)
    db.session.commit()
    return True

def get_user_vocabulary(user_id, level=None, theme=None, limit=None):
    """Get vocabulary items saved by a specific user"""
    query = db.session.query(Vocabulary).join(
        user_vocabulary, 
        Vocabulary.id == user_vocabulary.c.vocabulary_id
    ).filter(user_vocabulary.c.user_id == user_id)
    
    if level:
        query = query.filter(Vocabulary.level == level)
    
    if theme:
        query = query.filter(Vocabulary.theme == theme)
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

def get_user_vocabulary_due_for_review(user_id, limit=20):
    """Get vocabulary items due for review based on spaced repetition algorithm"""
    now = datetime.utcnow()
    
    query = db.session.query(Vocabulary).join(
        user_vocabulary, 
        Vocabulary.id == user_vocabulary.c.vocabulary_id
    ).filter(
        user_vocabulary.c.user_id == user_id,
        user_vocabulary.c.next_review <= now
    ).order_by(user_vocabulary.c.next_review).limit(limit)
    
    return query.all()

def update_vocabulary_familiarity(user_id, vocab_id, known):
    """
    Update familiarity level of a vocabulary item for a user
    known: True if user knew the word, False if they didn't
    """
    # Get current record
    record = db.session.query(user_vocabulary).filter_by(
        user_id=user_id, vocabulary_id=vocab_id
    ).first()
    
    if not record:
        return False
    
    # Calculate new familiarity level and next review time
    current_level = record.familiarity_level
    
    if known:
        # If known, increase familiarity level (max 5)
        new_level = min(current_level + 1, 5)
    else:
        # If not known, decrease familiarity level (min 0)
        new_level = max(current_level - 1, 0)
    
    # Calculate next review time based on spaced repetition
    # Higher familiarity = longer interval before next review
    intervals = {
        0: timedelta(hours=1),    # Complete beginner - review in 1 hour
        1: timedelta(days=1),     # Basic recognition - review in 1 day
        2: timedelta(days=3),     # Familiar - review in 3 days
        3: timedelta(days=7),     # Good knowledge - review in 1 week
        4: timedelta(days=14),    # Very good knowledge - review in 2 weeks
        5: timedelta(days=30)     # Mastered - review in 1 month
    }
    
    next_review = datetime.utcnow() + intervals[new_level]
    
    # Update record
    stmt = user_vocabulary.update().where(
        (user_vocabulary.c.user_id == user_id) & 
        (user_vocabulary.c.vocabulary_id == vocab_id)
    ).values(
        familiarity_level=new_level,
        next_review=next_review
    )
    
    db.session.execute(stmt)
    db.session.commit()
    return True

def add_new_vocabulary(german, english, level, part_of_speech=None, theme=None, example=None):
    """Add a new vocabulary item to the database"""
    new_vocab = Vocabulary(
        german=german,
        english=english,
        level=level,
        part_of_speech=part_of_speech,
        theme=theme,
        example_sentence=example
    )
    
    db.session.add(new_vocab)
    db.session.commit()
    return new_vocab

def get_themes():
    """Get all available themes"""
    return Theme.query.all()

def get_user_vocabulary_stats(user_id):
    """Get statistics about a user's vocabulary"""
    total = db.session.query(func.count(user_vocabulary.c.vocabulary_id)).filter(
        user_vocabulary.c.user_id == user_id
    ).scalar() or 0
    
    mastered = db.session.query(func.count(user_vocabulary.c.vocabulary_id)).filter(
        user_vocabulary.c.user_id == user_id,
        user_vocabulary.c.familiarity_level >= 4
    ).scalar() or 0
    
    learning = db.session.query(func.count(user_vocabulary.c.vocabulary_id)).filter(
        user_vocabulary.c.user_id == user_id,
        user_vocabulary.c.familiarity_level.between(1, 3)
    ).scalar() or 0
    
    new = db.session.query(func.count(user_vocabulary.c.vocabulary_id)).filter(
        user_vocabulary.c.user_id == user_id,
        user_vocabulary.c.familiarity_level == 0
    ).scalar() or 0
    
    # Get vocabulary by level
    a1_count = db.session.query(func.count(Vocabulary.id)).join(
        user_vocabulary, Vocabulary.id == user_vocabulary.c.vocabulary_id
    ).filter(
        user_vocabulary.c.user_id == user_id,
        Vocabulary.level == 'a1'
    ).scalar() or 0
    
    a2_count = db.session.query(func.count(Vocabulary.id)).join(
        user_vocabulary, Vocabulary.id == user_vocabulary.c.vocabulary_id
    ).filter(
        user_vocabulary.c.user_id == user_id,
        Vocabulary.level == 'a2'
    ).scalar() or 0
    
    b1_count = db.session.query(func.count(Vocabulary.id)).join(
        user_vocabulary, Vocabulary.id == user_vocabulary.c.vocabulary_id
    ).filter(
        user_vocabulary.c.user_id == user_id,
        Vocabulary.level == 'b1'
    ).scalar() or 0
    
    return {
        'total': total,
        'mastered': mastered,
        'learning': learning,
        'new': new,
        'levels': {
            'a1': a1_count,
            'a2': a2_count,
            'b1': b1_count
        }
    }