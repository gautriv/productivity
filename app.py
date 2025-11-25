"""
Productivity Tracker - Main Application
A local productivity tracking system with SQLite database
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime, date, timedelta
import sqlite3
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

DATABASE = 'productivity.db'

def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Tasks table - master list of all tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            complexity INTEGER DEFAULT 1 CHECK(complexity >= 1 AND complexity <= 5),
            cognitive_load TEXT CHECK(cognitive_load IN ('deep_work', 'active_work', 'admin', 'learning')),
            time_estimate INTEGER DEFAULT 30,
            parent_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            archived BOOLEAN DEFAULT 0,
            FOREIGN KEY (parent_id) REFERENCES tasks(id)
        )
    ''')
    
    # Daily tasks - tasks assigned to specific days
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            scheduled_date DATE NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'abandoned')),
            rolled_over_count INTEGER DEFAULT 0,
            penalty_points INTEGER DEFAULT 0,
            actual_time INTEGER,
            completed_at TIMESTAMP,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            UNIQUE(task_id, scheduled_date)
        )
    ''')
    
    # Daily summaries for quick lookups
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_date DATE UNIQUE NOT NULL,
            total_tasks INTEGER DEFAULT 0,
            completed_tasks INTEGER DEFAULT 0,
            total_points_earned INTEGER DEFAULT 0,
            total_penalty_points INTEGER DEFAULT 0,
            total_estimated_time INTEGER DEFAULT 0,
            total_actual_time INTEGER DEFAULT 0,
            deep_work_completed INTEGER DEFAULT 0,
            active_work_completed INTEGER DEFAULT 0,
            admin_completed INTEGER DEFAULT 0,
            learning_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def calculate_task_points(task):
    """Calculate points for a task based on complexity, cognitive load, and time"""
    base_points = task['complexity'] * 10
    
    # Cognitive load multiplier
    load_multipliers = {
        'deep_work': 2.0,
        'learning': 1.5,
        'active_work': 1.2,
        'admin': 1.0
    }
    multiplier = load_multipliers.get(task['cognitive_load'], 1.0)
    
    # Time bonus (every 30 min adds 5 points)
    time_bonus = (task['time_estimate'] // 30) * 5
    
    return int((base_points + time_bonus) * multiplier)

def calculate_penalty(rolled_over_count):
    """Calculate cumulative penalty for rolled over tasks"""
    return rolled_over_count * 2

# ============== API ROUTES ==============

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

# ----- Task Management -----

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all non-archived tasks"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, 
               (SELECT COUNT(*) FROM tasks st WHERE st.parent_id = t.id) as subtask_count,
               (SELECT COUNT(*) FROM tasks st 
                JOIN daily_tasks dt ON st.id = dt.task_id 
                WHERE st.parent_id = t.id AND dt.status = 'completed') as subtasks_completed
        FROM tasks t 
        WHERE t.archived = 0 AND t.parent_id IS NULL
        ORDER BY t.created_at DESC
    ''')
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tasks (title, description, complexity, cognitive_load, time_estimate, parent_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['title'],
        data.get('description', ''),
        data.get('complexity', 3),
        data.get('cognitive_load', 'active_work'),
        data.get('time_estimate', 30),
        data.get('parent_id')
    ))
    
    task_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = dict(cursor.fetchone())
    conn.close()
    
    return jsonify(task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE tasks 
        SET title = ?, description = ?, complexity = ?, cognitive_load = ?, time_estimate = ?
        WHERE id = ?
    ''', (
        data['title'],
        data.get('description', ''),
        data.get('complexity', 3),
        data.get('cognitive_load', 'active_work'),
        data.get('time_estimate', 30),
        task_id
    ))
    
    conn.commit()
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = dict(cursor.fetchone())
    conn.close()
    
    return jsonify(task)

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Archive a task (soft delete)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET archived = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/tasks/<int:task_id>/subtasks', methods=['GET'])
def get_subtasks(task_id):
    """Get subtasks for a task"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE parent_id = ? AND archived = 0', (task_id,))
    subtasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(subtasks)

# ----- Daily Task Management -----

@app.route('/api/daily/<date_str>', methods=['GET'])
def get_daily_tasks(date_str):
    """Get all tasks for a specific day"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT dt.*, t.title, t.description, t.complexity, t.cognitive_load, t.time_estimate,
               (SELECT COUNT(*) FROM tasks st WHERE st.parent_id = t.id) as subtask_count
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.scheduled_date = ?
        ORDER BY 
            CASE dt.status 
                WHEN 'in_progress' THEN 1 
                WHEN 'pending' THEN 2 
                WHEN 'completed' THEN 3 
                WHEN 'abandoned' THEN 4 
            END,
            t.complexity DESC
    ''', (date_str,))
    
    tasks = [dict(row) for row in cursor.fetchall()]
    
    # Calculate points for each task
    for task in tasks:
        task['points'] = calculate_task_points(task)
        task['net_points'] = task['points'] - task['penalty_points'] if task['status'] == 'completed' else -task['penalty_points']
    
    conn.close()
    return jsonify(tasks)

@app.route('/api/daily/<date_str>/add', methods=['POST'])
def add_task_to_day(date_str):
    """Add a task to a specific day"""
    data = request.json
    task_id = data['task_id']
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if task already exists for this day
    cursor.execute('SELECT id FROM daily_tasks WHERE task_id = ? AND scheduled_date = ?', (task_id, date_str))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Task already scheduled for this day'}), 400
    
    cursor.execute('''
        INSERT INTO daily_tasks (task_id, scheduled_date, rolled_over_count, penalty_points)
        VALUES (?, ?, ?, ?)
    ''', (task_id, date_str, data.get('rolled_over_count', 0), data.get('penalty_points', 0)))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201

@app.route('/api/daily/<date_str>/quick-add', methods=['POST'])
def quick_add_task(date_str):
    """Create a new task and add it to the day in one step"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    # Create the task
    cursor.execute('''
        INSERT INTO tasks (title, description, complexity, cognitive_load, time_estimate)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['title'],
        data.get('description', ''),
        data.get('complexity', 3),
        data.get('cognitive_load', 'active_work'),
        data.get('time_estimate', 30)
    ))
    
    task_id = cursor.lastrowid
    
    # Add to daily tasks
    cursor.execute('''
        INSERT INTO daily_tasks (task_id, scheduled_date)
        VALUES (?, ?)
    ''', (task_id, date_str))
    
    conn.commit()
    
    # Return the full task info
    cursor.execute('''
        SELECT dt.*, t.title, t.description, t.complexity, t.cognitive_load, t.time_estimate
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.id = last_insert_rowid()
    ''')
    task = dict(cursor.fetchone())
    task['points'] = calculate_task_points(task)
    
    conn.close()
    return jsonify(task), 201

@app.route('/api/daily/task/<int:daily_task_id>/status', methods=['PUT'])
def update_task_status(daily_task_id):
    """Update the status of a daily task"""
    data = request.json
    new_status = data['status']
    
    conn = get_db()
    cursor = conn.cursor()
    
    completed_at = datetime.now().isoformat() if new_status == 'completed' else None
    actual_time = data.get('actual_time')
    
    cursor.execute('''
        UPDATE daily_tasks 
        SET status = ?, completed_at = ?, actual_time = ?
        WHERE id = ?
    ''', (new_status, completed_at, actual_time, daily_task_id))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/daily/task/<int:daily_task_id>', methods=['DELETE'])
def remove_daily_task(daily_task_id):
    """Remove a task from a day (doesn't delete the task itself)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM daily_tasks WHERE id = ?', (daily_task_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ----- Rollover System -----

@app.route('/api/rollover', methods=['POST'])
def process_rollover():
    """Process end-of-day rollover for incomplete tasks"""
    data = request.json
    from_date = data.get('from_date', (date.today() - timedelta(days=1)).isoformat())
    to_date = data.get('to_date', date.today().isoformat())
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get incomplete tasks from the previous day
    cursor.execute('''
        SELECT dt.*, t.title, t.complexity, t.cognitive_load, t.time_estimate
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.scheduled_date = ? AND dt.status IN ('pending', 'in_progress')
    ''', (from_date,))
    
    incomplete_tasks = cursor.fetchall()
    rolled_over = []
    
    for task in incomplete_tasks:
        new_rolled_count = task['rolled_over_count'] + 1
        new_penalty = calculate_penalty(new_rolled_count)
        
        # Check if already exists in target date
        cursor.execute('SELECT id FROM daily_tasks WHERE task_id = ? AND scheduled_date = ?', 
                      (task['task_id'], to_date))
        
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO daily_tasks (task_id, scheduled_date, rolled_over_count, penalty_points, status)
                VALUES (?, ?, ?, ?, 'pending')
            ''', (task['task_id'], to_date, new_rolled_count, new_penalty))
            
            rolled_over.append({
                'task_id': task['task_id'],
                'title': task['title'],
                'rolled_over_count': new_rolled_count,
                'penalty_points': new_penalty
            })
        
        # Mark original as abandoned
        cursor.execute('''
            UPDATE daily_tasks SET status = 'abandoned' WHERE id = ?
        ''', (task['id'],))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'rolled_over_count': len(rolled_over),
        'tasks': rolled_over
    })

# ----- Analytics & Insights -----

@app.route('/api/analytics/daily/<date_str>', methods=['GET'])
def get_daily_analytics(date_str):
    """Get analytics for a specific day"""
    conn = get_db()
    cursor = conn.cursor()
    
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
    
    conn.close()
    
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

@app.route('/api/analytics/trends', methods=['GET'])
def get_trends():
    """Get productivity trends over time"""
    days = request.args.get('days', 30, type=int)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            dt.scheduled_date,
            COUNT(*) as total_tasks,
            SUM(CASE WHEN dt.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
            SUM(dt.penalty_points) as penalties,
            t.cognitive_load,
            t.complexity,
            t.time_estimate,
            dt.actual_time,
            dt.status
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.scheduled_date BETWEEN ? AND ?
        GROUP BY dt.scheduled_date
        ORDER BY dt.scheduled_date
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    daily_data = {}
    
    # Re-query for detailed breakdown
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
    
    conn.close()
    return jsonify(trends)

@app.route('/api/analytics/insights', methods=['GET'])
def get_insights():
    """Generate smart insights and suggestions"""
    days = request.args.get('days', 14, type=int)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    conn = get_db()
    cursor = conn.cursor()
    
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
    
    # 4. Day of week patterns
    cursor.execute('''
        SELECT 
            strftime('%w', scheduled_date) as day_of_week,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
        FROM daily_tasks
        WHERE scheduled_date BETWEEN ? AND ?
        GROUP BY strftime('%w', scheduled_date)
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_rates = []
    
    for row in cursor.fetchall():
        if row['total'] >= 2:
            rate = row['completed'] / row['total'] * 100
            day_rates.append((int(row['day_of_week']), rate, row['total']))
    
    if day_rates:
        best_day = max(day_rates, key=lambda x: x[1])
        worst_day = min(day_rates, key=lambda x: x[1])
        
        if best_day[1] - worst_day[1] > 20:
            insights.append({
                'type': 'info',
                'category': 'energy_patterns',
                'title': 'Weekly Energy Pattern Detected',
                'message': f'{day_names[best_day[0]]}s are your best ({best_day[1]:.0f}% completion). {day_names[worst_day[0]]}s are hardest ({worst_day[1]:.0f}%). Plan accordingly.',
                'metric': best_day[1] - worst_day[1],
                'best_day': day_names[best_day[0]],
                'worst_day': day_names[worst_day[0]]
            })
    
    # 5. Penalty accumulation
    cursor.execute('''
        SELECT SUM(penalty_points) as total_penalties
        FROM daily_tasks
        WHERE scheduled_date BETWEEN ? AND ?
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    row = cursor.fetchone()
    if row['total_penalties'] and row['total_penalties'] > 50:
        insights.append({
            'type': 'warning',
            'category': 'penalties',
            'title': 'High Penalty Accumulation',
            'message': f'You\'ve accumulated {row["total_penalties"]} penalty points from rollovers. Focus on completing or abandoning stale tasks.',
            'metric': row['total_penalties']
        })
    
    conn.close()
    
    # Sort insights: warnings first, then info, then success
    type_order = {'warning': 0, 'info': 1, 'success': 2}
    insights.sort(key=lambda x: type_order.get(x['type'], 3))
    
    return jsonify(insights)

@app.route('/api/analytics/summary', methods=['GET'])
def get_summary():
    """Get overall productivity summary"""
    days = request.args.get('days', 30, type=int)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    conn = get_db()
    cursor = conn.cursor()
    
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
    
    conn.close()
    
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

if __name__ == '__main__':
    init_db()
    print("\n🚀 Productivity Tracker is running!")
    print("📊 Open http://localhost:5000 in your browser")
    print("💾 Database: productivity.db\n")
    app.run(debug=True, port=5000)
