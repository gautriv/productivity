"""
World-Class Trends Engine
Advanced trend analysis with predictive forecasting, momentum indicators,
pattern detection, and comparative analytics
"""
from datetime import datetime, date, timedelta
from models.database import get_db, calculate_task_points
from collections import defaultdict
import math


class TrendsEngine:
    """
    World-Class Trends Analysis Engine
    Features:
    - Predictive forecasting (next 7 days)
    - Momentum & velocity indicators
    - Comparative analysis (week-over-week, month-over-month)
    - Trend anomaly detection
    - Moving averages & smoothing
    - Seasonal pattern detection
    - Performance trajectory
    """
    
    # ===== MOMENTUM THRESHOLDS =====
    MOMENTUM = {
        'surging': {'threshold': 0.25, 'icon': '🚀', 'color': '#22c55e', 'message': 'Exceptional momentum!'},
        'accelerating': {'threshold': 0.10, 'icon': '📈', 'color': '#3b82f6', 'message': 'Building momentum'},
        'steady': {'threshold': -0.05, 'icon': '➡️', 'color': '#a855f7', 'message': 'Stable performance'},
        'slowing': {'threshold': -0.15, 'icon': '📉', 'color': '#f59e0b', 'message': 'Momentum decreasing'},
        'declining': {'threshold': -1.0, 'icon': '⚠️', 'color': '#ef4444', 'message': 'Needs attention'}
    }
    
    # ===== PERFORMANCE ZONES =====
    PERFORMANCE_ZONES = {
        'peak': {'min': 90, 'icon': '🏆', 'color': '#ffd700', 'description': 'Peak Performance Zone'},
        'optimal': {'min': 75, 'icon': '⭐', 'color': '#22c55e', 'description': 'Optimal Performance'},
        'productive': {'min': 60, 'icon': '✅', 'color': '#3b82f6', 'description': 'Productive'},
        'developing': {'min': 40, 'icon': '📊', 'color': '#f59e0b', 'description': 'Developing'},
        'building': {'min': 0, 'icon': '🔨', 'color': '#ef4444', 'description': 'Building Foundation'}
    }
    
    @staticmethod
    def get_comprehensive_trends(days=30):
        """
        Get comprehensive trend analysis with all metrics
        """
        db = get_db()
        cursor = db.cursor()
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get raw data
        cursor.execute('''
            SELECT 
                dt.scheduled_date,
                dt.status,
                dt.rolled_over_count,
                dt.penalty_points,
                dt.actual_time,
                dt.completed_at,
                t.complexity,
                t.cognitive_load,
                t.time_estimate
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.scheduled_date BETWEEN ? AND ?
            ORDER BY dt.scheduled_date
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        raw_data = [dict(row) for row in cursor.fetchall()]
        
        if len(raw_data) < 3:
            return {
                'status': 'insufficient_data',
                'message': 'Complete more tasks over several days to see trends',
                'minimum_required': 7,
                'current_count': len(raw_data)
            }
        
        # Process daily metrics
        daily_metrics = TrendsEngine._calculate_daily_metrics(raw_data)
        
        # Calculate trends and indicators
        trend_analysis = TrendsEngine._analyze_trend(daily_metrics)
        momentum = TrendsEngine._calculate_momentum(daily_metrics)
        velocity = TrendsEngine._calculate_velocity(daily_metrics)
        moving_averages = TrendsEngine._calculate_moving_averages(daily_metrics)
        comparisons = TrendsEngine._comparative_analysis(daily_metrics)
        patterns = TrendsEngine._detect_patterns(daily_metrics, raw_data)
        forecast = TrendsEngine._generate_forecast(daily_metrics, trend_analysis)
        anomalies = TrendsEngine._detect_anomalies(daily_metrics)
        performance_zone = TrendsEngine._get_performance_zone(daily_metrics)
        
        return {
            'status': 'success',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days,
                'active_days': len(daily_metrics)
            },
            'daily_data': daily_metrics,
            'trend': trend_analysis,
            'momentum': momentum,
            'velocity': velocity,
            'moving_averages': moving_averages,
            'comparisons': comparisons,
            'patterns': patterns,
            'forecast': forecast,
            'anomalies': anomalies,
            'performance_zone': performance_zone,
            'summary': TrendsEngine._generate_summary(
                trend_analysis, momentum, velocity, comparisons, forecast
            )
        }
    
    @staticmethod
    def _calculate_daily_metrics(raw_data):
        """Calculate metrics for each day"""
        daily = defaultdict(lambda: {
            'total': 0, 'completed': 0, 'points': 0, 'penalties': 0,
            'estimated_time': 0, 'actual_time': 0, 'deep_work': 0,
            'complexity_sum': 0, 'rollovers': 0
        })
        
        for task in raw_data:
            d = task['scheduled_date']
            daily[d]['total'] += 1
            daily[d]['complexity_sum'] += task['complexity']
            daily[d]['estimated_time'] += task['time_estimate'] or 0
            daily[d]['rollovers'] += task['rolled_over_count'] or 0
            
            if task['status'] == 'completed':
                daily[d]['completed'] += 1
                daily[d]['points'] += calculate_task_points(task)
                daily[d]['actual_time'] += task['actual_time'] or task['time_estimate'] or 0
                if task['cognitive_load'] == 'deep_work':
                    daily[d]['deep_work'] += 1
            else:
                daily[d]['penalties'] += task['penalty_points'] or 0
        
        # Convert to list with calculated rates
        metrics = []
        for d in sorted(daily.keys()):
            data = daily[d]
            metrics.append({
                'date': d,
                'day_name': datetime.fromisoformat(d).strftime('%A'),
                'day_of_week': datetime.fromisoformat(d).weekday(),
                'total_tasks': data['total'],
                'completed_tasks': data['completed'],
                'completion_rate': round(data['completed'] / data['total'] * 100, 1) if data['total'] > 0 else 0,
                'points_earned': data['points'],
                'penalties': data['penalties'],
                'net_points': data['points'] - data['penalties'],
                'avg_complexity': round(data['complexity_sum'] / data['total'], 1) if data['total'] > 0 else 0,
                'deep_work_tasks': data['deep_work'],
                'deep_work_rate': round(data['deep_work'] / data['completed'] * 100, 1) if data['completed'] > 0 else 0,
                'estimated_time': data['estimated_time'],
                'actual_time': data['actual_time'],
                'time_accuracy': round(data['estimated_time'] / data['actual_time'] * 100, 1) if data['actual_time'] > 0 else 100,
                'rollover_count': data['rollovers']
            })
        
        return metrics
    
    @staticmethod
    def _analyze_trend(daily_metrics):
        """Analyze overall trend using linear regression"""
        if len(daily_metrics) < 3:
            return {'direction': 'insufficient_data', 'strength': 0}
        
        # Use completion rates for trend
        n = len(daily_metrics)
        x = list(range(n))
        y = [m['completion_rate'] for m in daily_metrics]
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Calculate R-squared for confidence
        ss_res = sum((y[i] - (y_mean + slope * (x[i] - x_mean))) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine trend direction and strength
        if slope > 2:
            direction = 'strongly_improving'
            icon = '🚀'
        elif slope > 0.5:
            direction = 'improving'
            icon = '📈'
        elif slope > -0.5:
            direction = 'stable'
            icon = '➡️'
        elif slope > -2:
            direction = 'declining'
            icon = '📉'
        else:
            direction = 'strongly_declining'
            icon = '⚠️'
        
        return {
            'direction': direction,
            'icon': icon,
            'slope': round(slope, 3),
            'strength': round(abs(slope), 3),
            'confidence': round(max(0, r_squared) * 100, 1),
            'avg_completion_rate': round(y_mean, 1),
            'trend_change_per_day': round(slope, 2),
            'projected_change_weekly': round(slope * 7, 1)
        }
    
    @staticmethod
    def _calculate_momentum(daily_metrics):
        """Calculate momentum using recent vs older performance"""
        if len(daily_metrics) < 7:
            return {'status': 'insufficient_data', 'value': 0}
        
        # Compare last 7 days vs previous 7 days
        recent = daily_metrics[-7:]
        previous = daily_metrics[-14:-7] if len(daily_metrics) >= 14 else daily_metrics[:-7]
        
        if not previous:
            return {'status': 'insufficient_data', 'value': 0}
        
        recent_avg = sum(m['completion_rate'] for m in recent) / len(recent)
        previous_avg = sum(m['completion_rate'] for m in previous) / len(previous)
        
        # Calculate momentum as percentage change
        if previous_avg > 0:
            momentum_value = (recent_avg - previous_avg) / previous_avg
        else:
            momentum_value = 0.25 if recent_avg > 0 else 0
        
        # Determine momentum status
        for status, config in TrendsEngine.MOMENTUM.items():
            if momentum_value >= config['threshold']:
                return {
                    'status': status,
                    'value': round(momentum_value * 100, 1),
                    'icon': config['icon'],
                    'color': config['color'],
                    'message': config['message'],
                    'recent_avg': round(recent_avg, 1),
                    'previous_avg': round(previous_avg, 1),
                    'change': round(recent_avg - previous_avg, 1)
                }
        
        return {
            'status': 'declining',
            'value': round(momentum_value * 100, 1),
            'icon': '⚠️',
            'color': '#ef4444',
            'message': 'Needs attention'
        }
    
    @staticmethod
    def _calculate_velocity(daily_metrics):
        """Calculate productivity velocity (rate of point accumulation)"""
        if len(daily_metrics) < 3:
            return {'status': 'insufficient_data'}
        
        # Calculate points per day velocity
        total_points = sum(m['net_points'] for m in daily_metrics)
        avg_daily_points = total_points / len(daily_metrics)
        
        # Calculate acceleration (change in velocity)
        if len(daily_metrics) >= 7:
            first_half = daily_metrics[:len(daily_metrics)//2]
            second_half = daily_metrics[len(daily_metrics)//2:]
            
            first_velocity = sum(m['net_points'] for m in first_half) / len(first_half)
            second_velocity = sum(m['net_points'] for m in second_half) / len(second_half)
            
            acceleration = second_velocity - first_velocity
        else:
            acceleration = 0
        
        # Calculate consistency (standard deviation of daily points)
        variance = sum((m['net_points'] - avg_daily_points) ** 2 for m in daily_metrics) / len(daily_metrics)
        std_dev = math.sqrt(variance)
        consistency = max(0, 100 - (std_dev / max(avg_daily_points, 1) * 100))
        
        return {
            'daily_average': round(avg_daily_points, 1),
            'total_period': total_points,
            'acceleration': round(acceleration, 2),
            'accelerating': acceleration > 5,
            'consistency_score': round(consistency, 1),
            'projected_weekly': round(avg_daily_points * 7, 0),
            'projected_monthly': round(avg_daily_points * 30, 0),
            'best_day': max(daily_metrics, key=lambda x: x['net_points'])['date'],
            'best_day_points': max(m['net_points'] for m in daily_metrics)
        }
    
    @staticmethod
    def _calculate_moving_averages(daily_metrics):
        """Calculate moving averages for smoothed trend view"""
        if len(daily_metrics) < 3:
            return {}
        
        result = {
            'ma_3': [],  # 3-day moving average
            'ma_7': [],  # 7-day moving average
            'ema_5': []  # 5-day exponential moving average
        }
        
        rates = [m['completion_rate'] for m in daily_metrics]
        
        # Simple moving averages
        for i in range(len(rates)):
            if i >= 2:
                ma3 = sum(rates[i-2:i+1]) / 3
                result['ma_3'].append({'date': daily_metrics[i]['date'], 'value': round(ma3, 1)})
            
            if i >= 6:
                ma7 = sum(rates[i-6:i+1]) / 7
                result['ma_7'].append({'date': daily_metrics[i]['date'], 'value': round(ma7, 1)})
        
        # Exponential moving average (more weight to recent)
        alpha = 2 / 6  # Smoothing factor for 5-day EMA
        ema = rates[0]
        for i, rate in enumerate(rates):
            ema = alpha * rate + (1 - alpha) * ema
            result['ema_5'].append({'date': daily_metrics[i]['date'], 'value': round(ema, 1)})
        
        return result
    
    @staticmethod
    def _comparative_analysis(daily_metrics):
        """Compare performance across time periods"""
        today = date.today()
        comparisons = {}
        
        if len(daily_metrics) >= 14:
            # This week vs last week
            this_week = [m for m in daily_metrics[-7:]]
            last_week = [m for m in daily_metrics[-14:-7]]
            
            this_week_avg = sum(m['completion_rate'] for m in this_week) / len(this_week)
            last_week_avg = sum(m['completion_rate'] for m in last_week) / len(last_week)
            
            wow_change = this_week_avg - last_week_avg
            
            comparisons['week_over_week'] = {
                'this_week': round(this_week_avg, 1),
                'last_week': round(last_week_avg, 1),
                'change': round(wow_change, 1),
                'change_percent': round((wow_change / last_week_avg * 100) if last_week_avg > 0 else 0, 1),
                'improved': wow_change > 0,
                'icon': '📈' if wow_change > 0 else '📉' if wow_change < 0 else '➡️'
            }
        
        # Day of week comparison
        dow_performance = defaultdict(list)
        for m in daily_metrics:
            dow_performance[m['day_of_week']].append(m['completion_rate'])
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_averages = {}
        for dow, rates in dow_performance.items():
            dow_averages[day_names[dow]] = round(sum(rates) / len(rates), 1)
        
        if dow_averages:
            best_day = max(dow_averages.items(), key=lambda x: x[1])
            worst_day = min(dow_averages.items(), key=lambda x: x[1])
            
            comparisons['day_of_week'] = {
                'averages': dow_averages,
                'best_day': {'name': best_day[0], 'rate': best_day[1]},
                'worst_day': {'name': worst_day[0], 'rate': worst_day[1]},
                'variance': round(best_day[1] - worst_day[1], 1)
            }
        
        # Weekend vs weekday comparison
        weekday_metrics = [m for m in daily_metrics if m['day_of_week'] < 5]
        weekend_metrics = [m for m in daily_metrics if m['day_of_week'] >= 5]
        
        if weekday_metrics and weekend_metrics:
            weekday_avg = sum(m['completion_rate'] for m in weekday_metrics) / len(weekday_metrics)
            weekend_avg = sum(m['completion_rate'] for m in weekend_metrics) / len(weekend_metrics)
            
            comparisons['weekday_vs_weekend'] = {
                'weekday_avg': round(weekday_avg, 1),
                'weekend_avg': round(weekend_avg, 1),
                'difference': round(weekday_avg - weekend_avg, 1),
                'weekday_better': weekday_avg > weekend_avg
            }
        
        return comparisons
    
    @staticmethod
    def _detect_patterns(daily_metrics, raw_data):
        """Detect recurring patterns in the data"""
        patterns = []
        
        # Pattern 1: Consistent high performers (90%+ for 3+ consecutive days)
        consecutive_high = 0
        max_consecutive_high = 0
        for m in daily_metrics:
            if m['completion_rate'] >= 90:
                consecutive_high += 1
                max_consecutive_high = max(max_consecutive_high, consecutive_high)
            else:
                consecutive_high = 0
        
        if max_consecutive_high >= 3:
            patterns.append({
                'type': 'high_performance_streak',
                'icon': '🔥',
                'title': 'High Performance Streaks',
                'description': f'You\'ve had {max_consecutive_high} consecutive days of 90%+ completion',
                'insight': 'You perform best when building momentum. Try to maintain streaks.',
                'strength': 'high'
            })
        
        # Pattern 2: Monday motivation (higher Monday performance)
        monday_metrics = [m for m in daily_metrics if m['day_of_week'] == 0]
        other_metrics = [m for m in daily_metrics if m['day_of_week'] != 0]
        
        if monday_metrics and other_metrics:
            monday_avg = sum(m['completion_rate'] for m in monday_metrics) / len(monday_metrics)
            other_avg = sum(m['completion_rate'] for m in other_metrics) / len(other_metrics)
            
            if monday_avg > other_avg + 10:
                patterns.append({
                    'type': 'monday_motivation',
                    'icon': '📅',
                    'title': 'Monday Motivation',
                    'description': f'Your Mondays are {round(monday_avg - other_avg, 1)}% more productive',
                    'insight': 'You start weeks strong. Protect Monday mornings for important tasks.',
                    'strength': 'medium'
                })
        
        # Pattern 3: Friday fatigue
        friday_metrics = [m for m in daily_metrics if m['day_of_week'] == 4]
        if friday_metrics and len(daily_metrics) > 10:
            friday_avg = sum(m['completion_rate'] for m in friday_metrics) / len(friday_metrics)
            week_avg = sum(m['completion_rate'] for m in daily_metrics) / len(daily_metrics)
            
            if friday_avg < week_avg - 15:
                patterns.append({
                    'type': 'friday_fatigue',
                    'icon': '😴',
                    'title': 'Friday Fatigue',
                    'description': f'Friday productivity is {round(week_avg - friday_avg, 1)}% below average',
                    'insight': 'Schedule lighter tasks or wrap-up activities on Fridays.',
                    'strength': 'medium'
                })
        
        # Pattern 4: Deep work correlation
        deep_work_days = [m for m in daily_metrics if m['deep_work_tasks'] > 0]
        no_deep_work_days = [m for m in daily_metrics if m['deep_work_tasks'] == 0]
        
        if deep_work_days and no_deep_work_days:
            dw_points_avg = sum(m['net_points'] for m in deep_work_days) / len(deep_work_days)
            no_dw_points_avg = sum(m['net_points'] for m in no_deep_work_days) / len(no_deep_work_days)
            
            if dw_points_avg > no_dw_points_avg * 1.5:
                patterns.append({
                    'type': 'deep_work_impact',
                    'icon': '🧠',
                    'title': 'Deep Work Impact',
                    'description': f'Days with deep work earn {round(dw_points_avg - no_dw_points_avg, 0)} more points',
                    'insight': 'Deep work significantly boosts your productivity. Prioritize it.',
                    'strength': 'high'
                })
        
        # Pattern 5: Complexity avoidance
        high_complexity = [t for t in raw_data if t['complexity'] >= 4]
        low_complexity = [t for t in raw_data if t['complexity'] <= 2]
        
        if high_complexity and low_complexity:
            high_completion = sum(1 for t in high_complexity if t['status'] == 'completed') / len(high_complexity)
            low_completion = sum(1 for t in low_complexity if t['status'] == 'completed') / len(low_complexity)
            
            if high_completion < low_completion - 0.2:
                patterns.append({
                    'type': 'complexity_challenge',
                    'icon': '🎯',
                    'title': 'Complex Task Challenge',
                    'description': f'High complexity tasks complete {round((low_completion - high_completion) * 100, 0)}% less often',
                    'insight': 'Break complex tasks into smaller subtasks for better completion.',
                    'strength': 'medium'
                })
        
        # Pattern 6: Time estimation pattern
        underestimated = sum(1 for t in raw_data if t.get('actual_time') and t.get('time_estimate') 
                           and t['actual_time'] > t['time_estimate'] * 1.3)
        overestimated = sum(1 for t in raw_data if t.get('actual_time') and t.get('time_estimate')
                          and t['actual_time'] < t['time_estimate'] * 0.7)
        
        if underestimated > len(raw_data) * 0.3:
            patterns.append({
                'type': 'chronic_underestimation',
                'icon': '⏱️',
                'title': 'Chronic Underestimation',
                'description': f'{round(underestimated / len(raw_data) * 100, 0)}% of tasks take longer than planned',
                'insight': 'Add 30% buffer to your time estimates for more realistic planning.',
                'strength': 'high'
            })
        elif overestimated > len(raw_data) * 0.3:
            patterns.append({
                'type': 'overestimation',
                'icon': '⚡',
                'title': 'Faster Than Expected',
                'description': f'{round(overestimated / len(raw_data) * 100, 0)}% of tasks finish early',
                'insight': 'You\'re faster than you think! Consider taking on more challenging work.',
                'strength': 'positive'
            })
        
        return patterns
    
    @staticmethod
    def _generate_forecast(daily_metrics, trend_analysis):
        """Generate 7-day forecast based on trends"""
        if len(daily_metrics) < 7:
            return {'status': 'insufficient_data'}
        
        # Use recent trend and historical day-of-week performance
        today = date.today()
        slope = trend_analysis.get('slope', 0)
        
        # Calculate day-of-week averages
        dow_averages = defaultdict(list)
        for m in daily_metrics:
            dow_averages[m['day_of_week']].append(m['completion_rate'])
        
        dow_baseline = {dow: sum(rates) / len(rates) for dow, rates in dow_averages.items()}
        
        # Generate forecasts
        forecasts = []
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i in range(1, 8):
            forecast_date = today + timedelta(days=i)
            dow = forecast_date.weekday()
            
            # Base prediction from day-of-week average
            base = dow_baseline.get(dow, sum(dow_baseline.values()) / len(dow_baseline) if dow_baseline else 50)
            
            # Adjust for trend
            trend_adjustment = slope * (len(daily_metrics) + i)
            predicted = min(100, max(0, base + trend_adjustment))
            
            # Calculate confidence (decreases with distance)
            confidence = max(50, 95 - (i * 7))
            
            forecasts.append({
                'date': forecast_date.isoformat(),
                'day_name': day_names[dow],
                'predicted_completion': round(predicted, 1),
                'confidence': confidence,
                'range': {
                    'low': round(max(0, predicted - 15), 1),
                    'high': round(min(100, predicted + 15), 1)
                }
            })
        
        # Overall forecast summary
        avg_forecast = sum(f['predicted_completion'] for f in forecasts) / len(forecasts)
        recent_avg = sum(m['completion_rate'] for m in daily_metrics[-7:]) / min(7, len(daily_metrics))
        
        return {
            'status': 'success',
            'daily_forecasts': forecasts,
            'summary': {
                'avg_predicted': round(avg_forecast, 1),
                'current_avg': round(recent_avg, 1),
                'expected_change': round(avg_forecast - recent_avg, 1),
                'outlook': 'improving' if avg_forecast > recent_avg else 'declining' if avg_forecast < recent_avg else 'stable'
            },
            'best_predicted_day': max(forecasts, key=lambda x: x['predicted_completion']),
            'challenging_day': min(forecasts, key=lambda x: x['predicted_completion'])
        }
    
    @staticmethod
    def _detect_anomalies(daily_metrics):
        """Detect anomalies in the data (unusually good or bad days)"""
        if len(daily_metrics) < 5:
            return []
        
        # Calculate mean and standard deviation
        rates = [m['completion_rate'] for m in daily_metrics]
        mean = sum(rates) / len(rates)
        variance = sum((r - mean) ** 2 for r in rates) / len(rates)
        std_dev = math.sqrt(variance)
        
        anomalies = []
        for m in daily_metrics:
            z_score = (m['completion_rate'] - mean) / std_dev if std_dev > 0 else 0
            
            if z_score > 2:
                anomalies.append({
                    'date': m['date'],
                    'day_name': m['day_name'],
                    'type': 'exceptional_high',
                    'icon': '🌟',
                    'value': m['completion_rate'],
                    'z_score': round(z_score, 2),
                    'message': f'Exceptional day: {m["completion_rate"]}% completion'
                })
            elif z_score < -2:
                anomalies.append({
                    'date': m['date'],
                    'day_name': m['day_name'],
                    'type': 'unusual_low',
                    'icon': '⚠️',
                    'value': m['completion_rate'],
                    'z_score': round(z_score, 2),
                    'message': f'Challenging day: {m["completion_rate"]}% completion'
                })
        
        return anomalies
    
    @staticmethod
    def _get_performance_zone(daily_metrics):
        """Determine current performance zone"""
        if not daily_metrics:
            return None
        
        # Use recent 7-day average
        recent = daily_metrics[-7:] if len(daily_metrics) >= 7 else daily_metrics
        avg_rate = sum(m['completion_rate'] for m in recent) / len(recent)
        
        for zone_name, zone_config in TrendsEngine.PERFORMANCE_ZONES.items():
            if avg_rate >= zone_config['min']:
                return {
                    'zone': zone_name,
                    'current_rate': round(avg_rate, 1),
                    'icon': zone_config['icon'],
                    'color': zone_config['color'],
                    'description': zone_config['description'],
                    'next_zone': None
                }
        
        return None
    
    @staticmethod
    def _generate_summary(trend, momentum, velocity, comparisons, forecast):
        """Generate human-readable trend summary"""
        summaries = []
        
        # Trend summary
        if trend.get('direction') == 'strongly_improving':
            summaries.append('🚀 You\'re on fire! Performance is surging upward.')
        elif trend.get('direction') == 'improving':
            summaries.append('📈 Great progress! Your productivity is steadily improving.')
        elif trend.get('direction') == 'stable':
            summaries.append('➡️ Consistent performance. Consider pushing for new heights.')
        elif trend.get('direction') == 'declining':
            summaries.append('📉 Performance is slipping. Time to refocus.')
        
        # Momentum insight
        if momentum.get('status') == 'surging':
            summaries.append('⚡ Momentum is exceptional - ride this wave!')
        elif momentum.get('status') == 'slowing':
            summaries.append('🔋 Momentum is decreasing. Consider taking strategic breaks.')
        
        # Comparison insight
        wow = comparisons.get('week_over_week', {})
        if wow.get('improved') and wow.get('change', 0) > 10:
            summaries.append(f'📊 This week is {wow["change"]}% better than last week!')
        elif wow.get('change', 0) < -10:
            summaries.append(f'📊 This week is {abs(wow["change"])}% below last week. Time to rally!')
        
        # Forecast insight
        if forecast.get('summary', {}).get('outlook') == 'improving':
            summaries.append('🔮 Forecast looks positive for the coming week.')
        
        return summaries

