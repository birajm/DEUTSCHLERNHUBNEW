"""
Badge and gamification utilities for DeutschLernHub
Handles badge awarding, point calculation, and streak tracking
"""

import json
from datetime import datetime
from app import db
from models import User, Badge, UserBadge, QuizResult, Progress

def get_all_badges():
    """Get all available badges"""
    return Badge.query.all()

def get_user_badges(user_id):
    """Get all badges earned by a user"""
    return UserBadge.query.filter_by(user_id=user_id).all()

def award_badge(user_id, badge_id):
    """Award a badge to a user if they don't already have it"""
    # Check if user already has this badge
    existing = UserBadge.query.filter_by(user_id=user_id, badge_id=badge_id).first()
    
    if not existing:
        new_badge = UserBadge(user_id=user_id, badge_id=badge_id)
        db.session.add(new_badge)
        db.session.commit()
        return True
    return False

def check_badge_eligibility(user_id):
    """Check if user is eligible for any badges they don't have yet"""
    user = User.query.get(user_id)
    if not user:
        return []
    
    # Get all badges the user doesn't have yet
    earned_badge_ids = [ub.badge_id for ub in UserBadge.query.filter_by(user_id=user_id).all()]
    available_badges = Badge.query.filter(~Badge.id.in_(earned_badge_ids)).all() if earned_badge_ids else Badge.query.all()
    
    newly_earned_badges = []
    
    for badge in available_badges:
        # Parse requirements JSON
        requirements = json.loads(badge.requirements)
        
        if 'quiz_score' in requirements:
            # Check quiz score requirements
            req_level = requirements.get('level')
            req_topic = requirements.get('topic')
            req_score = requirements['quiz_score']
            
            # Query for quiz results
            query = QuizResult.query.filter_by(user_id=user_id)
            if req_level:
                query = query.filter_by(level=req_level)
            if req_topic:
                query = query.filter_by(topic=req_topic)
            
            # Check if any quiz meets the score requirement
            for result in query.all():
                score_percentage = (result.score / result.max_score) * 100
                if score_percentage >= req_score:
                    if award_badge(user_id, badge.id):
                        newly_earned_badges.append(badge)
                    break
        
        elif 'streak_days' in requirements:
            # Check streak requirements
            req_days = requirements['streak_days']
            if user.streak_days >= req_days:
                if award_badge(user_id, badge.id):
                    newly_earned_badges.append(badge)
        
        elif 'points' in requirements:
            # Check points requirements
            req_points = requirements['points']
            if user.points >= req_points:
                if award_badge(user_id, badge.id):
                    newly_earned_badges.append(badge)
        
        elif 'lessons_completed' in requirements:
            # Check lesson completion requirements
            req_count = requirements['lessons_completed']
            req_level = requirements.get('level')
            
            # Query for completed lessons
            query = Progress.query.filter_by(user_id=user_id, completed=True)
            if req_level:
                query = query.filter_by(level=req_level)
            
            if query.count() >= req_count:
                if award_badge(user_id, badge.id):
                    newly_earned_badges.append(badge)
    
    return newly_earned_badges

def create_initial_badges():
    """Create initial badges in the system if they don't exist"""
    badges = [
        {
            'name': 'Beginner',
            'description': 'Completed your first lesson',
            'icon': 'fa-star',
            'requirements': json.dumps({'lessons_completed': 1})
        },
        {
            'name': 'Quick Learner',
            'description': 'Achieved a perfect score on any quiz',
            'icon': 'fa-trophy',
            'requirements': json.dumps({'quiz_score': 100})
        },
        {
            'name': 'A1 Master',
            'description': 'Completed all A1 lessons',
            'icon': 'fa-graduation-cap',
            'requirements': json.dumps({'lessons_completed': 10, 'level': 'a1'})
        },
        {
            'name': 'Streak Hunter',
            'description': 'Maintained a 7-day learning streak',
            'icon': 'fa-fire',
            'requirements': json.dumps({'streak_days': 7})
        },
        {
            'name': 'Word Collector',
            'description': 'Learned 50 vocabulary words',
            'icon': 'fa-book',
            'requirements': json.dumps({'vocabulary_count': 50})
        }
    ]
    
    for badge_data in badges:
        # Check if badge already exists
        existing = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing:
            new_badge = Badge(
                name=badge_data['name'],
                description=badge_data['description'],
                icon=badge_data['icon'],
                requirements=badge_data['requirements']
            )
            db.session.add(new_badge)
    
    db.session.commit()

def update_user_points(user_id, points_to_add, reason=None):
    """
    Add points to a user and update their streak
    reasons: 'quiz', 'lesson', 'streak', 'login', etc.
    """
    user = User.query.get(user_id)
    if user:
        user.add_points(points_to_add)
        user.update_streak()
        db.session.commit()
        return user.points
    return None

def get_leaderboard(limit=10):
    """Get top users based on points"""
    return User.query.order_by(User.points.desc()).limit(limit).all()

def calculate_quiz_points(score, max_score, level):
    """Calculate points to award for a quiz result"""
    # Base points for completing a quiz
    base_points = 10
    
    # Points based on percentage score
    score_percentage = (score / max_score) * 100
    score_points = int(score_percentage / 10)  # 10 points for each 10% correct
    
    # Bonus points for higher levels
    level_bonus = {
        'a1': 0,
        'a2': 5,
        'b1': 10
    }
    
    # Bonus for perfect score
    perfect_bonus = 20 if score == max_score else 0
    
    total_points = base_points + score_points + level_bonus.get(level.lower(), 0) + perfect_bonus
    
    return total_points

def calculate_lesson_points(level):
    """Calculate points to award for completing a lesson"""
    level_points = {
        'a1': 5,
        'a2': 10,
        'b1': 15
    }
    
    return level_points.get(level.lower(), 5)