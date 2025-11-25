# Productivity Tracker

A local productivity tracking system with SQLite database, designed to help you track task complexity, cognitive load, time estimates, and productivity trends.

## Features

- **Daily Task Management**: Add, complete, and organize tasks for each day
- **Complexity Scoring**: Rate tasks 1-5 based on difficulty
- **Cognitive Load Categories**: 
  - 🧠 Deep Work - Focus-intensive tasks
  - ⚡ Active Work - Meetings, calls, routine tasks
  - 🔄 Admin - Emails, scheduling
  - 📚 Learning - Self-development
- **Time Estimates**: 15m, 30m, 1h, 2h, 4h, 8h options
- **Point System**: Earn points based on complexity, cognitive load, and time
- **Rollover with Penalties**: Incomplete tasks roll to next day with cumulative penalties (-2, -4, -6...)
- **Analytics Dashboard**:
  - Daily stats
  - 14-day trends
  - Smart insights based on patterns
- **Suggestions Engine**:
  - Completion rate analysis
  - Task type patterns
  - Time estimation accuracy
  - Day-of-week energy patterns

## Setup

### Requirements
- Python 3.8+
- pip

### Installation

1. Navigate to the project directory:
```bash
cd productivity-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser to:
```
http://localhost:5000
```

## Database

The SQLite database (`productivity.db`) is created automatically in the project directory. You can:
- Query it directly with any SQLite tool
- Back it up by copying the file
- Reset by deleting the file (a new one will be created on next run)

### Database Schema

**tasks** - Master list of all tasks
- id, title, description, complexity (1-5), cognitive_load, time_estimate, parent_id, created_at, archived

**daily_tasks** - Tasks assigned to specific days
- id, task_id, scheduled_date, status, rolled_over_count, penalty_points, actual_time, completed_at, notes

**daily_summaries** - Cached daily statistics (auto-generated)

## Point Calculation

Points are calculated as:
```
base_points = complexity × 10
time_bonus = (time_estimate / 30) × 5
multiplier = cognitive_load_multiplier (deep_work: 2.0, learning: 1.5, active_work: 1.2, admin: 1.0)

total_points = (base_points + time_bonus) × multiplier
```

## Rollover Penalties

When a task isn't completed:
- Day 1 incomplete → rolls to Day 2 with **-2 points**
- Day 2 still incomplete → rolls to Day 3 with **-4 points** (cumulative)
- Day 3 still incomplete → **-6 points**
- And so on...

Click "Process Rollover" in the sidebar to manually trigger this (useful at end of day).

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks` | GET | Get all tasks |
| `/api/tasks` | POST | Create new task |
| `/api/daily/<date>` | GET | Get tasks for a day |
| `/api/daily/<date>/quick-add` | POST | Create and add task to day |
| `/api/daily/task/<id>/status` | PUT | Update task status |
| `/api/rollover` | POST | Process end-of-day rollover |
| `/api/analytics/daily/<date>` | GET | Get daily analytics |
| `/api/analytics/trends` | GET | Get trend data |
| `/api/analytics/insights` | GET | Get smart suggestions |
| `/api/analytics/summary` | GET | Get overall summary |

## Tech Stack

- **Backend**: Python, Flask, SQLite
- **Frontend**: React 18, Chart.js
- **Fonts**: JetBrains Mono, Space Grotesk

## License

MIT

A powerful local to-do list application that tracks productivity through complexity-weighted points, cognitive load categorization, and intelligent suggestions based on your patterns.

## Features

### Task Management
- **Complexity Scoring (1-5)**: Rate task difficulty
- **Cognitive Load Categories**:
  - 🧠 Deep Work - Focused, high-value tasks
  - ⚡ Active Work - Meetings, calls, routine tasks
  - 🔄 Admin - Emails, scheduling, quick items
  - 📚 Learning - Self-development activities
- **Time Estimates**: Track estimated vs actual time
- **Subtasks**: Break down complex tasks

### Points System
Points are calculated based on:
- Base: `complexity_score × 10`
- Cognitive multiplier: Deep Work (2x), Active Work (1.5x), Learning (1.3x), Admin (1x)
- Time bonus: +1 point per 30 minutes estimated
- Subtask bonus: +5 for parent tasks with subtasks

### Rollover Penalties (Cumulative)
- Day 1 incomplete: -2 points
- Day 2 incomplete: -4 points
- Day 3 incomplete: -6 points
- And so on...

### Intelligent Suggestions
Analyzes your data to provide actionable insights:
- **Completion Rate**: Are you overplanning or crushing it?
- **Task Type Patterns**: Are you avoiding deep work?
- **Time Accuracy**: Do you underestimate certain task types?
- **Energy Patterns**: Which days are you most productive?
- **Rollover Patterns**: Are you accumulating penalties?

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pydantic --break-system-packages
```

### 2. Start the Server

```bash
cd productivity-tracker
chmod +x start.sh
./start.sh
```

Or manually:
```bash
cd backend
python main.py
```

### 3. Open the App

- **Frontend**: http://localhost:8000/app
- **API Docs**: http://localhost:8000/docs

## Database

SQLite database is stored at: `~/productivity_tracker.db`

You can query it directly:
```bash
sqlite3 ~/productivity_tracker.db
```

### Tables
- `tasks` - All tasks with complexity, points, status
- `daily_logs` - Aggregated daily statistics
- `suggestions` - History of generated suggestions

## API Endpoints

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks` | Create a task |
| GET | `/api/tasks/date/{date}` | Get tasks for date |
| POST | `/api/tasks/{id}/complete` | Complete a task |
| POST | `/api/tasks/{id}/abandon` | Abandon a task |
| DELETE | `/api/tasks/{id}` | Delete a task |
| POST | `/api/tasks/rollover` | Roll over pending tasks |

### Statistics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/daily/{date}` | Daily stats |
| GET | `/api/weekly/{date}` | Weekly summary |
| GET | `/api/suggestions` | Get AI suggestions |
| GET | `/api/today` | Full today overview |

### Example API Usage

```bash
# Create a task
curl -X POST "http://localhost:8000/api/tasks?target_date=2024-01-15" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Write blog post",
    "complexity_score": 4,
    "cognitive_load": "deep_work",
    "estimated_minutes": 120
  }'

# Complete a task
curl -X POST "http://localhost:8000/api/tasks/1/complete" \
  -H "Content-Type: application/json" \
  -d '{"actual_minutes": 90}'

# Get suggestions
curl "http://localhost:8000/api/suggestions"
```

## File Structure

```
productivity-tracker/
├── backend/
│   ├── database.py      # SQLite models & business logic
│   ├── main.py          # FastAPI application
│   └── requirements.txt # Python dependencies
├── frontend/
│   └── index.html       # React single-page app
├── start.sh             # Startup script
└── README.md            # This file
```

## Tips for Best Results

1. **Start small**: Add 3-4 tasks per day initially
2. **Be honest**: Rate complexity accurately
3. **Track time**: Note actual minutes to improve estimates
4. **Check suggestions**: Review weekly for patterns
5. **Don't abandon easily**: Penalties hurt, but completing builds momentum

## Customization

### Change Database Location
Edit `backend/database.py`:
```python
DB_PATH = Path("/your/preferred/path/productivity.db")
```

### Adjust Point Calculations
Edit `backend/database.py`:
```python
cognitive_multipliers = {
    'deep_work': 2.5,    # Increase deep work value
    'active_work': 1.5,
    'learning': 1.5,     # Value learning more
    'admin': 0.8         # Penalize admin tasks
}
```

### Change Penalty Rate
Edit `backend/database.py`:
```python
def calculate_rollover_penalty(rollover_count: int) -> int:
    return rollover_count * 3  # Harsher penalties
```

## Troubleshooting

**Server won't start?**
```bash
pip install --upgrade fastapi uvicorn pydantic --break-system-packages
```

**Database locked?**
```bash
# Close any other connections, then restart
fuser -k ~/productivity_tracker.db
```

**Reset everything?**
```bash
rm ~/productivity_tracker.db
python backend/database.py  # Recreates fresh DB
```

---

Built for productivity nerds who want data-driven insights without cloud dependencies.
