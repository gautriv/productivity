"""
Productivity Tracker - Entry Point
World-class modular Flask application
"""
from flask import Flask
from flask_cors import CORS
from models.database import init_db, migrate_add_display_order

def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')

    # Configuration
    app.config['DATABASE'] = 'productivity.db'
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

    if config:
        app.config.update(config)

    # Enable CORS
    CORS(app)

    # Initialize database
    with app.app_context():
        init_db()
        migrate_add_display_order()

    # Register blueprints
    from blueprints.api import api_bp
    from blueprints.analytics import analytics_bp
    from blueprints.motivation import motivation_bp
    from blueprints.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(motivation_bp, url_prefix='/api/motivation')

    return app

# Create the app instance
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
    print("\n💫 Open http://localhost:5555 in your browser")
    print("💾 Database: productivity.db")
    print("="*60 + "\n")

    app.run(debug=True, port=5555)

