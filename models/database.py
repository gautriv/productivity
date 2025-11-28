"""
Database models and operations
Centralized database management
"""
import sqlite3
from flask import current_app, g

def get_db():
    """Get database connection with row factory"""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with schema"""
    db = get_db()
    cursor = db.cursor()
    
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
            display_order INTEGER DEFAULT 0,
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
    
    # Achievements table - for gamification
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            type TEXT CHECK(type IN ('streak', 'points', 'tasks', 'special')),
            requirement INTEGER,
            unlocked_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User stats for motivation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_date DATE UNIQUE NOT NULL,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            total_points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0,
            achievements_unlocked INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Task predictions for ML features
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            predicted_completion_time REAL,
            predicted_success_rate REAL,
            optimal_time_of_day TEXT,
            difficulty_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')
    
    db.commit()

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

def migrate_add_display_order():
    """Add display_order column to existing daily_tasks if it doesn't exist"""
    db = get_db()
    cursor = db.cursor()

    # Check if column exists
    cursor.execute("PRAGMA table_info(daily_tasks)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'display_order' not in columns:
        print("Adding display_order column to daily_tasks...")
        cursor.execute('ALTER TABLE daily_tasks ADD COLUMN display_order INTEGER DEFAULT 0')

        # Set initial display_order for existing tasks based on current order
        cursor.execute('''
            SELECT id, scheduled_date
            FROM daily_tasks
            ORDER BY scheduled_date,
                CASE status
                    WHEN 'in_progress' THEN 1
                    WHEN 'pending' THEN 2
                    WHEN 'completed' THEN 3
                    WHEN 'abandoned' THEN 4
                END, id
        ''')

        tasks = cursor.fetchall()
        current_date = None
        order = 0

        for task in tasks:
            if task[1] != current_date:
                current_date = task[1]
                order = 0

            cursor.execute('UPDATE daily_tasks SET display_order = ? WHERE id = ?', (order, task[0]))
            order += 1

        db.commit()
        print("Migration completed successfully!")

