"""
Motivation & Gamification Service
World-class motivation system to keep users engaged
"""
from datetime import datetime, date, timedelta
from models.database import get_db
import random

class MotivationEngine:
    """Gamification and motivation system"""
    
    # Achievement definitions
    ACHIEVEMENTS = {
        'first_task': {
            'name': 'Getting Started',
            'description': 'Complete your first task',
            'icon': '🎯',
            'type': 'tasks',
            'requirement': 1,
            'points': 10
        },
        'streak_3': {
            'name': 'Consistency',
            'description': 'Maintain a 3-day streak',
            'icon': '🔥',
            'type': 'streak',
            'requirement': 3,
            'points': 50
        },
        'streak_7': {
            'name': 'Week Warrior',
            'description': 'Maintain a 7-day streak',
            'icon': '⭐',
            'type': 'streak',
            'requirement': 7,
            'points': 150
        },
        'streak_30': {
            'name': 'Unstoppable',
            'description': 'Maintain a 30-day streak',
            'icon': '👑',
            'type': 'streak',
            'requirement': 30,
            'points': 1000
        },
        'points_100': {
            'name': 'Century',
            'description': 'Earn 100 points in one day',
            'icon': '💯',
            'type': 'points',
            'requirement': 100,
            'points': 100
        },
        'points_500': {
            'name': 'Point Master',
            'description': 'Earn 500 total points',
            'icon': '💎',
            'type': 'points',
            'requirement': 500,
            'points': 250
        },
        'deep_work_10': {
            'name': 'Deep Thinker',
            'description': 'Complete 10 deep work tasks',
            'icon': '🧠',
            'type': 'special',
            'requirement': 10,
            'points': 200
        },
        'perfect_day': {
            'name': 'Perfect Day',
            'description': 'Complete all tasks in one day',
            'icon': '✨',
            'type': 'special',
            'requirement': 1,
            'points': 150
        },
        'early_bird': {
            'name': 'Early Bird',
            'description': 'Complete a task before 7 AM',
            'icon': '🌅',
            'type': 'special',
            'requirement': 1,
            'points': 75
        },
        'night_owl': {
            'name': 'Night Owl',
            'description': 'Complete a task after 10 PM',
            'icon': '🦉',
            'type': 'special',
            'requirement': 1,
            'points': 75
        },
        'comeback': {
            'name': 'Comeback Kid',
            'description': 'Complete a task rolled over 3+ times',
            'icon': '💪',
            'type': 'special',
            'requirement': 1,
            'points': 100
        }
    }
    
    # Motivational quotes by context
    QUOTES = {
        'morning': [
            "Today is a fresh start. Make it count! ☀️",
            "The early bird catches the worm. Let's go! 🚀",
            "Your future self will thank you for what you do today. 💪",
            "Small steps every day lead to big changes. 🎯",
            "Focus on progress, not perfection. 📈"
        ],
        'struggling': [
            "Every expert was once a beginner. Keep going! 🌱",
            "Difficult roads often lead to beautiful destinations. 🗺️",
            "You're stronger than you think. One task at a time. 💎",
            "Progress is progress, no matter how small. 🐢",
            "The comeback is always stronger than the setback. ⚡"
        ],
        'winning': [
            "You're on fire! Keep this momentum going! 🔥",
            "Unstoppable! Look at you crushing those goals! 🎯",
            "This is what peak performance looks like! ⭐",
            "You're in the zone! Ride this wave! 🌊",
            "Excellence is a habit, and you're building it! 👑"
        ],
        'evening': [
            "Finish strong! Tomorrow you starts tonight. 🌙",
            "One more task before you rest. You've got this! ✨",
            "End the day with a win. Your future self will thank you. 🙏",
            "Make tonight count. Small wins add up! 📊",
            "Close the day with purpose. You're doing great! 💫"
        ]
    }
    
    @staticmethod
    def check_achievements(user_id='default'):
        """Check and unlock new achievements based on user progress"""
        db = get_db()
        cursor = db.cursor()
        
        newly_unlocked = []
        
        # Get current achievements
        cursor.execute('SELECT name FROM achievements WHERE unlocked_at IS NOT NULL')
        unlocked = {row['name'] for row in cursor.fetchall()}
        
        # Check each achievement
        for achievement_id, achievement in MotivationEngine.ACHIEVEMENTS.items():
            if achievement['name'] in unlocked:
                continue
            
            unlocked_achievement = False
            
            if achievement['type'] == 'tasks':
                # Check total completed tasks
                cursor.execute('''
                    SELECT COUNT(*) as count
                    FROM daily_tasks
                    WHERE status = 'completed'
                ''')
                count = cursor.fetchone()['count']
                if count >= achievement['requirement']:
                    unlocked_achievement = True
            
            elif achievement['type'] == 'streak':
                # Check current streak
                streak = MotivationEngine.calculate_current_streak()
                if streak >= achievement['requirement']:
                    unlocked_achievement = True
            
            elif achievement['type'] == 'points':
                if 'day' in achievement['description']:
                    # Daily points
                    cursor.execute('''
                        SELECT dt.scheduled_date, 
                               SUM(t.complexity * 10) as points
                        FROM daily_tasks dt
                        JOIN tasks t ON dt.task_id = t.id
                        WHERE dt.status = 'completed'
                        GROUP BY dt.scheduled_date
                        HAVING points >= ?
                    ''', (achievement['requirement'],))
                    if cursor.fetchone():
                        unlocked_achievement = True
                else:
                    # Total points
                    cursor.execute('''
                        SELECT SUM(t.complexity * 10) as total_points
                        FROM daily_tasks dt
                        JOIN tasks t ON dt.task_id = t.id
                        WHERE dt.status = 'completed'
                    ''')
                    total = cursor.fetchone()['total_points'] or 0
                    if total >= achievement['requirement']:
                        unlocked_achievement = True
            
            elif achievement['type'] == 'special':
                # Special achievements
                if achievement_id == 'perfect_day':
                    cursor.execute('''
                        SELECT scheduled_date,
                               COUNT(*) as total,
                               SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                        FROM daily_tasks
                        GROUP BY scheduled_date
                        HAVING total = completed AND total > 0
                    ''')
                    if cursor.fetchone():
                        unlocked_achievement = True
                
                elif achievement_id == 'deep_work_10':
                    cursor.execute('''
                        SELECT COUNT(*) as count
                        FROM daily_tasks dt
                        JOIN tasks t ON dt.task_id = t.id
                        WHERE t.cognitive_load = 'deep_work'
                        AND dt.status = 'completed'
                    ''')
                    count = cursor.fetchone()['count']
                    if count >= 10:
                        unlocked_achievement = True
                
                elif achievement_id == 'early_bird':
                    cursor.execute('''
                        SELECT COUNT(*) as count
                        FROM daily_tasks
                        WHERE status = 'completed'
                        AND completed_at IS NOT NULL
                        AND CAST(strftime('%H', completed_at) AS INTEGER) < 7
                    ''')
                    if cursor.fetchone()['count'] > 0:
                        unlocked_achievement = True
                
                elif achievement_id == 'night_owl':
                    cursor.execute('''
                        SELECT COUNT(*) as count
                        FROM daily_tasks
                        WHERE status = 'completed'
                        AND completed_at IS NOT NULL
                        AND CAST(strftime('%H', completed_at) AS INTEGER) >= 22
                    ''')
                    if cursor.fetchone()['count'] > 0:
                        unlocked_achievement = True
                
                elif achievement_id == 'comeback':
                    cursor.execute('''
                        SELECT COUNT(*) as count
                        FROM daily_tasks
                        WHERE status = 'completed'
                        AND rolled_over_count >= 3
                    ''')
                    if cursor.fetchone()['count'] > 0:
                        unlocked_achievement = True
            
            if unlocked_achievement:
                cursor.execute('''
                    INSERT INTO achievements (name, description, icon, type, requirement, unlocked_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (achievement['name'], achievement['description'], achievement['icon'],
                      achievement['type'], achievement['requirement'], datetime.now().isoformat()))
                
                newly_unlocked.append(achievement)
        
        db.commit()
        return newly_unlocked
    
    @staticmethod
    def calculate_current_streak():
        """Calculate current active streak"""
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
        
        # Allow today to count even if no tasks completed yet
        if check_date.isoformat() not in completed_dates and streak == 0:
            check_date = check_date - timedelta(days=1)
        
        while check_date.isoformat() in completed_dates:
            streak += 1
            check_date = check_date - timedelta(days=1)
        
        return streak
    
    @staticmethod
    def calculate_level_and_xp(total_points):
        """Calculate user level and experience based on points"""
        # Exponential leveling: level = sqrt(points / 50)
        level = int((total_points / 50) ** 0.5) + 1
        
        # XP needed for current level
        points_for_level = ((level - 1) ** 2) * 50
        points_for_next = (level ** 2) * 50
        
        current_xp = total_points - points_for_level
        xp_needed = points_for_next - points_for_level
        
        return {
            'level': level,
            'current_xp': current_xp,
            'xp_needed': xp_needed,
            'xp_percentage': round((current_xp / xp_needed * 100), 1)
        }
    
    @staticmethod
    def get_motivational_message(context='general'):
        """Get context-aware motivational message"""
        db = get_db()
        cursor = db.cursor()
        
        # Determine context if general
        if context == 'general':
            hour = datetime.now().hour
            
            if 5 <= hour < 12:
                context = 'morning'
            elif 18 <= hour < 23:
                context = 'evening'
            else:
                # Check if user is struggling or winning
                today = date.today().isoformat()
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                    FROM daily_tasks
                    WHERE scheduled_date = ?
                ''', (today,))
                
                row = cursor.fetchone()
                if row['total'] > 0:
                    completion_rate = row['completed'] / row['total']
                    context = 'winning' if completion_rate >= 0.7 else 'struggling'
                else:
                    context = 'morning'
        
        quotes = MotivationEngine.QUOTES.get(context, MotivationEngine.QUOTES['morning'])
        return random.choice(quotes)
    
    @staticmethod
    def get_daily_challenge(date_str):
        """Generate a personalized daily challenge"""
        db = get_db()
        cursor = db.cursor()
        
        # Analyze recent performance
        end_date = datetime.fromisoformat(date_str)
        start_date = end_date - timedelta(days=7)
        
        cursor.execute('''
            SELECT 
                t.cognitive_load,
                COUNT(*) as total,
                SUM(CASE WHEN dt.status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.scheduled_date BETWEEN ? AND ?
            GROUP BY t.cognitive_load
        ''', (start_date.date().isoformat(), end_date.date().isoformat()))
        
        performance = {row['cognitive_load']: {
            'total': row['total'],
            'completed': row['completed'],
            'rate': row['completed'] / row['total'] if row['total'] > 0 else 0
        } for row in cursor.fetchall()}
        
        # Find weakness
        if performance:
            weakest = min(performance.items(), key=lambda x: x[1]['rate'])
            strongest = max(performance.items(), key=lambda x: x[1]['rate'])
            
            challenges = {
                'deep_work': "Complete 2 hours of deep work today 🧠",
                'active_work': "Finish 5 active work tasks today ⚡",
                'admin': "Clear all admin tasks today 📋",
                'learning': "Spend 1 hour learning something new 📚"
            }
            
            return {
                'challenge': challenges.get(weakest[0], "Complete all tasks today 🎯"),
                'type': weakest[0],
                'reason': f"You've been at {int(weakest[1]['rate'] * 100)}% on {weakest[0].replace('_', ' ')} tasks",
                'bonus_points': 50
            }
        
        return {
            'challenge': "Complete your first task today! 🚀",
            'type': 'general',
            'reason': "Let's start building your productivity streak",
            'bonus_points': 25
        }
    
    @staticmethod
    def get_user_stats():
        """Get comprehensive user statistics for dashboard"""
        db = get_db()
        cursor = db.cursor()
        
        # Total points
        cursor.execute('''
            SELECT SUM(t.complexity * 10) as total_points
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.status = 'completed'
        ''')
        total_points = cursor.fetchone()['total_points'] or 0
        
        # Level and XP
        level_info = MotivationEngine.calculate_level_and_xp(total_points)
        
        # Streak
        current_streak = MotivationEngine.calculate_current_streak()
        
        # Get longest streak
        cursor.execute('''
            SELECT scheduled_date
            FROM daily_tasks
            WHERE status = 'completed'
            GROUP BY scheduled_date
            ORDER BY scheduled_date
        ''')
        
        dates_with_completions = [row['scheduled_date'] for row in cursor.fetchall()]
        
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
        
        # Achievements count
        cursor.execute('SELECT COUNT(*) as count FROM achievements WHERE unlocked_at IS NOT NULL')
        achievements_unlocked = cursor.fetchone()['count']
        
        # Total tasks completed
        cursor.execute('SELECT COUNT(*) as count FROM daily_tasks WHERE status = "completed"')
        total_completed = cursor.fetchone()['count']
        
        return {
            'total_points': total_points,
            'level': level_info['level'],
            'current_xp': level_info['current_xp'],
            'xp_needed': level_info['xp_needed'],
            'xp_percentage': level_info['xp_percentage'],
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'achievements_unlocked': achievements_unlocked,
            'total_achievements': len(MotivationEngine.ACHIEVEMENTS),
            'total_completed': total_completed
        }

