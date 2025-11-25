"""
Advanced Analytics Service
World-class algorithms for productivity insights
"""
from datetime import datetime, date, timedelta
from app.models.database import get_db, calculate_task_points
import math
from collections import defaultdict

class ProductivityAnalytics:
    """Advanced analytics engine for productivity patterns"""
    
    @staticmethod
    def calculate_productivity_score(date_str, window_days=7):
        """
        Calculate a comprehensive productivity score (0-100)
        Uses multiple factors: completion rate, points, consistency, and difficulty
        """
        db = get_db()
        cursor = db.cursor()
        
        end_date = datetime.fromisoformat(date_str)
        start_date = end_date - timedelta(days=window_days)
        
        cursor.execute('''
            SELECT 
                dt.status,
                dt.penalty_points,
                dt.actual_time,
                t.complexity,
                t.cognitive_load,
                t.time_estimate,
                dt.scheduled_date
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.scheduled_date BETWEEN ? AND ?
        ''', (start_date.date().isoformat(), date_str))
        
        tasks = [dict(row) for row in cursor.fetchall()]
        
        if not tasks:
            return 0
        
        # Factor 1: Completion rate (40%)
        completed = sum(1 for t in tasks if t['status'] == 'completed')
        completion_score = (completed / len(tasks)) * 40
        
        # Factor 2: Points earned vs potential (30%)
        total_points = sum(calculate_task_points(t) for t in tasks if t['status'] == 'completed')
        potential_points = sum(calculate_task_points(t) for t in tasks)
        points_score = (total_points / potential_points * 30) if potential_points > 0 else 0
        
        # Factor 3: Consistency (20%)
        daily_completion = defaultdict(int)
        daily_total = defaultdict(int)
        for t in tasks:
            daily_total[t['scheduled_date']] += 1
            if t['status'] == 'completed':
                daily_completion[t['scheduled_date']] += 1
        
        consistency = sum(1 for d in daily_completion if daily_completion[d] > 0) / len(daily_total)
        consistency_score = consistency * 20
        
        # Factor 4: Penalty avoidance (10%)
        total_penalties = sum(t.get('penalty_points', 0) for t in tasks)
        penalty_score = max(0, 10 - (total_penalties / 10))
        
        total_score = completion_score + points_score + consistency_score + penalty_score
        
        return min(100, round(total_score, 1))
    
    @staticmethod
    def find_optimal_task_time(cognitive_load, historical_days=30):
        """
        Analyze when user completes tasks of a given cognitive load most successfully
        Returns optimal hour ranges
        """
        db = get_db()
        cursor = db.cursor()
        
        end_date = date.today()
        start_date = end_date - timedelta(days=historical_days)
        
        cursor.execute('''
            SELECT 
                dt.completed_at,
                dt.status,
                dt.actual_time,
                t.time_estimate
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE t.cognitive_load = ?
            AND dt.scheduled_date BETWEEN ? AND ?
            AND dt.status = 'completed'
            AND dt.completed_at IS NOT NULL
        ''', (cognitive_load, start_date.isoformat(), end_date.isoformat()))
        
        results = cursor.fetchall()
        
        if not results:
            return None
        
        # Analyze completion times by hour
        hour_performance = defaultdict(lambda: {'count': 0, 'efficiency': []})
        
        for row in results:
            completed_time = datetime.fromisoformat(row['completed_at'])
            hour = completed_time.hour
            
            # Calculate efficiency (estimated vs actual)
            if row['actual_time'] and row['time_estimate']:
                efficiency = row['time_estimate'] / row['actual_time']
                hour_performance[hour]['efficiency'].append(efficiency)
            hour_performance[hour]['count'] += 1
        
        # Find best hours (highest efficiency and frequency)
        hour_scores = {}
        for hour, data in hour_performance.items():
            if data['count'] >= 2:  # Need at least 2 samples
                avg_efficiency = sum(data['efficiency']) / len(data['efficiency']) if data['efficiency'] else 1
                frequency_weight = min(data['count'] / 10, 1)  # Cap at 10 tasks
                hour_scores[hour] = avg_efficiency * frequency_weight
        
        if not hour_scores:
            return None
        
        # Get top 3 hours
        top_hours = sorted(hour_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'optimal_hours': [h[0] for h in top_hours],
            'confidence': min(len(results) / 20, 1.0),  # Higher confidence with more data
            'sample_size': len(results)
        }
    
    @staticmethod
    def predict_task_completion_probability(task_data, date_str):
        """
        Predict probability of task completion based on historical patterns
        Uses naive Bayes-like approach with multiple factors
        """
        db = get_db()
        cursor = db.cursor()
        
        # Get historical data for similar tasks
        cursor.execute('''
            SELECT dt.status, dt.rolled_over_count, dt.scheduled_date
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE t.complexity = ?
            AND t.cognitive_load = ?
            AND dt.scheduled_date < ?
            LIMIT 100
        ''', (task_data.get('complexity', 3), 
              task_data.get('cognitive_load', 'active_work'),
              date_str))
        
        historical = [dict(row) for row in cursor.fetchall()]
        
        if len(historical) < 5:
            return 0.5  # Not enough data, return neutral probability
        
        # Factor 1: Base completion rate for similar tasks
        completed = sum(1 for h in historical if h['status'] == 'completed')
        base_rate = completed / len(historical)
        
        # Factor 2: Day of week effect
        target_date = datetime.fromisoformat(date_str)
        target_dow = target_date.weekday()
        
        dow_completion = [h for h in historical 
                         if datetime.fromisoformat(h['scheduled_date']).weekday() == target_dow]
        if dow_completion:
            dow_rate = sum(1 for h in dow_completion if h['status'] == 'completed') / len(dow_completion)
        else:
            dow_rate = base_rate
        
        # Factor 3: Rollover penalty
        rollover_count = task_data.get('rolled_over_count', 0)
        rollover_penalty = 0.1 * rollover_count  # 10% reduction per rollover
        
        # Combine factors
        probability = (base_rate * 0.5 + dow_rate * 0.5) - rollover_penalty
        
        return max(0.1, min(0.95, probability))
    
    @staticmethod
    def calculate_cognitive_load_balance(date_str):
        """
        Calculate if daily cognitive load is balanced
        Returns recommendations for optimal distribution
        """
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT 
                t.cognitive_load,
                COUNT(*) as task_count,
                SUM(t.time_estimate) as total_time
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.scheduled_date = ?
            AND dt.status != 'abandoned'
            GROUP BY t.cognitive_load
        ''', (date_str,))
        
        load_distribution = {row['cognitive_load']: {
            'count': row['task_count'],
            'time': row['total_time']
        } for row in cursor.fetchall()}
        
        # Optimal distribution (based on cognitive science)
        optimal = {
            'deep_work': 0.25,  # 25% deep work
            'active_work': 0.40,  # 40% active work
            'admin': 0.20,  # 20% admin
            'learning': 0.15  # 15% learning
        }
        
        total_time = sum(d['time'] for d in load_distribution.values())
        
        if total_time == 0:
            return {'balanced': True, 'score': 100, 'recommendations': []}
        
        # Calculate deviation from optimal
        deviations = {}
        for load_type, optimal_pct in optimal.items():
            actual_pct = load_distribution.get(load_type, {'time': 0})['time'] / total_time
            deviations[load_type] = abs(actual_pct - optimal_pct)
        
        # Balance score (0-100)
        avg_deviation = sum(deviations.values()) / len(deviations)
        balance_score = max(0, 100 - (avg_deviation * 200))
        
        # Generate recommendations
        recommendations = []
        for load_type, deviation in deviations.items():
            if deviation > 0.15:
                actual_pct = load_distribution.get(load_type, {'time': 0})['time'] / total_time
                optimal_pct = optimal[load_type]
                
                if actual_pct < optimal_pct:
                    recommendations.append({
                        'type': load_type,
                        'action': 'increase',
                        'message': f'Consider adding more {load_type.replace("_", " ")} tasks'
                    })
                else:
                    recommendations.append({
                        'type': load_type,
                        'action': 'decrease',
                        'message': f'Too many {load_type.replace("_", " ")} tasks - consider moving some to another day'
                    })
        
        return {
            'balanced': balance_score >= 70,
            'score': round(balance_score, 1),
            'distribution': load_distribution,
            'recommendations': recommendations
        }
    
    @staticmethod
    def detect_productivity_patterns(days=30):
        """
        Detect patterns in productivity using time-series analysis
        Returns insights about patterns, trends, and anomalies
        """
        db = get_db()
        cursor = db.cursor()
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                dt.scheduled_date,
                COUNT(*) as total_tasks,
                SUM(CASE WHEN dt.status = 'completed' THEN 1 ELSE 0 END) as completed,
                t.cognitive_load,
                t.complexity
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.scheduled_date BETWEEN ? AND ?
            GROUP BY dt.scheduled_date
            ORDER BY dt.scheduled_date
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        daily_data = defaultdict(lambda: {'total': 0, 'completed': 0})
        for row in cursor.fetchall():
            d = row['scheduled_date']
            daily_data[d]['total'] += 1
            daily_data[d]['completed'] += row['completed']
        
        if len(daily_data) < 7:
            return {'patterns': [], 'trend': 'insufficient_data'}
        
        # Calculate completion rates
        completion_rates = []
        dates = sorted(daily_data.keys())
        
        for d in dates:
            rate = daily_data[d]['completed'] / daily_data[d]['total'] if daily_data[d]['total'] > 0 else 0
            completion_rates.append(rate)
        
        # Detect trend (using simple linear regression)
        n = len(completion_rates)
        x = list(range(n))
        y = completion_rates
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Classify trend
        if slope > 0.01:
            trend = 'improving'
        elif slope < -0.01:
            trend = 'declining'
        else:
            trend = 'stable'
        
        # Detect weekly patterns
        weekly_pattern = defaultdict(list)
        for d in dates:
            dow = datetime.fromisoformat(d).weekday()
            rate = daily_data[d]['completed'] / daily_data[d]['total'] if daily_data[d]['total'] > 0 else 0
            weekly_pattern[dow].append(rate)
        
        avg_by_day = {dow: sum(rates) / len(rates) for dow, rates in weekly_pattern.items() if rates}
        
        best_day = max(avg_by_day.items(), key=lambda x: x[1]) if avg_by_day else None
        worst_day = min(avg_by_day.items(), key=lambda x: x[1]) if avg_by_day else None
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        patterns = []
        if best_day and worst_day and (best_day[1] - worst_day[1]) > 0.2:
            patterns.append({
                'type': 'weekly_variance',
                'best_day': day_names[best_day[0]],
                'worst_day': day_names[worst_day[0]],
                'difference': round((best_day[1] - worst_day[1]) * 100, 1)
            })
        
        # Detect streaks
        current_streak = 0
        for d in reversed(dates):
            if daily_data[d]['completed'] > 0:
                current_streak += 1
            else:
                break
        
        if current_streak >= 3:
            patterns.append({
                'type': 'streak',
                'length': current_streak,
                'status': 'active'
            })
        
        return {
            'trend': trend,
            'trend_strength': abs(slope),
            'patterns': patterns,
            'avg_completion_rate': round(y_mean * 100, 1),
            'weekly_performance': {day_names[dow]: round(rate * 100, 1) 
                                  for dow, rate in avg_by_day.items()}
        }

