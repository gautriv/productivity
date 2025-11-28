"""
Motivation Blueprint
World-class gamification and motivation endpoints
"""
from flask import Blueprint, jsonify, request
from datetime import date, datetime
from models.database import get_db
from services.motivation import MotivationEngine, DailyChallengeEngine, PointsEngine
from services.motivation.gamification import GamificationEngine
from services.motivation.quotes import MotivationQuotesEngine
from services.motivation.achievements import AchievementEngine
from utils.helpers import handle_errors

motivation_bp = Blueprint('motivation', __name__)

@motivation_bp.route('/achievements', methods=['GET'])
@handle_errors
def get_achievements():
    """Get all achievements with tiers, progress, and unlock status"""
    achievements = AchievementEngine.get_all_achievements()
    
    # Filter hidden achievements that aren't unlocked
    visible_achievements = [
        a for a in achievements 
        if not a.get('hidden', False) or a['unlocked']
    ]
    
    return jsonify(visible_achievements)

@motivation_bp.route('/achievements/all', methods=['GET'])
@handle_errors
def get_all_achievements_detailed():
    """Get all achievements with full details including hidden ones (for admin/debug)"""
    return jsonify(AchievementEngine.get_all_achievements())

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
    """Get smart context-aware motivational quote"""
    context = request.args.get('context', 'general')
    quote = MotivationEngine.get_motivational_message(context)
    
    # Get current time info for client
    from datetime import datetime
    now = datetime.now()
    
    return jsonify({
        'quote': quote,
        'context': context,
        'time_of_day': 'morning' if 5 <= now.hour < 12 else 
                       'afternoon' if 12 <= now.hour < 18 else 'evening',
        'day_of_week': now.strftime('%A'),
        'total_quotes_available': sum(len(q) for q in MotivationEngine.QUOTES.values())
    })

@motivation_bp.route('/quote/refresh', methods=['POST'])
@handle_errors
def refresh_quote():
    """Get a new quote (forces different from current)"""
    current_quote = request.json.get('current_quote', '')
    
    # Get new quote, ensuring it's different
    max_attempts = 5
    for _ in range(max_attempts):
        new_quote = MotivationEngine.get_motivational_message('general')
        if new_quote != current_quote:
            break
    
    return jsonify({
        'quote': new_quote,
        'refreshed': True
    })

@motivation_bp.route('/daily-challenge/<date_str>', methods=['GET'])
@handle_errors
def get_daily_challenge(date_str):
    """Get personalized daily challenge with smart selection"""
    challenge = MotivationEngine.get_daily_challenge(date_str)
    return jsonify(challenge)

@motivation_bp.route('/daily-challenge/<date_str>/check', methods=['POST'])
@handle_errors
def check_challenge_completion(date_str):
    """Check if daily challenge is completed"""
    result = DailyChallengeEngine.check_challenge_completion(date_str)
    
    # If just completed, get the challenge details for bonus
    if result.get('just_completed'):
        challenge = DailyChallengeEngine.get_daily_challenge(date_str)
        result['bonus_points'] = challenge.get('bonus_points', 0)
        result['challenge_title'] = challenge.get('title', '')
    
    return jsonify(result)

@motivation_bp.route('/challenge-stats', methods=['GET'])
@handle_errors
def get_challenge_stats():
    """Get challenge completion statistics"""
    stats = DailyChallengeEngine.get_challenge_stats()
    return jsonify(stats)

@motivation_bp.route('/challenges/all', methods=['GET'])
@handle_errors  
def get_all_challenges():
    """Get list of all available challenges (for reference/help)"""
    challenges = []
    for challenge_id, challenge in DailyChallengeEngine.CHALLENGES.items():
        difficulty = DailyChallengeEngine.DIFFICULTY[challenge['difficulty']]
        challenges.append({
            'id': challenge_id,
            'title': challenge['title'],
            'description': challenge['description'],
            'icon': challenge['icon'],
            'category': challenge['category'],
            'difficulty': challenge['difficulty'],
            'difficulty_color': difficulty['color'],
            'bonus_range': f"{difficulty['min_bonus']}-{difficulty['max_bonus']}",
            'tags': challenge.get('tags', [])
        })
    
    # Group by category
    by_category = {}
    for c in challenges:
        cat = c['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(c)
    
    return jsonify({
        'total_challenges': len(challenges),
        'challenges': challenges,
        'by_category': by_category,
        'categories': list(by_category.keys()),
        'difficulties': list(DailyChallengeEngine.DIFFICULTY.keys())
    })

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
    stats = GamificationEngine.get_user_stats()
    
    current_level = stats['level']
    
    # Get level up rewards
    rewards = GamificationEngine.get_level_up_rewards(current_level)
    
    return jsonify({
        'current_level': current_level,
        'rank': stats['rank'],
        'rank_icon': stats['rank_icon'],
        'tier': stats['tier'],
        'rewards': rewards,
        'message': f'You are Level {current_level} - {stats["rank"]}!'
    })

# ===== NEW WORLD-CLASS GAMIFICATION ENDPOINTS =====

@motivation_bp.route('/gamification/stats', methods=['GET'])
@handle_errors
def get_gamification_stats():
    """Get comprehensive gamification statistics"""
    stats = GamificationEngine.get_user_stats()
    return jsonify(stats)

@motivation_bp.route('/gamification/rank/<int:level>', methods=['GET'])
@handle_errors
def get_rank_info(level):
    """Get rank information for a specific level"""
    rank_info = GamificationEngine.get_rank_info(level)
    return jsonify(rank_info)

@motivation_bp.route('/gamification/ranks', methods=['GET'])
@handle_errors
def get_all_ranks():
    """Get all available ranks"""
    ranks = []
    for level, rank in GamificationEngine.RANKS.items():
        xp_needed = GamificationEngine.calculate_xp_for_level(level)
        ranks.append({
            'level': level,
            'title': rank['title'],
            'icon': rank['icon'],
            'color': rank['color'],
            'tier': rank['tier'],
            'xp_required': xp_needed
        })
    
    return jsonify({
        'total_ranks': len(ranks),
        'ranks': ranks,
        'max_level': 50
    })

@motivation_bp.route('/gamification/milestones', methods=['GET'])
@handle_errors
def get_milestones():
    """Get all milestones and rewards"""
    milestones = []
    for level, milestone in GamificationEngine.MILESTONES.items():
        milestones.append({
            'level': level,
            'reward': milestone['reward'],
            'bonus_xp': milestone['bonus_xp'],
            'description': milestone['description'],
            'xp_required': GamificationEngine.calculate_xp_for_level(level)
        })
    
    return jsonify({
        'total_milestones': len(milestones),
        'milestones': milestones
    })

@motivation_bp.route('/gamification/streak-bonus', methods=['GET'])
@handle_errors
def get_streak_bonus():
    """Get current streak multiplier and bonuses"""
    current_streak = GamificationEngine._calculate_current_streak()
    streak_info = GamificationEngine.get_streak_multiplier(current_streak)
    
    return jsonify(streak_info)

@motivation_bp.route('/gamification/xp-breakdown', methods=['GET'])
@handle_errors
def get_xp_breakdown():
    """Get detailed XP breakdown by source"""
    stats = GamificationEngine.get_user_stats()
    
    return jsonify({
        'total_xp': stats['total_xp'],
        'breakdown': stats['xp_breakdown'],
        'today_xp': stats['today_xp'],
        'daily_goal': GamificationEngine.get_daily_xp_goal(stats['level']),
        'weekly_goal': GamificationEngine.get_weekly_xp_goal(stats['level'])
    })

@motivation_bp.route('/gamification/multipliers', methods=['GET'])
@handle_errors
def get_multipliers():
    """Get all available XP multipliers"""
    return jsonify(GamificationEngine.MULTIPLIERS)

@motivation_bp.route('/gamification/level-preview/<int:target_level>', methods=['GET'])
@handle_errors
def preview_level(target_level):
    """Preview what a specific level looks like"""
    if target_level < 1 or target_level > 50:
        return jsonify({'error': 'Level must be between 1 and 50'}), 400
    
    rank_info = GamificationEngine.get_rank_info(target_level)
    xp_needed = GamificationEngine.calculate_xp_for_level(target_level)
    rewards = GamificationEngine.get_level_up_rewards(target_level)
    
    return jsonify({
        'level': target_level,
        'rank': rank_info,
        'xp_required': xp_needed,
        'rewards': rewards
    })

@motivation_bp.route('/quotes/categories', methods=['GET'])
@handle_errors
def get_quote_categories():
    """Get all quote categories and counts"""
    categories = {}
    for category, quotes in MotivationQuotesEngine.QUOTES.items():
        categories[category] = len(quotes)
    
    return jsonify({
        'total_quotes': MotivationQuotesEngine.get_quote_count(),
        'categories': categories
    })

@motivation_bp.route('/achievements/stats', methods=['GET'])
@handle_errors
def get_achievement_stats():
    """Get achievement statistics"""
    stats = AchievementEngine.get_achievement_stats()
    return jsonify(stats)

@motivation_bp.route('/achievements/categories', methods=['GET'])
@handle_errors
def get_achievement_categories():
    """Get all achievement categories with progress"""
    stats = AchievementEngine.get_achievement_stats()
    return jsonify({
        'categories': AchievementEngine.CATEGORIES,
        'progress': stats['by_category'],
        'tiers': AchievementEngine.TIERS
    })

@motivation_bp.route('/achievements/next', methods=['GET'])
@handle_errors
def get_next_achievements():
    """Get achievements closest to being unlocked"""
    limit = request.args.get('limit', 5, type=int)
    next_achievements = AchievementEngine.get_next_achievements(limit)
    return jsonify({
        'next_achievements': next_achievements,
        'count': len(next_achievements)
    })

@motivation_bp.route('/achievements/showcase', methods=['GET'])
@handle_errors
def get_achievement_showcase():
    """Get user's achievement showcase (best achievements)"""
    achievements = AchievementEngine.get_all_achievements()
    
    # Get top tier unlocked achievements for showcase
    unlocked = [a for a in achievements if a['unlocked']]
    
    # Sort by tier (diamond first) then by points
    tier_order = {'diamond': 0, 'platinum': 1, 'gold': 2, 'silver': 3, 'bronze': 4}
    unlocked.sort(key=lambda x: (tier_order.get(x['tier'], 5), -x['points']))
    
    showcase = unlocked[:6]  # Top 6 achievements
    
    return jsonify({
        'showcase': showcase,
        'total_unlocked': len(unlocked),
        'total_points': sum(a['points'] for a in unlocked)
    })

# ===== WORLD-CLASS POINTS ENDPOINTS =====

@motivation_bp.route('/points/calculate', methods=['POST'])
@handle_errors
def calculate_task_points():
    """Calculate points for a task with full breakdown"""
    task_data = request.json
    breakdown = PointsEngine.calculate_task_points(task_data)
    return jsonify(breakdown)

@motivation_bp.route('/points/daily/<date_str>', methods=['GET'])
@handle_errors
def get_daily_points(date_str):
    """Get detailed daily point statistics"""
    stats = PointsEngine.get_daily_stats(date_str)
    return jsonify(stats)

@motivation_bp.route('/points/weekly', methods=['GET'])
@handle_errors
def get_weekly_points():
    """Get weekly point summary"""
    summary = PointsEngine.get_weekly_summary()
    return jsonify(summary)

@motivation_bp.route('/points/all-time', methods=['GET'])
@handle_errors
def get_all_time_points():
    """Get all-time point statistics"""
    stats = PointsEngine.get_all_time_stats()
    return jsonify(stats)

@motivation_bp.route('/points/breakdown', methods=['GET'])
@handle_errors
def get_points_breakdown():
    """Get full points system breakdown (multipliers, bonuses, etc.)"""
    return jsonify(PointsEngine.get_points_breakdown())

@motivation_bp.route('/points/multipliers', methods=['GET'])
@handle_errors
def get_point_multipliers():
    """Get all available point multipliers"""
    return jsonify({
        'cognitive_multipliers': PointsEngine.COGNITIVE_MULTIPLIERS,
        'time_bonuses': PointsEngine.TIME_BONUSES,
        'combo_multipliers': PointsEngine.COMBO_MULTIPLIERS,
        'special_bonuses': PointsEngine.SPECIAL_BONUSES
    })

@motivation_bp.route('/points/milestones', methods=['GET'])
@handle_errors
def get_point_milestones():
    """Get all point milestones and rewards"""
    stats = PointsEngine.get_all_time_stats()
    return jsonify({
        'milestones': PointsEngine.MILESTONES,
        'milestones_reached': stats.get('milestones_reached', []),
        'next_milestone': stats.get('next_milestone')
    })

@motivation_bp.route('/points/goals', methods=['GET'])
@handle_errors
def get_daily_goals():
    """Get daily point goals by tier"""
    return jsonify({
        'goals': PointsEngine.DAILY_GOALS,
        'description': 'Complete tasks to earn points and reach your daily goal'
    })

