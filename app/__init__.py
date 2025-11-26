"""
Productivity Tracker - Application Factory
World-class modular Flask application
"""
from flask import Flask
from flask_cors import CORS
from app.models.database import init_db, migrate_add_display_order

def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__,
                static_folder='static',
                template_folder='../templates')

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
    from app.blueprints.api import api_bp
    from app.blueprints.analytics import analytics_bp
    from app.blueprints.motivation import motivation_bp
    from app.blueprints.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(motivation_bp, url_prefix='/api/motivation')
    
    return app

