from app import db
from models import Progress, QuizResult
from datetime import datetime

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
    return quiz_result

def get_quiz_results(user_id, level=None):
    """Retrieve a user's quiz results, optionally filtered by level"""
    if level:
        return QuizResult.query.filter_by(user_id=user_id, level=level).order_by(QuizResult.completed_at.desc()).all()
    else:
        return QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.completed_at.desc()).all()

def get_leaderboard(limit=10):
    """Get top users based on quiz results"""
    # This is a simplified version that calculates average scores
    # A more sophisticated approach would use a SQL query with aggregations
    
    # Get all quiz results grouped by user
    users_scores = {}
    quiz_results = QuizResult.query.all()
    
    for result in quiz_results:
        user_id = result.user_id
        score_percent = (result.score / result.max_score) * 100
        
        if user_id in users_scores:
            users_scores[user_id]["total"] += score_percent
            users_scores[user_id]["count"] += 1
        else:
            users_scores[user_id] = {"total": score_percent, "count": 1}
    
    # Calculate averages and sort
    leaderboard = []
    for user_id, data in users_scores.items():
        avg_score = data["total"] / data["count"]
        leaderboard.append({"user_id": user_id, "avg_score": avg_score})
    
    # Sort by average score and limit results
    leaderboard.sort(key=lambda x: x["avg_score"], reverse=True)
    return leaderboard[:limit]
