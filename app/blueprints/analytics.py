"""
Analytics Blueprint
Advanced analytics endpoints with world-class algorithms
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, date, timedelta
from app.models.database import get_db, calculate_task_points
from app.services.analytics import ProductivityAnalytics
from app.utils.helpers import handle_errors

analytics_bp = Blueprint('analytics', __name__)

# ----- Original Analytics (Maintained) -----

@analytics_bp.route('/daily/<date_str>', methods=['GET'])
@handle_errors
def get_daily_analytics(date_str):
    """Get analytics for a specific day"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_tasks,
            SUM(CASE WHEN dt.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
            SUM(CASE WHEN dt.status = 'pending' THEN 1 ELSE 0 END) as pending_tasks,
            SUM(CASE WHEN dt.status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_tasks,
            SUM(CASE WHEN dt.status = 'abandoned' THEN 1 ELSE 0 END) as abandoned_tasks,
            SUM(t.time_estimate) as total_estimated_time,
            SUM(CASE WHEN dt.status = 'completed' THEN dt.actual_time ELSE 0 END) as total_actual_time,
            SUM(CASE WHEN dt.status = 'completed' THEN t.complexity * 10 ELSE 0 END) as base_points,
            SUM(dt.penalty_points) as total_penalties
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.scheduled_date = ?
    ''', (date_str,))
    
    row = cursor.fetchone()
    
    # Get cognitive load breakdown
    cursor.execute('''
        SELECT 
            t.cognitive_load,
            COUNT(*) as total,
            SUM(CASE WHEN dt.status = 'completed' THEN 1 ELSE 0 END) as completed
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.scheduled_date = ?
        GROUP BY t.cognitive_load
    ''', (date_str,))
    
    cognitive_breakdown = {row['cognitive_load']: {'total': row['total'], 'completed': row['completed']} 
                          for row in cursor.fetchall()}
    
    # Calculate detailed points
    cursor.execute('''
        SELECT dt.*, t.complexity, t.cognitive_load, t.time_estimate
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.scheduled_date = ? AND dt.status = 'completed'
    ''', (date_str,))
    
    total_points = sum(calculate_task_points(dict(t)) for t in cursor.fetchall())
    
    # Get penalty points for incomplete tasks
    cursor.execute('''
        SELECT SUM(penalty_points) as penalties
        FROM daily_tasks
        WHERE scheduled_date = ? AND status != 'completed'
    ''', (date_str,))
    
    penalty_row = cursor.fetchone()
    total_penalties = penalty_row['penalties'] or 0
    
    completion_rate = (row['completed_tasks'] / row['total_tasks'] * 100) if row['total_tasks'] > 0 else 0
    
    return jsonify({
        'date': date_str,
        'total_tasks': row['total_tasks'] or 0,
        'completed_tasks': row['completed_tasks'] or 0,
        'pending_tasks': row['pending_tasks'] or 0,
        'in_progress_tasks': row['in_progress_tasks'] or 0,
        'abandoned_tasks': row['abandoned_tasks'] or 0,
        'completion_rate': round(completion_rate, 1),
        'total_estimated_time': row['total_estimated_time'] or 0,
        'total_actual_time': row['total_actual_time'] or 0,
        'total_points': total_points,
        'total_penalties': total_penalties,
        'net_points': total_points - total_penalties,
        'cognitive_breakdown': cognitive_breakdown
    })

@analytics_bp.route('/trends', methods=['GET'])
@handle_errors
def get_trends():
    """Get productivity trends over time"""
    days = request.args.get('days', 30, type=int)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    db = get_db()
    cursor = db.cursor()
    
    daily_data = {}
    
    # Get detailed breakdown
    cursor.execute('''
        SELECT 
            dt.scheduled_date,
            dt.status,
            dt.penalty_points,
            dt.actual_time,
            t.cognitive_load,
            t.complexity,
            t.time_estimate
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.scheduled_date BETWEEN ? AND ?
        ORDER BY dt.scheduled_date
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    for row in cursor.fetchall():
        d = row['scheduled_date']
        if d not in daily_data:
            daily_data[d] = {
                'date': d,
                'total_tasks': 0,
                'completed_tasks': 0,
                'points': 0,
                'penalties': 0,
                'estimated_time': 0,
                'actual_time': 0,
                'by_cognitive_load': {'deep_work': 0, 'active_work': 0, 'admin': 0, 'learning': 0}
            }
        
        daily_data[d]['total_tasks'] += 1
        daily_data[d]['estimated_time'] += row['time_estimate'] or 0
        
        if row['status'] == 'completed':
            daily_data[d]['completed_tasks'] += 1
            daily_data[d]['points'] += calculate_task_points(dict(row))
            daily_data[d]['actual_time'] += row['actual_time'] or row['time_estimate'] or 0
            if row['cognitive_load']:
                daily_data[d]['by_cognitive_load'][row['cognitive_load']] += 1
        else:
            daily_data[d]['penalties'] += row['penalty_points'] or 0
    
    # Calculate completion rates and net points
    trends = []
    for d in sorted(daily_data.keys()):
        data = daily_data[d]
        data['completion_rate'] = round((data['completed_tasks'] / data['total_tasks'] * 100) if data['total_tasks'] > 0 else 0, 1)
        data['net_points'] = data['points'] - data['penalties']
        trends.append(data)
    
    return jsonify(trends)

@analytics_bp.route('/insights', methods=['GET'])
@handle_errors
def get_insights():
    """Generate smart insights and suggestions"""
    days = request.args.get('days', 14, type=int)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    db = get_db()
    cursor = db.cursor()
    
    insights = []
    
    # 1. Completion rate analysis
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
        FROM daily_tasks
        WHERE scheduled_date BETWEEN ? AND ?
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    row = cursor.fetchone()
    if row['total'] > 0:
        completion_rate = row['completed'] / row['total'] * 100
        if completion_rate < 50:
            insights.append({
                'type': 'warning',
                'category': 'completion_rate',
                'title': 'Low Completion Rate',
                'message': f'Your completion rate is {completion_rate:.0f}%. Consider planning fewer tasks or breaking them into smaller pieces.',
                'metric': completion_rate
            })
        elif completion_rate > 90:
            insights.append({
                'type': 'success',
                'category': 'completion_rate',
                'title': 'Excellent Completion Rate',
                'message': f'You\'re completing {completion_rate:.0f}% of tasks. You might be ready to take on more challenging work.',
                'metric': completion_rate
            })
    
    # 2. Task type patterns
    cursor.execute('''
        SELECT 
            t.cognitive_load,
            COUNT(*) as total,
            SUM(CASE WHEN dt.status = 'completed' THEN 1 ELSE 0 END) as completed,
            AVG(dt.rolled_over_count) as avg_rollover
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.scheduled_date BETWEEN ? AND ?
        GROUP BY t.cognitive_load
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    for row in cursor.fetchall():
        if row['total'] >= 3:
            rate = row['completed'] / row['total'] * 100
            load_name = row['cognitive_load'].replace('_', ' ').title()
            
            if rate < 40:
                insights.append({
                    'type': 'warning',
                    'category': 'task_type',
                    'title': f'{load_name} Tasks Struggling',
                    'message': f'Only {rate:.0f}% of {load_name} tasks completed. Try scheduling these when your energy is highest.',
                    'metric': rate,
                    'cognitive_load': row['cognitive_load']
                })
            elif row['avg_rollover'] and row['avg_rollover'] > 1:
                insights.append({
                    'type': 'info',
                    'category': 'task_type',
                    'title': f'{load_name} Tasks Rolling Over',
                    'message': f'{load_name} tasks roll over {row["avg_rollover"]:.1f} times on average. Consider smaller time estimates.',
                    'metric': row['avg_rollover'],
                    'cognitive_load': row['cognitive_load']
                })
    
    # 3. Time estimation accuracy
    cursor.execute('''
        SELECT 
            t.cognitive_load,
            AVG(t.time_estimate) as avg_estimated,
            AVG(dt.actual_time) as avg_actual
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.scheduled_date BETWEEN ? AND ?
            AND dt.status = 'completed'
            AND dt.actual_time IS NOT NULL
        GROUP BY t.cognitive_load
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    for row in cursor.fetchall():
        if row['avg_estimated'] and row['avg_actual']:
            ratio = row['avg_actual'] / row['avg_estimated']
            load_name = row['cognitive_load'].replace('_', ' ').title()
            
            if ratio > 1.5:
                insights.append({
                    'type': 'warning',
                    'category': 'time_accuracy',
                    'title': f'Underestimating {load_name}',
                    'message': f'{load_name} tasks take {ratio:.1f}x longer than estimated. Add buffer time to future estimates.',
                    'metric': ratio,
                    'cognitive_load': row['cognitive_load']
                })
            elif ratio < 0.7:
                insights.append({
                    'type': 'info',
                    'category': 'time_accuracy',
                    'title': f'Overestimating {load_name}',
                    'message': f'{load_name} tasks complete {((1-ratio)*100):.0f}% faster than estimated. You can plan more ambitiously.',
                    'metric': ratio,
                    'cognitive_load': row['cognitive_load']
                })
    
    # Sort insights
    type_order = {'warning': 0, 'info': 1, 'success': 2}
    insights.sort(key=lambda x: type_order.get(x['type'], 3))
    
    return jsonify(insights)

@analytics_bp.route('/summary', methods=['GET'])
@handle_errors
def get_summary():
    """Get overall productivity summary"""
    days = request.args.get('days', 30, type=int)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_tasks,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
            SUM(CASE WHEN status = 'abandoned' THEN 1 ELSE 0 END) as abandoned_tasks,
            SUM(penalty_points) as total_penalties,
            COUNT(DISTINCT scheduled_date) as active_days
        FROM daily_tasks
        WHERE scheduled_date BETWEEN ? AND ?
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    row = cursor.fetchone()
    
    # Calculate total points earned
    cursor.execute('''
        SELECT dt.*, t.complexity, t.cognitive_load, t.time_estimate
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.scheduled_date BETWEEN ? AND ?
            AND dt.status = 'completed'
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    total_points = sum(calculate_task_points(dict(t)) for t in cursor.fetchall())
    
    # Current streak
    cursor.execute('''
        SELECT scheduled_date
        FROM daily_tasks
        WHERE status = 'completed'
        GROUP BY scheduled_date
        ORDER BY scheduled_date DESC
    ''')
    
    streak = 0
    check_date = date.today()
    completed_dates = {row['scheduled_date'] for row in cursor.fetchall()}
    
    while check_date.isoformat() in completed_dates or (check_date == date.today() and streak == 0):
        if check_date.isoformat() in completed_dates:
            streak += 1
        check_date -= timedelta(days=1)
        if streak == 0 and check_date < date.today() - timedelta(days=1):
            break
    
    completion_rate = (row['completed_tasks'] / row['total_tasks'] * 100) if row['total_tasks'] > 0 else 0
    
    return jsonify({
        'period_days': days,
        'active_days': row['active_days'] or 0,
        'total_tasks': row['total_tasks'] or 0,
        'completed_tasks': row['completed_tasks'] or 0,
        'abandoned_tasks': row['abandoned_tasks'] or 0,
        'completion_rate': round(completion_rate, 1),
        'total_points': total_points,
        'total_penalties': row['total_penalties'] or 0,
        'net_points': total_points - (row['total_penalties'] or 0),
        'current_streak': streak,
        'avg_tasks_per_day': round((row['total_tasks'] or 0) / max(row['active_days'] or 1, 1), 1)
    })

# ----- NEW ADVANCED ANALYTICS -----

@analytics_bp.route('/productivity-score/<date_str>', methods=['GET'])
@handle_errors
def get_productivity_score(date_str):
    """Get comprehensive productivity score (0-100)"""
    window_days = request.args.get('window', 7, type=int)
    score = ProductivityAnalytics.calculate_productivity_score(date_str, window_days)
    
    # Get rating
    if score >= 90:
        rating = 'Exceptional'
        color = 'green'
    elif score >= 75:
        rating = 'Great'
        color = 'blue'
    elif score >= 60:
        rating = 'Good'
        color = 'yellow'
    elif score >= 40:
        rating = 'Fair'
        color = 'orange'
    else:
        rating = 'Needs Improvement'
        color = 'red'
    
    return jsonify({
        'score': score,
        'rating': rating,
        'color': color,
        'window_days': window_days
    })

@analytics_bp.route('/optimal-time/<cognitive_load>', methods=['GET'])
@handle_errors
def get_optimal_time(cognitive_load):
    """Get optimal time for task type"""
    historical_days = request.args.get('days', 30, type=int)
    result = ProductivityAnalytics.find_optimal_task_time(cognitive_load, historical_days)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({
            'optimal_hours': [],
            'confidence': 0,
            'sample_size': 0,
            'message': 'Not enough data yet. Complete more tasks to get recommendations.'
        })

@analytics_bp.route('/predict-completion', methods=['POST'])
@handle_errors
def predict_completion():
    """Predict task completion probability"""
    data = request.json
    date_str = data.get('date', date.today().isoformat())
    
    probability = ProductivityAnalytics.predict_task_completion_probability(data, date_str)
    
    # Get recommendation
    if probability >= 0.8:
        recommendation = 'High chance of success! Go for it!'
        level = 'high'
    elif probability >= 0.6:
        recommendation = 'Good chance. Stay focused!'
        level = 'medium'
    elif probability >= 0.4:
        recommendation = 'Moderate risk. Break it down or schedule wisely.'
        level = 'medium-low'
    else:
        recommendation = 'Consider breaking this into smaller tasks or rescheduling.'
        level = 'low'
    
    return jsonify({
        'probability': round(probability, 2),
        'percentage': round(probability * 100, 1),
        'recommendation': recommendation,
        'level': level
    })

@analytics_bp.route('/cognitive-balance/<date_str>', methods=['GET'])
@handle_errors
def get_cognitive_balance(date_str):
    """Check cognitive load balance for a day"""
    result = ProductivityAnalytics.calculate_cognitive_load_balance(date_str)
    return jsonify(result)

@analytics_bp.route('/patterns', methods=['GET'])
@handle_errors
def get_patterns():
    """Detect productivity patterns"""
    days = request.args.get('days', 30, type=int)
    patterns = ProductivityAnalytics.detect_productivity_patterns(days)
    return jsonify(patterns)

