"""
API Blueprint
Task management endpoints - maintains all existing features
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, date, timedelta
from models.database import get_db, calculate_task_points, calculate_penalty
from utils.helpers import handle_errors, validate_task_data

api_bp = Blueprint('api', __name__)

# ----- Task Management -----

@api_bp.route('/tasks', methods=['GET'])
@handle_errors
def get_tasks():
    """Get all non-archived tasks"""
    db = get_db()
    cursor = db.cursor()
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
    return jsonify(tasks)

@api_bp.route('/tasks', methods=['POST'])
@handle_errors
def create_task():
    """Create a new task"""
    data = request.json
    
    # Validate data
    errors = validate_task_data(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    db = get_db()
    cursor = db.cursor()
    
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
    db.commit()
    
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = dict(cursor.fetchone())
    
    return jsonify(task), 201

@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@handle_errors
def update_task(task_id):
    """Update a task"""
    data = request.json
    
    # Validate data
    errors = validate_task_data(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    db = get_db()
    cursor = db.cursor()
    
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
    
    db.commit()
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = dict(cursor.fetchone())
    
    return jsonify(task)

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@handle_errors
def delete_task(task_id):
    """Archive a task (soft delete)"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE tasks SET archived = 1 WHERE id = ?', (task_id,))
    db.commit()
    return jsonify({'success': True})

@api_bp.route('/tasks/<int:task_id>/subtasks', methods=['GET'])
@handle_errors
def get_subtasks(task_id):
    """Get subtasks for a task"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM tasks WHERE parent_id = ? AND archived = 0', (task_id,))
    subtasks = [dict(row) for row in cursor.fetchall()]
    return jsonify(subtasks)

# ----- Daily Task Management -----

@api_bp.route('/daily/<date_str>', methods=['GET'])
@handle_errors
def get_daily_tasks(date_str):
    """Get all tasks for a specific day"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT dt.*, t.title, t.description, t.complexity, t.cognitive_load, t.time_estimate,
               t.parent_id,
               (SELECT COUNT(*) FROM tasks st
                JOIN daily_tasks dt_sub ON st.id = dt_sub.task_id
                WHERE st.parent_id = t.id AND dt_sub.scheduled_date = dt.scheduled_date) as subtask_count,
               (SELECT dt2.id FROM daily_tasks dt2
                JOIN tasks t2 ON dt2.task_id = t2.id
                WHERE t2.id = t.parent_id AND dt2.scheduled_date = dt.scheduled_date) as parent_daily_task_id
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.scheduled_date = ?
        ORDER BY dt.display_order ASC, dt.id ASC
    ''', (date_str,))
    
    tasks = [dict(row) for row in cursor.fetchall()]
    
    # Calculate points for each task
    for task in tasks:
        task['points'] = calculate_task_points(task)
        task['net_points'] = task['points'] - task['penalty_points'] if task['status'] == 'completed' else -task['penalty_points']
        task['is_subtask'] = task['parent_id'] is not None
    
    return jsonify(tasks)

@api_bp.route('/daily/<date_str>/add', methods=['POST'])
@handle_errors
def add_task_to_day(date_str):
    """Add a task to a specific day"""
    data = request.json
    task_id = data['task_id']
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if task already exists for this day
    cursor.execute('SELECT id FROM daily_tasks WHERE task_id = ? AND scheduled_date = ?', (task_id, date_str))
    if cursor.fetchone():
        return jsonify({'error': 'Task already scheduled for this day'}), 400
    
    cursor.execute('''
        INSERT INTO daily_tasks (task_id, scheduled_date, rolled_over_count, penalty_points)
        VALUES (?, ?, ?, ?)
    ''', (task_id, date_str, data.get('rolled_over_count', 0), data.get('penalty_points', 0)))
    
    db.commit()
    return jsonify({'success': True}), 201

@api_bp.route('/daily/<date_str>/quick-add', methods=['POST'])
@handle_errors
def quick_add_task(date_str):
    """Create a new task and add it to the day in one step"""
    data = request.json
    
    # Validate data
    errors = validate_task_data(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    db = get_db()
    cursor = db.cursor()
    
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

    # Get the max display_order for this date
    cursor.execute('''
        SELECT COALESCE(MAX(display_order), -1) + 1 as next_order
        FROM daily_tasks
        WHERE scheduled_date = ?
    ''', (date_str,))
    next_order = cursor.fetchone()[0]

    # Add to daily tasks
    cursor.execute('''
        INSERT INTO daily_tasks (task_id, scheduled_date, display_order)
        VALUES (?, ?, ?)
    ''', (task_id, date_str, next_order))
    
    db.commit()
    
    # Return the full task info
    cursor.execute('''
        SELECT dt.*, t.title, t.description, t.complexity, t.cognitive_load, t.time_estimate
        FROM daily_tasks dt
        JOIN tasks t ON dt.task_id = t.id
        WHERE dt.id = last_insert_rowid()
    ''')
    task = dict(cursor.fetchone())
    task['points'] = calculate_task_points(task)
    
    return jsonify(task), 201

@api_bp.route('/daily/task/<int:daily_task_id>/status', methods=['PUT'])
@handle_errors
def update_task_status(daily_task_id):
    """Update the status of a daily task"""
    data = request.json
    new_status = data['status']
    
    db = get_db()
    cursor = db.cursor()
    
    completed_at = datetime.now().isoformat() if new_status == 'completed' else None
    actual_time = data.get('actual_time')
    
    cursor.execute('''
        UPDATE daily_tasks 
        SET status = ?, completed_at = ?, actual_time = ?
        WHERE id = ?
    ''', (new_status, completed_at, actual_time, daily_task_id))
    
    db.commit()
    return jsonify({'success': True})

@api_bp.route('/daily/task/<int:daily_task_id>', methods=['DELETE'])
@handle_errors
def remove_daily_task(daily_task_id):
    """Remove a task from a day (doesn't delete the task itself)"""
    db = get_db()
    cursor = db.cursor()
    
    # Get the task_id before deleting
    cursor.execute('SELECT task_id FROM daily_tasks WHERE id = ?', (daily_task_id,))
    daily_task = cursor.fetchone()
    
    if daily_task:
        task_id = daily_task['task_id']
        
        # Convert any subtasks of this task to main tasks
        cursor.execute('UPDATE tasks SET parent_id = NULL WHERE parent_id = ?', (task_id,))
    
    # Delete the daily task
    cursor.execute('DELETE FROM daily_tasks WHERE id = ?', (daily_task_id,))
    db.commit()
    return jsonify({'success': True})

# ----- Rollover System -----

@api_bp.route('/rollover', methods=['POST'])
@handle_errors
def process_rollover():
    """Process end-of-day rollover for incomplete tasks"""
    data = request.json
    from_date = data.get('from_date', (date.today() - timedelta(days=1)).isoformat())
    to_date = data.get('to_date', date.today().isoformat())
    
    db = get_db()
    cursor = db.cursor()
    
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
    
    db.commit()
    
    return jsonify({
        'rolled_over_count': len(rolled_over),
        'tasks': rolled_over
    })

# ----- Task Reordering -----

@api_bp.route('/daily/<date_str>/reorder', methods=['PUT'])
@handle_errors
def reorder_tasks(date_str):
    """Reorder tasks for a specific day"""
    data = request.json
    task_orders = data.get('task_orders', [])

    if not task_orders:
        return jsonify({'error': 'No task orders provided'}), 400

    db = get_db()
    cursor = db.cursor()

    # Update display_order for each task
    for item in task_orders:
        task_id = item['id']
        new_order = item['order']

        cursor.execute('''
            UPDATE daily_tasks
            SET display_order = ?
            WHERE id = ? AND scheduled_date = ?
        ''', (new_order, task_id, date_str))

    db.commit()

    return jsonify({'success': True, 'updated_count': len(task_orders)})

# ----- Task Hierarchy (Subtask Conversion) -----

@api_bp.route('/daily/task/<int:daily_task_id>/set-parent', methods=['PUT'])
@handle_errors
def set_task_parent(daily_task_id):
    """Set or remove parent for a daily task"""
    data = request.json
    parent_daily_task_id = data.get('parent_daily_task_id')
    
    db = get_db()
    cursor = db.cursor()
    
    # Get the actual task_id for this daily task
    cursor.execute('SELECT task_id FROM daily_tasks WHERE id = ?', (daily_task_id,))
    daily_task = cursor.fetchone()
    if not daily_task:
        return jsonify({'error': 'Daily task not found'}), 404
    
    task_id = daily_task['task_id']
    
    if parent_daily_task_id is None:
        # Remove parent - convert to main task
        cursor.execute('UPDATE tasks SET parent_id = NULL WHERE id = ?', (task_id,))
        db.commit()
        return jsonify({'success': True, 'task_id': task_id, 'parent_id': None})
    
    # Get the actual task_id for the parent daily task
    cursor.execute('SELECT task_id FROM daily_tasks WHERE id = ?', (parent_daily_task_id,))
    parent_daily_task = cursor.fetchone()
    if not parent_daily_task:
        return jsonify({'error': 'Parent daily task not found'}), 404
    
    parent_task_id = parent_daily_task['task_id']
    
    # Prevent circular reference
    if parent_task_id == task_id:
        return jsonify({'error': 'A task cannot be its own parent'}), 400
    
    # Verify parent is not itself a subtask (only allow 1 level of nesting)
    cursor.execute('SELECT parent_id FROM tasks WHERE id = ?', (parent_task_id,))
    parent_task = cursor.fetchone()
    if parent_task and parent_task['parent_id'] is not None:
        return jsonify({'error': 'Cannot nest subtasks more than one level deep'}), 400
    
    # Check if the task being converted has subtasks
    cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE parent_id = ?', (task_id,))
    subtask_count = cursor.fetchone()['count']
    if subtask_count > 0:
        return jsonify({'error': 'Cannot make a task with subtasks into a subtask'}), 400
    
    # Update the task to be a subtask
    cursor.execute('UPDATE tasks SET parent_id = ? WHERE id = ?', (parent_task_id, task_id))
    db.commit()
    
    return jsonify({'success': True, 'task_id': task_id, 'parent_id': parent_task_id})

