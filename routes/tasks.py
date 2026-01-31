"""
Task management routes with Firebase (CRUD operations)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models.firebase_models import Task

# Create blueprint
tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('/')
@login_required
def index():
    """
    Display all tasks for current user - Firebase version
    """
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    
    # Get all tasks for user from Firebase
    tasks = Task.query_by_user(current_user.id)
    
    # Apply filters
    if status_filter != 'all':
        tasks = [t for t in tasks if t.status == status_filter]
    
    # Sort by deadline
    tasks = sorted(tasks, key=lambda t: t.deadline or '', reverse=False)
    
    # Separate overdue and upcoming tasks
    overdue_tasks = [t for t in tasks if t.is_overdue()]
    pending_tasks = [t for t in tasks if not t.is_overdue() and t.status == Task.STATUS_PENDING]
    completed_tasks = [t for t in tasks if t.status == Task.STATUS_COMPLETED]
    
    return render_template(
        'tasks.html',
        tasks=tasks,
        overdue_tasks=overdue_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        status_filter=status_filter,
        Task=Task
    )

@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new task - Firebase version
    """
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Other')
        deadline_str = request.form.get('deadline', '')
        
        # Handle custom category
        if category == '__custom__':
            category = request.form.get('category_custom', 'Other').strip()
        
        # Validation
        if not title:
            flash('Task title is required!', 'error')
            return redirect(url_for('tasks.create'))
        
        # Parse deadline
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str).isoformat()
            except ValueError:
                flash('Invalid deadline format!', 'error')
                return redirect(url_for('tasks.create'))
        
        # Create task in Firebase
        try:
            new_task = Task()
            new_task.user_id = str(current_user.id)
            new_task.title = title
            new_task.description = description
            new_task.category = category
            new_task.deadline = deadline
            new_task.status = Task.STATUS_PENDING
            new_task.save()
            
            flash('Task created successfully!', 'success')
            return redirect(url_for('tasks.index'))
        except Exception as e:
            flash(f'Error creating task: {str(e)}', 'error')
            return redirect(url_for('tasks.create'))
    
    return render_template('task_form.html', Task=Task)

@tasks_bp.route('/<task_id>')
@login_required
def view(task_id):
    """View task details"""
    task = Task.get_by_id(task_id)
    
    if not task or str(task.user_id) != str(current_user.id):
        flash('Task not found!', 'error')
        return redirect(url_for('tasks.index'))
    
    return render_template('task_form.html', task=task, Task=Task)

@tasks_bp.route('/<task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    """Edit task - Firebase version"""
    task = Task.get_by_id(task_id)
    
    if not task or str(task.user_id) != str(current_user.id):
        flash('Task not found!', 'error')
        return redirect(url_for('tasks.index'))
    
    if request.method == 'POST':
        # Update task fields
        task.title = request.form.get('title', '').strip()
        task.description = request.form.get('description', '').strip()
        task.category = request.form.get('category', 'Other')
        
        # Handle custom category
        if task.category == '__custom__':
            task.category = request.form.get('category_custom', 'Other').strip()
        
        deadline_str = request.form.get('deadline', '')
        if deadline_str:
            try:
                task.deadline = datetime.fromisoformat(deadline_str).isoformat()
            except ValueError:
                flash('Invalid deadline format!', 'error')
                return redirect(url_for('tasks.edit', task_id=task_id))
        
        try:
            task.save()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('tasks.index'))
        except Exception as e:
            flash(f'Error updating task: {str(e)}', 'error')
            return redirect(url_for('tasks.edit', task_id=task_id))
    
    return render_template('task_form.html', task=task, Task=Task)

@tasks_bp.route('/<task_id>/delete', methods=['POST'])
@login_required
def delete(task_id):
    """Delete task - Firebase version"""
    task = Task.get_by_id(task_id)
    
    if not task or str(task.user_id) != str(current_user.id):
        flash('Task not found!', 'error')
        return redirect(url_for('tasks.index'))
    
    try:
        task.delete()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting task: {str(e)}', 'error')
    
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/<task_id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(task_id):
    """Toggle task status between Pending and Completed - Firebase version"""
    task = Task.get_by_id(task_id)
    
    if not task or str(task.user_id) != str(current_user.id):
        flash('Task not found!', 'error')
        return redirect(url_for('tasks.index'))
    
    try:
        # Toggle status
        if task.status == Task.STATUS_PENDING:
            task.status = Task.STATUS_COMPLETED
            task.completed_at = datetime.utcnow().isoformat()
            message = 'Task marked as completed!'
        else:
            task.status = Task.STATUS_PENDING
            task.completed_at = None
            message = 'Task marked as pending!'
        
        task.save()
        flash(message, 'success')
    except Exception as e:
        flash(f'Error updating task: {str(e)}', 'error')
    
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/api/tasks')
@login_required
def api_tasks():
    """API endpoint to get tasks as JSON for AJAX"""
    try:
        tasks = Task.query_by_user(current_user.id)
        return jsonify({
            'success': True,
            'tasks': [
                {
                    'id': t.id,
                    'title': t.title,
                    'status': t.status,
                    'deadline': t.deadline,
                    'category': t.category
                }
                for t in tasks
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tasks_bp.route('/<task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    """Mark a task as completed - JSON API endpoint"""
    try:
        task = Task.get_by_id(task_id)
        if not task or str(task.user_id) != str(current_user.id):
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        if task.status != Task.STATUS_COMPLETED:
            task.status = Task.STATUS_COMPLETED
            task.completed_at = datetime.utcnow().isoformat()
            task.save()
        
        return jsonify({'success': True, 'message': 'Task marked as completed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tasks_bp.route('/api/<task_id>/complete', methods=['POST'])
@login_required
def api_complete_task(task_id):
    """API endpoint to mark task as complete (alias for /tasks/<task_id>/complete)"""
    try:
        task = Task.get_by_id(task_id)
        if not task or str(task.user_id) != str(current_user.id):
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        if task.status != Task.STATUS_COMPLETED:
            task.status = Task.STATUS_COMPLETED
            task.completed_at = datetime.utcnow().isoformat()
            task.save()
        
        return jsonify({'success': True, 'message': 'Task completed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
