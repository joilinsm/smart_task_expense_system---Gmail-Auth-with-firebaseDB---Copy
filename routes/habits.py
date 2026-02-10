"""
Habit management routes with Firebase (CRUD operations)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models.firebase_models import Habit, HabitCompletion

# Create blueprint
habits_bp = Blueprint('habits', __name__, url_prefix='/habits')

def _parse_completion_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
        except (ValueError, TypeError):
            return None
    if hasattr(value, 'date'):
        try:
            return value.date()
        except Exception:
            return None
    return None

def _get_latest_completion_date(completions, today):
    latest = None
    for completion in completions:
        comp_date = _parse_completion_date(getattr(completion, 'completion_date', None))
        if comp_date and comp_date < today and (latest is None or comp_date > latest):
            latest = comp_date
    return latest

@habits_bp.route('/')
@login_required
def index():
    """
    Display all habits for current user - Firebase version
    """
    # Get all habits from Firebase
    habits = Habit.query_by_user(current_user.id)
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    
    # Apply filters
    if status_filter != 'all':
        if status_filter == 'active':
            habits = [h for h in habits if h.is_active and not h.is_completed]
        elif status_filter == 'paused':
            habits = [h for h in habits if not h.is_active and not h.is_completed]
        elif status_filter == 'completed':
            habits = [h for h in habits if h.is_completed]
    
    # Separate habits by status
    active_habits = [h for h in habits if h.is_active and not h.is_completed]
    paused_habits = [h for h in habits if not h.is_active and not h.is_completed]
    completed_habits = [h for h in habits if h.is_completed]
    
    return render_template(
        'habits.html',
        habits=habits,
        active_habits=active_habits,
        paused_habits=paused_habits,
        completed_habits=completed_habits,
        status_filter=status_filter,
        Habit=Habit
    )

@habits_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new habit - Firebase version
    """
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', 'Health').strip()
            frequency = request.form.get('frequency', Habit.FREQUENCY_DAILY)
            deadline_str = request.form.get('deadline', '').strip()
            
            # Handle custom category
            if category == '__custom__':
                category = request.form.get('category_custom', 'Other').strip()
            
            # Validation
            if not title:
                flash('Habit name is required!', 'error')
                return redirect(url_for('habits.create'))
            
            # Create habit in Firebase
            new_habit = Habit()
            new_habit.user_id = str(current_user.id)
            new_habit.title = title
            new_habit.name = title  # Store in name field as well for compatibility
            new_habit.description = description
            new_habit.category = category
            new_habit.frequency = frequency
            new_habit.is_active = True
            new_habit.current_streak = 0
            new_habit.longest_streak = 0
            
            # Handle optional deadline
            if deadline_str:
                from datetime import datetime
                try:
                    new_habit.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').isoformat()
                except ValueError:
                    pass
            
            new_habit.save()
            
            flash('Habit created successfully!', 'success')
            return redirect(url_for('habits.index'))
        except Exception as e:
            flash(f'Error creating habit: {str(e)}', 'error')
            return redirect(url_for('habits.create'))
    
    return render_template('habit_form.html', Habit=Habit)

@habits_bp.route('/<habit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(habit_id):
    """Edit habit - Firebase version"""
    habit = Habit.get_by_id(habit_id)
    
    if not habit or str(habit.user_id) != str(current_user.id):
        flash('Habit not found!', 'error')
        return redirect(url_for('habits.index'))
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', 'Health').strip()
            frequency = request.form.get('frequency', Habit.FREQUENCY_DAILY)
            deadline_str = request.form.get('deadline', '').strip()
            
            # Handle custom category
            if category == '__custom__':
                category = request.form.get('category_custom', 'Other').strip()
            
            if not title:
                flash('Habit name is required!', 'error')
                return redirect(url_for('habits.edit', habit_id=habit_id))
            
            habit.title = title
            habit.name = title  # Keep name in sync with title
            habit.description = description
            habit.category = category
            habit.frequency = frequency
            
            # Handle optional deadline
            if deadline_str:
                from datetime import datetime
                try:
                    habit.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').isoformat()
                except ValueError:
                    pass
            else:
                habit.deadline = None
            
            # Handle status field if present (converts to is_active)
            status = request.form.get('status')
            if status:
                habit.status = status
            
            habit.save()
            flash('Habit updated successfully!', 'success')
            return redirect(url_for('habits.index'))
        except Exception as e:
            flash(f'Error updating habit: {str(e)}', 'error')
            return redirect(url_for('habits.edit', habit_id=habit_id))
    
    return render_template('habit_form.html', habit=habit, Habit=Habit)

@habits_bp.route('/<habit_id>/delete', methods=['POST'])
@login_required
def delete(habit_id):
    """Delete habit - Firebase version"""
    habit = Habit.get_by_id(habit_id)
    
    if not habit or str(habit.user_id) != str(current_user.id):
        flash('Habit not found!', 'error')
        return redirect(url_for('habits.index'))
    
    try:
        # Delete habit and all completions
        completions = HabitCompletion.query_by_habit(habit_id)
        for completion in completions:
            completion.delete()
        
        habit.delete()
        flash('Habit deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting habit: {str(e)}', 'error')
    
    return redirect(url_for('habits.index'))

@habits_bp.route('/<habit_id>/mark-complete', methods=['POST'])
@login_required
def mark_complete(habit_id):
    """Mark habit as completed for today - Firebase version"""
    habit = Habit.get_by_id(habit_id)
    
    if not habit or str(habit.user_id) != str(current_user.id):
        flash('Habit not found!', 'error')
        return redirect(url_for('habits.index'))
    
    try:
        # Check if already completed today
        if habit.is_completed_today():
            flash('Already completed today!', 'info')
            return redirect(url_for('habits.index'))

        today = datetime.utcnow().date()
        completions = HabitCompletion.query_by_habit(habit_id)
        last_completion_date = _get_latest_completion_date(completions, today)
        
        # Create completion record
        completion = HabitCompletion()
        completion.habit_id = str(habit_id)
        completion.user_id = str(current_user.id)
        completion.completion_date = datetime.utcnow().isoformat()
        notes = request.form.get('notes', '').strip()
        if notes:
            completion.notes = notes
        completion.save()
        
        # Update streak with missed-day reset
        current_streak = int(habit.current_streak) if habit.current_streak is not None else 0
        if last_completion_date is None:
            habit.current_streak = 1
        else:
            gap_days = (today - last_completion_date).days
            habit.current_streak = current_streak + 1 if gap_days == 1 else 1
        if habit.current_streak > habit.longest_streak:
            habit.longest_streak = habit.current_streak
        habit.save()
        
        flash(f'Great! Streak: {habit.current_streak} days 🔥', 'success')
    except Exception as e:
        flash(f'Error marking habit complete: {str(e)}', 'error')
    
    return redirect(url_for('habits.index'))

@habits_bp.route('/<habit_id>/toggle', methods=['POST'])
@login_required
def toggle_completion(habit_id):
    """Toggle habit completion for today - AJAX endpoint"""
    from datetime import datetime as dt
    import traceback
    
    print(f"\n🔷 TOGGLE COMPLETION DEBUG - Habit ID: {habit_id}")
    
    habit = Habit.get_by_id(habit_id)
    print(f"🔷 Habit retrieved: {habit}")
    
    if not habit or str(habit.user_id) != str(current_user.id):
        return jsonify({'success': False, 'error': 'Habit not found'}), 404
    
    try:
        today = dt.utcnow().date()
        print(f"🔷 Today's date: {today}")
        
        completions = HabitCompletion.query_by_habit(habit_id)
        print(f"🔷 Found {len(completions)} completions for this habit")
        
        # Find today's completion
        today_completion = None
        for completion in completions:
            try:
                comp_date = completion.completion_date
                print(f"🔷 Checking completion date: {comp_date} (type: {type(comp_date)})")
                
                if isinstance(comp_date, str):
                    comp_date = dt.fromisoformat(comp_date).date()
                else:
                    comp_date = comp_date.date() if comp_date else None
                
                print(f"🔷 Parsed date: {comp_date}, Today: {today}, Match: {comp_date == today}")
                
                if comp_date == today:
                    today_completion = completion
                    print(f"🔷 Found today's completion: {completion.id}")
                    break
            except Exception as ce:
                print(f"🔷 Error checking completion: {ce}")
                pass
        
        if today_completion:
            # Already completed today - remove the completion and decrease streak
            print(f"🔷 Removing completion {today_completion.id}, streak before: {habit.current_streak}")
            today_completion.delete()
            # Ensure current_streak is a number
            current_streak = int(habit.current_streak) if habit.current_streak is not None else 0
            habit.current_streak = max(0, current_streak - 1)
            print(f"🔷 Streak after: {habit.current_streak}")
            habit.save()
            print(f"🔷 Habit saved with streak: {habit.current_streak}")
            return jsonify({
                'success': True,
                'message': 'Habit completion removed',
                'completed': False,
                'streak': habit.current_streak
            })
        else:
            # Not completed today - add completion and increase streak
            print(f"🔷 Adding new completion, streak before: {habit.current_streak}")
            last_completion_date = _get_latest_completion_date(completions, today)
            completion = HabitCompletion()
            completion.habit_id = str(habit_id)
            completion.user_id = str(current_user.id)
            completion.completion_date = dt.utcnow().isoformat()
            comp_id = completion.save()
            print(f"🔷 Completion saved with ID: {comp_id}")
            
            # Ensure current_streak is a number
            current_streak = int(habit.current_streak) if habit.current_streak is not None else 0
            if last_completion_date is None:
                habit.current_streak = 1
            else:
                gap_days = (today - last_completion_date).days
                habit.current_streak = current_streak + 1 if gap_days == 1 else 1
            if habit.current_streak > (habit.longest_streak or 0):
                habit.longest_streak = habit.current_streak
            print(f"🔷 Streak after: {habit.current_streak}")
            habit.save()
            print(f"🔷 Habit saved")
            
            return jsonify({
                'success': True,
                'message': f'Great! Streak: {habit.current_streak} days 🔥',
                'completed': True,
                'streak': habit.current_streak
            })
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"🔷 ERROR: {error_msg}")
        return jsonify({'success': False, 'error': str(e)}), 500

@habits_bp.route('/<habit_id>/reset-streak', methods=['POST'])
@login_required
def reset_streak(habit_id):
    """Reset habit streak - Firebase version"""
    habit = Habit.get_by_id(habit_id)
    
    if not habit or str(habit.user_id) != str(current_user.id):
        flash('Habit not found!', 'error')
        return redirect(url_for('habits.index'))
    
    try:
        habit.current_streak = 0
        habit.save()
        flash('Streak reset. Keep going! 💪', 'success')
    except Exception as e:
        flash(f'Error resetting streak: {str(e)}', 'error')
    
    return redirect(url_for('habits.index'))

@habits_bp.route('/<habit_id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(habit_id):
    """Toggle habit active/paused status - Firebase version"""
    habit = Habit.get_by_id(habit_id)
    
    if not habit or str(habit.user_id) != str(current_user.id):
        flash('Habit not found!', 'error')
        return redirect(url_for('habits.index'))
    
    try:
        habit.is_active = not habit.is_active
        habit.save()
        status = 'activated' if habit.is_active else 'paused'
        flash(f'Habit {status} successfully!', 'success')
    except Exception as e:
        flash(f'Error updating habit: {str(e)}', 'error')
    
    return redirect(url_for('habits.index'))

@habits_bp.route('/<habit_id>/pause', methods=['POST'])
@login_required
def pause_habit(habit_id):
    """Pause a habit - Firebase version"""
    habit = Habit.get_by_id(habit_id)
    
    if not habit or str(habit.user_id) != str(current_user.id):
        flash('Habit not found!', 'error')
        return redirect(url_for('habits.index'))
    
    try:
        habit.is_active = False
        habit.save()
        flash('Habit paused successfully!', 'success')
    except Exception as e:
        flash(f'Error pausing habit: {str(e)}', 'error')
    
    return redirect(url_for('habits.index'))

@habits_bp.route('/<habit_id>/resume', methods=['POST'])
@login_required
def resume_habit(habit_id):
    """Resume a paused habit - Firebase version"""
    habit = Habit.get_by_id(habit_id)
    
    if not habit or str(habit.user_id) != str(current_user.id):
        flash('Habit not found!', 'error')
        return redirect(url_for('habits.index'))
    
    try:
        habit.is_active = True
        habit.is_completed = False
        habit.save()
        flash('Habit resumed successfully! Keep going! 💪', 'success')
    except Exception as e:
        flash(f'Error resuming habit: {str(e)}', 'error')
    
    return redirect(url_for('habits.index'))

@habits_bp.route('/<habit_id>/calendar', methods=['GET'])
@login_required
def calendar_view(habit_id):
    """
    Display individual calendar view for a specific habit
    Supports Daily, Weekly, and Monthly habits with color-coded completion status
    Calendar timeline starts from habit creation date
    """
    from datetime import datetime
    
    habit = Habit.get_by_id(habit_id)
    
    if not habit or str(habit.user_id) != str(current_user.id):
        flash('Habit not found!', 'error')
        return redirect(url_for('habits.index'))
    
    # Parse habit creation date (supports created_at/createdAt/creationTimestamp)
    creation_date = habit.get_creation_date()
    
    # Get year and month parameters (default to current)
    year = request.args.get('year', datetime.utcnow().year, type=int)
    month = request.args.get('month', datetime.utcnow().month, type=int)
    
    # Validate month and year
    if month < 1 or month > 12:
        month = datetime.utcnow().month
    if year < 2020 or year > 2030:
        year = datetime.utcnow().year
    
    # Ensure calendar does not go before habit creation date
    # If requested month/year is before creation, show creation month instead
    requested_date = datetime(year, month, 1).date()
    creation_month_date = datetime(creation_date.year, creation_date.month, 1).date()
    
    if requested_date < creation_month_date:
        year = creation_date.year
        month = creation_date.month
    
    # Get calendar data with color coding and creation date boundary
    calendar_data = habit.get_calendar_data(year, month, creation_date)
    
    # Get habit completion statistics
    completions = HabitCompletion.query_by_habit(habit_id)
    
    # Calculate next/previous month links
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Determine if previous button should be disabled (at creation month)
    is_at_creation_month = (year == creation_date.year and month == creation_date.month)
    
    return render_template(
        'habit_calendar.html',
        habit=habit,
        calendar=calendar_data,
        completions=completions,
        year=year,
        month=month,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
        creation_date=creation_date,
        is_at_creation_month=is_at_creation_month,
        Habit=Habit
    )

@habits_bp.route('/api/habits')
@login_required
def api_habits():
    """API endpoint to get habits as JSON for AJAX - Firebase version"""
    try:
        habits = Habit.query_by_user(current_user.id)
        return jsonify({
            'success': True,
            'habits': [
                {
                    'id': h.id,
                    'name': h.name,
                    'frequency': h.frequency,
                    'current_streak': h.current_streak,
                    'is_active': h.is_active
                }
                for h in habits
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@habits_bp.route('/api/<habit_id>/stats')
@login_required
def api_habit_stats(habit_id):
    """API endpoint to get habit statistics - Firebase version"""
    try:
        habit = Habit.get_by_id(habit_id)
        if not habit or str(habit.user_id) != str(current_user.id):
            return jsonify({'success': False, 'error': 'Habit not found'}), 404
        
        completions = HabitCompletion.query_by_habit(habit_id)
        
        return jsonify({
            'success': True,
            'habit': {
                'name': habit.name,
                'current_streak': habit.current_streak,
                'longest_streak': habit.longest_streak,
                'total_completions': len(completions),
                'frequency': habit.frequency,
                'is_active': habit.is_active
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
