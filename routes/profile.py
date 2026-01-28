"""
User Profile & Preferences Management Routes with Firebase
Handles:
- User profile viewing and editing
- User preferences management (priority, budget, theme, notifications)
- Input validation and error handling
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.firebase_models import User

# Create blueprint
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
@login_required
def view_profile():
    """
    View user profile and preferences - Firebase version
    """
    return render_template(
        'profile.html',
        user=current_user
    )

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Edit user profile (name, email) - Firebase version
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        country_code = request.form.get('country_code', '+91').strip()
        phone_number = request.form.get('phone_number', '').strip()
        monthly_budget = request.form.get('monthly_budget', '0').strip()
        
        # Validation
        if not username:
            flash('Username is required!', 'error')
            return redirect(url_for('profile.edit_profile'))
        
        if not email:
            flash('Email is required!', 'error')
            return redirect(url_for('profile.edit_profile'))
        
        # Check username uniqueness (if changed)
        if username != current_user.username:
            existing_user = User.query_by_username(username)
            if existing_user:
                flash('Username already taken! Please choose a different username.', 'error')
                return redirect(url_for('profile.edit_profile'))
            
            # Validate username format (alphanumeric and underscores only)
            if not username.replace('_', '').isalnum():
                flash('Username can only contain letters, numbers, and underscores!', 'error')
                return redirect(url_for('profile.edit_profile'))
        
        # Check email uniqueness (if changed)
        if email != current_user.email:
            existing_user = User.query_by_email(email)
            if existing_user:
                flash('Email already registered!', 'error')
                return redirect(url_for('profile.edit_profile'))
        
        # Validate phone number format if provided
        if phone_number:
            if not phone_number.isdigit():
                flash('Phone number should contain only digits!', 'error')
                return redirect(url_for('profile.edit_profile'))
            if len(phone_number) < 7 or len(phone_number) > 15:
                flash('Phone number should be between 7 and 15 digits!', 'error')
                return redirect(url_for('profile.edit_profile'))
        
        # Parse budget
        try:
            budget_amount = float(monthly_budget) if monthly_budget else 0.0
        except ValueError:
            flash('Invalid budget amount!', 'error')
            return redirect(url_for('profile.edit_profile'))
        
        try:
            # Update user in Firebase
            current_user.username = username
            current_user.first_name = first_name
            current_user.last_name = last_name
            current_user.email = email
            current_user.country_code = country_code
            current_user.phone_number = phone_number
            current_user.monthly_budget = budget_amount
            current_user.save()
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile.view_profile'))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
            return redirect(url_for('profile.edit_profile'))
    
    return render_template('profile_edit.html', user=current_user)

@profile_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """
    Manage user preferences (theme, priority, notifications) - Firebase version
    """
    if request.method == 'POST':
        default_task_priority = request.form.get('default_task_priority', 'Medium')
        theme_preference = request.form.get('theme_preference', 'blue')
        notification_enabled = request.form.get('notification_enabled') == 'on'
        
        try:
            current_user.default_task_priority = default_task_priority
            current_user.theme_preference = theme_preference
            current_user.notification_enabled = notification_enabled
            current_user.save()
            
            flash('Preferences updated successfully!', 'success')
            return redirect(url_for('profile.preferences'))
        except Exception as e:
            flash(f'Error updating preferences: {str(e)}', 'error')
            return redirect(url_for('profile.preferences'))
    
    return render_template('preferences.html', user=current_user)

@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change user password - Firebase version
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect!', 'error')
            return redirect(url_for('profile.change_password'))
        
        # Validate new password
        if not new_password:
            flash('New password is required!', 'error')
            return redirect(url_for('profile.change_password'))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return redirect(url_for('profile.change_password'))
        
        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('profile.change_password'))
        
        try:
            current_user.set_password(new_password)
            current_user.save()
            
            flash('Password changed successfully! Please log in again.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error changing password: {str(e)}', 'error')
            return redirect(url_for('profile.change_password'))
    
    return render_template('change_password.html', user=current_user)
