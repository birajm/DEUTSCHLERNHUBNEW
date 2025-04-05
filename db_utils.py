from app import db
from models import Progress, QuizResult, User
from datetime import datetime
from badge_utils import update_user_points, calculate_quiz_points, calculate_lesson_points, check_badge_eligibility

def get_user_progress(user_id):
    """Retrieve a user's learning progress"""
    return Progress.query.filter_by(user_id=user_id).all()

def save_progress(user_id, level, section, lesson, completed):
    """Save or update a user's progress for a specific lesson"""
    # Check if progress entry already exists
    progress = Progress.query.filter_by(
        user_id=user_id,
        level=level,
        section=section,
        lesson=lesson
    ).first()
    
    was_already_completed = progress.completed if progress else False
    
    if progress:
        # Update existing progress
        progress.completed = completed
        progress.last_accessed = datetime.utcnow()
    else:
        # Create new progress entry
        progress = Progress(
            user_id=user_id,
            level=level,
            section=section,
            lesson=lesson,
            completed=completed,
            last_accessed=datetime.utcnow()
        )
        db.session.add(progress)
    
    db.session.commit()
    
    # Award points for newly completed lessons
    if completed and not was_already_completed:
        points = calculate_lesson_points(level)
        update_user_points(user_id, points, 'lesson')
        
        # Check for badges
        newly_earned_badges = check_badge_eligibility(user_id)
    
    return progress

def save_quiz_result(user_id, level, topic, score, max_score):
    """Save a user's quiz result"""
    quiz_result = QuizResult(
        user_id=user_id,
        level=level,
        topic=topic,
        score=score,
        max_score=max_score,
        completed_at=datetime.utcnow()
    )
    
    db.session.add(quiz_result)
    db.session.commit()
    
    # Award points for quiz completion
    points = calculate_quiz_points(score, max_score, level)
    update_user_points(user_id, points, 'quiz')
    
    # Check for badges
    newly_earned_badges = check_badge_eligibility(user_id)
    
    return quiz_result

def get_quiz_results(user_id, level=None):
    """Retrieve a user's quiz results, optionally filtered by level"""
    if level:
        return QuizResult.query.filter_by(user_id=user_id, level=level).order_by(QuizResult.completed_at.desc()).all()
    else:
        return QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.completed_at.desc()).all()

def get_user_stats(user_id):
    """Get comprehensive statistics for a user"""
    user = User.query.get(user_id)
    if not user:
        return None
    
    # Get completed lessons count
    total_lessons = Progress.query.filter_by(user_id=user_id).count()
    completed_lessons = Progress.query.filter_by(user_id=user_id, completed=True).count()
    
    # Get quiz statistics
    quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
    quiz_count = len(quiz_results)
    
    total_score = 0
    total_possible = 0
    for result in quiz_results:
        total_score += result.score
        total_possible += result.max_score
    
    average_score = (total_score / total_possible * 100) if total_possible > 0 else 0
    
    # Get level-specific stats
    a1_completed = Progress.query.filter_by(user_id=user_id, level='a1', completed=True).count()
    a2_completed = Progress.query.filter_by(user_id=user_id, level='a2', completed=True).count()
    b1_completed = Progress.query.filter_by(user_id=user_id, level='b1', completed=True).count()
    
    return {
        'username': user.username,
        'points': user.points,
        'streak_days': user.streak_days,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'completion_percentage': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
        'quiz_count': quiz_count,
        'average_score': average_score,
        'level_progress': {
            'a1': a1_completed,
            'a2': a2_completed,
            'b1': b1_completed
        },
        'badges': [ub.badge for ub in user.badges]
    }

def get_leaderboard(limit=10):
    """Get top users based on points"""
    users = User.query.order_by(User.points.desc()).limit(limit).all()
    
    leaderboard = []
    for user in users:
        completed_lessons = Progress.query.filter_by(user_id=user.id, completed=True).count()
        
        leaderboard.append({
            'user_id': user.id,
            'username': user.username,
            'points': user.points,
            'streak': user.streak_days,
            'completed_lessons': completed_lessons,
            'badge_count': user.badges.count()
        })
    
    return leaderboard

def get_lesson_completion_count(level=None):
    """Get count of users who have completed lessons, optionally by level"""
    if level:
        completed_lessons = db.session.query(Progress.user_id, db.func.count(Progress.id)).filter_by(
            level=level, completed=True
        ).group_by(Progress.user_id).all()
    else:
        completed_lessons = db.session.query(Progress.user_id, db.func.count(Progress.id)).filter_by(
            completed=True
        ).group_by(Progress.user_id).all()
    
    return completed_lessons
