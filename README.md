# Productivity Tracker

A sophisticated, gamified productivity tracking system with advanced analytics, predictive algorithms, and motivational features.

## Overview

This is a comprehensive productivity tracking application built with Flask and React that helps you manage tasks, analyze patterns, and stay motivated through gamification. The system uses advanced algorithms to provide insights and predictions about your productivity patterns.

## Key Features

### Core Task Management
- Create, edit, and delete tasks
- Cognitive load classification (Deep Work, Active Work, Admin, Learning)
- Complexity rating system (1-5 scale)
- Time estimation and actual time tracking
- Subtask support and task hierarchies
- Task rollover system with penalty calculations
- Daily task scheduling and status tracking

### Advanced Analytics & Algorithms
- **Productivity Score** - Comprehensive 0-100 score based on completion rate, points, consistency, and penalties
- **Pattern Detection** - Identifies weekly patterns, trends, and anomalies in your productivity
- **Optimal Time Finder** - ML-based algorithm that determines the best times of day for different task types
- **Completion Prediction** - Predicts probability of task completion based on historical data
- **Cognitive Load Balancing** - Analyzes and recommends optimal distribution of task types
- **Time Estimation Analysis** - Tracks accuracy of time estimates and provides adjustment recommendations

### Gamification System
- **Leveling System** - XP-based progression with dynamic level calculations
- **Achievement System** - 11 different achievements including:
  - First Task, Consistency, Week Warrior, Unstoppable (30-day streak)
  - Century (100 points in one day), Point Master (500 total points)
  - Deep Thinker, Perfect Day, Early Bird, Night Owl, Comeback Kid
- **Streak Tracking** - Current and longest streak monitoring
- **Points System** - Dynamic point calculation based on complexity, cognitive load, and time
- **Daily Challenges** - Personalized challenges with bonus points

### User Experience
- **World-Class Animations** - Smooth transitions, micro-interactions, and entrance animations
- **Custom Scrollbars** - Minimal, smooth scrollbars with hover effects
- **Responsive Design** - Works on desktop, tablet, and mobile devices
- **Dark Theme** - Professional dark color scheme optimized for long sessions
- **Real-time Updates** - Instant feedback and achievement notifications
- **Motivational Quotes** - Context-aware motivational messages

## Project Structure

```
productivity-tracker/
├── app/
│   ├── __init__.py              # Application factory
│   ├── blueprints/              # Route handlers
│   │   ├── main.py              # Frontend routes
│   │   ├── api.py               # Task management API
│   │   ├── analytics.py         # Analytics & insights API
│   │   └── motivation.py        # Gamification API
│   ├── models/                  # Database models
│   │   └── database.py          # Schema & DB operations
│   ├── services/                # Business logic
│   │   ├── analytics.py         # Advanced analytics algorithms
│   │   └── motivation.py        # Gamification engine
│   ├── utils/                   # Utility functions
│   │   └── helpers.py           # Common utilities
│   └── static/                  # Static assets
│       ├── css/
│       │   └── styles.css       # All application styles
│       └── js/
│           └── app.jsx          # React application
├── templates/
│   └── index.html               # Main HTML template
├── app.py                       # Application entry point
├── run.py                       # Alternative entry point
├── requirements.txt             # Python dependencies
└── productivity.db              # SQLite database (generated)
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup Steps

1. Clone or download the repository

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Using app.py
```bash
python app.py
```

### Using run.py
```bash
python run.py
```

The application will start on `http://localhost:5555`

## Database Schema

### Tables

**tasks** - Master list of all tasks
- id, title, description, complexity, cognitive_load, time_estimate
- parent_id (for subtasks), created_at, archived

**daily_tasks** - Tasks assigned to specific days
- id, task_id, scheduled_date, status (pending/in_progress/completed/abandoned)
- rolled_over_count, penalty_points, actual_time, completed_at, notes

**daily_summaries** - Aggregated daily statistics
- summary_date, total_tasks, completed_tasks, total_points_earned
- total_penalty_points, cognitive load breakdowns

**achievements** - Unlocked achievements
- name, description, icon, type, requirement, unlocked_at

**user_stats** - User progression tracking
- stat_date, current_streak, longest_streak, total_points
- level, experience, achievements_unlocked

**task_predictions** - ML-based task predictions
- task_id, predicted_completion_time, predicted_success_rate
- optimal_time_of_day, difficulty_score

## API Endpoints

### Task Management
- `GET /api/tasks` - Get all non-archived tasks
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/<id>` - Update a task
- `DELETE /api/tasks/<id>` - Archive a task
- `GET /api/tasks/<id>/subtasks` - Get subtasks

### Daily Tasks
- `GET /api/daily/<date>` - Get tasks for specific date
- `POST /api/daily/<date>/add` - Add existing task to date
- `POST /api/daily/<date>/quick-add` - Create and add task
- `PUT /api/daily/task/<id>/status` - Update task status
- `DELETE /api/daily/task/<id>` - Remove from daily schedule

### Analytics
- `GET /api/analytics/daily/<date>` - Daily statistics
- `GET /api/analytics/trends?days=30` - Productivity trends
- `GET /api/analytics/insights?days=14` - Smart insights
- `GET /api/analytics/summary?days=30` - Overall summary
- `GET /api/analytics/productivity-score/<date>` - Productivity score
- `GET /api/analytics/optimal-time/<cognitive_load>` - Best time for task type
- `POST /api/analytics/predict-completion` - Predict task success
- `GET /api/analytics/cognitive-balance/<date>` - Load balance check
- `GET /api/analytics/patterns?days=30` - Pattern detection

### Motivation & Gamification
- `GET /api/motivation/achievements` - All achievements
- `POST /api/motivation/check-achievements` - Check for new unlocks
- `GET /api/motivation/stats` - User statistics
- `GET /api/motivation/quote?context=<context>` - Motivational quote
- `GET /api/motivation/daily-challenge/<date>` - Daily challenge
- `GET /api/motivation/streak` - Streak information

### System
- `POST /api/rollover` - Process end-of-day rollover

## Algorithms & Formulas

### Point Calculation
```
base_points = complexity * 10
multiplier = cognitive_load_multiplier (deep_work: 2.0, learning: 1.5, active_work: 1.2, admin: 1.0)
time_bonus = (time_estimate / 30) * 5
total_points = (base_points + time_bonus) * multiplier
```

### Penalty Calculation
```
penalty = rolled_over_count * 2
```

### Productivity Score (0-100)
- Completion Rate: 40%
- Points Earned vs Potential: 30%
- Consistency (days with completions): 20%
- Penalty Avoidance: 10%

### Level System
```
level = floor(sqrt(total_points / 50)) + 1
xp_for_current_level = (level - 1)^2 * 50
xp_for_next_level = level^2 * 50
```

## Technology Stack

### Backend
- Flask 3.0.0 - Web framework
- Flask-CORS 4.0.0 - Cross-origin resource sharing
- SQLite - Database
- Python 3.9+ - Programming language

### Frontend
- React 18 - UI library
- Chart.js - Data visualization
- Babel Standalone - JSX compilation
- Custom CSS - Styling with animations

### Design System
- Space Grotesk - Primary font
- JetBrains Mono - Monospace font
- Dark theme with smooth animations
- Responsive grid layout

## Configuration

### Database
- Default: `productivity.db` in root directory
- Automatically created on first run
- SQLite format for portability

### Server
- Host: localhost
- Port: 5555
- Debug mode: Enabled in development

## Development

### Adding New Features

1. **New API Endpoint**: Add to appropriate blueprint in `app/blueprints/`
2. **New Algorithm**: Add to `app/services/analytics.py`
3. **New Achievement**: Update `MotivationEngine.ACHIEVEMENTS` in `app/services/motivation.py`
4. **New Database Table**: Update schema in `app/models/database.py`
5. **UI Changes**: Modify `app/static/js/app.jsx` and `app/static/css/styles.css`

### Code Organization
- **Blueprints**: Route handlers, minimal logic
- **Services**: Business logic and algorithms
- **Models**: Database operations only
- **Utils**: Shared helper functions

## Best Practices

### Task Management
- Break large tasks into subtasks
- Use appropriate cognitive load classification
- Be realistic with time estimates
- Review and adjust based on insights

### Maximizing Productivity
- Complete high-value (complex + deep work) tasks during peak hours
- Balance cognitive load distribution throughout the day
- Maintain consistency for streak bonuses
- Review daily challenges for bonus points

### Using Analytics
- Check productivity score weekly
- Adjust scheduling based on optimal time recommendations
- Pay attention to pattern detection insights
- Use completion predictions for planning

## Troubleshooting

### Application Won't Start
- Ensure virtual environment is activated
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)

### Database Errors
- Delete `productivity.db` to reset (WARNING: loses all data)
- Check file permissions on database file
- Ensure sufficient disk space

### Frontend Not Loading
- Check browser console for errors
- Verify static files exist in `app/static/`
- Clear browser cache
- Try different browser

### No Achievements Unlocking
- Complete tasks to trigger achievement checks
- Check `/api/motivation/check-achievements` endpoint
- Verify database has achievements table

## Performance

- Lightweight SQLite database
- Efficient queries with proper indexing
- Lazy loading of analytics data
- Optimized React rendering
- Smooth 60fps animations

## Security Considerations

- Currently designed for local/single-user use
- No authentication system (add if exposing to network)
- Database not encrypted (contains productivity data only)
- CORS enabled for localhost development

## Future Enhancements

Potential additions (not yet implemented):
- Multi-user support with authentication
- Cloud sync capabilities
- Mobile app
- Export data to CSV/JSON
- Integration with calendar systems
- Pomodoro timer integration
- Team productivity features
- Custom achievement creation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ⚠️ Liability and warranty disclaimer

## Support

For issues or questions:
1. Check this README thoroughly
2. Review code comments in source files
3. Check browser console for frontend errors
4. Review Flask debug output for backend errors

## Credits

### Author
Built with dedication and attention to detail by passionate developers who believe in the power of productivity and self-improvement.

### Inspiration
This project combines principles from:
- **Productivity Science** - Evidence-based task management methodologies
- **Gamification Theory** - Motivation through achievement systems
- **Behavioral Psychology** - Habit formation and streak mechanics
- **Data Science** - Predictive analytics and pattern recognition

### Technologies & Libraries
- **Flask** - Web framework by Pallets
- **React** - UI library by Meta
- **Chart.js** - Data visualization
- **SQLite** - Database engine
- **Flask-CORS** - CORS handling

### Version Information
- **Version**: 2.0.0
- **Release Date**: November 2025
- **Status**: Active Development

---

**Built with ❤️ for high performers who want to track, analyze, and optimize their productivity journey.**
