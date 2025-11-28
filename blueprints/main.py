"""
Main Blueprint
Serves the frontend application
"""
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

