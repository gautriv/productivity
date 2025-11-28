"""
World-Class Net Points Engine
Sophisticated points system with multipliers, combos, bonuses, and real-time feedback
"""
from datetime import datetime, date, timedelta
from models.database import get_db
import math


class PointsEngine:
    """
    World-Class Points System
    Features:
    - Dynamic point calculation with 10+ factors
    - Combo system for consecutive completions
    - Time-of-day bonuses (early bird, night owl, power hours)
    - Streak multipliers
    - Category mastery bonuses
    - Daily/Weekly goals with rewards
    - Point milestones
    - Real-time feedback and animations
    """
    
    # ===== BASE POINT VALUES =====
    BASE_POINTS = {
        'complexity': {
            1: 10,   # Simple task
            2: 20,   # Easy task
            3: 35,   # Medium task
            4: 55,   # Hard task
            5: 80    # Complex task
        },
        'time_bonus': 5,  # Per 30 minutes
    }
    
    # ===== COGNITIVE LOAD MULTIPLIERS =====
    COGNITIVE_MULTIPLIERS = {
        'deep_work': {
            'multiplier': 2.0,
            'name': 'Deep Work',
            'icon': '🧠',
            'description': 'Intense focus tasks earn double points'
        },
        'learning': {
            'multiplier': 1.5,
            'name': 'Learning',
            'icon': '📚',
            'description': 'Growth activities earn 50% bonus'
        },
        'active_work': {
            'multiplier': 1.2,
            'name': 'Active Work',
            'icon': '⚡',
            'description': 'Standard productive tasks earn 20% bonus'
        },
        'admin': {
            'multiplier': 1.0,
            'name': 'Admin',
            'icon': '📋',
            'description': 'Necessary tasks at base rate'
        }
    }
    
    # ===== TIME-OF-DAY BONUSES =====
    TIME_BONUSES = {
        'early_bird': {
            'hours': (5, 7),
            'multiplier': 1.3,
            'name': 'Early Bird',
            'icon': '🌅',
            'description': 'Complete tasks before 7 AM for +30%'
        },
        'morning_power': {
            'hours': (7, 9),
            'multiplier': 1.15,
            'name': 'Morning Power',
            'icon': '☀️',
            'description': 'Morning momentum: +15%'
        },
        'focus_hours': {
            'hours': (9, 12),
            'multiplier': 1.1,
            'name': 'Focus Hours',
            'icon': '🎯',
            'description': 'Peak productivity hours: +10%'
        },
        'afternoon_push': {
            'hours': (14, 17),
            'multiplier': 1.05,
            'name': 'Afternoon Push',
            'icon': '💪',
            'description': 'Push through the afternoon: +5%'
        },
        'evening_grind': {
            'hours': (19, 22),
            'multiplier': 1.1,
            'name': 'Evening Grind',
            'icon': '🌙',
            'description': 'Evening dedication: +10%'
        },
        'night_owl': {
            'hours': (22, 24),
            'multiplier': 1.25,
            'name': 'Night Owl',
            'icon': '🦉',
            'description': 'Late night warriors: +25%'
        },
        'midnight_legend': {
            'hours': (0, 5),
            'multiplier': 1.4,
            'name': 'Midnight Legend',
            'icon': '🌟',
            'description': 'Legendary dedication: +40%'
        }
    }
    
    # ===== COMBO SYSTEM =====
    # Points multiplier based on consecutive task completions
    COMBO_MULTIPLIERS = {
        2: {'multiplier': 1.1, 'name': 'Double!', 'icon': '2️⃣'},
        3: {'multiplier': 1.2, 'name': 'Triple!', 'icon': '3️⃣'},
        4: {'multiplier': 1.3, 'name': 'Quad!', 'icon': '4️⃣'},
        5: {'multiplier': 1.5, 'name': 'Penta!', 'icon': '5️⃣'},
        6: {'multiplier': 1.6, 'name': 'Hexa!', 'icon': '6️⃣'},
        7: {'multiplier': 1.75, 'name': 'Lucky Seven!', 'icon': '🍀'},
        8: {'multiplier': 1.9, 'name': 'Octuple!', 'icon': '8️⃣'},
        9: {'multiplier': 2.0, 'name': 'Niner!', 'icon': '9️⃣'},
        10: {'multiplier': 2.5, 'name': 'PERFECT 10!', 'icon': '🔟'},
    }
    
    # ===== STREAK POINT BONUSES =====
    STREAK_BONUSES = {
        3: {'bonus': 25, 'name': '3-Day Fire', 'icon': '🔥'},
        7: {'bonus': 75, 'name': 'Week Warrior', 'icon': '⭐'},
        14: {'bonus': 200, 'name': 'Fortnight Force', 'icon': '💪'},
        30: {'bonus': 500, 'name': 'Monthly Master', 'icon': '👑'},
        60: {'bonus': 1200, 'name': 'Bi-Monthly Beast', 'icon': '🦁'},
        90: {'bonus': 2500, 'name': 'Quarter Champion', 'icon': '🏆'},
        180: {'bonus': 6000, 'name': 'Half-Year Hero', 'icon': '🦸'},
        365: {'bonus': 15000, 'name': 'Year Legend', 'icon': '🌟'}
    }
    
    # ===== SPECIAL BONUSES =====
    SPECIAL_BONUSES = {
        'first_of_day': {
            'bonus': 15,
            'name': 'First Blood',
            'icon': '🎯',
            'description': 'First completed task of the day'
        },
        'perfect_day': {
            'multiplier': 1.5,
            'name': 'Perfect Day',
            'icon': '✨',
            'description': 'Complete 100% of scheduled tasks'
        },
        'comeback': {
            'bonus': 25,
            'name': 'Comeback',
            'icon': '💪',
            'description': 'Complete a rolled-over task'
        },
        'complexity_master': {
            'bonus': 50,
            'name': 'Complexity Master',
            'icon': '🐉',
            'description': 'Complete a complexity 5 task'
        },
        'speed_demon': {
            'multiplier': 1.2,
            'name': 'Speed Demon',
            'icon': '⚡',
            'description': 'Complete task faster than estimated'
        },
        'category_sweep': {
            'bonus': 100,
            'name': 'Category Sweep',
            'icon': '🧹',
            'description': 'Complete tasks from all 4 categories in one day'
        },
        'weekend_warrior': {
            'multiplier': 1.15,
            'name': 'Weekend Warrior',
            'icon': '🏋️',
            'description': 'Working on weekends: +15%'
        },
        'monday_momentum': {
            'bonus': 20,
            'name': 'Monday Momentum',
            'icon': '🚀',
            'description': 'First task on Monday'
        },
        'friday_finish': {
            'bonus': 30,
            'name': 'Friday Finisher',
            'icon': '🎉',
            'description': 'Complete all tasks on Friday'
        }
    }
    
    # ===== PENALTY SYSTEM =====
    PENALTIES = {
        'rollover_base': 3,  # Base penalty per rollover
        'rollover_escalation': 1.5,  # Multiplier for each additional rollover
        'abandoned_penalty': 10,  # Penalty for abandoning a task
        'max_penalty_per_task': 25  # Cap on penalties per task
    }
    
    # ===== DAILY GOALS =====
    DAILY_GOALS = {
        'beginner': {'points': 50, 'tasks': 3},
        'intermediate': {'points': 100, 'tasks': 5},
        'advanced': {'points': 200, 'tasks': 8},
        'expert': {'points': 350, 'tasks': 12}
    }
    
    # ===== POINT MILESTONES =====
    MILESTONES = {
        100: {'name': 'Century', 'icon': '💯', 'reward': 25},
        500: {'name': 'Half Grand', 'icon': '🪙', 'reward': 75},
        1000: {'name': 'Grand', 'icon': '💰', 'reward': 150},
        2500: {'name': 'Big Shot', 'icon': '💎', 'reward': 300},
        5000: {'name': 'High Roller', 'icon': '🎰', 'reward': 500},
        10000: {'name': 'Point King', 'icon': '👑', 'reward': 1000},
        25000: {'name': 'Point Emperor', 'icon': '🏛️', 'reward': 2500},
        50000: {'name': 'Point Legend', 'icon': '🌟', 'reward': 5000},
        100000: {'name': 'Point God', 'icon': '⚜️', 'reward': 10000}
    }
    
    @staticmethod
    def calculate_task_points(task_data, context=None):
        """
        Calculate comprehensive points for a completed task
        Returns detailed breakdown of all point sources
        """
        if context is None:
            context = PointsEngine._get_task_context(task_data)
        
        breakdown = {
            'base_points': 0,
            'time_bonus': 0,
            'cognitive_bonus': 0,
            'time_of_day_bonus': 0,
            'combo_bonus': 0,
            'streak_bonus': 0,
            'special_bonuses': [],
            'penalties': 0,
            'multipliers_applied': [],
            'total_points': 0,
            'net_points': 0
        }
        
        complexity = task_data.get('complexity', 3)
        cognitive_load = task_data.get('cognitive_load', 'active_work')
        time_estimate = task_data.get('time_estimate', 30)
        rolled_over_count = task_data.get('rolled_over_count', 0)
        
        # 1. Base points from complexity
        breakdown['base_points'] = PointsEngine.BASE_POINTS['complexity'].get(complexity, 35)
        
        # 2. Time bonus
        breakdown['time_bonus'] = (time_estimate // 30) * PointsEngine.BASE_POINTS['time_bonus']
        
        # Start with base + time bonus
        points = breakdown['base_points'] + breakdown['time_bonus']
        
        # 3. Cognitive load multiplier
        cog_info = PointsEngine.COGNITIVE_MULTIPLIERS.get(cognitive_load, 
                                                         PointsEngine.COGNITIVE_MULTIPLIERS['active_work'])
        cog_multiplier = cog_info['multiplier']
        breakdown['cognitive_bonus'] = int(points * (cog_multiplier - 1))
        breakdown['multipliers_applied'].append({
            'name': cog_info['name'],
            'icon': cog_info['icon'],
            'multiplier': cog_multiplier
        })
        points = int(points * cog_multiplier)
        
        # 4. Time of day bonus
        if context.get('completion_hour') is not None:
            time_bonus_info = PointsEngine._get_time_bonus(context['completion_hour'])
            if time_bonus_info:
                time_mult = time_bonus_info['multiplier']
                breakdown['time_of_day_bonus'] = int(points * (time_mult - 1))
                breakdown['multipliers_applied'].append({
                    'name': time_bonus_info['name'],
                    'icon': time_bonus_info['icon'],
                    'multiplier': time_mult
                })
                points = int(points * time_mult)
        
        # 5. Combo bonus
        if context.get('combo_count', 0) >= 2:
            combo_info = PointsEngine._get_combo_info(context['combo_count'])
            if combo_info:
                combo_mult = combo_info['multiplier']
                breakdown['combo_bonus'] = int(points * (combo_mult - 1))
                breakdown['multipliers_applied'].append({
                    'name': combo_info['name'],
                    'icon': combo_info['icon'],
                    'multiplier': combo_mult
                })
                points = int(points * combo_mult)
        
        # 6. Special bonuses
        # First task of day
        if context.get('is_first_of_day'):
            bonus = PointsEngine.SPECIAL_BONUSES['first_of_day']
            points += bonus['bonus']
            breakdown['special_bonuses'].append({
                'name': bonus['name'],
                'icon': bonus['icon'],
                'points': bonus['bonus']
            })
        
        # Complexity master
        if complexity == 5:
            bonus = PointsEngine.SPECIAL_BONUSES['complexity_master']
            points += bonus['bonus']
            breakdown['special_bonuses'].append({
                'name': bonus['name'],
                'icon': bonus['icon'],
                'points': bonus['bonus']
            })
        
        # Comeback bonus
        if rolled_over_count > 0:
            bonus = PointsEngine.SPECIAL_BONUSES['comeback']
            points += bonus['bonus']
            breakdown['special_bonuses'].append({
                'name': bonus['name'],
                'icon': bonus['icon'],
                'points': bonus['bonus']
            })
        
        # Weekend warrior
        if context.get('is_weekend'):
            bonus = PointsEngine.SPECIAL_BONUSES['weekend_warrior']
            extra = int(points * (bonus['multiplier'] - 1))
            points += extra
            breakdown['special_bonuses'].append({
                'name': bonus['name'],
                'icon': bonus['icon'],
                'points': extra
            })
        
        # Speed demon (completed faster than estimate)
        if context.get('actual_time') and context['actual_time'] < time_estimate * 0.8:
            bonus = PointsEngine.SPECIAL_BONUSES['speed_demon']
            extra = int(points * (bonus['multiplier'] - 1))
            points += extra
            breakdown['special_bonuses'].append({
                'name': bonus['name'],
                'icon': bonus['icon'],
                'points': extra
            })
        
        breakdown['total_points'] = points
        
        # 7. Calculate penalties (for incomplete tasks)
        if task_data.get('status') != 'completed':
            penalty = PointsEngine._calculate_penalty(rolled_over_count)
            breakdown['penalties'] = penalty
            breakdown['net_points'] = -penalty
        else:
            breakdown['net_points'] = points
        
        return breakdown
    
    @staticmethod
    def _get_task_context(task_data):
        """Get context for point calculation"""
        db = get_db()
        cursor = db.cursor()
        
        today = date.today().isoformat()
        now = datetime.now()
        
        context = {
            'completion_hour': now.hour,
            'is_weekend': now.weekday() >= 5,
            'is_monday': now.weekday() == 0,
            'is_friday': now.weekday() == 4,
            'is_first_of_day': False,
            'combo_count': 0,
            'actual_time': task_data.get('actual_time')
        }
        
        # Check if first task of day
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM daily_tasks
            WHERE scheduled_date = ? AND status = 'completed'
        ''', (today,))
        completed_today = cursor.fetchone()['count']
        context['is_first_of_day'] = completed_today == 0
        
        # Get combo count (consecutive completions today)
        # This is simplified - in production would track actual sequence
        context['combo_count'] = completed_today + 1
        
        return context
    
    @staticmethod
    def _get_time_bonus(hour):
        """Get time-of-day bonus based on hour"""
        for key, bonus in PointsEngine.TIME_BONUSES.items():
            start, end = bonus['hours']
            if start <= hour < end:
                return bonus
            # Handle midnight crossing
            if start > end and (hour >= start or hour < end):
                return bonus
        return None
    
    @staticmethod
    def _get_combo_info(combo_count):
        """Get combo multiplier info"""
        # Find highest applicable combo
        for count in sorted(PointsEngine.COMBO_MULTIPLIERS.keys(), reverse=True):
            if combo_count >= count:
                return PointsEngine.COMBO_MULTIPLIERS[count]
        return None
    
    @staticmethod
    def _calculate_penalty(rolled_over_count):
        """Calculate penalty for rolled over tasks"""
        if rolled_over_count <= 0:
            return 0
        
        base = PointsEngine.PENALTIES['rollover_base']
        escalation = PointsEngine.PENALTIES['rollover_escalation']
        
        # Escalating penalty: 3, 4.5, 6.75, etc.
        penalty = 0
        for i in range(rolled_over_count):
            penalty += base * (escalation ** i)
        
        return min(int(penalty), PointsEngine.PENALTIES['max_penalty_per_task'])
    
    @staticmethod
    def get_daily_stats(date_str):
        """Get comprehensive daily point statistics"""
        db = get_db()
        cursor = db.cursor()
        
        # Get all tasks for the day
        cursor.execute('''
            SELECT 
                dt.id,
                dt.status,
                dt.rolled_over_count,
                dt.actual_time,
                dt.penalty_points,
                t.complexity,
                t.cognitive_load,
                t.time_estimate
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.scheduled_date = ?
        ''', (date_str,))
        
        tasks = cursor.fetchall()
        
        stats = {
            'date': date_str,
            'total_tasks': len(tasks),
            'completed_tasks': 0,
            'pending_tasks': 0,
            'points_earned': 0,
            'penalties': 0,
            'net_points': 0,
            'bonuses_earned': [],
            'combo_max': 0,
            'cognitive_breakdown': {
                'deep_work': {'tasks': 0, 'points': 0},
                'learning': {'tasks': 0, 'points': 0},
                'active_work': {'tasks': 0, 'points': 0},
                'admin': {'tasks': 0, 'points': 0}
            },
            'time_bonuses_earned': [],
            'daily_goal': None,
            'goal_progress': 0
        }
        
        for task in tasks:
            task_dict = dict(task)
            
            if task_dict['status'] == 'completed':
                stats['completed_tasks'] += 1
                
                # Calculate points for this task
                breakdown = PointsEngine.calculate_task_points(task_dict, {
                    'completion_hour': datetime.now().hour,
                    'is_weekend': datetime.now().weekday() >= 5,
                    'is_first_of_day': stats['completed_tasks'] == 1,
                    'combo_count': stats['completed_tasks'],
                    'actual_time': task_dict.get('actual_time')
                })
                
                stats['points_earned'] += breakdown['total_points']
                
                # Track cognitive breakdown
                cog_load = task_dict['cognitive_load'] or 'active_work'
                if cog_load in stats['cognitive_breakdown']:
                    stats['cognitive_breakdown'][cog_load]['tasks'] += 1
                    stats['cognitive_breakdown'][cog_load]['points'] += breakdown['total_points']
                
                # Track max combo
                stats['combo_max'] = max(stats['combo_max'], stats['completed_tasks'])
                
                # Track bonuses
                stats['bonuses_earned'].extend(breakdown['special_bonuses'])
                
            else:
                stats['pending_tasks'] += 1
                stats['penalties'] += task_dict.get('penalty_points', 0)
        
        stats['net_points'] = stats['points_earned'] - stats['penalties']
        
        # Determine daily goal based on activity level
        if stats['total_tasks'] <= 3:
            goal_tier = 'beginner'
        elif stats['total_tasks'] <= 6:
            goal_tier = 'intermediate'
        elif stats['total_tasks'] <= 10:
            goal_tier = 'advanced'
        else:
            goal_tier = 'expert'
        
        stats['daily_goal'] = PointsEngine.DAILY_GOALS[goal_tier]
        stats['goal_progress'] = min(100, int(stats['net_points'] / stats['daily_goal']['points'] * 100))
        
        return stats
    
    @staticmethod
    def get_weekly_summary():
        """Get weekly point summary"""
        db = get_db()
        cursor = db.cursor()
        
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        cursor.execute('''
            SELECT 
                dt.scheduled_date,
                COUNT(*) as total_tasks,
                SUM(CASE WHEN dt.status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(dt.penalty_points) as penalties
            FROM daily_tasks dt
            WHERE dt.scheduled_date BETWEEN ? AND ?
            GROUP BY dt.scheduled_date
            ORDER BY dt.scheduled_date
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        daily_data = []
        total_points = 0
        total_penalties = 0
        
        for row in cursor.fetchall():
            day_stats = PointsEngine.get_daily_stats(row['scheduled_date'])
            daily_data.append({
                'date': row['scheduled_date'],
                'points': day_stats['points_earned'],
                'penalties': day_stats['penalties'],
                'net': day_stats['net_points'],
                'tasks_completed': row['completed'],
                'total_tasks': row['total_tasks']
            })
            total_points += day_stats['points_earned']
            total_penalties += day_stats['penalties']
        
        return {
            'period': f"{start_date.isoformat()} to {end_date.isoformat()}",
            'total_points': total_points,
            'total_penalties': total_penalties,
            'net_points': total_points - total_penalties,
            'daily_average': int(total_points / 7) if total_points > 0 else 0,
            'best_day': max(daily_data, key=lambda x: x['net'])['date'] if daily_data else None,
            'daily_breakdown': daily_data
        }
    
    @staticmethod
    def get_all_time_stats():
        """Get all-time point statistics"""
        db = get_db()
        cursor = db.cursor()
        
        # Total points earned
        cursor.execute('''
            SELECT 
                COUNT(*) as total_completed,
                SUM(t.complexity) as total_complexity
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.status = 'completed'
        ''')
        
        row = cursor.fetchone()
        
        # Get milestone progress
        total_points = (row['total_complexity'] or 0) * 15  # Rough estimate
        
        next_milestone = None
        for threshold in sorted(PointsEngine.MILESTONES.keys()):
            if total_points < threshold:
                milestone = PointsEngine.MILESTONES[threshold]
                next_milestone = {
                    'target': threshold,
                    'current': total_points,
                    'remaining': threshold - total_points,
                    'progress': int(total_points / threshold * 100),
                    'reward': milestone
                }
                break
        
        return {
            'total_points_earned': total_points,
            'total_tasks_completed': row['total_completed'] or 0,
            'next_milestone': next_milestone,
            'milestones_reached': [
                {'threshold': t, **m} 
                for t, m in PointsEngine.MILESTONES.items() 
                if total_points >= t
            ]
        }
    
    @staticmethod
    def get_points_breakdown():
        """Get detailed breakdown of all point multipliers and bonuses"""
        return {
            'base_points': PointsEngine.BASE_POINTS,
            'cognitive_multipliers': PointsEngine.COGNITIVE_MULTIPLIERS,
            'time_bonuses': PointsEngine.TIME_BONUSES,
            'combo_multipliers': PointsEngine.COMBO_MULTIPLIERS,
            'streak_bonuses': PointsEngine.STREAK_BONUSES,
            'special_bonuses': PointsEngine.SPECIAL_BONUSES,
            'penalties': PointsEngine.PENALTIES,
            'milestones': PointsEngine.MILESTONES
        }

