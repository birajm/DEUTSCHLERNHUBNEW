"""
Resource utilities for DeutschLernHub
Handles operations for accessing and managing learning resources
"""
from app import db
from models import Resource
from sqlalchemy import func, distinct

def get_resources_by_level(level):
    """Get all resources for a specific level (A1, A2, B1)"""
    return Resource.query.filter_by(level=level).all()

def get_resources_by_category(category, level=None):
    """Get all resources for a specific category, optionally filtered by level"""
    if level:
        return Resource.query.filter_by(category=category, level=level).all()
    return Resource.query.filter_by(category=category).all()

def get_resources_by_topic(topic, level=None):
    """Get all resources for a specific topic, optionally filtered by level"""
    if level:
        return Resource.query.filter_by(topic=topic, level=level).all()
    return Resource.query.filter_by(topic=topic).all()

def get_free_resources(level=None):
    """Get all free resources, optionally filtered by level"""
    if level:
        return Resource.query.filter_by(is_free=True, level=level).all()
    return Resource.query.filter_by(is_free=True).all()

def get_resource_by_id(resource_id):
    """Get a resource by its ID"""
    return Resource.query.get(resource_id)

def search_resources(query, level=None):
    """Search resources by title or description"""
    search_term = f"%{query}%"
    if level:
        return Resource.query.filter(
            (Resource.title.ilike(search_term) | Resource.description.ilike(search_term)) &
            (Resource.level == level)
        ).all()
    return Resource.query.filter(
        Resource.title.ilike(search_term) | Resource.description.ilike(search_term)
    ).all()

def add_resource(title, resource_type, level, category, description=None, url=None, 
                topic=None, is_free=True, icon=None):
    """Add a new resource to the database"""
    resource = Resource(
        title=title,
        description=description,
        url=url,
        resource_type=resource_type,
        level=level,
        category=category,
        topic=topic,
        is_free=is_free,
        icon=icon
    )
    db.session.add(resource)
    db.session.commit()
    return resource

def create_initial_resources():
    """Add initial resources to the database if they don't exist"""
    # Check if we already have resources
    if Resource.query.count() > 0:
        return
        
    # A1 Level Resources
    add_resource(
        title="Slow German mit Annik Rubens",
        resource_type="podcast",
        level="A1",
        category="listening",
        description="Podcast episodes in slow German, perfect for beginners",
        url="https://slowgerman.com/",
        is_free=True,
        icon="podcast"
    )
    
    add_resource(
        title="Learn German with Anja - Alphabet",
        resource_type="video",
        level="A1",
        category="basics",
        topic="alphabet",
        description="Pronunciation guide to the German alphabet",
        url="https://www.youtube.com/watch?v=wpQDLM6ZD3w",
        is_free=True,
        icon="youtube"
    )
    
    add_resource(
        title="German for Beginners - Deutsche Welle",
        resource_type="website",
        level="A1",
        category="comprehensive",
        description="Free online course with audio, video, and exercises",
        url="https://learngerman.dw.com/en/beginners/c-36519687",
        is_free=True,
        icon="globe"
    )
    
    # A2 Level Resources
    add_resource(
        title="Lingolia - German Grammar Practice",
        resource_type="website",
        level="A2",
        category="grammar",
        description="Detailed explanations and exercises for A2 grammar topics",
        url="https://deutsch.lingolia.com/en/grammar",
        is_free=True,
        icon="language"
    )
    
    add_resource(
        title="Nachrichtenleicht",
        resource_type="website",
        level="A2",
        category="reading",
        description="News articles in simplified German",
        url="https://www.nachrichtenleicht.de/",
        is_free=True,
        icon="newspaper"
    )
    
    add_resource(
        title="Easy German - Past Tense",
        resource_type="video",
        level="A2",
        category="grammar",
        topic="past_tense",
        description="Explanation of German's Perfect tense with examples",
        url="https://www.youtube.com/watch?v=vnT0zT9caRw",
        is_free=True,
        icon="youtube"
    )
    
    # B1 Level Resources
    add_resource(
        title="Coffee Break German",
        resource_type="podcast",
        level="B1",
        category="comprehensive",
        description="Audio lessons for intermediate learners",
        url="https://radiolingua.com/coffeebreakgerman/",
        is_free=False,
        icon="coffee"
    )
    
    add_resource(
        title="Goethe Institut - Online German Course",
        resource_type="app",
        level="B1",
        category="comprehensive",
        description="Interactive course with focus on all language skills",
        url="https://www.goethe.de/en/spr/kup/kur/do.html",
        is_free=False,
        icon="graduation-cap"
    )
    
    add_resource(
        title="Duolingo German",
        resource_type="app",
        level="A1-B1",
        category="comprehensive",
        description="Gamified language learning app",
        url="https://www.duolingo.com/course/de/en/Learn-German",
        is_free=True,
        icon="mobile-alt"
    )

    # Grammar-specific resources
    add_resource(
        title="Learn German with Anja - Modal Verbs",
        resource_type="video",
        level="A2",
        category="grammar",
        topic="modal_verbs",
        description="Explanation of modal verbs and their usage",
        url="https://www.youtube.com/watch?v=A93Y_wX8lO4",
        is_free=True,
        icon="youtube"
    )
    
    db.session.commit()
def get_all_resources():
    """Get all resources ordered by level and title"""
    return Resource.query.order_by(Resource.level, Resource.title).all()

def get_resource_categories():
    """Get all unique resource categories"""
    categories = db.session.query(Resource.category).distinct().order_by(Resource.category).all()
    return [category[0] for category in categories]

def get_resource_categories_by_level(level):
    """Get all unique resource categories for a specific level"""
    categories = db.session.query(Resource.category).filter(Resource.level == level).distinct().order_by(Resource.category).all()
    return [category[0] for category in categories]

def get_resource_topics():
    """Get all unique resource topics"""
    topics = db.session.query(Resource.topic).filter(Resource.topic != None).distinct().order_by(Resource.topic).all()
    return [topic[0] for topic in topics]

def get_resource_topics_by_level(level):
    """Get all unique resource topics for a specific level"""
    topics = db.session.query(Resource.topic).filter(Resource.level == level, Resource.topic != None).distinct().order_by(Resource.topic).all()
    return [topic[0] for topic in topics]

def get_resource_levels():
    """Get all unique resource levels"""
    levels = db.session.query(Resource.level).distinct().order_by(Resource.level).all()
    return [level[0] for level in levels]
