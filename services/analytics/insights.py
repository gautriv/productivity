"""
World-Class Insights Engine
AI-powered actionable insights with hidden pattern detection,
personalized recommendations, and productivity DNA profiling
"""
from datetime import datetime, date, timedelta
from models.database import get_db, calculate_task_points
from collections import defaultdict
import math


class InsightsEngine:
    """
    World-Class Insights Analysis Engine
    Features:
    - AI-powered actionable recommendations
    - Hidden pattern detection
    - Energy level correlation
    - Procrastination pattern detection
    - Time-of-day optimization
    - Task pairing recommendations
    - Productivity DNA profiling
    - Performance unlocks discovery
    """
    
    # ===== INSIGHT CATEGORIES =====
    CATEGORIES = {
        'performance': {'icon': '📊', 'name': 'Performance', 'priority': 1},
        'timing': {'icon': '⏰', 'name': 'Timing', 'priority': 2},
        'patterns': {'icon': '🔍', 'name': 'Patterns', 'priority': 3},
        'energy': {'icon': '🔋', 'name': 'Energy', 'priority': 4},
        'optimization': {'icon': '⚡', 'name': 'Optimization', 'priority': 5},
        'achievement': {'icon': '🏆', 'name': 'Achievement', 'priority': 6},
        'warning': {'icon': '⚠️', 'name': 'Warning', 'priority': 0}
    }
    
    # ===== PRODUCTIVITY DNA TRAITS =====
    DNA_TRAITS = {
        'early_bird': {
            'name': 'Early Bird',
            'icon': '🌅',
            'description': 'Most productive in early morning hours',
            'strength_factor': 'morning_performance'
        },
        'night_owl': {
            'name': 'Night Owl',
            'icon': '🦉',
            'description': 'Peak performance in evening/night hours',
            'strength_factor': 'evening_performance'
        },
        'deep_diver': {
            'name': 'Deep Diver',
            'icon': '🧠',
            'description': 'Excels at complex, focused work',
            'strength_factor': 'deep_work_rate'
        },
        'multitasker': {
            'name': 'Multitasker',
            'icon': '🔄',
            'description': 'Handles varied task types effectively',
            'strength_factor': 'task_variety'
        },
        'sprinter': {
            'name': 'Sprinter',
            'icon': '⚡',
            'description': 'High intensity, shorter bursts of productivity',
            'strength_factor': 'peak_days'
        },
        'marathon_runner': {
            'name': 'Marathon Runner',
            'icon': '🏃',
            'description': 'Consistent steady output over time',
            'strength_factor': 'consistency'
        },
        'streak_builder': {
            'name': 'Streak Builder',
            'icon': '🔥',
            'description': 'Gains momentum from consecutive successes',
            'strength_factor': 'streak_impact'
        },
        'complexity_crusher': {
            'name': 'Complexity Crusher',
            'icon': '💪',
            'description': 'Thrives on challenging, complex tasks',
            'strength_factor': 'high_complexity_rate'
        },
        'quick_starter': {
            'name': 'Quick Starter',
            'icon': '🚀',
            'description': 'Excellent at initiating and completing quickly',
            'strength_factor': 'first_task_success'
        },
        'finisher': {
            'name': 'Finisher',
            'icon': '🏁',
            'description': 'Strong at completing what\'s started',
            'strength_factor': 'completion_rate'
        }
    }
    
    @staticmethod
    def get_comprehensive_insights(days=30):
        """
        Generate comprehensive insights with all analysis types
        """
        db = get_db()
        cursor = db.cursor()
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get all task data
        cursor.execute('''
            SELECT 
                dt.id,
                dt.scheduled_date,
                dt.status,
                dt.rolled_over_count,
                dt.penalty_points,
                dt.actual_time,
                dt.completed_at,
                t.title,
                t.complexity,
                t.cognitive_load,
                t.time_estimate
            FROM daily_tasks dt
            JOIN tasks t ON dt.task_id = t.id
            WHERE dt.scheduled_date BETWEEN ? AND ?
            ORDER BY dt.scheduled_date, dt.completed_at
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        raw_data = [dict(row) for row in cursor.fetchall()]
        
        if len(raw_data) < 10:
            return {
                'status': 'insufficient_data',
                'message': 'Complete more tasks to unlock insights',
                'minimum_required': 10,
                'current_count': len(raw_data)
            }
        
        # Generate all insights
        performance_insights = InsightsEngine._analyze_performance(raw_data)
        timing_insights = InsightsEngine._analyze_timing(raw_data)
        pattern_insights = InsightsEngine._detect_hidden_patterns(raw_data)
        energy_insights = InsightsEngine._analyze_energy_patterns(raw_data)
        optimization_insights = InsightsEngine._generate_optimizations(raw_data)
        procrastination_insights = InsightsEngine._detect_procrastination(raw_data)
        productivity_dna = InsightsEngine._calculate_productivity_dna(raw_data)
        unlocks = InsightsEngine._discover_unlocks(raw_data)
        task_pairings = InsightsEngine._analyze_task_pairings(raw_data)
        
        # Combine and prioritize all insights
        all_insights = (
            performance_insights + 
            timing_insights + 
            pattern_insights + 
            energy_insights + 
            optimization_insights + 
            procrastination_insights
        )
        
        # Sort by priority and impact
        all_insights.sort(key=lambda x: (
            InsightsEngine.CATEGORIES.get(x.get('category', 'patterns'), {}).get('priority', 10),
            -x.get('impact_score', 0)
        ))
        
        return {
            'status': 'success',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days,
                'tasks_analyzed': len(raw_data)
            },
            'insights': all_insights[:15],  # Top 15 insights
            'productivity_dna': productivity_dna,
            'unlocks': unlocks,
            'task_pairings': task_pairings,
            'categories': InsightsEngine.CATEGORIES,
            'insight_count': len(all_insights)
        }
    
    @staticmethod
    def _analyze_performance(raw_data):
        """Analyze performance patterns and generate insights"""
        insights = []
        
        # Calculate overall stats
        completed = [t for t in raw_data if t['status'] == 'completed']
        completion_rate = len(completed) / len(raw_data) * 100
        
        # Insight 1: Overall completion rate
        if completion_rate >= 85:
            insights.append({
                'category': 'performance',
                'type': 'achievement',
                'icon': '🏆',
                'title': 'Excellence Achieved',
                'message': f'Your {completion_rate:.0f}% completion rate is exceptional! You\'re in the top tier of productivity.',
                'impact_score': 90,
                'metric': completion_rate,
                'action': 'Consider challenging yourself with higher complexity tasks.'
            })
        elif completion_rate < 50:
            insights.append({
                'category': 'warning',
                'type': 'improvement_needed',
                'icon': '⚠️',
                'title': 'Completion Rate Alert',
                'message': f'Only {completion_rate:.0f}% of tasks completed. This is holding back your progress.',
                'impact_score': 95,
                'metric': completion_rate,
                'action': 'Try planning fewer, more achievable tasks. Quality over quantity.'
            })
        
        # Insight 2: Complexity vs completion
        by_complexity = defaultdict(lambda: {'total': 0, 'completed': 0})
        for t in raw_data:
            by_complexity[t['complexity']]['total'] += 1
            if t['status'] == 'completed':
                by_complexity[t['complexity']]['completed'] += 1
        
        # Find complexity sweet spot
        completion_by_complexity = {
            c: (data['completed'] / data['total'] * 100) if data['total'] > 0 else 0
            for c, data in by_complexity.items()
        }
        
        if len(completion_by_complexity) >= 3:
            best_complexity = max(completion_by_complexity.items(), key=lambda x: x[1])
            worst_complexity = min(completion_by_complexity.items(), key=lambda x: x[1])
            
            if best_complexity[1] - worst_complexity[1] > 30:
                insights.append({
                    'category': 'optimization',
                    'type': 'complexity_insight',
                    'icon': '🎯',
                    'title': 'Complexity Sweet Spot Found',
                    'message': f'You crush complexity {best_complexity[0]} tasks ({best_complexity[1]:.0f}% complete) but struggle with complexity {worst_complexity[0]} ({worst_complexity[1]:.0f}%).',
                    'impact_score': 80,
                    'action': f'Break complexity {worst_complexity[0]} tasks into smaller complexity {best_complexity[0]} tasks.'
                })
        
        # Insight 3: Points per task efficiency
        if completed:
            total_points = sum(calculate_task_points(t) for t in completed)
            points_per_task = total_points / len(completed)
            
            high_value = [t for t in completed if calculate_task_points(t) > points_per_task * 1.5]
            high_value_pct = len(high_value) / len(completed) * 100
            
            if high_value_pct < 20:
                insights.append({
                    'category': 'optimization',
                    'type': 'value_optimization',
                    'icon': '💎',
                    'title': 'Unlock Higher Value Work',
                    'message': f'Only {high_value_pct:.0f}% of your tasks are high-value. You\'re leaving points on the table.',
                    'impact_score': 75,
                    'action': 'Prioritize deep work and complex tasks for maximum point efficiency.'
                })
        
        return insights
    
    @staticmethod
    def _analyze_timing(raw_data):
        """Analyze timing patterns for insights"""
        insights = []
        
        # Get completion times
        completed_with_time = [t for t in raw_data if t['status'] == 'completed' and t['completed_at']]
        
        if len(completed_with_time) < 5:
            return insights
        
        # Hour analysis
        hour_performance = defaultdict(lambda: {'count': 0, 'points': 0, 'complexity_sum': 0})
        
        for t in completed_with_time:
            try:
                completed_time = datetime.fromisoformat(t['completed_at'])
                hour = completed_time.hour
                hour_performance[hour]['count'] += 1
                hour_performance[hour]['points'] += calculate_task_points(t)
                hour_performance[hour]['complexity_sum'] += t['complexity']
            except:
                continue
        
        if len(hour_performance) >= 3:
            # Find peak hours
            hour_scores = {
                h: data['points'] / data['count'] 
                for h, data in hour_performance.items() 
                if data['count'] >= 2
            }
            
            if hour_scores:
                best_hour = max(hour_scores.items(), key=lambda x: x[1])
                worst_hour = min(hour_scores.items(), key=lambda x: x[1])
                
                # Time period classification
                def get_period(hour):
                    if 5 <= hour < 9:
                        return 'early morning'
                    elif 9 <= hour < 12:
                        return 'morning'
                    elif 12 <= hour < 14:
                        return 'midday'
                    elif 14 <= hour < 17:
                        return 'afternoon'
                    elif 17 <= hour < 20:
                        return 'evening'
                    else:
                        return 'night'
                
                insights.append({
                    'category': 'timing',
                    'type': 'peak_hour',
                    'icon': '⏰',
                    'title': 'Your Power Hour Revealed',
                    'message': f'You\'re most productive around {best_hour[0]}:00 ({get_period(best_hour[0])}). Tasks completed then earn {best_hour[1]:.0f} points on average.',
                    'impact_score': 85,
                    'action': f'Schedule your most important tasks between {best_hour[0]}:00-{(best_hour[0]+2)%24}:00.'
                })
                
                if best_hour[1] > worst_hour[1] * 1.5:
                    insights.append({
                        'category': 'timing',
                        'type': 'timing_variance',
                        'icon': '📉',
                        'title': 'Timing Matters More Than You Think',
                        'message': f'Your {get_period(best_hour[0])} productivity is {((best_hour[1]/worst_hour[1])-1)*100:.0f}% higher than {get_period(worst_hour[0])}.',
                        'impact_score': 75,
                        'action': f'Avoid scheduling important tasks during {get_period(worst_hour[0])} hours.'
                    })
        
        # Day of week analysis
        dow_performance = defaultdict(lambda: {'count': 0, 'points': 0})
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for t in completed_with_time:
            dow = datetime.fromisoformat(t['scheduled_date']).weekday()
            dow_performance[dow]['count'] += 1
            dow_performance[dow]['points'] += calculate_task_points(t)
        
        if len(dow_performance) >= 5:
            dow_avg = {
                dow: data['points'] / data['count']
                for dow, data in dow_performance.items()
                if data['count'] >= 2
            }
            
            if dow_avg:
                best_day = max(dow_avg.items(), key=lambda x: x[1])
                insights.append({
                    'category': 'timing',
                    'type': 'best_day',
                    'icon': '📅',
                    'title': f'{day_names[best_day[0]]} Is Your Superpower Day',
                    'message': f'You earn {best_day[1]:.0f} points per task on {day_names[best_day[0]]}s - your highest!',
                    'impact_score': 70,
                    'action': f'Reserve {day_names[best_day[0]]}s for your most challenging work.'
                })
        
        return insights
    
    @staticmethod
    def _detect_hidden_patterns(raw_data):
        """Detect hidden patterns users wouldn't normally notice"""
        insights = []
        
        # Pattern 1: Task sequence impact
        # Are certain task types better as first tasks vs last?
        daily_tasks = defaultdict(list)
        for t in raw_data:
            if t['completed_at']:
                daily_tasks[t['scheduled_date']].append(t)
        
        first_task_success = {'deep_work': 0, 'active_work': 0, 'admin': 0, 'learning': 0}
        first_task_total = {'deep_work': 0, 'active_work': 0, 'admin': 0, 'learning': 0}
        
        for day_tasks in daily_tasks.values():
            if len(day_tasks) >= 2:
                # Sort by completion time
                sorted_tasks = sorted(day_tasks, key=lambda x: x['completed_at'] or '')
                first_task = sorted_tasks[0]
                
                if first_task['cognitive_load']:
                    first_task_total[first_task['cognitive_load']] += 1
                    # Check if day was successful (80%+ completion)
                    day_completion = sum(1 for t in sorted_tasks if t['status'] == 'completed') / len(sorted_tasks)
                    if day_completion >= 0.8:
                        first_task_success[first_task['cognitive_load']] += 1
        
        # Find best first task type
        first_task_rates = {
            k: (first_task_success[k] / first_task_total[k] * 100) if first_task_total[k] >= 3 else 0
            for k in first_task_total
        }
        
        if any(v > 0 for v in first_task_rates.values()):
            best_first = max(first_task_rates.items(), key=lambda x: x[1])
            if best_first[1] >= 60:
                insights.append({
                    'category': 'patterns',
                    'type': 'first_task_pattern',
                    'icon': '🌅',
                    'title': 'Winning Start Pattern Discovered',
                    'message': f'Days starting with {best_first[0].replace("_", " ")} have {best_first[1]:.0f}% success rate!',
                    'impact_score': 85,
                    'action': f'Start each day with a {best_first[0].replace("_", " ")} task to set up for success.'
                })
        
        # Pattern 2: Rollover spiral detection
        rollover_tasks = [t for t in raw_data if t['rolled_over_count'] >= 2]
        if len(rollover_tasks) >= 3:
            rollover_types = defaultdict(int)
            for t in rollover_tasks:
                rollover_types[t['cognitive_load']] += 1
            
            if rollover_types:
                worst_type = max(rollover_types.items(), key=lambda x: x[1])
                total_of_type = sum(1 for t in raw_data if t['cognitive_load'] == worst_type[0])
                
                if worst_type[1] / total_of_type > 0.3:
                    insights.append({
                        'category': 'warning',
                        'type': 'rollover_pattern',
                        'icon': '🔄',
                        'title': 'Rollover Spiral Detected',
                        'message': f'{worst_type[0].replace("_", " ").title()} tasks are your rollover trap - {worst_type[1]} tasks stuck in limbo.',
                        'impact_score': 90,
                        'action': 'Break these tasks into 15-minute chunks that feel instantly achievable.'
                    })
        
        # Pattern 3: Completion timing within day
        same_day_completion = []
        next_day_completion = []
        
        for t in raw_data:
            if t['status'] == 'completed' and t['completed_at']:
                completed = datetime.fromisoformat(t['completed_at']).date()
                scheduled = datetime.fromisoformat(t['scheduled_date']).date()
                
                if completed == scheduled:
                    same_day_completion.append(t)
                elif (completed - scheduled).days == 1:
                    next_day_completion.append(t)
        
        if len(same_day_completion) >= 5 and len(next_day_completion) >= 5:
            same_day_points = sum(calculate_task_points(t) for t in same_day_completion) / len(same_day_completion)
            next_day_points = sum(calculate_task_points(t) for t in next_day_completion) / len(next_day_completion)
            
            if same_day_points > next_day_points * 1.3:
                insights.append({
                    'category': 'patterns',
                    'type': 'same_day_effect',
                    'icon': '⚡',
                    'title': 'Same-Day Magic Effect',
                    'message': f'Tasks completed same-day earn {same_day_points:.0f} pts vs {next_day_points:.0f} pts when delayed.',
                    'impact_score': 75,
                    'action': 'Push to complete at least one task same-day to maintain momentum.'
                })
        
        return insights
    
    @staticmethod
    def _analyze_energy_patterns(raw_data):
        """Analyze energy patterns throughout the day/week"""
        insights = []
        
        # Group by time of day
        morning = []    # 6-12
        afternoon = []  # 12-18
        evening = []    # 18-24
        
        for t in raw_data:
            if t['completed_at']:
                try:
                    hour = datetime.fromisoformat(t['completed_at']).hour
                    if 6 <= hour < 12:
                        morning.append(t)
                    elif 12 <= hour < 18:
                        afternoon.append(t)
                    else:
                        evening.append(t)
                except:
                    continue
        
        # Calculate complexity handling by time
        def avg_complexity(tasks):
            if not tasks:
                return 0
            return sum(t['complexity'] for t in tasks) / len(tasks)
        
        morning_complexity = avg_complexity(morning)
        afternoon_complexity = avg_complexity(afternoon)
        evening_complexity = avg_complexity(evening)
        
        complexities = [
            ('morning', morning_complexity, morning),
            ('afternoon', afternoon_complexity, afternoon),
            ('evening', evening_complexity, evening)
        ]
        
        valid_periods = [(name, comp, tasks) for name, comp, tasks in complexities if len(tasks) >= 3]
        
        if len(valid_periods) >= 2:
            best_for_complex = max(valid_periods, key=lambda x: x[1])
            
            insights.append({
                'category': 'energy',
                'type': 'energy_peak',
                'icon': '🔋',
                'title': 'Your Energy Peak Identified',
                'message': f'You handle complexity {best_for_complex[1]:.1f}/5 tasks best in the {best_for_complex[0]}.',
                'impact_score': 80,
                'action': f'Reserve {best_for_complex[0]}s for deep work and complex tasks.'
            })
        
        # Weekly energy pattern
        daily_completion = defaultdict(lambda: {'total': 0, 'completed': 0})
        for t in raw_data:
            dow = datetime.fromisoformat(t['scheduled_date']).weekday()
            daily_completion[dow]['total'] += 1
            if t['status'] == 'completed':
                daily_completion[dow]['completed'] += 1
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_rates = {
            dow: (data['completed'] / data['total'] * 100) if data['total'] > 0 else 0
            for dow, data in daily_completion.items()
        }
        
        # Detect energy dips
        if len(weekday_rates) >= 5:
            avg_rate = sum(weekday_rates.values()) / len(weekday_rates)
            dip_days = [dow for dow, rate in weekday_rates.items() if rate < avg_rate - 15]
            
            if dip_days:
                dip_day_names = [day_names[d] for d in dip_days]
                insights.append({
                    'category': 'energy',
                    'type': 'energy_dip',
                    'icon': '📉',
                    'title': 'Energy Dip Pattern Found',
                    'message': f'Your energy dips on {", ".join(dip_day_names)}. Completion drops significantly.',
                    'impact_score': 70,
                    'action': f'Plan lighter tasks or recovery activities on these days.'
                })
        
        return insights
    
    @staticmethod
    def _generate_optimizations(raw_data):
        """Generate specific optimization recommendations"""
        insights = []
        
        # Optimization 1: Task batching opportunities
        by_load = defaultdict(list)
        for t in raw_data:
            by_load[t['cognitive_load']].append(t)
        
        # Check if same-type tasks do better when grouped
        for load_type, tasks in by_load.items():
            if len(tasks) < 10:
                continue
            
            # Check for context switching penalty
            completed = [t for t in tasks if t['status'] == 'completed']
            if not completed:
                continue
            
            with_actual = [t for t in completed if t['actual_time'] and t['time_estimate']]
            if len(with_actual) >= 5:
                time_ratio = sum(t['actual_time'] for t in with_actual) / sum(t['time_estimate'] for t in with_actual)
                
                if time_ratio > 1.3:
                    insights.append({
                        'category': 'optimization',
                        'type': 'batching',
                        'icon': '📦',
                        'title': f'Batch {load_type.replace("_", " ").title()} Tasks',
                        'message': f'These tasks take {(time_ratio-1)*100:.0f}% longer than estimated. Batching reduces context switching.',
                        'impact_score': 70,
                        'action': f'Group all {load_type.replace("_", " ")} tasks into dedicated time blocks.'
                    })
                    break
        
        # Optimization 2: Complexity distribution
        daily_complexity = defaultdict(list)
        for t in raw_data:
            daily_complexity[t['scheduled_date']].append(t['complexity'])
        
        overloaded_days = 0
        for day, complexities in daily_complexity.items():
            if sum(complexities) > 15:  # More than 15 complexity points
                overloaded_days += 1
        
        if overloaded_days > len(daily_complexity) * 0.3:
            insights.append({
                'category': 'optimization',
                'type': 'complexity_distribution',
                'icon': '⚖️',
                'title': 'Redistribute Complexity',
                'message': f'{round(overloaded_days/len(daily_complexity)*100)}% of days are overloaded with complex tasks.',
                'impact_score': 75,
                'action': 'Spread complex tasks across multiple days. Max 2-3 high complexity tasks per day.'
            })
        
        # Optimization 3: Time estimation calibration
        time_ratios = []
        for t in raw_data:
            if t['status'] == 'completed' and t['actual_time'] and t['time_estimate']:
                time_ratios.append(t['actual_time'] / t['time_estimate'])
        
        if len(time_ratios) >= 10:
            avg_ratio = sum(time_ratios) / len(time_ratios)
            
            if avg_ratio > 1.4:
                multiplier = round(avg_ratio, 1)
                insights.append({
                    'category': 'optimization',
                    'type': 'time_calibration',
                    'icon': '⏱️',
                    'title': 'Calibrate Your Time Estimates',
                    'message': f'Tasks take {multiplier}x longer than you plan. This causes cascading delays.',
                    'impact_score': 85,
                    'action': f'Multiply your estimates by {multiplier} for realistic planning.'
                })
            elif avg_ratio < 0.6:
                insights.append({
                    'category': 'optimization',
                    'type': 'underutilization',
                    'icon': '🚀',
                    'title': 'You\'re Faster Than You Think!',
                    'message': f'You complete tasks in {avg_ratio*100:.0f}% of estimated time. You\'re underutilizing potential!',
                    'impact_score': 70,
                    'action': 'Take on more challenging work or tighter deadlines.'
                })
        
        return insights
    
    @staticmethod
    def _detect_procrastination(raw_data):
        """Detect procrastination patterns"""
        insights = []
        
        # Pattern 1: High rollover rate on specific types
        rollover_rates = defaultdict(lambda: {'rolled': 0, 'total': 0})
        
        for t in raw_data:
            key = (t['cognitive_load'], t['complexity'])
            rollover_rates[key]['total'] += 1
            if t['rolled_over_count'] >= 1:
                rollover_rates[key]['rolled'] += 1
        
        for (load, complexity), data in rollover_rates.items():
            if data['total'] >= 5:
                rate = data['rolled'] / data['total']
                if rate > 0.4:
                    insights.append({
                        'category': 'warning',
                        'type': 'procrastination',
                        'icon': '😬',
                        'title': 'Procrastination Pattern Detected',
                        'message': f'You procrastinate on {load.replace("_", " ")} complexity-{complexity} tasks {rate*100:.0f}% of the time.',
                        'impact_score': 85,
                        'action': 'Use the 2-minute rule: if it takes <2 min, do it now. Otherwise, schedule it for your peak hour.'
                    })
                    break
        
        # Pattern 2: End-of-day rush
        completed_with_time = [t for t in raw_data if t['status'] == 'completed' and t['completed_at']]
        late_completions = [t for t in completed_with_time 
                          if datetime.fromisoformat(t['completed_at']).hour >= 21]
        
        if len(completed_with_time) >= 10:
            late_rate = len(late_completions) / len(completed_with_time)
            
            if late_rate > 0.3:
                insights.append({
                    'category': 'patterns',
                    'type': 'deadline_driven',
                    'icon': '🌙',
                    'title': 'Deadline-Driven Behavior',
                    'message': f'{late_rate*100:.0f}% of tasks completed after 9 PM. You\'re a last-minute finisher.',
                    'impact_score': 65,
                    'action': 'Set artificial deadlines 2 hours before actual ones. Use timers.'
                })
        
        return insights
    
    @staticmethod
    def _calculate_productivity_dna(raw_data):
        """Calculate user's productivity DNA profile"""
        traits = {}
        
        # Calculate trait scores (0-100)
        completed = [t for t in raw_data if t['status'] == 'completed']
        
        if len(completed) < 10:
            return {'status': 'insufficient_data'}
        
        # 1. Early Bird vs Night Owl
        morning_completed = [t for t in completed if t['completed_at'] and 
                           5 <= datetime.fromisoformat(t['completed_at']).hour < 12]
        evening_completed = [t for t in completed if t['completed_at'] and 
                           datetime.fromisoformat(t['completed_at']).hour >= 18]
        
        if morning_completed or evening_completed:
            morning_score = len(morning_completed) / len(completed) * 100
            evening_score = len(evening_completed) / len(completed) * 100
            
            if morning_score > evening_score + 20:
                traits['early_bird'] = min(100, morning_score * 1.5)
            elif evening_score > morning_score + 20:
                traits['night_owl'] = min(100, evening_score * 1.5)
        
        # 2. Deep Diver
        deep_work = [t for t in completed if t['cognitive_load'] == 'deep_work']
        if deep_work:
            deep_work_rate = len(deep_work) / len(completed) * 100
            if deep_work_rate > 25:
                traits['deep_diver'] = min(100, deep_work_rate * 2)
        
        # 3. Complexity Crusher
        high_complexity = [t for t in completed if t['complexity'] >= 4]
        if high_complexity:
            high_complex_rate = len(high_complexity) / len(completed) * 100
            if high_complex_rate > 20:
                traits['complexity_crusher'] = min(100, high_complex_rate * 2.5)
        
        # 4. Finisher (completion rate)
        completion_rate = len(completed) / len(raw_data) * 100
        if completion_rate >= 70:
            traits['finisher'] = min(100, completion_rate)
        
        # 5. Marathon Runner (consistency)
        daily_completion = defaultdict(int)
        for t in completed:
            daily_completion[t['scheduled_date']] += 1
        
        if len(daily_completion) >= 7:
            values = list(daily_completion.values())
            avg = sum(values) / len(values)
            variance = sum((v - avg) ** 2 for v in values) / len(values)
            consistency = max(0, 100 - (math.sqrt(variance) / max(avg, 1) * 50))
            if consistency > 60:
                traits['marathon_runner'] = consistency
        
        # 6. Sprinter (high peak days)
        if daily_completion:
            max_daily = max(daily_completion.values())
            if max_daily >= 8:
                traits['sprinter'] = min(100, max_daily * 10)
        
        # 7. Quick Starter
        first_tasks = []
        daily_tasks = defaultdict(list)
        for t in completed:
            if t['completed_at']:
                daily_tasks[t['scheduled_date']].append(t)
        
        for tasks in daily_tasks.values():
            sorted_tasks = sorted(tasks, key=lambda x: x['completed_at'] or '')
            if sorted_tasks:
                first_tasks.append(sorted_tasks[0])
        
        if first_tasks:
            first_task_before_9 = sum(1 for t in first_tasks 
                                     if datetime.fromisoformat(t['completed_at']).hour < 9)
            quick_start_rate = first_task_before_9 / len(first_tasks) * 100
            if quick_start_rate > 50:
                traits['quick_starter'] = quick_start_rate
        
        # Sort by score and take top 3
        sorted_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)[:3]
        
        primary_traits = []
        for trait_id, score in sorted_traits:
            trait_info = InsightsEngine.DNA_TRAITS.get(trait_id, {})
            primary_traits.append({
                'id': trait_id,
                'name': trait_info.get('name', trait_id),
                'icon': trait_info.get('icon', '🔷'),
                'description': trait_info.get('description', ''),
                'score': round(score, 1)
            })
        
        return {
            'status': 'success',
            'primary_traits': primary_traits,
            'all_traits': {k: round(v, 1) for k, v in sorted(traits.items(), key=lambda x: x[1], reverse=True)},
            'profile_strength': round(sum(traits.values()) / max(len(traits), 1), 1)
        }
    
    @staticmethod
    def _discover_unlocks(raw_data):
        """Discover productivity unlocks (hidden potential)"""
        unlocks = []
        
        completed = [t for t in raw_data if t['status'] == 'completed']
        
        if len(completed) < 5:
            return unlocks
        
        # Unlock 1: Untapped deep work potential
        deep_work = [t for t in completed if t['cognitive_load'] == 'deep_work']
        other_work = [t for t in completed if t['cognitive_load'] != 'deep_work']
        
        if deep_work and other_work:
            deep_work_points = sum(calculate_task_points(t) for t in deep_work) / len(deep_work)
            other_points = sum(calculate_task_points(t) for t in other_work) / len(other_work)
            
            if deep_work_points > other_points * 1.5 and len(deep_work) < len(completed) * 0.3:
                potential_gain = (deep_work_points - other_points) * len(other_work) * 0.2
                unlocks.append({
                    'type': 'deep_work_potential',
                    'icon': '🧠',
                    'title': 'Unlock Deep Work Power',
                    'message': f'Deep work earns {deep_work_points/other_points:.1f}x more points but you only do {len(deep_work)/len(completed)*100:.0f}% deep work.',
                    'potential_gain': f'+{potential_gain:.0f} points/month',
                    'action': 'Shift 20% more tasks to deep work blocks'
                })
        
        # Unlock 2: Morning potential
        completed_with_time = [t for t in completed if t['completed_at']]
        if len(completed_with_time) >= 10:
            morning = [t for t in completed_with_time 
                      if datetime.fromisoformat(t['completed_at']).hour < 10]
            rest = [t for t in completed_with_time 
                   if datetime.fromisoformat(t['completed_at']).hour >= 10]
            
            if morning and rest and len(morning) < len(completed_with_time) * 0.3:
                morning_efficiency = sum(t['time_estimate']/(t['actual_time'] or t['time_estimate']) for t in morning) / len(morning)
                rest_efficiency = sum(t['time_estimate']/(t['actual_time'] or t['time_estimate']) for t in rest) / len(rest)
                
                if morning_efficiency > rest_efficiency * 1.2:
                    unlocks.append({
                        'type': 'morning_potential',
                        'icon': '🌅',
                        'title': 'Morning Momentum Available',
                        'message': f'You\'re {(morning_efficiency/rest_efficiency-1)*100:.0f}% more efficient before 10 AM.',
                        'potential_gain': 'Save 2+ hours/week',
                        'action': 'Start 1 hour earlier on important days'
                    })
        
        return unlocks
    
    @staticmethod
    def _analyze_task_pairings(raw_data):
        """Analyze which task combinations work well together"""
        pairings = []
        
        # Group tasks by day
        daily_tasks = defaultdict(list)
        for t in raw_data:
            if t['status'] == 'completed':
                daily_tasks[t['scheduled_date']].append(t)
        
        # Analyze task sequences
        good_sequences = defaultdict(lambda: {'count': 0, 'success': 0})
        
        for day, tasks in daily_tasks.items():
            if len(tasks) < 2:
                continue
            
            sorted_tasks = sorted(tasks, key=lambda x: x['completed_at'] or '')
            
            for i in range(len(sorted_tasks) - 1):
                current = sorted_tasks[i]['cognitive_load']
                next_task = sorted_tasks[i + 1]['cognitive_load']
                
                if current and next_task:
                    pair = f"{current}→{next_task}"
                    good_sequences[pair]['count'] += 1
                    
                    # Check if both completed successfully (no rollover)
                    if sorted_tasks[i]['rolled_over_count'] == 0 and sorted_tasks[i + 1]['rolled_over_count'] == 0:
                        good_sequences[pair]['success'] += 1
        
        # Find best pairings
        for pair, data in good_sequences.items():
            if data['count'] >= 5:
                success_rate = data['success'] / data['count']
                if success_rate >= 0.8:
                    parts = pair.split('→')
                    pairings.append({
                        'sequence': pair,
                        'first': parts[0].replace('_', ' ').title(),
                        'second': parts[1].replace('_', ' ').title(),
                        'success_rate': round(success_rate * 100, 1),
                        'occurrences': data['count']
                    })
        
        # Sort by success rate
        pairings.sort(key=lambda x: x['success_rate'], reverse=True)
        
        return pairings[:5]  # Top 5 pairings

