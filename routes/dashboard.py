"""
Dashboard and analytics routes with Firebase
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models.firebase_models import Task, Expense, Habit
from ml.insights import InsightsGenerator

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """
    Main dashboard showing overview of tasks and expenses
    Includes analytics and AI insights - Firebase version
    """
    # Get user data from Firebase
    all_tasks = Task.query_by_user(current_user.id)
    all_expenses = Expense.query_by_user(current_user.id)
    all_habits = Habit.query_by_user(current_user.id)
    
    # Task statistics
    total_tasks = len(all_tasks)
    completed_tasks = len([t for t in all_tasks if t.status == Task.STATUS_COMPLETED])
    pending_tasks = len([t for t in all_tasks if t.status == Task.STATUS_PENDING])
    overdue_tasks = len([t for t in all_tasks if t.is_overdue()])
    
    # Priority breakdown
    high_priority = len([t for t in all_tasks if t.priority == Task.PRIORITY_HIGH])
    medium_priority = len([t for t in all_tasks if t.priority == Task.PRIORITY_MEDIUM])
    low_priority = len([t for t in all_tasks if t.priority == Task.PRIORITY_LOW])
    
    # Habit statistics
    total_habits = len(all_habits)
    active_habits = len([h for h in all_habits if h.is_active])
    total_streak = sum(h.current_streak for h in all_habits)
    
    # Get daily habits for display - sorted with unmarked first, then marked
    daily_habits = [h for h in all_habits if h.frequency == Habit.FREQUENCY_DAILY and h.is_active]
    daily_habits.sort(key=lambda h: (h.is_completed_today(), h.title))
    
    # Expense statistics
    total_expenses = sum(e.amount for e in all_expenses)
    
    # Current month expenses
    now = datetime.utcnow()
    current_month_start = now.replace(day=1)
    current_month_expenses = [
        e for e in all_expenses
        if (e.date if isinstance(e.date, datetime) else datetime.fromisoformat(e.date)) >= current_month_start
    ]
    current_month_total = sum(e.amount for e in current_month_expenses)
    
    # Category-wise expense breakdown
    category_totals = {}
    for expense in all_expenses:
        if expense.category not in category_totals:
            category_totals[expense.category] = 0
        category_totals[expense.category] += expense.amount
    
    # Upcoming tasks (next 7 days)
    upcoming_tasks = []
    for task in all_tasks:
        if task.status == Task.STATUS_PENDING:
            try:
                task_date = task.deadline if isinstance(task.deadline, datetime) else datetime.fromisoformat(task.deadline)
                days_until = (task_date - now).days
                if 0 <= days_until <= 7:
                    upcoming_tasks.append(task)
            except (ValueError, TypeError):
                pass
    
    # AI Insights
    try:
        insights_gen = InsightsGenerator(current_user.id)
        all_insights = insights_gen.generate_all_insights()
        risk_prediction = insights_gen.predict_high_risk_month()
    except Exception as e:
        all_insights = {
            'task_insights': [],
            'expense_insights': [],
            'combined_insights': []
        }
        risk_prediction = {'level': 'Unknown', 'explanation': 'Unable to generate prediction'}
    
    return render_template(
        'dashboard.html',
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        high_priority=high_priority,
        medium_priority=medium_priority,
        low_priority=low_priority,
        total_habits=total_habits,
        active_habits=active_habits,
        total_streak=total_streak,
        daily_habits=daily_habits,
        total_expenses=total_expenses,
        current_month_total=current_month_total,
        upcoming_tasks=upcoming_tasks,
        category_totals=category_totals,
        task_insights=all_insights['task_insights'],
        expense_insights=all_insights['expense_insights'],
        combined_insights=all_insights['combined_insights'],
        risk_prediction=risk_prediction,
        Task=Task,
        Expense=Expense,
        Habit=Habit
    )

@dashboard_bp.route('/api/task-stats')
@login_required
def task_stats():
    """
    API endpoint for task statistics - Firebase version
    """
    try:
        all_tasks = Task.query_by_user(current_user.id)
        
        stats = {
            'total': len(all_tasks),
            'completed': len([t for t in all_tasks if t.status == Task.STATUS_COMPLETED]),
            'pending': len([t for t in all_tasks if t.status == Task.STATUS_PENDING]),
            'overdue': len([t for t in all_tasks if t.is_overdue()]),
            'high_priority': len([t for t in all_tasks if t.priority == Task.PRIORITY_HIGH]),
            'medium_priority': len([t for t in all_tasks if t.priority == Task.PRIORITY_MEDIUM]),
            'low_priority': len([t for t in all_tasks if t.priority == Task.PRIORITY_LOW])
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/expense-stats')
@login_required
def expense_stats():
    """
    API endpoint for expense statistics - Firebase version
    """
    try:
        all_expenses = Expense.query_by_user(current_user.id)
        
        # Current month
        now = datetime.utcnow()
        current_month_start = now.replace(day=1)
        current_month_expenses = [
            e for e in all_expenses
            if (e.date if isinstance(e.date, datetime) else datetime.fromisoformat(e.date)) >= current_month_start
        ]
        
        # Category breakdown
        category_data = {}
        for expense in all_expenses:
            if expense.category not in category_data:
                category_data[expense.category] = 0
            category_data[expense.category] += expense.amount
        
        stats = {
            'total': sum(e.amount for e in all_expenses),
            'current_month': sum(e.amount for e in current_month_expenses),
            'count': len(all_expenses),
            'categories': category_data
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/habit-stats')
@login_required
def habit_stats():
    """
    API endpoint for habit statistics - Firebase version
    """
    try:
        all_habits = Habit.query_by_user(current_user.id)
        
        stats = {
            'total': len(all_habits),
            'active': len([h for h in all_habits if h.is_active]),
            'total_streak': sum(h.current_streak for h in all_habits),
            'max_streak': max([h.longest_streak for h in all_habits]) if all_habits else 0
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/monthly-trend')
@login_required
def monthly_trend():
    """
    API endpoint for monthly expense trend - Firebase version
    """
    try:
        all_expenses = Expense.query_by_user(current_user.id)
        
        monthly_data = {}
        for expense in all_expenses:
            try:
                # expense.date is already a datetime object after from_dict conversion
                expense_date = expense.date if isinstance(expense.date, datetime) else datetime.fromisoformat(expense.date)
                month_key = expense_date.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = 0
                monthly_data[month_key] += expense.amount
            except (ValueError, AttributeError):
                pass
        
        # Get last 6 months
        sorted_months = sorted(monthly_data.keys())[-6:]
        
        return jsonify({
            'months': sorted_months,
            'amounts': [monthly_data.get(m, 0) for m in sorted_months]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
