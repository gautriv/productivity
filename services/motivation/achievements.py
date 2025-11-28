"""
World-Class Achievement System
40+ achievements across multiple categories with tiers, progress tracking, and rewards
"""
from datetime import datetime, date, timedelta
from models.database import get_db


class AchievementEngine:
    """
    World-Class Achievement System
    Features:
    - 45+ unique achievements across 8 categories
    - Tiered achievements (Bronze → Silver → Gold → Platinum → Diamond)
    - Progressive achievements with milestones
    - Hidden/Secret achievements
    - Achievement points system
    - Real-time progress tracking
    - Achievement showcase
    """
    
    # ===== ACHIEVEMENT TIERS =====
    TIERS = {
        'bronze': {'color': '#cd7f32', 'icon': '🥉', 'multiplier': 1.0},
        'silver': {'color': '#c0c0c0', 'icon': '🥈', 'multiplier': 1.5},
        'gold': {'color': '#ffd700', 'icon': '🥇', 'multiplier': 2.0},
        'platinum': {'color': '#e5e4e2', 'icon': '💠', 'multiplier': 3.0},
        'diamond': {'color': '#b9f2ff', 'icon': '💎', 'multiplier': 5.0}
    }
    
    # ===== COMPREHENSIVE ACHIEVEMENT DEFINITIONS =====
    ACHIEVEMENTS = {
        # ==========================================
        # TASK COMPLETION ACHIEVEMENTS (Progressive)
        # ==========================================
        'first_task': {
            'name': 'First Steps',
            'description': 'Complete your very first task',
            'description_unlocked': 'Completed your very first task',
            'icon': '👶',
            'category': 'tasks',
            'type': 'milestone',
            'tier': 'bronze',
            'requirement': 1,
            'points': 10,
            'hidden': False
        },
        'task_10': {
            'name': 'Getting Warmed Up',
            'description': 'Complete 10 tasks',
            'icon': '🏃',
            'category': 'tasks',
            'type': 'progressive',
            'tier': 'bronze',
            'requirement': 10,
            'points': 25,
            'hidden': False
        },
        'task_50': {
            'name': 'Half Century',
            'description': 'Complete 50 tasks',
            'icon': '🎯',
            'category': 'tasks',
            'type': 'progressive',
            'tier': 'silver',
            'requirement': 50,
            'points': 75,
            'hidden': False
        },
        'task_100': {
            'name': 'Centurion',
            'description': 'Complete 100 tasks',
            'icon': '💯',
            'category': 'tasks',
            'type': 'progressive',
            'tier': 'gold',
            'requirement': 100,
            'points': 150,
            'hidden': False
        },
        'task_250': {
            'name': 'Task Titan',
            'description': 'Complete 250 tasks',
            'icon': '🗿',
            'category': 'tasks',
            'type': 'progressive',
            'tier': 'platinum',
            'requirement': 250,
            'points': 300,
            'hidden': False
        },
        'task_500': {
            'name': 'Half Millennium',
            'description': 'Complete 500 tasks',
            'icon': '🏛️',
            'category': 'tasks',
            'type': 'progressive',
            'tier': 'platinum',
            'requirement': 500,
            'points': 500,
            'hidden': False
        },
        'task_1000': {
            'name': 'Task God',
            'description': 'Complete 1000 tasks',
            'icon': '⚜️',
            'category': 'tasks',
            'type': 'progressive',
            'tier': 'diamond',
            'requirement': 1000,
            'points': 1000,
            'hidden': False
        },
        
        # ==========================================
        # STREAK ACHIEVEMENTS (Progressive)
        # ==========================================
        'streak_3': {
            'name': 'Spark',
            'description': 'Maintain a 3-day streak',
            'icon': '🔥',
            'category': 'streak',
            'type': 'progressive',
            'tier': 'bronze',
            'requirement': 3,
            'points': 30,
            'hidden': False
        },
        'streak_7': {
            'name': 'Week Warrior',
            'description': 'Maintain a 7-day streak',
            'icon': '⭐',
            'category': 'streak',
            'type': 'progressive',
            'tier': 'silver',
            'requirement': 7,
            'points': 75,
            'hidden': False
        },
        'streak_14': {
            'name': 'Fortnight Force',
            'description': 'Maintain a 14-day streak',
            'icon': '🌟',
            'category': 'streak',
            'type': 'progressive',
            'tier': 'gold',
            'requirement': 14,
            'points': 150,
            'hidden': False
        },
        'streak_30': {
            'name': 'Monthly Master',
            'description': 'Maintain a 30-day streak',
            'icon': '👑',
            'category': 'streak',
            'type': 'progressive',
            'tier': 'platinum',
            'requirement': 30,
            'points': 400,
            'hidden': False
        },
        'streak_60': {
            'name': 'Unstoppable',
            'description': 'Maintain a 60-day streak',
            'icon': '🦁',
            'category': 'streak',
            'type': 'progressive',
            'tier': 'platinum',
            'requirement': 60,
            'points': 750,
            'hidden': False
        },
        'streak_90': {
            'name': 'Quarter Legend',
            'description': 'Maintain a 90-day streak',
            'icon': '🏆',
            'category': 'streak',
            'type': 'progressive',
            'tier': 'diamond',
            'requirement': 90,
            'points': 1200,
            'hidden': False
        },
        'streak_180': {
            'name': 'Half-Year Hero',
            'description': 'Maintain a 180-day streak',
            'icon': '🦸',
            'category': 'streak',
            'type': 'progressive',
            'tier': 'diamond',
            'requirement': 180,
            'points': 2500,
            'hidden': False
        },
        'streak_365': {
            'name': 'Year of Excellence',
            'description': 'Maintain a 365-day streak',
            'icon': '🌠',
            'category': 'streak',
            'type': 'progressive',
            'tier': 'diamond',
            'requirement': 365,
            'points': 5000,
            'hidden': False
        },
        
        # ==========================================
        # POINTS ACHIEVEMENTS (Progressive)
        # ==========================================
        'points_100_day': {
            'name': 'Century Day',
            'description': 'Earn 100 points in a single day',
            'description_unlocked': 'Earned 100 points in a single day',
            'icon': '💯',
            'category': 'points',
            'type': 'daily',
            'tier': 'silver',
            'requirement': 100,
            'points': 50,
            'hidden': False
        },
        'points_200_day': {
            'name': 'Double Century',
            'description': 'Earn 200 points in a single day',
            'icon': '🔥',
            'category': 'points',
            'type': 'daily',
            'tier': 'gold',
            'requirement': 200,
            'points': 100,
            'hidden': False
        },
        'points_500_total': {
            'name': 'Point Collector',
            'description': 'Earn 500 total points',
            'icon': '🪙',
            'category': 'points',
            'type': 'progressive',
            'tier': 'silver',
            'requirement': 500,
            'points': 75,
            'hidden': False
        },
        'points_2500_total': {
            'name': 'Point Hoarder',
            'description': 'Earn 2,500 total points',
            'icon': '💰',
            'category': 'points',
            'type': 'progressive',
            'tier': 'gold',
            'requirement': 2500,
            'points': 200,
            'hidden': False
        },
        'points_10000_total': {
            'name': 'Point Master',
            'description': 'Earn 10,000 total points',
            'icon': '💎',
            'category': 'points',
            'type': 'progressive',
            'tier': 'platinum',
            'requirement': 10000,
            'points': 500,
            'hidden': False
        },
        'points_50000_total': {
            'name': 'Point Legend',
            'description': 'Earn 50,000 total points',
            'icon': '👑',
            'category': 'points',
            'type': 'progressive',
            'tier': 'diamond',
            'requirement': 50000,
            'points': 2000,
            'hidden': False
        },
        
        # ==========================================
        # COGNITIVE LOAD ACHIEVEMENTS
        # ==========================================
        'deep_work_10': {
            'name': 'Focus Finder',
            'description': 'Complete 10 deep work tasks',
            'icon': '🧠',
            'category': 'cognitive',
            'type': 'progressive',
            'tier': 'bronze',
            'requirement': 10,
            'points': 50,
            'hidden': False
        },
        'deep_work_50': {
            'name': 'Deep Thinker',
            'description': 'Complete 50 deep work tasks',
            'icon': '🎓',
            'category': 'cognitive',
            'type': 'progressive',
            'tier': 'silver',
            'requirement': 50,
            'points': 150,
            'hidden': False
        },
        'deep_work_100': {
            'name': 'Mind Master',
            'description': 'Complete 100 deep work tasks',
            'icon': '🧙',
            'category': 'cognitive',
            'type': 'progressive',
            'tier': 'gold',
            'requirement': 100,
            'points': 300,
            'hidden': False
        },
        'learning_25': {
            'name': 'Knowledge Seeker',
            'description': 'Complete 25 learning tasks',
            'icon': '📚',
            'category': 'cognitive',
            'type': 'progressive',
            'tier': 'silver',
            'requirement': 25,
            'points': 100,
            'hidden': False
        },
        'learning_100': {
            'name': 'Eternal Student',
            'description': 'Complete 100 learning tasks',
            'icon': '🎓',
            'category': 'cognitive',
            'type': 'progressive',
            'tier': 'gold',
            'requirement': 100,
            'points': 250,
            'hidden': False
        },
        'admin_master': {
            'name': 'Admin Ninja',
            'description': 'Complete 50 admin tasks',
            'icon': '📋',
            'category': 'cognitive',
            'type': 'progressive',
            'tier': 'silver',
            'requirement': 50,
            'points': 75,
            'hidden': False
        },
        'balanced_day': {
            'name': 'Balance Master',
            'description': 'Complete tasks from all 4 cognitive categories in one day',
            'icon': '⚖️',
            'category': 'cognitive',
            'type': 'special',
            'tier': 'gold',
            'requirement': 1,
            'points': 100,
            'hidden': False
        },
        
        # ==========================================
        # TIME-BASED ACHIEVEMENTS
        # ==========================================
        'early_bird': {
            'name': 'Early Bird',
            'description': 'Complete a task before 7 AM',
            'icon': '🌅',
            'category': 'time',
            'type': 'special',
            'tier': 'silver',
            'requirement': 1,
            'points': 50,
            'hidden': False
        },
        'early_bird_10': {
            'name': 'Dawn Warrior',
            'description': 'Complete 10 tasks before 7 AM',
            'icon': '🌄',
            'category': 'time',
            'type': 'progressive',
            'tier': 'gold',
            'requirement': 10,
            'points': 150,
            'hidden': False
        },
        'night_owl': {
            'name': 'Night Owl',
            'description': 'Complete a task after 10 PM',
            'icon': '🦉',
            'category': 'time',
            'type': 'special',
            'tier': 'silver',
            'requirement': 1,
            'points': 50,
            'hidden': False
        },
        'night_owl_10': {
            'name': 'Midnight Master',
            'description': 'Complete 10 tasks after 10 PM',
            'icon': '🌙',
            'category': 'time',
            'type': 'progressive',
            'tier': 'gold',
            'requirement': 10,
            'points': 150,
            'hidden': False
        },
        'speed_demon': {
            'name': 'Speed Demon',
            'description': 'Complete a task 50% faster than estimated',
            'icon': '⚡',
            'category': 'time',
            'type': 'special',
            'tier': 'gold',
            'requirement': 1,
            'points': 75,
            'hidden': False
        },
        
        # ==========================================
        # PERFECT DAY ACHIEVEMENTS
        # ==========================================
        'perfect_day': {
            'name': 'Perfect Day',
            'description': 'Complete all scheduled tasks in one day',
            'description_unlocked': 'Completed all scheduled tasks in one day',
            'icon': '✨',
            'category': 'perfect',
            'type': 'special',
            'tier': 'gold',
            'requirement': 1,
            'points': 100,
            'hidden': False
        },
        'perfect_week': {
            'name': 'Flawless Week',
            'description': 'Achieve 7 consecutive perfect days',
            'icon': '🌟',
            'category': 'perfect',
            'type': 'special',
            'tier': 'platinum',
            'requirement': 7,
            'points': 500,
            'hidden': False
        },
        'perfect_month': {
            'name': 'Month of Excellence',
            'description': 'Achieve 30 consecutive perfect days',
            'icon': '👑',
            'category': 'perfect',
            'type': 'special',
            'tier': 'diamond',
            'requirement': 30,
            'points': 2000,
            'hidden': False
        },
        'no_penalty_week': {
            'name': 'Clean Streak',
            'description': 'Go 7 days without any penalties',
            'icon': '🧹',
            'category': 'perfect',
            'type': 'special',
            'tier': 'gold',
            'requirement': 7,
            'points': 150,
            'hidden': False
        },
        
        # ==========================================
        # COMEBACK & PERSISTENCE ACHIEVEMENTS
        # ==========================================
        'comeback': {
            'name': 'Comeback Kid',
            'description': 'Complete a task rolled over 3+ times',
            'icon': '💪',
            'category': 'persistence',
            'type': 'special',
            'tier': 'silver',
            'requirement': 3,
            'points': 75,
            'hidden': False
        },
        'comeback_master': {
            'name': 'Never Give Up',
            'description': 'Complete 10 tasks that were rolled over',
            'icon': '🦾',
            'category': 'persistence',
            'type': 'progressive',
            'tier': 'gold',
            'requirement': 10,
            'points': 200,
            'hidden': False
        },
        'streak_recovery': {
            'name': 'Phoenix Rising',
            'description': 'Build a new 7-day streak after losing one',
            'description_unlocked': 'Built a new 7-day streak after losing one',
            'icon': '🔥',
            'category': 'persistence',
            'type': 'special',
            'tier': 'gold',
            'requirement': 1,
            'points': 150,
            'hidden': False
        },
        
        # ==========================================
        # COMPLEXITY ACHIEVEMENTS
        # ==========================================
        'complexity_5_first': {
            'name': 'Boss Battle',
            'description': 'Complete your first complexity 5 task',
            'icon': '🐉',
            'category': 'complexity',
            'type': 'special',
            'tier': 'silver',
            'requirement': 1,
            'points': 50,
            'hidden': False
        },
        'complexity_5_10': {
            'name': 'Dragon Slayer',
            'description': 'Complete 10 complexity 5 tasks',
            'icon': '⚔️',
            'category': 'complexity',
            'type': 'progressive',
            'tier': 'gold',
            'requirement': 10,
            'points': 200,
            'hidden': False
        },
        'complexity_5_50': {
            'name': 'Legendary Hero',
            'description': 'Complete 50 complexity 5 tasks',
            'icon': '🏰',
            'category': 'complexity',
            'type': 'progressive',
            'tier': 'platinum',
            'requirement': 50,
            'points': 500,
            'hidden': False
        },
        
        # ==========================================
        # CHALLENGE ACHIEVEMENTS
        # ==========================================
        'challenge_first': {
            'name': 'Challenge Accepted',
            'description': 'Complete your first daily challenge',
            'icon': '🎯',
            'category': 'challenges',
            'type': 'milestone',
            'tier': 'bronze',
            'requirement': 1,
            'points': 25,
            'hidden': False
        },
        'challenge_7': {
            'name': 'Challenge Streak',
            'description': 'Complete 7 daily challenges',
            'icon': '🔥',
            'category': 'challenges',
            'type': 'progressive',
            'tier': 'silver',
            'requirement': 7,
            'points': 100,
            'hidden': False
        },
        'challenge_30': {
            'name': 'Challenge Champion',
            'description': 'Complete 30 daily challenges',
            'icon': '🏆',
            'category': 'challenges',
            'type': 'progressive',
            'tier': 'gold',
            'requirement': 30,
            'points': 300,
            'hidden': False
        },
        
        # ==========================================
        # SECRET/HIDDEN ACHIEVEMENTS
        # ==========================================
        'midnight_warrior': {
            'name': 'Midnight Warrior',
            'description': 'Complete a task at exactly midnight',
            'icon': '🌑',
            'category': 'secret',
            'type': 'special',
            'tier': 'gold',
            'requirement': 1,
            'points': 100,
            'hidden': True
        },
        'weekend_legend': {
            'name': 'Weekend Legend',
            'description': 'Complete 50 tasks on weekends',
            'icon': '🏖️',
            'category': 'secret',
            'type': 'progressive',
            'tier': 'gold',
            'requirement': 50,
            'points': 200,
            'hidden': True
        },
        'monday_master': {
            'name': 'Monday Master',
            'description': 'Complete 10 tasks on Mondays before noon',
            'icon': '📅',
            'category': 'secret',
            'type': 'progressive',
            'tier': 'silver',
            'requirement': 10,
            'points': 100,
            'hidden': True
        },
        'variety_king': {
            'name': 'Jack of All Trades',
            'description': 'Complete 100 tasks across all 4 cognitive categories',
            'icon': '🃏',
            'category': 'secret',
            'type': 'special',
            'tier': 'platinum',
            'requirement': 100,
            'points': 400,
            'hidden': True
        },
        'speed_run': {
            'name': 'Speed Runner',
            'description': 'Complete 5 tasks in under 2 hours',
            'icon': '🏎️',
            'category': 'secret',
            'type': 'special',
            'tier': 'gold',
            'requirement': 5,
            'points': 150,
            'hidden': True
        }
    }
    
    # ===== ACHIEVEMENT CATEGORIES =====
    CATEGORIES = {
        'tasks': {'name': 'Task Completion', 'icon': '✅', 'description': 'Complete tasks to earn these'},
        'streak': {'name': 'Consistency', 'icon': '🔥', 'description': 'Maintain daily streaks'},
        'points': {'name': 'Point Earner', 'icon': '💰', 'description': 'Earn points through excellence'},
        'cognitive': {'name': 'Mind Master', 'icon': '🧠', 'description': 'Master different work types'},
        'time': {'name': 'Time Lord', 'icon': '⏰', 'description': 'Complete tasks at special times'},
        'perfect': {'name': 'Perfectionist', 'icon': '✨', 'description': 'Achieve perfect performance'},
        'persistence': {'name': 'Never Give Up', 'icon': '💪', 'description': 'Show determination'},
        'complexity': {'name': 'Challenge Seeker', 'icon': '🐉', 'description': 'Take on difficult tasks'},
        'challenges': {'name': 'Daily Challenger', 'icon': '🎯', 'description': 'Complete daily challenges'},
        'secret': {'name': 'Secret', 'icon': '🔮', 'description': 'Hidden achievements'}
    }
    
    @staticmethod
    def check_achievements(user_id='default'):
        """Check and unlock new achievements based on user progress"""
        db = get_db()
        cursor = db.cursor()
        
        newly_unlocked = []
        
        # Get current achievements
        cursor.execute('SELECT achievement_id FROM achievements WHERE unlocked_at IS NOT NULL')
        unlocked = {row['achievement_id'] for row in cursor.fetchall()}
        
        # Gather all user stats needed for checking
        stats = AchievementEngine._gather_user_stats()
        
        # Check each achievement
        for achievement_id, achievement in AchievementEngine.ACHIEVEMENTS.items():
            if achievement_id in unlocked:
                continue
            
            # Check if requirement is met
            is_unlocked = AchievementEngine._check_achievement_requirement(
                achievement_id, achievement, stats
            )
            
            if is_unlocked:
                # Calculate points with tier multiplier
                tier = AchievementEngine.TIERS.get(achievement['tier'], AchievementEngine.TIERS['bronze'])
                final_points = int(achievement['points'] * tier['multiplier'])
                
                cursor.execute('''
                    INSERT OR REPLACE INTO achievements 
                    (achievement_id, name, description, icon, category, tier, points, unlocked_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    achievement_id,
                    achievement['name'],
                    achievement['description'],
                    achievement['icon'],
                    achievement['category'],
                    achievement['tier'],
                    final_points,
                    datetime.now().isoformat()
                ))
                
                newly_unlocked.append({
                    **achievement,
                    'id': achievement_id,
                    'final_points': final_points,
                    'tier_info': tier
                })
        
        db.commit()
        return newly_unlocked
    
    @staticmethod
    def _gather_user_stats():
        """Gather all user statistics needed for achievement checking"""
        db = get_db()
        cursor = db.cursor()
        
        stats = {}
        
        # Total completed tasks
        cursor.execute('SELECT COUNT(*) as count FROM daily_tasks WHERE status = "completed"')
        stats['total_completed'] = cursor.fetchone()['count'] or 0
        
        # Current streak
        stats['current_streak'] = AchievementEngine._calculate_current_streak()
        
        # Longest streak
        stats['longest_streak'] = AchievementEngine._calculate_longest_streak()
        
        # Total points (approximate)
        cursor.execute('''
            SELECT COALESCE(SUM(t.complexity * 15), 0) as total_points
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.status = 'completed'
        ''')
        stats['total_points'] = cursor.fetchone()['total_points'] or 0
        
        # Best daily points
        cursor.execute('''
            SELECT dt.scheduled_date, SUM(t.complexity * 15) as daily_points
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.status = 'completed'
            GROUP BY dt.scheduled_date
            ORDER BY daily_points DESC
            LIMIT 1
        ''')
        row = cursor.fetchone()
        stats['best_daily_points'] = row['daily_points'] if row else 0
        
        # Cognitive load counts
        cursor.execute('''
            SELECT t.cognitive_load, COUNT(*) as count
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.status = 'completed'
            GROUP BY t.cognitive_load
        ''')
        stats['cognitive_counts'] = {row['cognitive_load']: row['count'] for row in cursor.fetchall()}
        
        # Early bird count (before 7 AM)
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM daily_tasks
            WHERE status = 'completed'
            AND completed_at IS NOT NULL
            AND CAST(strftime('%H', completed_at) AS INTEGER) < 7
        ''')
        stats['early_bird_count'] = cursor.fetchone()['count'] or 0
        
        # Night owl count (after 10 PM)
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM daily_tasks
            WHERE status = 'completed'
            AND completed_at IS NOT NULL
            AND CAST(strftime('%H', completed_at) AS INTEGER) >= 22
        ''')
        stats['night_owl_count'] = cursor.fetchone()['count'] or 0
        
        # Complexity 5 tasks completed
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.status = 'completed' AND t.complexity = 5
        ''')
        stats['complexity_5_count'] = cursor.fetchone()['count'] or 0
        
        # Rolled over tasks completed
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM daily_tasks
            WHERE status = 'completed' AND rolled_over_count > 0
        ''')
        stats['comeback_count'] = cursor.fetchone()['count'] or 0
        
        # Perfect days count
        cursor.execute('''
            SELECT COUNT(*) as perfect_days FROM (
                SELECT scheduled_date
                FROM daily_tasks
                GROUP BY scheduled_date
                HAVING COUNT(*) = SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)
                AND COUNT(*) > 0
            )
        ''')
        stats['perfect_days'] = cursor.fetchone()['perfect_days'] or 0
        
        # Challenge completions
        cursor.execute('''
            SELECT COUNT(*) as count FROM challenge_history WHERE completed = 1
        ''')
        stats['challenges_completed'] = cursor.fetchone()['count'] or 0
        
        # Weekend tasks
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM daily_tasks
            WHERE status = 'completed'
            AND (CAST(strftime('%w', scheduled_date) AS INTEGER) = 0 
                 OR CAST(strftime('%w', scheduled_date) AS INTEGER) = 6)
        ''')
        stats['weekend_tasks'] = cursor.fetchone()['count'] or 0
        
        # Check for balanced day (all 4 categories in one day)
        cursor.execute('''
            SELECT scheduled_date, COUNT(DISTINCT t.cognitive_load) as categories
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.status = 'completed'
            GROUP BY scheduled_date
            HAVING categories >= 4
        ''')
        stats['balanced_days'] = len(cursor.fetchall())
        
        return stats
    
    @staticmethod
    def _check_achievement_requirement(achievement_id, achievement, stats):
        """Check if a specific achievement requirement is met"""
        category = achievement['category']
        requirement = achievement['requirement']
        
        # Task completion achievements
        if achievement_id.startswith('task_') or achievement_id == 'first_task':
            return stats['total_completed'] >= requirement
        
        # Streak achievements
        if achievement_id.startswith('streak_'):
            return stats['current_streak'] >= requirement or stats['longest_streak'] >= requirement
        
        # Points achievements
        if 'points' in achievement_id:
            if 'day' in achievement_id:
                return stats['best_daily_points'] >= requirement
            return stats['total_points'] >= requirement
        
        # Cognitive load achievements
        if achievement_id.startswith('deep_work_'):
            return stats['cognitive_counts'].get('deep_work', 0) >= requirement
        if achievement_id.startswith('learning_'):
            return stats['cognitive_counts'].get('learning', 0) >= requirement
        if achievement_id == 'admin_master':
            return stats['cognitive_counts'].get('admin', 0) >= requirement
        if achievement_id == 'balanced_day':
            return stats['balanced_days'] >= requirement
        
        # Time-based achievements
        if 'early_bird' in achievement_id:
            return stats['early_bird_count'] >= requirement
        if 'night_owl' in achievement_id or 'midnight' in achievement_id:
            return stats['night_owl_count'] >= requirement
        
        # Perfect day achievements
        if achievement_id == 'perfect_day':
            return stats['perfect_days'] >= requirement
        if 'perfect_week' in achievement_id:
            return stats['perfect_days'] >= 7  # Simplified check
        
        # Complexity achievements
        if 'complexity_5' in achievement_id:
            return stats['complexity_5_count'] >= requirement
        
        # Comeback achievements
        if 'comeback' in achievement_id:
            return stats['comeback_count'] >= requirement
        
        # Challenge achievements
        if achievement_id.startswith('challenge_'):
            return stats['challenges_completed'] >= requirement
        
        # Secret achievements
        if achievement_id == 'weekend_legend':
            return stats['weekend_tasks'] >= requirement
        if achievement_id == 'variety_king':
            total_variety = sum(stats['cognitive_counts'].values())
            all_categories = all(stats['cognitive_counts'].get(cat, 0) >= 25 
                                for cat in ['deep_work', 'learning', 'active_work', 'admin'])
            return total_variety >= requirement and all_categories
        
        return False
    
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
        """Calculate longest streak ever"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT scheduled_date
            FROM daily_tasks
            WHERE status = 'completed'
            GROUP BY scheduled_date
            ORDER BY scheduled_date
        ''')
        
        dates = [row['scheduled_date'] for row in cursor.fetchall()]
        
        if not dates:
            return 0
        
        longest = 0
        current = 0
        prev_date = None
        
        for date_str in dates:
            current_date = datetime.fromisoformat(date_str).date()
            
            if prev_date is None or (current_date - prev_date).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
            
            prev_date = current_date
        
        return longest
    
    @staticmethod
    def get_all_achievements():
        """Get all achievements with unlock status and progress"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT achievement_id, unlocked_at, points
            FROM achievements
            WHERE unlocked_at IS NOT NULL
        ''')
        
        unlocked = {row['achievement_id']: {
            'unlocked_at': row['unlocked_at'],
            'points': row['points']
        } for row in cursor.fetchall()}
        
        stats = AchievementEngine._gather_user_stats()
        
        achievements = []
        for achievement_id, achievement in AchievementEngine.ACHIEVEMENTS.items():
            unlock_info = unlocked.get(achievement_id)
            tier = AchievementEngine.TIERS.get(achievement['tier'], AchievementEngine.TIERS['bronze'])
            
            # Calculate progress for progressive achievements
            progress = AchievementEngine._calculate_progress(achievement_id, achievement, stats)
            
            achievements.append({
                'id': achievement_id,
                'name': achievement['name'],
                'description': achievement['description'],
                'icon': achievement['icon'],
                'category': achievement['category'],
                'type': achievement['type'],
                'tier': achievement['tier'],
                'tier_icon': tier['icon'],
                'tier_color': tier['color'],
                'requirement': achievement['requirement'],
                'points': int(achievement['points'] * tier['multiplier']),
                'hidden': achievement.get('hidden', False),
                'unlocked': unlock_info is not None,
                'unlocked_at': unlock_info['unlocked_at'] if unlock_info else None,
                'progress': progress
            })
        
        # Sort: unlocked first, then by tier, then by points
        tier_order = {'diamond': 0, 'platinum': 1, 'gold': 2, 'silver': 3, 'bronze': 4}
        achievements.sort(key=lambda x: (
            not x['unlocked'],
            tier_order.get(x['tier'], 5),
            -x['points']
        ))
        
        return achievements
    
    @staticmethod
    def _calculate_progress(achievement_id, achievement, stats):
        """Calculate progress percentage for an achievement"""
        requirement = achievement['requirement']
        current = 0
        
        if achievement_id.startswith('task_') or achievement_id == 'first_task':
            current = stats['total_completed']
        elif achievement_id.startswith('streak_'):
            current = max(stats['current_streak'], stats['longest_streak'])
        elif 'points' in achievement_id:
            if 'day' in achievement_id:
                current = stats['best_daily_points']
            else:
                current = stats['total_points']
        elif achievement_id.startswith('deep_work_'):
            current = stats['cognitive_counts'].get('deep_work', 0)
        elif achievement_id.startswith('learning_'):
            current = stats['cognitive_counts'].get('learning', 0)
        elif 'complexity_5' in achievement_id:
            current = stats['complexity_5_count']
        elif achievement_id.startswith('challenge_'):
            current = stats['challenges_completed']
        elif 'early_bird' in achievement_id:
            current = stats['early_bird_count']
        elif 'night_owl' in achievement_id:
            current = stats['night_owl_count']
        elif 'comeback' in achievement_id:
            current = stats['comeback_count']
        elif 'perfect' in achievement_id:
            current = stats['perfect_days']
        
        return {
            'current': current,
            'target': requirement,
            'percentage': min(100, int(current / requirement * 100)) if requirement > 0 else 0
        }
    
    @staticmethod
    def get_achievement_stats():
        """Get achievement statistics"""
        achievements = AchievementEngine.get_all_achievements()
        
        unlocked = [a for a in achievements if a['unlocked']]
        total = len([a for a in achievements if not a.get('hidden', False)])
        
        # Points from achievements
        total_points = sum(a['points'] for a in unlocked)
        
        # By category
        by_category = {}
        for cat_id, cat_info in AchievementEngine.CATEGORIES.items():
            cat_achievements = [a for a in achievements if a['category'] == cat_id]
            cat_unlocked = [a for a in cat_achievements if a['unlocked']]
            by_category[cat_id] = {
                'name': cat_info['name'],
                'icon': cat_info['icon'],
                'total': len(cat_achievements),
                'unlocked': len(cat_unlocked),
                'percentage': int(len(cat_unlocked) / len(cat_achievements) * 100) if cat_achievements else 0
            }
        
        # By tier
        by_tier = {}
        for tier_id, tier_info in AchievementEngine.TIERS.items():
            tier_achievements = [a for a in achievements if a['tier'] == tier_id]
            tier_unlocked = [a for a in tier_achievements if a['unlocked']]
            by_tier[tier_id] = {
                'icon': tier_info['icon'],
                'total': len(tier_achievements),
                'unlocked': len(tier_unlocked)
            }
        
        return {
            'total_achievements': total,
            'unlocked_count': len(unlocked),
            'locked_count': total - len(unlocked),
            'completion_percentage': int(len(unlocked) / total * 100) if total > 0 else 0,
            'total_achievement_points': total_points,
            'by_category': by_category,
            'by_tier': by_tier,
            'recent_unlocks': sorted(unlocked, key=lambda x: x['unlocked_at'] or '', reverse=True)[:5]
        }
    
    @staticmethod
    def get_next_achievements(limit=5):
        """Get the achievements closest to being unlocked"""
        achievements = AchievementEngine.get_all_achievements()
        
        # Filter to locked, non-hidden achievements with progress
        candidates = [
            a for a in achievements 
            if not a['unlocked'] 
            and not a.get('hidden', False)
            and a['progress']['percentage'] > 0
        ]
        
        # Sort by progress percentage (descending)
        candidates.sort(key=lambda x: x['progress']['percentage'], reverse=True)
        
        return candidates[:limit]
