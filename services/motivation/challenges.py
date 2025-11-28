"""
Daily Challenge Engine
World-class challenge system with 45+ unique challenges
Smart selection algorithm with anti-repetition
"""
from datetime import datetime, date, timedelta
from models.database import get_db
import random
import json


class DailyChallengeEngine:
    """
    World-class Daily Challenge System
    45+ unique challenges with smart selection and anti-repetition
    """
    
    # Difficulty levels with bonus point ranges
    DIFFICULTY = {
        'easy': {'min_bonus': 25, 'max_bonus': 40, 'color': 'green'},
        'medium': {'min_bonus': 45, 'max_bonus': 70, 'color': 'blue'},
        'hard': {'min_bonus': 75, 'max_bonus': 100, 'color': 'purple'},
        'epic': {'min_bonus': 110, 'max_bonus': 150, 'color': 'gold'}
    }
    
    # Comprehensive challenge pool - 45+ unique challenges
    CHALLENGES = {
        # ===== COGNITIVE LOAD CHALLENGES (8) =====
        'deep_work_1h': {
            'title': 'Deep Focus Session',
            'description': 'Complete 1 hour of deep work tasks',
            'icon': '🧠',
            'category': 'cognitive',
            'difficulty': 'easy',
            'requirement': {'type': 'cognitive_time', 'load': 'deep_work', 'minutes': 60},
            'tags': ['focus', 'deep_work']
        },
        'deep_work_2h': {
            'title': 'Deep Work Marathon',
            'description': 'Complete 2 hours of deep work tasks',
            'icon': '🧠',
            'category': 'cognitive',
            'difficulty': 'medium',
            'requirement': {'type': 'cognitive_time', 'load': 'deep_work', 'minutes': 120},
            'tags': ['focus', 'deep_work']
        },
        'deep_work_3_tasks': {
            'title': 'Triple Focus',
            'description': 'Complete 3 deep work tasks',
            'icon': '🎯',
            'category': 'cognitive',
            'difficulty': 'hard',
            'requirement': {'type': 'cognitive_count', 'load': 'deep_work', 'count': 3},
            'tags': ['focus', 'deep_work']
        },
        'admin_blitz': {
            'title': 'Admin Blitz',
            'description': 'Clear all your admin tasks today',
            'icon': '📋',
            'category': 'cognitive',
            'difficulty': 'medium',
            'requirement': {'type': 'clear_category', 'load': 'admin'},
            'tags': ['admin', 'cleanup']
        },
        'learning_hour': {
            'title': 'Knowledge Seeker',
            'description': 'Spend 1 hour on learning tasks',
            'icon': '📚',
            'category': 'cognitive',
            'difficulty': 'easy',
            'requirement': {'type': 'cognitive_time', 'load': 'learning', 'minutes': 60},
            'tags': ['learning', 'growth']
        },
        'active_work_5': {
            'title': 'Action Hero',
            'description': 'Complete 5 active work tasks',
            'icon': '⚡',
            'category': 'cognitive',
            'difficulty': 'medium',
            'requirement': {'type': 'cognitive_count', 'load': 'active_work', 'count': 5},
            'tags': ['active_work', 'productivity']
        },
        'balance_master': {
            'title': 'Balance Master',
            'description': 'Complete tasks from all 4 cognitive categories',
            'icon': '⚖️',
            'category': 'cognitive',
            'difficulty': 'hard',
            'requirement': {'type': 'all_categories'},
            'tags': ['balance', 'variety']
        },
        'cognitive_diversity': {
            'title': 'Mind Mixer',
            'description': 'Complete tasks from at least 3 different categories',
            'icon': '🎨',
            'category': 'cognitive',
            'difficulty': 'medium',
            'requirement': {'type': 'category_count', 'count': 3},
            'tags': ['balance', 'variety']
        },
        
        # ===== QUANTITY CHALLENGES (8) =====
        'three_tasks': {
            'title': 'Triple Threat',
            'description': 'Complete 3 tasks today',
            'icon': '3️⃣',
            'category': 'quantity',
            'difficulty': 'easy',
            'requirement': {'type': 'task_count', 'count': 3},
            'tags': ['quantity', 'beginner']
        },
        'five_tasks': {
            'title': 'High Five',
            'description': 'Complete 5 tasks today',
            'icon': '🖐️',
            'category': 'quantity',
            'difficulty': 'medium',
            'requirement': {'type': 'task_count', 'count': 5},
            'tags': ['quantity', 'productive']
        },
        'seven_tasks': {
            'title': 'Lucky Seven',
            'description': 'Complete 7 tasks today',
            'icon': '🍀',
            'category': 'quantity',
            'difficulty': 'hard',
            'requirement': {'type': 'task_count', 'count': 7},
            'tags': ['quantity', 'ambitious']
        },
        'ten_tasks': {
            'title': 'Perfect Ten',
            'description': 'Complete 10 tasks in one day',
            'icon': '🔟',
            'category': 'quantity',
            'difficulty': 'epic',
            'requirement': {'type': 'task_count', 'count': 10},
            'tags': ['quantity', 'epic']
        },
        'first_task_quick': {
            'title': 'Quick Start',
            'description': 'Complete your first task within 30 minutes of starting',
            'icon': '🚀',
            'category': 'quantity',
            'difficulty': 'easy',
            'requirement': {'type': 'first_task_quick', 'minutes': 30},
            'tags': ['speed', 'momentum']
        },
        'double_yesterday': {
            'title': 'Double Up',
            'description': 'Complete more tasks than yesterday',
            'icon': '📈',
            'category': 'quantity',
            'difficulty': 'medium',
            'requirement': {'type': 'beat_yesterday'},
            'tags': ['improvement', 'growth']
        },
        'task_sprint': {
            'title': 'Task Sprint',
            'description': 'Complete 3 tasks in 2 hours',
            'icon': '🏃',
            'category': 'quantity',
            'difficulty': 'hard',
            'requirement': {'type': 'sprint', 'tasks': 3, 'hours': 2},
            'tags': ['speed', 'focus']
        },
        'minimum_viable': {
            'title': 'Minimum Viable Day',
            'description': 'Complete at least 1 task (perfect for tough days)',
            'icon': '✅',
            'category': 'quantity',
            'difficulty': 'easy',
            'requirement': {'type': 'task_count', 'count': 1},
            'tags': ['easy', 'recovery']
        },
        
        # ===== POINTS CHALLENGES (6) =====
        'earn_50_points': {
            'title': 'Half Century',
            'description': 'Earn 50 points today',
            'icon': '🪙',
            'category': 'points',
            'difficulty': 'easy',
            'requirement': {'type': 'daily_points', 'points': 50},
            'tags': ['points', 'beginner']
        },
        'earn_100_points': {
            'title': 'Century Club',
            'description': 'Earn 100 points today',
            'icon': '💯',
            'category': 'points',
            'difficulty': 'medium',
            'requirement': {'type': 'daily_points', 'points': 100},
            'tags': ['points', 'ambitious']
        },
        'earn_150_points': {
            'title': 'Point Crusher',
            'description': 'Earn 150 points today',
            'icon': '💎',
            'category': 'points',
            'difficulty': 'hard',
            'requirement': {'type': 'daily_points', 'points': 150},
            'tags': ['points', 'hard']
        },
        'earn_200_points': {
            'title': 'Point Legend',
            'description': 'Earn 200 points in a single day',
            'icon': '👑',
            'category': 'points',
            'difficulty': 'epic',
            'requirement': {'type': 'daily_points', 'points': 200},
            'tags': ['points', 'epic']
        },
        'no_penalties': {
            'title': 'Clean Slate',
            'description': 'Complete all tasks with zero penalties',
            'icon': '✨',
            'category': 'points',
            'difficulty': 'medium',
            'requirement': {'type': 'zero_penalties'},
            'tags': ['quality', 'focus']
        },
        'positive_net': {
            'title': 'Positive Vibes',
            'description': 'End the day with positive net points',
            'icon': '📊',
            'category': 'points',
            'difficulty': 'easy',
            'requirement': {'type': 'positive_net'},
            'tags': ['points', 'balance']
        },
        
        # ===== TIME-BASED CHALLENGES (7) =====
        'early_bird': {
            'title': 'Early Bird',
            'description': 'Complete a task before 9 AM',
            'icon': '🌅',
            'category': 'time',
            'difficulty': 'medium',
            'requirement': {'type': 'complete_before_hour', 'hour': 9},
            'tags': ['morning', 'early']
        },
        'super_early_bird': {
            'title': 'Dawn Warrior',
            'description': 'Complete a task before 7 AM',
            'icon': '🌄',
            'category': 'time',
            'difficulty': 'hard',
            'requirement': {'type': 'complete_before_hour', 'hour': 7},
            'tags': ['morning', 'extreme']
        },
        'finish_by_noon': {
            'title': 'Morning Crusher',
            'description': 'Complete 3 tasks before noon',
            'icon': '☀️',
            'category': 'time',
            'difficulty': 'medium',
            'requirement': {'type': 'tasks_before_hour', 'hour': 12, 'count': 3},
            'tags': ['morning', 'productive']
        },
        'finish_by_5pm': {
            'title': 'Work-Life Balance',
            'description': 'Complete all tasks before 5 PM',
            'icon': '🏠',
            'category': 'time',
            'difficulty': 'hard',
            'requirement': {'type': 'all_before_hour', 'hour': 17},
            'tags': ['balance', 'efficiency']
        },
        'night_owl': {
            'title': 'Night Owl',
            'description': 'Complete a task after 9 PM',
            'icon': '🦉',
            'category': 'time',
            'difficulty': 'easy',
            'requirement': {'type': 'complete_after_hour', 'hour': 21},
            'tags': ['evening', 'night']
        },
        'time_boxer': {
            'title': 'Time Boxer',
            'description': 'Complete a task within its estimated time',
            'icon': '⏱️',
            'category': 'time',
            'difficulty': 'medium',
            'requirement': {'type': 'within_estimate'},
            'tags': ['efficiency', 'planning']
        },
        'speed_demon': {
            'title': 'Speed Demon',
            'description': 'Complete a task 25% faster than estimated',
            'icon': '⚡',
            'category': 'time',
            'difficulty': 'hard',
            'requirement': {'type': 'beat_estimate', 'percentage': 25},
            'tags': ['speed', 'efficiency']
        },
        
        # ===== STREAK & CONSISTENCY CHALLENGES (5) =====
        'keep_streak': {
            'title': 'Streak Guardian',
            'description': 'Complete at least 1 task to maintain your streak',
            'icon': '🔥',
            'category': 'streak',
            'difficulty': 'easy',
            'requirement': {'type': 'maintain_streak'},
            'tags': ['streak', 'consistency']
        },
        'streak_builder': {
            'title': 'Streak Builder',
            'description': 'Extend your streak by completing 2+ tasks',
            'icon': '🔥',
            'category': 'streak',
            'difficulty': 'medium',
            'requirement': {'type': 'extend_streak', 'min_tasks': 2},
            'tags': ['streak', 'growth']
        },
        'weekend_warrior': {
            'title': 'Weekend Warrior',
            'description': 'Complete 3 tasks on the weekend',
            'icon': '🏆',
            'category': 'streak',
            'difficulty': 'medium',
            'requirement': {'type': 'weekend_tasks', 'count': 3},
            'tags': ['weekend', 'dedication']
        },
        'monday_momentum': {
            'title': 'Monday Momentum',
            'description': 'Start the week strong with 4+ completed tasks',
            'icon': '💪',
            'category': 'streak',
            'difficulty': 'medium',
            'requirement': {'type': 'monday_tasks', 'count': 4},
            'tags': ['monday', 'start']
        },
        'friday_finish': {
            'title': 'Friday Finisher',
            'description': 'Clear your task list before the weekend',
            'icon': '🎉',
            'category': 'streak',
            'difficulty': 'hard',
            'requirement': {'type': 'friday_clear'},
            'tags': ['friday', 'completion']
        },
        
        # ===== COMPLEXITY CHALLENGES (5) =====
        'complexity_5': {
            'title': 'Boss Battle',
            'description': 'Complete a complexity 5 task',
            'icon': '🐉',
            'category': 'complexity',
            'difficulty': 'hard',
            'requirement': {'type': 'complexity_task', 'complexity': 5},
            'tags': ['hard', 'challenge']
        },
        'complexity_average_4': {
            'title': 'Challenge Seeker',
            'description': 'Complete 3 tasks with complexity 4 or higher',
            'icon': '🎮',
            'category': 'complexity',
            'difficulty': 'epic',
            'requirement': {'type': 'high_complexity_count', 'min_complexity': 4, 'count': 3},
            'tags': ['hard', 'ambitious']
        },
        'easy_wins': {
            'title': 'Easy Wins',
            'description': 'Complete 5 complexity 1-2 tasks (momentum builder)',
            'icon': '🎯',
            'category': 'complexity',
            'difficulty': 'easy',
            'requirement': {'type': 'low_complexity_count', 'max_complexity': 2, 'count': 5},
            'tags': ['easy', 'momentum']
        },
        'complexity_variety': {
            'title': 'Complexity Explorer',
            'description': 'Complete tasks of 3 different complexity levels',
            'icon': '🌈',
            'category': 'complexity',
            'difficulty': 'medium',
            'requirement': {'type': 'complexity_variety', 'count': 3},
            'tags': ['variety', 'balance']
        },
        'no_easy_mode': {
            'title': 'No Easy Mode',
            'description': 'Complete only tasks with complexity 3+',
            'icon': '💎',
            'category': 'complexity',
            'difficulty': 'hard',
            'requirement': {'type': 'min_complexity_day', 'min_complexity': 3},
            'tags': ['hard', 'focus']
        },
        
        # ===== SPECIAL & COMEBACK CHALLENGES (6) =====
        'perfect_day': {
            'title': 'Perfect Day',
            'description': 'Complete 100% of your scheduled tasks',
            'icon': '🌟',
            'category': 'special',
            'difficulty': 'hard',
            'requirement': {'type': 'perfect_completion'},
            'tags': ['perfect', 'completion']
        },
        'comeback_kid': {
            'title': 'Comeback Kid',
            'description': 'Clear a task that was rolled over',
            'icon': '💪',
            'category': 'special',
            'difficulty': 'medium',
            'requirement': {'type': 'clear_rollover'},
            'tags': ['comeback', 'persistence']
        },
        'rollover_slayer': {
            'title': 'Rollover Slayer',
            'description': 'Clear all rolled over tasks',
            'icon': '⚔️',
            'category': 'special',
            'difficulty': 'hard',
            'requirement': {'type': 'clear_all_rollovers'},
            'tags': ['comeback', 'cleanup']
        },
        'fresh_start': {
            'title': 'Fresh Start',
            'description': 'Complete a task after missing yesterday',
            'icon': '🌱',
            'category': 'special',
            'difficulty': 'easy',
            'requirement': {'type': 'break_recovery'},
            'tags': ['recovery', 'restart']
        },
        'overachiever': {
            'title': 'Overachiever',
            'description': 'Complete more than your daily average',
            'icon': '🚀',
            'category': 'special',
            'difficulty': 'medium',
            'requirement': {'type': 'beat_average'},
            'tags': ['growth', 'improvement']
        },
        'zen_master': {
            'title': 'Zen Master',
            'description': 'Complete tasks without any rolled over from previous days',
            'icon': '🧘',
            'category': 'special',
            'difficulty': 'medium',
            'requirement': {'type': 'no_rollovers'},
            'tags': ['clean', 'focus']
        }
    }
    
    @staticmethod
    def get_user_context(date_str):
        """Gather comprehensive user context for smart challenge selection"""
        db = get_db()
        cursor = db.cursor()
        
        target_date = datetime.fromisoformat(date_str).date()
        week_ago = target_date - timedelta(days=7)
        
        context = {
            'day_of_week': target_date.weekday(),
            'is_weekend': target_date.weekday() >= 5,
            'is_monday': target_date.weekday() == 0,
            'is_friday': target_date.weekday() == 4,
            'current_streak': 0,
            'has_streak': False,
            'missed_yesterday': False,
            'avg_daily_tasks': 0,
            'avg_completion_rate': 0,
            'cognitive_performance': {},
            'has_rollovers': False,
            'rollover_count': 0,
            'recent_challenges': [],
            'total_completed_ever': 0,
            'user_level': 1
        }
        
        # Get current streak
        cursor.execute('''
            SELECT DISTINCT scheduled_date
            FROM daily_tasks
            WHERE status = 'completed'
            ORDER BY scheduled_date DESC
        ''')
        completed_dates = [row['scheduled_date'] for row in cursor.fetchall()]
        
        if completed_dates:
            streak = 0
            check_date = target_date - timedelta(days=1)
            while check_date.isoformat() in completed_dates:
                streak += 1
                check_date -= timedelta(days=1)
            context['current_streak'] = streak
            context['has_streak'] = streak > 0
            
            yesterday = (target_date - timedelta(days=1)).isoformat()
            context['missed_yesterday'] = yesterday not in completed_dates
        
        # Get average daily tasks and completion rate
        cursor.execute('''
            SELECT 
                scheduled_date,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM daily_tasks
            WHERE scheduled_date BETWEEN ? AND ?
            GROUP BY scheduled_date
        ''', ((target_date - timedelta(days=14)).isoformat(), (target_date - timedelta(days=1)).isoformat()))
        
        daily_stats = cursor.fetchall()
        if daily_stats:
            total_tasks = sum(row['total'] for row in daily_stats)
            total_completed = sum(row['completed'] for row in daily_stats)
            active_days = len(daily_stats)
            context['avg_daily_tasks'] = round(total_tasks / active_days, 1) if active_days > 0 else 0
            context['avg_completion_rate'] = round(total_completed / total_tasks * 100, 1) if total_tasks > 0 else 0
        
        # Get cognitive load performance
        cursor.execute('''
            SELECT 
                t.cognitive_load,
                COUNT(*) as total,
                SUM(CASE WHEN dt.status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.scheduled_date BETWEEN ? AND ?
            GROUP BY t.cognitive_load
        ''', (week_ago.isoformat(), (target_date - timedelta(days=1)).isoformat()))
        
        for row in cursor.fetchall():
            if row['cognitive_load']:
                context['cognitive_performance'][row['cognitive_load']] = {
                    'total': row['total'],
                    'completed': row['completed'],
                    'rate': round(row['completed'] / row['total'] * 100, 1) if row['total'] > 0 else 0
                }
        
        # Check for rolled over tasks
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM daily_tasks
            WHERE scheduled_date = ? AND rolled_over_count > 0
        ''', (date_str,))
        rollover_result = cursor.fetchone()
        context['rollover_count'] = rollover_result['count'] if rollover_result else 0
        context['has_rollovers'] = context['rollover_count'] > 0
        
        # Get recent challenges
        cursor.execute('''
            SELECT challenge_id
            FROM challenge_history
            WHERE challenge_date >= ?
            ORDER BY challenge_date DESC
        ''', (week_ago.isoformat(),))
        context['recent_challenges'] = [row['challenge_id'] for row in cursor.fetchall()]
        
        # Get total completed ever
        cursor.execute('SELECT COUNT(*) as count FROM daily_tasks WHERE status = "completed"')
        context['total_completed_ever'] = cursor.fetchone()['count'] or 0
        
        # Estimate user level
        if context['total_completed_ever'] < 10:
            context['user_level'] = 1
        elif context['total_completed_ever'] < 50:
            context['user_level'] = 2
        elif context['total_completed_ever'] < 150:
            context['user_level'] = 3
        else:
            context['user_level'] = 4
        
        return context
    
    @staticmethod
    def select_challenge(date_str):
        """Smart challenge selection algorithm"""
        context = DailyChallengeEngine.get_user_context(date_str)
        
        eligible = []
        for challenge_id, challenge in DailyChallengeEngine.CHALLENGES.items():
            if challenge_id in context['recent_challenges'][:5]:
                continue
            
            score = DailyChallengeEngine._calculate_challenge_score(challenge_id, challenge, context)
            if score > 0:
                eligible.append((challenge_id, challenge, score))
        
        if not eligible:
            eligible = [(cid, c, 50) for cid, c in DailyChallengeEngine.CHALLENGES.items()]
        
        eligible.sort(key=lambda x: x[2], reverse=True)
        
        top_candidates = eligible[:5]
        total_score = sum(c[2] for c in top_candidates)
        
        if total_score > 0:
            rand_val = random.uniform(0, total_score)
            cumulative = 0
            for challenge_id, challenge, score in top_candidates:
                cumulative += score
                if rand_val <= cumulative:
                    return challenge_id, challenge
        
        return random.choice(list(DailyChallengeEngine.CHALLENGES.items()))
    
    @staticmethod
    def _calculate_challenge_score(challenge_id, challenge, context):
        """Calculate relevance score for a challenge"""
        score = 50
        
        difficulty = challenge['difficulty']
        category = challenge['category']
        tags = challenge.get('tags', [])
        
        # Difficulty adjustment
        difficulty_scores = {
            1: {'easy': 30, 'medium': 10, 'hard': -20, 'epic': -50},
            2: {'easy': 20, 'medium': 25, 'hard': 5, 'epic': -20},
            3: {'easy': 5, 'medium': 20, 'hard': 25, 'epic': 10},
            4: {'easy': -10, 'medium': 15, 'hard': 30, 'epic': 25}
        }
        score += difficulty_scores.get(context['user_level'], {}).get(difficulty, 0)
        
        # Day of week relevance
        if context['is_weekend'] and 'weekend' in tags:
            score += 40
        if context['is_monday'] and 'monday' in tags:
            score += 40
        if context['is_friday'] and 'friday' in tags:
            score += 40
        if not context['is_weekend'] and 'weekend' in tags:
            score -= 50
        
        # Streak relevance
        if context['has_streak'] and category == 'streak':
            score += 25
        if context['current_streak'] >= 3 and 'keep_streak' in challenge_id:
            score += 30
        
        # Recovery relevance
        if context['missed_yesterday']:
            if 'recovery' in tags or 'easy' in tags:
                score += 35
            if 'streak' in tags:
                score -= 20
        
        # Rollover relevance
        if context['has_rollovers'] and 'comeback' in tags:
            score += 40
        
        # Cognitive load weakness targeting
        if category == 'cognitive' and context['cognitive_performance']:
            requirement = challenge.get('requirement', {})
            target_load = requirement.get('load')
            
            if target_load and target_load in context['cognitive_performance']:
                perf = context['cognitive_performance'][target_load]
                if perf['rate'] < 50:
                    score += 30
                elif perf['rate'] < 70:
                    score += 15
        
        # Completion rate adjustment
        if context['avg_completion_rate'] < 50:
            if difficulty == 'easy':
                score += 25
            elif difficulty == 'epic':
                score -= 30
        elif context['avg_completion_rate'] > 85:
            if difficulty == 'hard' or difficulty == 'epic':
                score += 20
        
        # New user boost
        if context['total_completed_ever'] < 5 and 'beginner' in tags:
            score += 40
        
        return max(0, score)
    
    @staticmethod
    def get_daily_challenge(date_str):
        """Get or generate the daily challenge"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT challenge_id, challenge_data, completed, completed_at
            FROM challenge_history
            WHERE challenge_date = ?
        ''', (date_str,))
        
        existing = cursor.fetchone()
        if existing:
            challenge_id = existing['challenge_id']
            challenge = DailyChallengeEngine.CHALLENGES.get(challenge_id)
            if challenge:
                difficulty = DailyChallengeEngine.DIFFICULTY[challenge['difficulty']]
                bonus = (difficulty['min_bonus'] + difficulty['max_bonus']) // 2
                
                return {
                    'id': challenge_id,
                    'title': challenge['title'],
                    'description': challenge['description'],
                    'icon': challenge['icon'],
                    'category': challenge['category'],
                    'difficulty': challenge['difficulty'],
                    'difficulty_color': difficulty['color'],
                    'bonus_points': bonus,
                    'requirement': challenge.get('requirement', {}),
                    'completed': bool(existing['completed']),
                    'completed_at': existing['completed_at'],
                    'tags': challenge.get('tags', [])
                }
        
        challenge_id, challenge = DailyChallengeEngine.select_challenge(date_str)
        difficulty = DailyChallengeEngine.DIFFICULTY[challenge['difficulty']]
        
        bonus_range = difficulty['max_bonus'] - difficulty['min_bonus']
        bonus = difficulty['min_bonus'] + random.randint(0, bonus_range)
        
        challenge_data = json.dumps({
            'bonus_points': bonus,
            'selected_at': datetime.now().isoformat()
        })
        
        cursor.execute('''
            INSERT OR REPLACE INTO challenge_history 
            (challenge_date, challenge_id, challenge_data, completed, created_at)
            VALUES (?, ?, ?, 0, ?)
        ''', (date_str, challenge_id, challenge_data, datetime.now().isoformat()))
        db.commit()
        
        return {
            'id': challenge_id,
            'title': challenge['title'],
            'description': challenge['description'],
            'icon': challenge['icon'],
            'category': challenge['category'],
            'difficulty': challenge['difficulty'],
            'difficulty_color': difficulty['color'],
            'bonus_points': bonus,
            'requirement': challenge.get('requirement', {}),
            'completed': False,
            'completed_at': None,
            'tags': challenge.get('tags', [])
        }
    
    @staticmethod
    def check_challenge_completion(date_str):
        """Check if today's challenge is completed"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT challenge_id, completed
            FROM challenge_history
            WHERE challenge_date = ?
        ''', (date_str,))
        
        result = cursor.fetchone()
        if not result or result['completed']:
            return {'completed': bool(result and result['completed']), 'just_completed': False}
        
        challenge_id = result['challenge_id']
        challenge = DailyChallengeEngine.CHALLENGES.get(challenge_id)
        if not challenge:
            return {'completed': False, 'just_completed': False}
        
        requirement = challenge.get('requirement', {})
        req_type = requirement.get('type')
        
        completed = False
        
        if req_type == 'task_count':
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM daily_tasks
                WHERE scheduled_date = ? AND status = 'completed'
            ''', (date_str,))
            count = cursor.fetchone()['count']
            completed = count >= requirement.get('count', 1)
        
        elif req_type == 'cognitive_count':
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM daily_tasks dt
                JOIN tasks t ON dt.task_id = t.id
                WHERE dt.scheduled_date = ? 
                AND dt.status = 'completed'
                AND t.cognitive_load = ?
            ''', (date_str, requirement.get('load')))
            count = cursor.fetchone()['count']
            completed = count >= requirement.get('count', 1)
        
        elif req_type == 'cognitive_time':
            cursor.execute('''
                SELECT COALESCE(SUM(t.time_estimate), 0) as total_time
                FROM daily_tasks dt
                JOIN tasks t ON dt.task_id = t.id
                WHERE dt.scheduled_date = ?
                AND dt.status = 'completed'
                AND t.cognitive_load = ?
            ''', (date_str, requirement.get('load')))
            total_time = cursor.fetchone()['total_time'] or 0
            completed = total_time >= requirement.get('minutes', 60)
        
        elif req_type == 'daily_points':
            cursor.execute('''
                SELECT COALESCE(SUM(t.complexity * 10), 0) as points
                FROM daily_tasks dt
                JOIN tasks t ON dt.task_id = t.id
                WHERE dt.scheduled_date = ? AND dt.status = 'completed'
            ''', (date_str,))
            points = cursor.fetchone()['points'] or 0
            completed = points >= requirement.get('points', 50)
        
        elif req_type == 'perfect_completion':
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                FROM daily_tasks
                WHERE scheduled_date = ?
            ''', (date_str,))
            row = cursor.fetchone()
            completed = row['total'] > 0 and row['total'] == row['completed']
        
        elif req_type == 'clear_rollover':
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM daily_tasks
                WHERE scheduled_date = ? 
                AND status = 'completed'
                AND rolled_over_count > 0
            ''', (date_str,))
            completed = cursor.fetchone()['count'] > 0
        
        elif req_type == 'all_categories':
            cursor.execute('''
                SELECT COUNT(DISTINCT t.cognitive_load) as cat_count
                FROM daily_tasks dt
                JOIN tasks t ON dt.task_id = t.id
                WHERE dt.scheduled_date = ? AND dt.status = 'completed'
            ''', (date_str,))
            completed = cursor.fetchone()['cat_count'] >= 4
        
        elif req_type == 'category_count':
            cursor.execute('''
                SELECT COUNT(DISTINCT t.cognitive_load) as cat_count
                FROM daily_tasks dt
                JOIN tasks t ON dt.task_id = t.id
                WHERE dt.scheduled_date = ? AND dt.status = 'completed'
            ''', (date_str,))
            completed = cursor.fetchone()['cat_count'] >= requirement.get('count', 3)
        
        elif req_type == 'maintain_streak':
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM daily_tasks
                WHERE scheduled_date = ? AND status = 'completed'
            ''', (date_str,))
            completed = cursor.fetchone()['count'] >= 1
        
        elif req_type == 'complexity_task':
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM daily_tasks dt
                JOIN tasks t ON dt.task_id = t.id
                WHERE dt.scheduled_date = ?
                AND dt.status = 'completed'
                AND t.complexity >= ?
            ''', (date_str, requirement.get('complexity', 5)))
            completed = cursor.fetchone()['count'] > 0
        
        elif req_type == 'zero_penalties':
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(penalty_points) as penalties
                FROM daily_tasks
                WHERE scheduled_date = ?
            ''', (date_str,))
            row = cursor.fetchone()
            completed = row['total'] > 0 and row['total'] == row['completed'] and (row['penalties'] or 0) == 0
        
        elif req_type == 'positive_net':
            cursor.execute('''
                SELECT 
                    COALESCE(SUM(CASE WHEN dt.status = 'completed' THEN t.complexity * 10 ELSE 0 END), 0) as points,
                    COALESCE(SUM(dt.penalty_points), 0) as penalties
                FROM daily_tasks dt
                JOIN tasks t ON dt.task_id = t.id
                WHERE dt.scheduled_date = ?
            ''', (date_str,))
            row = cursor.fetchone()
            net = (row['points'] or 0) - (row['penalties'] or 0)
            completed = net > 0
        
        if completed:
            cursor.execute('''
                UPDATE challenge_history
                SET completed = 1, completed_at = ?
                WHERE challenge_date = ?
            ''', (datetime.now().isoformat(), date_str))
            db.commit()
            
            return {'completed': True, 'just_completed': True}
        
        return {'completed': False, 'just_completed': False}
    
    @staticmethod
    def get_challenge_stats():
        """Get challenge completion statistics"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed
            FROM challenge_history
        ''')
        
        row = cursor.fetchone()
        total = row['total'] or 0
        completed = row['completed'] or 0
        
        cursor.execute('''
            SELECT challenge_date, completed
            FROM challenge_history
            ORDER BY challenge_date DESC
        ''')
        
        challenge_streak = 0
        for row in cursor.fetchall():
            if row['completed']:
                challenge_streak += 1
            else:
                break
        
        return {
            'total_challenges': total,
            'completed_challenges': completed,
            'completion_rate': round(completed / total * 100, 1) if total > 0 else 0,
            'challenge_streak': challenge_streak
        }

