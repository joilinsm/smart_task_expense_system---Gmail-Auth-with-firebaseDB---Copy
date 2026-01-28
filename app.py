"""
Smart Task & Expense Intelligence System
Main Flask Application

A comprehensive personal productivity and expense analytics system
designed for students and freelancers.

Features:
- User Authentication (Registration, Login, Logout)
- Task Management (CRUD, Priority, Deadlines, Status tracking)
- Expense Tracking (CRUD, Categorization, Monthly trends)
- Analytics Dashboard with Chart.js visualizations
- AI-powered Insights and Risk Predictions
- Simple ML-based recommendations

Tech Stack:
- Backend: Python Flask
- Database: SQLite (upgradable to MySQL)
- ORM: SQLAlchemy
- Frontend: HTML5, CSS3 (Bootstrap 5), JavaScript
- Charts: Chart.js
- ML: scikit-learn (rule-based logic)
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from config import DevelopmentConfig as config

# Import Firebase database and models
from firebase_db import firebase_db
from models.firebase_models import User, Task, Expense, Habit, HabitCompletion

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'  # Enhanced security

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login - Firebase version"""
    return User.get_by_id(user_id)

# Register Blueprints
from routes.auth import auth_bp
from routes.tasks import tasks_bp
from routes.expenses import expenses_bp
from routes.dashboard import dashboard_bp
from routes.habits import habits_bp
from routes.profile import profile_bp

app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(habits_bp)
app.register_blueprint(profile_bp)

# Root route - Redirect to dashboard if logged in, else to login
@app.route('/')
def index():
    """Root route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

# Error handlers
@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return render_template('403.html'), 403

# Application context
@app.shell_context_processor
def make_shell_context():
    """Add database objects to shell context"""
    return {
        'firebase_db': firebase_db,
        'User': User,
        'Task': Task,
        'Expense': Expense,
        'Habit': Habit,
        'HabitCompletion': HabitCompletion
    }

@app.before_request
def before_request():
    """Before request handler"""
    # Any initialization code can go here
    pass

@app.after_request
def after_request(response):
    """After request handler"""
    # Add custom headers if needed
    return response


def init_db():
    """Initialize Firebase database with demo user if empty"""
    try:
        # Check if users collection has any users
        users = User.all()
        if not users:
            # Create demo user
            demo_user = User()
            demo_user.username = 'demo'
            demo_user.email = 'demo@example.com'
            demo_user.first_name = 'Demo'
            demo_user.last_name = 'User'
            demo_user.set_password('demo123')
            demo_user.email_verified = True
            demo_user.balance_amount = 0.0
            demo_user.save()
            
            print('✅ Firebase database initialized with demo user!')
            print('   Username: demo')
            print('   Password: demo123')
        else:
            print('✅ Firebase database ready!')
    except Exception as e:
        print(f"⚠️ Warning during Firebase init: {e}")

if __name__ == '__main__':
    # Initialize Firebase database on startup
    init_db()
    
    # Run the application
    print('=' * 60)
    print('Smart Task & Expense Intelligence System')
    print('Firebase Edition')
    print('=' * 60)
    
    # Get host and port from environment variables
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('DEBUG', 'True') == 'True'
    
    print('\n✅ Application started!')
    print(f'🌐 Access at: http://{host}:{port}')
    print('\n📝 Demo Credentials:')
    print('   Username: demo')
    print('   Password: demo123')
    print('\n☁️  Database: Firebase Firestore')
    print(f'🔧 Environment: {"Development" if debug_mode else "Production"}')
    print('\n' + '=' * 60)
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            use_reloader=debug_mode
        )
    except KeyboardInterrupt:
        print('\n\nApplication stopped.')
        sys.exit(0)
