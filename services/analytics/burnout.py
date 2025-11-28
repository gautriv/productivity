"""
World-Class Burnout Analysis Engine
Comprehensive burnout detection with early warning system, stress tracking,
resilience scoring, and personalized recovery plans
"""
from datetime import datetime, date, timedelta
from models.database import get_db, calculate_task_points
from collections import defaultdict
import math


class BurnoutEngine:
    """
    World-Class Burnout Analysis Engine
    Features:
    - Multi-factor burnout risk assessment (12+ indicators)
    - Early warning system with predictive alerts
    - Stress accumulation tracking
    - Work-life balance scoring
    - Mental load assessment
    - Resilience scoring
    - Personalized recovery plans
    - Historical burnout pattern detection
    - Energy reserves estimation
    """
    
    # ===== BURNOUT RISK LEVELS =====
    RISK_LEVELS = {
        'thriving': {
            'range': (0, 15),
            'icon': '🌟',
            'color': '#22c55e',
            'title': 'Thriving',
            'description': 'Excellent balance and sustainable pace',
            'emoji_scale': '😊'
        },
        'healthy': {
            'range': (15, 30),
            'icon': '✅',
            'color': '#3b82f6',
            'title': 'Healthy',
            'description': 'Good balance with minor stress indicators',
            'emoji_scale': '🙂'
        },
        'caution': {
            'range': (30, 50),
            'icon': '⚠️',
            'color': '#f59e0b',
            'title': 'Caution Zone',
            'description': 'Early warning signs detected',
            'emoji_scale': '😐'
        },
        'elevated': {
            'range': (50, 70),
            'icon': '🔶',
            'color': '#f97316',
            'title': 'Elevated Risk',
            'description': 'Multiple burnout indicators present',
            'emoji_scale': '😟'
        },
        'high': {
            'range': (70, 85),
            'icon': '🔴',
            'color': '#ef4444',
            'title': 'High Risk',
            'description': 'Immediate intervention recommended',
            'emoji_scale': '😰'
        },
        'critical': {
            'range': (85, 100),
            'icon': '🚨',
            'color': '#dc2626',
            'title': 'Critical',
            'description': 'Severe burnout indicators - take action now',
            'emoji_scale': '😫'
        }
    }
    
    # ===== BURNOUT INDICATORS (12 factors) =====
    INDICATORS = {
        'declining_performance': {
            'weight': 12,
            'name': 'Declining Performance',
            'icon': '📉',
            'description': 'Completion rate dropping over time'
        },
        'excessive_workload': {
            'weight': 10,
            'name': 'Excessive Workload',
            'icon': '😤',
            'description': 'Too many tasks scheduled'
        },
        'chronic_rollover': {
            'weight': 10,
            'name': 'Chronic Rollover',
            'icon': '🔄',
            'description': 'Tasks repeatedly postponed'
        },
        'deep_work_overload': {
            'weight': 9,
            'name': 'Deep Work Overload',
            'icon': '🧠',
            'description': 'Excessive cognitive demands'
        },
        'no_rest_days': {
            'weight': 9,
            'name': 'Insufficient Rest',
            'icon': '😴',
            'description': 'Working without breaks'
        },
        'time_estimation_collapse': {
            'weight': 8,
            'name': 'Time Estimation Collapse',
            'icon': '⏰',
            'description': 'Severely underestimating task time'
        },
        'evening_work_creep': {
            'weight': 7,
            'name': 'Evening Work Creep',
            'icon': '🌙',
            'description': 'Work bleeding into personal time'
        },
        'complexity_avoidance': {
            'weight': 7,
            'name': 'Complexity Avoidance',
            'icon': '😬',
            'description': 'Avoiding challenging tasks'
        },
        'streak_breaking': {
            'weight': 6,
            'name': 'Streak Breaking',
            'icon': '💔',
            'description': 'Losing momentum and consistency'
        },
        'point_stagnation': {
            'weight': 6,
            'name': 'Point Stagnation',
            'icon': '📊',
            'description': 'No improvement in productivity'
        },
        'abandonment_increase': {
            'weight': 8,
            'name': 'Task Abandonment',
            'icon': '🚫',
            'description': 'Giving up on tasks'
        },
        'weekend_erosion': {
            'weight': 8,
            'name': 'Weekend Erosion',
            'icon': '📅',
            'description': 'Losing personal time boundaries'
        }
    }
    
    # ===== RECOVERY STRATEGIES =====
    RECOVERY_STRATEGIES = {
        'immediate': [
            {
                'name': 'Emergency Reset',
                'icon': '🛑',
                'description': 'Cancel non-essential tasks for the next 3 days',
                'duration': '3 days',
                'effectiveness': 'high'
            },
            {
                'name': 'Digital Detox Evening',
                'icon': '📵',
                'description': 'No work-related activities after 6 PM',
                'duration': '1 week',
                'effectiveness': 'high'
            },
            {
                'name': 'Task Triage',
                'icon': '🏥',
                'description': 'Keep only top 3 priorities, delegate or delete rest',
                'duration': 'immediate',
                'effectiveness': 'high'
            }
        ],
        'short_term': [
            {
                'name': 'Protected Mornings',
                'icon': '🌅',
                'description': 'No meetings or reactive work before 10 AM',
                'duration': '2 weeks',
                'effectiveness': 'medium-high'
            },
            {
                'name': '90-20 Rule',
                'icon': '⏱️',
                'description': 'Work 90 minutes, break 20 minutes. No exceptions.',
                'duration': 'ongoing',
                'effectiveness': 'medium'
            },
            {
                'name': 'Complexity Cap',
                'icon': '🎚️',
                'description': 'Maximum 2 high-complexity tasks per day',
                'duration': '1 week',
                'effectiveness': 'medium'
            }
        ],
        'long_term': [
            {
                'name': 'Weekly Review Ritual',
                'icon': '📋',
                'description': 'Sunday planning session: review capacity, set realistic goals',
                'duration': 'ongoing',
                'effectiveness': 'high'
            },
            {
                'name': 'Energy Management',
                'icon': '🔋',
                'description': 'Match task difficulty to energy levels throughout day',
                'duration': 'ongoing',
                'effectiveness': 'high'
            },
            {
                'name': 'Buffer Time',
                'icon': '🛡️',
                'description': 'Add 30% buffer to all time estimates',
                'duration': 'ongoing',
                'effectiveness': 'medium'
            }
        ]
    }
    
    @staticmethod
    def get_comprehensive_analysis(days=14):
        """
        Comprehensive burnout analysis with all metrics
        """
        db = get_db()
        cursor = db.cursor()
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get all task data
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
        
        if len(raw_data) < 5:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 5 days of task data for burnout analysis',
                'minimum_required': 5,
                'current_count': len(raw_data)
            }
        
        # Calculate all indicators
        indicator_scores = BurnoutEngine._calculate_all_indicators(raw_data, days)
        
        # Calculate overall burnout score
        total_weight = sum(BurnoutEngine.INDICATORS[k]['weight'] for k in indicator_scores)
        weighted_score = sum(
            score * BurnoutEngine.INDICATORS[k]['weight']
            for k, score in indicator_scores.items()
        )
        burnout_score = (weighted_score / total_weight) if total_weight > 0 else 0
        
        # Get risk level
        risk_level = BurnoutEngine._get_risk_level(burnout_score)
        
        # Calculate additional metrics
        energy_reserves = BurnoutEngine._estimate_energy_reserves(raw_data)
        work_life_balance = BurnoutEngine._calculate_work_life_balance(raw_data)
        resilience_score = BurnoutEngine._calculate_resilience(raw_data)
        stress_accumulation = BurnoutEngine._calculate_stress_accumulation(raw_data)
        
        # Generate personalized recovery plan
        recovery_plan = BurnoutEngine._generate_recovery_plan(
            burnout_score, indicator_scores, risk_level
        )
        
        # Historical comparison
        historical = BurnoutEngine._get_historical_comparison(cursor, days)
        
        # Predictive analysis
        prediction = BurnoutEngine._predict_trajectory(raw_data, burnout_score)
        
        # Active indicators (contributing to burnout)
        active_indicators = [
            {
                'id': k,
                'name': BurnoutEngine.INDICATORS[k]['name'],
                'icon': BurnoutEngine.INDICATORS[k]['icon'],
                'description': BurnoutEngine.INDICATORS[k]['description'],
                'severity': BurnoutEngine._get_severity(v),
                'score': round(v, 1),
                'contribution': round(v * BurnoutEngine.INDICATORS[k]['weight'] / total_weight * 100, 1)
            }
            for k, v in sorted(indicator_scores.items(), key=lambda x: x[1], reverse=True)
            if v > 20
        ]
        
        return {
            'status': 'success',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days,
                'tasks_analyzed': len(raw_data)
            },
            'burnout_score': round(burnout_score, 1),
            'risk_level': risk_level,
            'active_indicators': active_indicators,
            'all_indicators': {k: round(v, 1) for k, v in indicator_scores.items()},
            'energy_reserves': energy_reserves,
            'work_life_balance': work_life_balance,
            'resilience_score': resilience_score,
            'stress_accumulation': stress_accumulation,
            'recovery_plan': recovery_plan,
            'historical_comparison': historical,
            'prediction': prediction,
            'quick_stats': BurnoutEngine._get_quick_stats(raw_data)
        }
    
    @staticmethod
    def _calculate_all_indicators(raw_data, days):
        """Calculate all 12 burnout indicators"""
        scores = {}
        
        # Group by date
        daily = defaultdict(list)
        for t in raw_data:
            daily[t['scheduled_date']].append(t)
        
        dates = sorted(daily.keys())
        
        # 1. Declining Performance (compare first half vs second half)
        if len(dates) >= 6:
            first_half = dates[:len(dates)//2]
            second_half = dates[len(dates)//2:]
            
            first_completion = sum(
                sum(1 for t in daily[d] if t['status'] == 'completed') / len(daily[d])
                for d in first_half
            ) / len(first_half)
            
            second_completion = sum(
                sum(1 for t in daily[d] if t['status'] == 'completed') / len(daily[d])
                for d in second_half
            ) / len(second_half)
            
            decline = first_completion - second_completion
            scores['declining_performance'] = min(100, max(0, decline * 200))
        else:
            scores['declining_performance'] = 0
        
        # 2. Excessive Workload (avg tasks per day)
        avg_tasks = sum(len(daily[d]) for d in dates) / len(dates) if dates else 0
        if avg_tasks > 10:
            scores['excessive_workload'] = min(100, (avg_tasks - 10) * 15)
        elif avg_tasks > 7:
            scores['excessive_workload'] = min(100, (avg_tasks - 7) * 10)
        else:
            scores['excessive_workload'] = 0
        
        # 3. Chronic Rollover
        total_tasks = len(raw_data)
        rolled_tasks = sum(1 for t in raw_data if t['rolled_over_count'] >= 2)
        rollover_rate = rolled_tasks / total_tasks if total_tasks > 0 else 0
        scores['chronic_rollover'] = min(100, rollover_rate * 200)
        
        # 4. Deep Work Overload
        deep_work_time = sum(
            t['time_estimate'] or 0 for t in raw_data 
            if t['cognitive_load'] == 'deep_work'
        )
        total_time = sum(t['time_estimate'] or 0 for t in raw_data)
        deep_work_ratio = deep_work_time / total_time if total_time > 0 else 0
        
        # More than 50% deep work is concerning
        if deep_work_ratio > 0.5:
            scores['deep_work_overload'] = min(100, (deep_work_ratio - 0.5) * 200)
        else:
            scores['deep_work_overload'] = 0
        
        # Also check daily deep work hours
        for d in dates:
            daily_deep_work = sum(
                t['time_estimate'] or 0 for t in daily[d]
                if t['cognitive_load'] == 'deep_work'
            )
            if daily_deep_work > 300:  # More than 5 hours
                scores['deep_work_overload'] = max(
                    scores['deep_work_overload'],
                    min(100, (daily_deep_work - 300) / 60 * 30)
                )
        
        # 5. No Rest Days
        if len(dates) >= 7:
            weekends = [d for d in dates if datetime.fromisoformat(d).weekday() >= 5]
            working_weekends = sum(1 for d in weekends if len(daily[d]) > 0)
            weekend_ratio = working_weekends / len(weekends) if weekends else 0
            scores['no_rest_days'] = min(100, weekend_ratio * 100)
        else:
            scores['no_rest_days'] = 0
        
        # 6. Time Estimation Collapse
        tasks_with_actual = [t for t in raw_data if t['actual_time'] and t['time_estimate']]
        if len(tasks_with_actual) >= 5:
            overruns = [
                t for t in tasks_with_actual 
                if t['actual_time'] > t['time_estimate'] * 1.5
            ]
            overrun_rate = len(overruns) / len(tasks_with_actual)
            scores['time_estimation_collapse'] = min(100, overrun_rate * 150)
        else:
            scores['time_estimation_collapse'] = 0
        
        # 7. Evening Work Creep
        completed_with_time = [t for t in raw_data if t['completed_at'] and t['status'] == 'completed']
        if completed_with_time:
            evening_tasks = [
                t for t in completed_with_time
                if datetime.fromisoformat(t['completed_at']).hour >= 20
            ]
            evening_ratio = len(evening_tasks) / len(completed_with_time)
            scores['evening_work_creep'] = min(100, evening_ratio * 150)
        else:
            scores['evening_work_creep'] = 0
        
        # 8. Complexity Avoidance
        high_complexity = [t for t in raw_data if t['complexity'] >= 4]
        low_complexity = [t for t in raw_data if t['complexity'] <= 2]
        
        if high_complexity and low_complexity:
            high_completion = sum(1 for t in high_complexity if t['status'] == 'completed') / len(high_complexity)
            low_completion = sum(1 for t in low_complexity if t['status'] == 'completed') / len(low_complexity)
            
            avoidance = low_completion - high_completion
            if avoidance > 0.3:
                scores['complexity_avoidance'] = min(100, avoidance * 150)
            else:
                scores['complexity_avoidance'] = 0
        else:
            scores['complexity_avoidance'] = 0
        
        # 9. Streak Breaking
        streak_length = 0
        max_streak = 0
        for d in dates:
            completed_today = any(t['status'] == 'completed' for t in daily[d])
            if completed_today:
                streak_length += 1
                max_streak = max(max_streak, streak_length)
            else:
                streak_length = 0
        
        # If had a good streak that broke recently
        if max_streak >= 5 and streak_length == 0:
            scores['streak_breaking'] = 60
        elif max_streak >= 3 and streak_length == 0:
            scores['streak_breaking'] = 30
        else:
            scores['streak_breaking'] = 0
        
        # 10. Point Stagnation
        if len(dates) >= 10:
            first_points = sum(
                calculate_task_points(t) for d in dates[:5] for t in daily[d]
                if t['status'] == 'completed'
            )
            recent_points = sum(
                calculate_task_points(t) for d in dates[-5:] for t in daily[d]
                if t['status'] == 'completed'
            )
            
            if first_points > 0:
                change = (recent_points - first_points) / first_points
                if change < -0.2:
                    scores['point_stagnation'] = min(100, abs(change) * 150)
                else:
                    scores['point_stagnation'] = 0
            else:
                scores['point_stagnation'] = 0
        else:
            scores['point_stagnation'] = 0
        
        # 11. Abandonment Increase
        abandoned = [t for t in raw_data if t['status'] == 'abandoned']
        abandonment_rate = len(abandoned) / len(raw_data) if raw_data else 0
        scores['abandonment_increase'] = min(100, abandonment_rate * 200)
        
        # 12. Weekend Erosion
        weekend_tasks = [t for t in raw_data if datetime.fromisoformat(t['scheduled_date']).weekday() >= 5]
        if weekend_tasks and len(raw_data) > len(weekend_tasks):
            weekend_ratio = len(weekend_tasks) / len(raw_data)
            expected_ratio = 2 / 7  # 2 out of 7 days
            
            if weekend_ratio > expected_ratio * 1.5:
                scores['weekend_erosion'] = min(100, (weekend_ratio - expected_ratio) * 200)
            else:
                scores['weekend_erosion'] = 0
        else:
            scores['weekend_erosion'] = 0
        
        return scores
    
    @staticmethod
    def _get_risk_level(score):
        """Get risk level based on score"""
        for level_name, level_config in BurnoutEngine.RISK_LEVELS.items():
            if level_config['range'][0] <= score < level_config['range'][1]:
                return {
                    'level': level_name,
                    'score': round(score, 1),
                    **level_config
                }
        
        return BurnoutEngine.RISK_LEVELS['critical']
    
    @staticmethod
    def _get_severity(score):
        """Get severity label for indicator"""
        if score >= 70:
            return 'severe'
        elif score >= 50:
            return 'high'
        elif score >= 30:
            return 'moderate'
        elif score >= 15:
            return 'low'
        else:
            return 'minimal'
    
    @staticmethod
    def _estimate_energy_reserves(raw_data):
        """Estimate current energy reserves based on patterns"""
        # Factors: workload, completion rate, deep work ratio, rest days
        
        completed = sum(1 for t in raw_data if t['status'] == 'completed')
        total = len(raw_data)
        completion_rate = completed / total if total > 0 else 0
        
        # Calculate deep work burden
        deep_work = sum(1 for t in raw_data if t['cognitive_load'] == 'deep_work')
        deep_work_ratio = deep_work / total if total > 0 else 0
        
        # Check for rest days
        dates = set(t['scheduled_date'] for t in raw_data)
        rest_days = sum(1 for d in dates if datetime.fromisoformat(d).weekday() >= 5 
                       and all(t['scheduled_date'] != d or len([x for x in raw_data if x['scheduled_date'] == d]) < 3 
                              for t in raw_data))
        
        # Base energy (100)
        energy = 100
        
        # Deductions
        energy -= (1 - completion_rate) * 30  # Low completion drains energy
        energy -= deep_work_ratio * 20  # Deep work is draining
        energy -= max(0, (total / len(dates) - 5) * 5) if dates else 0  # Overload
        
        # Bonuses
        energy += min(rest_days * 10, 20)  # Rest days restore energy
        energy += completion_rate * 20  # Success builds energy
        
        energy = max(0, min(100, energy))
        
        if energy >= 70:
            status = 'healthy'
            icon = '🔋'
            message = 'Good energy reserves'
        elif energy >= 40:
            status = 'moderate'
            icon = '🪫'
            message = 'Energy levels declining'
        else:
            status = 'depleted'
            icon = '⚡'
            message = 'Energy reserves critically low'
        
        return {
            'level': round(energy, 1),
            'status': status,
            'icon': icon,
            'message': message,
            'factors': {
                'completion_impact': round((1 - completion_rate) * 30, 1),
                'deep_work_drain': round(deep_work_ratio * 20, 1),
                'rest_recovery': min(rest_days * 10, 20)
            }
        }
    
    @staticmethod
    def _calculate_work_life_balance(raw_data):
        """Calculate work-life balance score"""
        score = 100
        issues = []
        
        # Check evening work
        completed_with_time = [t for t in raw_data if t['completed_at']]
        if completed_with_time:
            evening_work = [t for t in completed_with_time 
                          if datetime.fromisoformat(t['completed_at']).hour >= 20]
            evening_ratio = len(evening_work) / len(completed_with_time)
            
            if evening_ratio > 0.3:
                score -= 25
                issues.append({
                    'issue': 'evening_work',
                    'icon': '🌙',
                    'message': f'{evening_ratio*100:.0f}% of work done after 8 PM'
                })
        
        # Check weekend work
        dates = set(t['scheduled_date'] for t in raw_data)
        weekends = [d for d in dates if datetime.fromisoformat(d).weekday() >= 5]
        
        if weekends and len(dates) > len(weekends):
            weekend_work_ratio = len(weekends) / len(dates)
            if weekend_work_ratio > 0.3:
                score -= 30
                issues.append({
                    'issue': 'weekend_work',
                    'icon': '📅',
                    'message': f'Working {weekend_work_ratio*100:.0f}% of weekends'
                })
        
        # Check workload
        avg_daily = len(raw_data) / len(dates) if dates else 0
        if avg_daily > 8:
            score -= 20
            issues.append({
                'issue': 'overload',
                'icon': '😤',
                'message': f'Averaging {avg_daily:.1f} tasks/day (recommended: 5-7)'
            })
        
        score = max(0, score)
        
        if score >= 70:
            status = 'healthy'
            icon = '⚖️'
        elif score >= 40:
            status = 'imbalanced'
            icon = '⚠️'
        else:
            status = 'poor'
            icon = '🔴'
        
        return {
            'score': score,
            'status': status,
            'icon': icon,
            'issues': issues,
            'recommendation': issues[0]['message'] if issues else 'Good work-life balance!'
        }
    
    @staticmethod
    def _calculate_resilience(raw_data):
        """Calculate resilience score based on recovery patterns"""
        
        # Resilience factors:
        # 1. Bounce back from bad days
        # 2. Handling rollovers
        # 3. Completing despite complexity
        
        score = 50  # Start at neutral
        factors = []
        
        # Factor 1: Recovery from low days
        daily = defaultdict(lambda: {'completed': 0, 'total': 0})
        for t in raw_data:
            daily[t['scheduled_date']]['total'] += 1
            if t['status'] == 'completed':
                daily[t['scheduled_date']]['completed'] += 1
        
        dates = sorted(daily.keys())
        recoveries = 0
        opportunities = 0
        
        for i in range(1, len(dates)):
            prev_rate = daily[dates[i-1]]['completed'] / daily[dates[i-1]]['total']
            curr_rate = daily[dates[i]]['completed'] / daily[dates[i]]['total']
            
            if prev_rate < 0.5:  # Bad day
                opportunities += 1
                if curr_rate >= 0.7:  # Good recovery
                    recoveries += 1
        
        if opportunities > 0:
            recovery_rate = recoveries / opportunities
            score += recovery_rate * 25
            factors.append({
                'factor': 'recovery',
                'score': round(recovery_rate * 100, 1),
                'message': f'Recovered from {recoveries}/{opportunities} difficult days'
            })
        
        # Factor 2: Rollover completion
        rolled = [t for t in raw_data if t['rolled_over_count'] >= 1]
        rolled_completed = [t for t in rolled if t['status'] == 'completed']
        
        if rolled:
            rollover_success = len(rolled_completed) / len(rolled)
            score += rollover_success * 15
            factors.append({
                'factor': 'persistence',
                'score': round(rollover_success * 100, 1),
                'message': f'Completed {len(rolled_completed)}/{len(rolled)} rolled-over tasks'
            })
        
        # Factor 3: Complex task handling
        complex_tasks = [t for t in raw_data if t['complexity'] >= 4]
        complex_completed = [t for t in complex_tasks if t['status'] == 'completed']
        
        if complex_tasks:
            complex_rate = len(complex_completed) / len(complex_tasks)
            score += complex_rate * 10
            factors.append({
                'factor': 'challenge_handling',
                'score': round(complex_rate * 100, 1),
                'message': f'Conquered {len(complex_completed)}/{len(complex_tasks)} complex tasks'
            })
        
        score = max(0, min(100, score))
        
        if score >= 70:
            status = 'strong'
            icon = '💪'
        elif score >= 40:
            status = 'moderate'
            icon = '🔄'
        else:
            status = 'developing'
            icon = '🌱'
        
        return {
            'score': round(score, 1),
            'status': status,
            'icon': icon,
            'factors': factors,
            'message': 'Strong ability to bounce back' if status == 'strong' else 'Building recovery capacity'
        }
    
    @staticmethod
    def _calculate_stress_accumulation(raw_data):
        """Track stress accumulation over the period"""
        stress_timeline = []
        cumulative_stress = 0
        
        daily = defaultdict(list)
        for t in raw_data:
            daily[t['scheduled_date']].append(t)
        
        for d in sorted(daily.keys()):
            tasks = daily[d]
            
            # Daily stress factors
            daily_stress = 0
            
            # Workload stress
            if len(tasks) > 7:
                daily_stress += (len(tasks) - 7) * 3
            
            # Incomplete stress
            incomplete = sum(1 for t in tasks if t['status'] != 'completed')
            daily_stress += incomplete * 2
            
            # Rollover stress
            rollovers = sum(t['rolled_over_count'] for t in tasks)
            daily_stress += rollovers * 1.5
            
            # Complexity stress
            high_complexity = sum(1 for t in tasks if t['complexity'] >= 4)
            daily_stress += high_complexity * 1
            
            # Recovery factor (weekends)
            is_weekend = datetime.fromisoformat(d).weekday() >= 5
            if is_weekend and len(tasks) < 3:
                daily_stress -= 10  # Rest recovery
            
            # Completion recovery
            completed = sum(1 for t in tasks if t['status'] == 'completed')
            if completed > 0:
                daily_stress -= completed * 0.5
            
            cumulative_stress = max(0, cumulative_stress + daily_stress)
            
            # Natural stress decay (daily)
            cumulative_stress *= 0.9
            
            stress_timeline.append({
                'date': d,
                'daily_stress': round(daily_stress, 1),
                'cumulative_stress': round(cumulative_stress, 1)
            })
        
        # Current stress level
        current_stress = cumulative_stress
        
        if current_stress >= 50:
            status = 'high'
            icon = '🔴'
        elif current_stress >= 25:
            status = 'moderate'
            icon = '🟡'
        else:
            status = 'low'
            icon = '🟢'
        
        return {
            'current_level': round(current_stress, 1),
            'status': status,
            'icon': icon,
            'timeline': stress_timeline[-7:],  # Last 7 days
            'trend': 'increasing' if len(stress_timeline) >= 2 and 
                     stress_timeline[-1]['cumulative_stress'] > stress_timeline[-2]['cumulative_stress'] 
                     else 'decreasing',
            'peak_day': max(stress_timeline, key=lambda x: x['cumulative_stress'])['date'] if stress_timeline else None
        }
    
    @staticmethod
    def _generate_recovery_plan(burnout_score, indicators, risk_level):
        """Generate personalized recovery plan"""
        plan = {
            'urgency': 'none',
            'strategies': [],
            'focus_areas': [],
            'timeline': None
        }
        
        level = risk_level.get('level', 'healthy')
        
        if level in ['critical', 'high']:
            plan['urgency'] = 'immediate'
            plan['strategies'] = BurnoutEngine.RECOVERY_STRATEGIES['immediate']
            plan['timeline'] = 'Start today - critical intervention needed'
        elif level in ['elevated', 'caution']:
            plan['urgency'] = 'soon'
            plan['strategies'] = BurnoutEngine.RECOVERY_STRATEGIES['short_term']
            plan['timeline'] = 'Implement within this week'
        else:
            plan['urgency'] = 'preventive'
            plan['strategies'] = BurnoutEngine.RECOVERY_STRATEGIES['long_term']
            plan['timeline'] = 'Ongoing maintenance'
        
        # Focus areas based on top indicators
        top_indicators = sorted(indicators.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for indicator_id, score in top_indicators:
            if score > 30:
                indicator = BurnoutEngine.INDICATORS.get(indicator_id, {})
                plan['focus_areas'].append({
                    'area': indicator.get('name', indicator_id),
                    'icon': indicator.get('icon', '⚠️'),
                    'score': round(score, 1),
                    'action': BurnoutEngine._get_specific_action(indicator_id)
                })
        
        return plan
    
    @staticmethod
    def _get_specific_action(indicator_id):
        """Get specific action for an indicator"""
        actions = {
            'declining_performance': 'Review and simplify your task list. Focus on quality over quantity.',
            'excessive_workload': 'Cut your daily task count by 30%. Prioritize ruthlessly.',
            'chronic_rollover': 'Break stuck tasks into 15-minute pieces. Start with the smallest.',
            'deep_work_overload': 'Limit deep work to 4 hours/day. Mix in lighter tasks.',
            'no_rest_days': 'Block one full day per week with zero work tasks.',
            'time_estimation_collapse': 'Triple your time estimates for the next week.',
            'evening_work_creep': 'Set a hard stop at 6 PM. No exceptions for one week.',
            'complexity_avoidance': 'Do one complex task first thing each morning.',
            'streak_breaking': 'Commit to completing just one small task daily.',
            'point_stagnation': 'Focus on higher-value deep work tasks.',
            'abandonment_increase': 'Review abandoned tasks - delete or break down.',
            'weekend_erosion': 'Remove all weekend tasks. Schedule them for weekdays.'
        }
        return actions.get(indicator_id, 'Focus on sustainable practices.')
    
    @staticmethod
    def _get_historical_comparison(cursor, days):
        """Compare current period to historical data"""
        today = date.today()
        current_start = today - timedelta(days=days)
        previous_start = current_start - timedelta(days=days)
        
        # Get previous period data
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                AVG(rolled_over_count) as avg_rollover
            FROM daily_tasks
            WHERE scheduled_date BETWEEN ? AND ?
        ''', (previous_start.isoformat(), current_start.isoformat()))
        
        previous = dict(cursor.fetchone())
        
        # Get current period data
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                AVG(rolled_over_count) as avg_rollover
            FROM daily_tasks
            WHERE scheduled_date BETWEEN ? AND ?
        ''', (current_start.isoformat(), today.isoformat()))
        
        current = dict(cursor.fetchone())
        
        if previous['total'] and current['total']:
            prev_rate = previous['completed'] / previous['total'] * 100
            curr_rate = current['completed'] / current['total'] * 100
            
            return {
                'has_comparison': True,
                'previous_period': {
                    'completion_rate': round(prev_rate, 1),
                    'avg_rollover': round(previous['avg_rollover'] or 0, 2)
                },
                'current_period': {
                    'completion_rate': round(curr_rate, 1),
                    'avg_rollover': round(current['avg_rollover'] or 0, 2)
                },
                'change': {
                    'completion_rate': round(curr_rate - prev_rate, 1),
                    'direction': 'improving' if curr_rate > prev_rate else 'declining'
                }
            }
        
        return {'has_comparison': False}
    
    @staticmethod
    def _predict_trajectory(raw_data, current_score):
        """Predict burnout trajectory"""
        # Simple prediction based on recent trend
        daily = defaultdict(lambda: {'stress': 0})
        
        for t in raw_data:
            d = t['scheduled_date']
            daily[d]['stress'] += t['rolled_over_count'] or 0
            daily[d]['stress'] += 1 if t['status'] != 'completed' else -0.5
        
        dates = sorted(daily.keys())
        
        if len(dates) < 5:
            return {'status': 'insufficient_data'}
        
        # Calculate trend
        recent_stress = sum(daily[d]['stress'] for d in dates[-3:]) / 3
        earlier_stress = sum(daily[d]['stress'] for d in dates[:3]) / 3
        
        trend = recent_stress - earlier_stress
        
        if trend > 2:
            return {
                'status': 'concerning',
                'icon': '📈',
                'message': 'Stress is increasing. Take preventive action.',
                'predicted_score': min(100, current_score + 15),
                'timeframe': 'next 2 weeks'
            }
        elif trend < -2:
            return {
                'status': 'improving',
                'icon': '📉',
                'message': 'Stress is decreasing. Keep up good habits.',
                'predicted_score': max(0, current_score - 10),
                'timeframe': 'next 2 weeks'
            }
        else:
            return {
                'status': 'stable',
                'icon': '➡️',
                'message': 'Stress levels are stable.',
                'predicted_score': current_score,
                'timeframe': 'next 2 weeks'
            }
    
    @staticmethod
    def _get_quick_stats(raw_data):
        """Get quick overview stats"""
        total = len(raw_data)
        completed = sum(1 for t in raw_data if t['status'] == 'completed')
        rolled = sum(1 for t in raw_data if t['rolled_over_count'] >= 1)
        
        dates = set(t['scheduled_date'] for t in raw_data)
        
        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round(completed / total * 100, 1) if total > 0 else 0,
            'rollover_rate': round(rolled / total * 100, 1) if total > 0 else 0,
            'active_days': len(dates),
            'avg_tasks_per_day': round(total / len(dates), 1) if dates else 0
        }

