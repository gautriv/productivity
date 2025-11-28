"""
World-Class Gamification Engine
Sophisticated Level & XP System with prestige, ranks, multipliers, and progression tracking
"""
from datetime import datetime, date, timedelta
from models.database import get_db, calculate_task_points
import math


def get_total_achievements_count():
    """Get total count of visible achievements (excluding hidden ones that aren't unlocked)"""
    try:
        from services.motivation.achievements import AchievementEngine
        all_achievements = AchievementEngine.get_all_achievements()
        # Filter hidden achievements that aren't unlocked (same logic as API endpoint)
        visible_achievements = [
            a for a in all_achievements
            if not a.get('hidden', False) or a.get('unlocked', False)
        ]
        return len(visible_achievements)
    except:
        return 46  # Fallback to current count


class GamificationEngine:
    """
    World-Class Level & XP System
    Features:
    - 50 levels with prestigious ranks
    - Exponential XP curve with diminishing returns prevention
    - XP multipliers for streaks, challenges, cognitive load
    - Prestige system for veteran users
    - Visual milestones and rewards
    - Detailed XP breakdown and statistics
    """
    
    # ===== LEVEL RANKS & TITLES =====
    # Each rank represents a tier of mastery
    RANKS = {
        # Tier 1: Levels 1-10 (Beginner)
        1: {'title': 'Novice', 'icon': '🌱', 'color': '#9ca3af', 'tier': 'beginner'},
        2: {'title': 'Apprentice', 'icon': '📚', 'color': '#9ca3af', 'tier': 'beginner'},
        3: {'title': 'Student', 'icon': '✏️', 'color': '#9ca3af', 'tier': 'beginner'},
        4: {'title': 'Learner', 'icon': '🎓', 'color': '#9ca3af', 'tier': 'beginner'},
        5: {'title': 'Initiate', 'icon': '🔰', 'color': '#22c55e', 'tier': 'beginner'},
        6: {'title': 'Trainee', 'icon': '💪', 'color': '#22c55e', 'tier': 'beginner'},
        7: {'title': 'Rookie', 'icon': '⭐', 'color': '#22c55e', 'tier': 'beginner'},
        8: {'title': 'Junior', 'icon': '🌟', 'color': '#22c55e', 'tier': 'beginner'},
        9: {'title': 'Adept', 'icon': '✨', 'color': '#22c55e', 'tier': 'beginner'},
        10: {'title': 'Skilled', 'icon': '🎯', 'color': '#3b82f6', 'tier': 'beginner'},
        
        # Tier 2: Levels 11-20 (Intermediate)
        11: {'title': 'Practitioner', 'icon': '🔧', 'color': '#3b82f6', 'tier': 'intermediate'},
        12: {'title': 'Journeyman', 'icon': '🛤️', 'color': '#3b82f6', 'tier': 'intermediate'},
        13: {'title': 'Craftsman', 'icon': '⚒️', 'color': '#3b82f6', 'tier': 'intermediate'},
        14: {'title': 'Artisan', 'icon': '🎨', 'color': '#3b82f6', 'tier': 'intermediate'},
        15: {'title': 'Specialist', 'icon': '🎖️', 'color': '#8b5cf6', 'tier': 'intermediate'},
        16: {'title': 'Professional', 'icon': '💼', 'color': '#8b5cf6', 'tier': 'intermediate'},
        17: {'title': 'Veteran', 'icon': '🏅', 'color': '#8b5cf6', 'tier': 'intermediate'},
        18: {'title': 'Expert', 'icon': '🧠', 'color': '#8b5cf6', 'tier': 'intermediate'},
        19: {'title': 'Mentor', 'icon': '📖', 'color': '#8b5cf6', 'tier': 'intermediate'},
        20: {'title': 'Master', 'icon': '🏆', 'color': '#f59e0b', 'tier': 'intermediate'},
        
        # Tier 3: Levels 21-30 (Advanced)
        21: {'title': 'Elite', 'icon': '💎', 'color': '#f59e0b', 'tier': 'advanced'},
        22: {'title': 'Champion', 'icon': '🥇', 'color': '#f59e0b', 'tier': 'advanced'},
        23: {'title': 'Conqueror', 'icon': '⚔️', 'color': '#f59e0b', 'tier': 'advanced'},
        24: {'title': 'Virtuoso', 'icon': '🎭', 'color': '#f59e0b', 'tier': 'advanced'},
        25: {'title': 'Grandmaster', 'icon': '👑', 'color': '#ef4444', 'tier': 'advanced'},
        26: {'title': 'Legendary', 'icon': '🌠', 'color': '#ef4444', 'tier': 'advanced'},
        27: {'title': 'Mythic', 'icon': '🔮', 'color': '#ef4444', 'tier': 'advanced'},
        28: {'title': 'Immortal', 'icon': '♾️', 'color': '#ef4444', 'tier': 'advanced'},
        29: {'title': 'Transcendent', 'icon': '🌌', 'color': '#ef4444', 'tier': 'advanced'},
        30: {'title': 'Ascended', 'icon': '👁️', 'color': '#ef4444', 'tier': 'advanced'},
        
        # Tier 4: Levels 31-40 (Elite)
        31: {'title': 'Overlord', 'icon': '🦅', 'color': '#ec4899', 'tier': 'elite'},
        32: {'title': 'Sovereign', 'icon': '🏛️', 'color': '#ec4899', 'tier': 'elite'},
        33: {'title': 'Emperor', 'icon': '🦁', 'color': '#ec4899', 'tier': 'elite'},
        34: {'title': 'Titan', 'icon': '🗿', 'color': '#ec4899', 'tier': 'elite'},
        35: {'title': 'Demigod', 'icon': '⚡', 'color': '#ec4899', 'tier': 'elite'},
        36: {'title': 'Divine', 'icon': '☀️', 'color': '#fbbf24', 'tier': 'elite'},
        37: {'title': 'Celestial', 'icon': '🌙', 'color': '#fbbf24', 'tier': 'elite'},
        38: {'title': 'Eternal', 'icon': '💫', 'color': '#fbbf24', 'tier': 'elite'},
        39: {'title': 'Infinity', 'icon': '🌀', 'color': '#fbbf24', 'tier': 'elite'},
        40: {'title': 'Omega', 'icon': 'Ω', 'color': '#fbbf24', 'tier': 'elite'},
        
        # Tier 5: Levels 41-50 (Legendary)
        41: {'title': 'Apex Predator', 'icon': '🐺', 'color': '#14b8a6', 'tier': 'legendary'},
        42: {'title': 'World Shaper', 'icon': '🌍', 'color': '#14b8a6', 'tier': 'legendary'},
        43: {'title': 'Time Master', 'icon': '⏳', 'color': '#14b8a6', 'tier': 'legendary'},
        44: {'title': 'Reality Bender', 'icon': '🎲', 'color': '#14b8a6', 'tier': 'legendary'},
        45: {'title': 'Cosmos Walker', 'icon': '🚀', 'color': '#14b8a6', 'tier': 'legendary'},
        46: {'title': 'Universe Architect', 'icon': '🏗️', 'color': '#f97316', 'tier': 'legendary'},
        47: {'title': 'Dimension Ruler', 'icon': '🌐', 'color': '#f97316', 'tier': 'legendary'},
        48: {'title': 'Existence Keeper', 'icon': '🔑', 'color': '#f97316', 'tier': 'legendary'},
        49: {'title': 'Productivity God', 'icon': '⚜️', 'color': '#f97316', 'tier': 'legendary'},
        50: {'title': 'The One', 'icon': '👁️‍🗨️', 'color': '#f97316', 'tier': 'legendary'}
    }
    
    # ===== XP MULTIPLIERS =====
    MULTIPLIERS = {
        # Cognitive load multipliers
        'cognitive_load': {
            'deep_work': 2.0,
            'learning': 1.5,
            'active_work': 1.2,
            'admin': 1.0
        },
        # Streak multipliers (streak length -> multiplier)
        'streak': {
            3: 1.1,    # 3-day streak: +10%
            7: 1.25,   # Week streak: +25%
            14: 1.4,   # 2-week streak: +40%
            30: 1.6,   # Month streak: +60%
            60: 1.8,   # 2-month streak: +80%
            90: 2.0,   # Quarter streak: +100%
            180: 2.5,  # Half-year streak: +150%
            365: 3.0   # Year streak: +200%
        },
        # Complexity multipliers
        'complexity': {
            1: 1.0,
            2: 1.2,
            3: 1.5,
            4: 2.0,
            5: 2.5
        },
        # Time bonuses
        'early_bird': 1.2,      # Before 7 AM
        'night_owl': 1.1,       # After 10 PM
        'perfect_day': 1.5,     # 100% completion
        'challenge_complete': 1.3  # Daily challenge done
    }
    
    # ===== MILESTONES & REWARDS =====
    MILESTONES = {
        5: {'reward': 'Beginner Badge', 'bonus_xp': 100, 'description': 'Completed your first week of productivity!'},
        10: {'reward': 'Bronze Badge', 'bonus_xp': 250, 'description': 'Reached double digits! You\'re building momentum.'},
        15: {'reward': 'Silver Badge', 'bonus_xp': 500, 'description': 'Halfway to mastery. Keep climbing!'},
        20: {'reward': 'Gold Badge', 'bonus_xp': 1000, 'description': 'Master level achieved! You\'re in the top tier.'},
        25: {'reward': 'Platinum Badge', 'bonus_xp': 2000, 'description': 'Grandmaster status. Elite productivity awaits!'},
        30: {'reward': 'Diamond Badge', 'bonus_xp': 3500, 'description': 'Ascended beyond ordinary. Truly exceptional!'},
        40: {'reward': 'Legendary Badge', 'bonus_xp': 5000, 'description': 'Omega tier reached. You are legendary!'},
        50: {'reward': 'Ultimate Badge', 'bonus_xp': 10000, 'description': 'The One. Maximum level achieved. Prestige unlocked!'}
    }
    
    # ===== PRESTIGE SYSTEM =====
    # After level 50, users can "prestige" to reset to level 1 with permanent bonuses
    PRESTIGE_BONUSES = {
        1: {'xp_bonus': 1.1, 'title_prefix': '⭐'},
        2: {'xp_bonus': 1.2, 'title_prefix': '⭐⭐'},
        3: {'xp_bonus': 1.35, 'title_prefix': '⭐⭐⭐'},
        4: {'xp_bonus': 1.5, 'title_prefix': '💫'},
        5: {'xp_bonus': 1.75, 'title_prefix': '🌟'},
        6: {'xp_bonus': 2.0, 'title_prefix': '✨'},
        7: {'xp_bonus': 2.5, 'title_prefix': '👑'},
        8: {'xp_bonus': 3.0, 'title_prefix': '🏆'},
        9: {'xp_bonus': 4.0, 'title_prefix': '💎'},
        10: {'xp_bonus': 5.0, 'title_prefix': '🔱'}
    }
    
    # ===== XP CALCULATION =====
    @staticmethod
    def calculate_xp_for_level(level):
        """
        Calculate total XP needed to reach a specific level
        Uses a smooth exponential curve that feels fair and achievable
        Formula: XP = 50 * (level^1.8) + 25 * level
        """
        if level <= 1:
            return 0
        return int(50 * (level ** 1.8) + 25 * level)
    
    @staticmethod
    def calculate_level_from_xp(total_xp):
        """Calculate level from total XP earned"""
        level = 1
        while GamificationEngine.calculate_xp_for_level(level + 1) <= total_xp:
            level += 1
            if level >= 50:  # Cap at level 50 (prestige required)
                break
        return level
    
    @staticmethod
    def get_xp_progress(total_xp):
        """Get detailed XP progress information"""
        level = GamificationEngine.calculate_level_from_xp(total_xp)
        
        xp_for_current = GamificationEngine.calculate_xp_for_level(level)
        xp_for_next = GamificationEngine.calculate_xp_for_level(level + 1)
        
        current_xp = total_xp - xp_for_current
        xp_needed = xp_for_next - xp_for_current
        
        return {
            'level': level,
            'total_xp': total_xp,
            'current_xp': current_xp,
            'xp_needed': xp_needed,
            'xp_for_next_level': xp_for_next,
            'percentage': round((current_xp / xp_needed * 100), 1) if xp_needed > 0 else 100,
            'is_max_level': level >= 50
        }
    
    @staticmethod
    def get_rank_info(level):
        """Get rank information for a level"""
        rank = GamificationEngine.RANKS.get(level, GamificationEngine.RANKS[50])
        
        # Find next milestone
        next_milestone = None
        for milestone_level in sorted(GamificationEngine.MILESTONES.keys()):
            if milestone_level > level:
                next_milestone = {
                    'level': milestone_level,
                    'levels_away': milestone_level - level,
                    **GamificationEngine.MILESTONES[milestone_level]
                }
                break
        
        return {
            'level': level,
            'title': rank['title'],
            'icon': rank['icon'],
            'color': rank['color'],
            'tier': rank['tier'],
            'next_milestone': next_milestone
        }
    
    # ===== XP EARNING =====
    @staticmethod
    def calculate_task_xp(task_data, streak_length=0, is_challenge_day=False, time_of_completion=None):
        """
        Calculate XP earned for completing a task
        Considers: complexity, cognitive load, streak, time bonuses, challenge completion
        """
        base_xp = task_data.get('complexity', 3) * 10
        
        # Cognitive load multiplier
        cognitive_load = task_data.get('cognitive_load', 'active_work')
        load_mult = GamificationEngine.MULTIPLIERS['cognitive_load'].get(cognitive_load, 1.0)
        
        # Complexity multiplier
        complexity = task_data.get('complexity', 3)
        complexity_mult = GamificationEngine.MULTIPLIERS['complexity'].get(complexity, 1.0)
        
        # Time bonus (every 30 min adds to base)
        time_estimate = task_data.get('time_estimate', 30)
        time_bonus = (time_estimate // 30) * 5
        
        # Calculate base with multipliers
        xp = (base_xp + time_bonus) * load_mult * complexity_mult
        
        # Streak multiplier
        streak_mult = 1.0
        for streak_threshold in sorted(GamificationEngine.MULTIPLIERS['streak'].keys(), reverse=True):
            if streak_length >= streak_threshold:
                streak_mult = GamificationEngine.MULTIPLIERS['streak'][streak_threshold]
                break
        xp *= streak_mult
        
        # Time of day bonuses
        if time_of_completion:
            hour = time_of_completion.hour
            if hour < 7:
                xp *= GamificationEngine.MULTIPLIERS['early_bird']
            elif hour >= 22:
                xp *= GamificationEngine.MULTIPLIERS['night_owl']
        
        # Challenge day bonus
        if is_challenge_day:
            xp *= GamificationEngine.MULTIPLIERS['challenge_complete']
        
        return int(xp)
    
    @staticmethod
    def get_streak_multiplier(streak_length):
        """Get current streak multiplier"""
        multiplier = 1.0
        for streak_threshold in sorted(GamificationEngine.MULTIPLIERS['streak'].keys(), reverse=True):
            if streak_length >= streak_threshold:
                multiplier = GamificationEngine.MULTIPLIERS['streak'][streak_threshold]
                break
        
        # Find next streak milestone
        next_milestone = None
        for threshold in sorted(GamificationEngine.MULTIPLIERS['streak'].keys()):
            if threshold > streak_length:
                next_milestone = {
                    'days_needed': threshold,
                    'days_away': threshold - streak_length,
                    'multiplier': GamificationEngine.MULTIPLIERS['streak'][threshold]
                }
                break
        
        return {
            'current_streak': streak_length,
            'multiplier': multiplier,
            'bonus_percentage': int((multiplier - 1) * 100),
            'next_milestone': next_milestone
        }
    
    # ===== USER STATS =====
    @staticmethod
    def get_user_stats():
        """Get comprehensive gamification stats for user"""
        db = get_db()
        cursor = db.cursor()
        
        # Calculate total XP from all completed tasks
        cursor.execute('''
            SELECT 
                dt.scheduled_date,
                dt.completed_at,
                t.complexity,
                t.cognitive_load,
                t.time_estimate
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.status = 'completed'
        ''')
        
        completed_tasks = cursor.fetchall()
        
        # Calculate total XP with historical context
        total_xp = 0
        xp_by_source = {
            'tasks': 0,
            'deep_work_bonus': 0,
            'complexity_bonus': 0,
            'streak_bonus': 0,
            'time_bonus': 0
        }
        
        # Get current streak for multiplier
        current_streak = GamificationEngine._calculate_current_streak()
        
        for task in completed_tasks:
            task_dict = dict(task)
            base_xp = task_dict['complexity'] * 10
            
            # Calculate various bonuses
            load_mult = GamificationEngine.MULTIPLIERS['cognitive_load'].get(task_dict['cognitive_load'], 1.0)
            complexity_mult = GamificationEngine.MULTIPLIERS['complexity'].get(task_dict['complexity'], 1.0)
            time_bonus = (task_dict['time_estimate'] // 30) * 5
            
            task_xp = (base_xp + time_bonus) * load_mult * complexity_mult
            
            xp_by_source['tasks'] += base_xp
            xp_by_source['time_bonus'] += time_bonus
            if task_dict['cognitive_load'] == 'deep_work':
                xp_by_source['deep_work_bonus'] += int(base_xp * (load_mult - 1))
            if task_dict['complexity'] >= 4:
                xp_by_source['complexity_bonus'] += int(base_xp * (complexity_mult - 1))
            
            total_xp += int(task_xp)
        
        # Get level and progress info
        progress = GamificationEngine.get_xp_progress(total_xp)
        rank_info = GamificationEngine.get_rank_info(progress['level'])
        streak_info = GamificationEngine.get_streak_multiplier(current_streak)
        
        # Get achievements count (count distinct achievement_ids to avoid duplicates)
        cursor.execute('''
            SELECT COUNT(DISTINCT achievement_id) as count
            FROM achievements
            WHERE unlocked_at IS NOT NULL AND achievement_id IS NOT NULL
        ''')
        achievements_unlocked = cursor.fetchone()['count']
        
        # Total tasks completed
        total_completed = len(completed_tasks)
        
        # Get longest streak
        longest_streak = GamificationEngine._calculate_longest_streak()
        
        # Get today's XP
        today = date.today().isoformat()
        cursor.execute('''
            SELECT 
                t.complexity,
                t.cognitive_load,
                t.time_estimate
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.status = 'completed' AND dt.scheduled_date = ?
        ''', (today,))
        
        today_xp = 0
        for task in cursor.fetchall():
            task_dict = dict(task)
            base = task_dict['complexity'] * 10
            load_mult = GamificationEngine.MULTIPLIERS['cognitive_load'].get(task_dict['cognitive_load'], 1.0)
            complexity_mult = GamificationEngine.MULTIPLIERS['complexity'].get(task_dict['complexity'], 1.0)
            time_bonus = (task_dict['time_estimate'] // 30) * 5
            today_xp += int((base + time_bonus) * load_mult * complexity_mult)
        
        return {
            # Core stats
            'total_xp': total_xp,
            'level': progress['level'],
            'current_xp': progress['current_xp'],
            'xp_needed': progress['xp_needed'],
            'xp_percentage': progress['percentage'],
            'is_max_level': progress['is_max_level'],
            
            # Rank info
            'rank': rank_info['title'],
            'rank_icon': rank_info['icon'],
            'rank_color': rank_info['color'],
            'tier': rank_info['tier'],
            'next_milestone': rank_info['next_milestone'],
            
            # Streak info
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'streak_multiplier': streak_info['multiplier'],
            'streak_bonus_percentage': streak_info['bonus_percentage'],
            'next_streak_milestone': streak_info['next_milestone'],
            
            # XP breakdown
            'xp_breakdown': xp_by_source,
            'today_xp': today_xp,
            
            # Activity stats
            'total_completed': total_completed,
            'achievements_unlocked': achievements_unlocked,
            'total_achievements': get_total_achievements_count()
        }
    
    @staticmethod
    def _calculate_current_streak():
        """Calculate current streak"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT DISTINCT scheduled_date
            FROM daily_tasks
            WHERE status = 'completed'
            ORDER BY scheduled_date DESC
        ''')
        
        completed_dates = [row['scheduled_date'] for row in cursor.fetchall()]
        
        if not completed_dates:
            return 0
        
        streak = 0
        check_date = date.today()
        
        if check_date.isoformat() not in completed_dates and streak == 0:
            check_date = check_date - timedelta(days=1)
        
        while check_date.isoformat() in completed_dates:
            streak += 1
            check_date = check_date - timedelta(days=1)
        
        return streak
    
    @staticmethod
    def _calculate_longest_streak():
        """Calculate longest streak ever achieved"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT scheduled_date
            FROM daily_tasks
            WHERE status = 'completed'
            GROUP BY scheduled_date
            ORDER BY scheduled_date
        ''')
        
        dates_with_completions = [row['scheduled_date'] for row in cursor.fetchall()]
        
        if not dates_with_completions:
            return 0
        
        longest_streak = 0
        temp_streak = 0
        prev_date = None
        
        for date_str in dates_with_completions:
            current_date = datetime.fromisoformat(date_str).date()
            
            if prev_date is None or (current_date - prev_date).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
            
            prev_date = current_date
        
        return longest_streak
    
    @staticmethod
    def get_level_up_rewards(new_level):
        """Get rewards for reaching a new level"""
        rewards = {
            'level': new_level,
            'rank': GamificationEngine.get_rank_info(new_level),
            'milestone_reward': None,
            'xp_to_next': GamificationEngine.calculate_xp_for_level(new_level + 1) - GamificationEngine.calculate_xp_for_level(new_level)
        }
        
        if new_level in GamificationEngine.MILESTONES:
            rewards['milestone_reward'] = GamificationEngine.MILESTONES[new_level]
        
        return rewards
    
    @staticmethod
    def get_xp_leaderboard_position(total_xp):
        """Calculate theoretical percentile position (for future multi-user)"""
        # Estimate based on XP distribution curve
        if total_xp < 500:
            return {'percentile': 'Top 100%', 'tier': 'bronze'}
        elif total_xp < 2000:
            return {'percentile': 'Top 75%', 'tier': 'silver'}
        elif total_xp < 5000:
            return {'percentile': 'Top 50%', 'tier': 'gold'}
        elif total_xp < 15000:
            return {'percentile': 'Top 25%', 'tier': 'platinum'}
        elif total_xp < 50000:
            return {'percentile': 'Top 10%', 'tier': 'diamond'}
        else:
            return {'percentile': 'Top 1%', 'tier': 'legendary'}
    
    @staticmethod
    def get_daily_xp_goal(level):
        """Get recommended daily XP goal based on level"""
        # Scale goal with level
        base_goal = 50
        level_bonus = level * 5
        return base_goal + level_bonus
    
    @staticmethod
    def get_weekly_xp_goal(level):
        """Get recommended weekly XP goal based on level"""
        return GamificationEngine.get_daily_xp_goal(level) * 5  # 5 active days

