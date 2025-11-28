"""
Motivation Blueprint
Gamification and motivation endpoints
"""
from flask import Blueprint, jsonify, request
from datetime import date
from models.database import get_db
from services.motivation import MotivationEngine
from utils.helpers import handle_errors

motivation_bp = Blueprint('motivation', __name__)

@motivation_bp.route('/achievements', methods=['GET'])
@handle_errors
def get_achievements():
    """Get all achievements (locked and unlocked)"""
    db = get_db()
    cursor = db.cursor()
    
    # Get unlocked achievements
    cursor.execute('''
        SELECT name, unlocked_at
        FROM achievements
        WHERE unlocked_at IS NOT NULL
        ORDER BY unlocked_at DESC
    ''')
    
    unlocked = {row['name']: row['unlocked_at'] for row in cursor.fetchall()}
    
    # Build complete achievement list
    achievements = []
    for achievement_id, achievement in MotivationEngine.ACHIEVEMENTS.items():
        unlocked_at = unlocked.get(achievement['name'])
        achievements.append({
            'id': achievement_id,
            'name': achievement['name'],
            'description': achievement['description'],
            'icon': achievement['icon'],
            'type': achievement['type'],
            'requirement': achievement['requirement'],
            'points': achievement['points'],
            'unlocked': unlocked_at is not None,
            'unlocked_at': unlocked_at
        })
    
    # Sort by unlocked status then by points
    achievements.sort(key=lambda x: (not x['unlocked'], -x['points']))
    
    return jsonify(achievements)

@motivation_bp.route('/check-achievements', methods=['POST'])
@handle_errors
def check_achievements():
    """Check for newly unlocked achievements"""
    user_id = request.json.get('user_id', 'default')
    newly_unlocked = MotivationEngine.check_achievements(user_id)
    
    return jsonify({
        'newly_unlocked': newly_unlocked,
        'count': len(newly_unlocked)
    })

@motivation_bp.route('/stats', methods=['GET'])
@handle_errors
def get_user_stats():
    """Get comprehensive user stats for gamification"""
    stats = MotivationEngine.get_user_stats()
    return jsonify(stats)

@motivation_bp.route('/quote', methods=['GET'])
@handle_errors
def get_quote():
    """Get motivational quote"""
    context = request.args.get('context', 'general')
    quote = MotivationEngine.get_motivational_message(context)
    
    return jsonify({
        'quote': quote,
        'context': context
    })

@motivation_bp.route('/daily-challenge/<date_str>', methods=['GET'])
@handle_errors
def get_daily_challenge(date_str):
    """Get personalized daily challenge"""
    challenge = MotivationEngine.get_daily_challenge(date_str)
    return jsonify(challenge)

@motivation_bp.route('/streak', methods=['GET'])
@handle_errors
def get_streak():
    """Get current streak information"""
    current_streak = MotivationEngine.calculate_current_streak()
    
    # Get longest streak from DB
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT MAX(longest_streak) as longest
        FROM user_stats
    ''')
    
    row = cursor.fetchone()
    longest_streak = row['longest'] if row and row['longest'] else current_streak
    
    # Update if current is longer
    if current_streak > longest_streak:
        longest_streak = current_streak
    
    return jsonify({
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'is_record': current_streak >= longest_streak,
        'days_to_next_milestone': _days_to_milestone(current_streak)
    })

def _days_to_milestone(streak):
    """Calculate days to next streak milestone"""
    milestones = [3, 7, 14, 21, 30, 60, 90, 180, 365]
    for milestone in milestones:
        if streak < milestone:
            return milestone - streak
    return 30  # Next 30 days

@motivation_bp.route('/leaderboard', methods=['GET'])
@handle_errors
def get_leaderboard():
    """Get leaderboard data (for future multi-user support)"""
    stats = MotivationEngine.get_user_stats()
    
    # For now, just return current user stats
    # In the future, this can be expanded for multiple users
    return jsonify({
        'leaderboard': [{
            'rank': 1,
            'user': 'You',
            'level': stats['level'],
            'total_points': stats['total_points'],
            'current_streak': stats['current_streak'],
            'achievements': stats['achievements_unlocked']
        }],
        'user_rank': 1
    })

@motivation_bp.route('/level-up', methods=['POST'])
@handle_errors
def check_level_up():
    """Check if user has leveled up"""
    stats = MotivationEngine.get_user_stats()
    
    # Calculate if recently leveled up (within last session)
    current_level = stats['level']
    total_points = stats['total_points']
    
    # Points for previous level
    prev_level_points = ((current_level - 2) ** 2) * 50 if current_level > 1 else 0
    
    recently_leveled = total_points - prev_level_points < 100  # Within ~100 points of level up
    
    return jsonify({
        'leveled_up': recently_leveled,
        'current_level': current_level,
        'message': f'Congratulations! You reached Level {current_level}!' if recently_leveled else None
    })

