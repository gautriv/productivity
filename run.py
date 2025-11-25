"""
Productivity Tracker - Application Entry Point
World-class modular productivity tracking system
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 PRODUCTIVITY TRACKER - WORLD-CLASS EDITION")
    print("="*60)
    print("📊 Features:")
    print("  • Advanced Analytics & Predictive Algorithms")
    print("  • Real-time Productivity Scoring")
    print("  • Gamification & Achievements")
    print("  • Cognitive Load Optimization")
    print("  • Pattern Detection & Insights")
    print("\n💫 Open http://localhost:5000 in your browser")
    print("💾 Database: productivity.db")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')

