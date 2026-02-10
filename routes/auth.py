"""
Authentication routes with Firebase (login, register, logout, email verification)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models.firebase_models import User
from utils.email_sender import send_otp_email, send_otp_email_async, send_verification_reminder_email, send_password_reset_email
import logging

# Create blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route with Firebase
    Handles user signup with validation
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        # Validation
        if not username or not email or not password:
            flash('Username, email, and password are required!', 'error')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if user exists (must be done before saving)
        if User.query_by_username(username):
            flash('Username already exists!', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query_by_email(email):
            flash('Email already registered!', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        try:
            new_user = User()
            new_user.username = username
            new_user.email = email
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.set_password(password)
            
            # Final uniqueness check before save to avoid false-positive UI errors
            if User.query_by_username(username) or User.query_by_email(email):
                flash('Username or email already exists!', 'error')
                return redirect(url_for('auth.register'))

            # Save to Firebase
            new_user.save()
            
            # Generate and send OTP
            otp_code = new_user.generate_otp()
            new_user.save()  # Save OTP secret to Firebase
            
            # Store user_id in session for verification
            session['pending_verification_user_id'] = new_user.id
            
            # Send OTP email
            send_otp_email_async(new_user.email, new_user.username, otp_code)
            flash('✅ Registration successful! OTP is being sent to your email. Check your inbox or spam folder.', 'success')
            
            return redirect(url_for('auth.verify_email'))
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route with Firebase
    Handles user authentication
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required!', 'error')
            return redirect(url_for('auth.login'))
        
        # Find user from Firebase
        user = User.query_by_username(username)
        
        if user and user.check_password(password):
            if not user.email_verified:
                # Store user ID for verification redirect
                session['pending_verification_user_id'] = user.id
                try:
                    otp_code = user.generate_otp()
                    user.save()
                    send_otp_email_async(user.email, user.username, otp_code)
                    flash('Please verify your email. A new OTP is being sent to your inbox.', 'warning')
                except Exception as e:
                    flash(f'Error sending verification code: {str(e)}', 'error')
                return redirect(url_for('auth.verify_email'))

            login_user(user, remember=request.form.get('remember_me'))
            flash(f'Welcome back, {user.first_name or user.username}!', 'success')

            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password!', 'error')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """
    Email verification route for OTP verification with Firebase
    """
    # Check if there's a pending verification
    user_id = session.get('pending_verification_user_id') or (current_user.id if current_user.is_authenticated else None)
    
    if not user_id:
        flash('No pending verification found. Please register or log in.', 'error')
        return redirect(url_for('auth.register'))
    
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.register'))
    
    if user.email_verified:
        flash('Email already verified! Please log in.', 'info')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code', '').strip()
        
        if not otp_code:
            flash('Please enter the verification code!', 'error')
            return render_template('verify_email.html', user=user)
        
        print(f"\n{'='*70}")
        print(f"🔐 OTP VERIFICATION ATTEMPT")
        print(f"{'='*70}")
        print(f"User: {user.username} ({user.email})")
        print(f"Entered OTP: {otp_code}")
        print(f"OTP Secret Exists: {bool(user.otp_secret)}")
        print(f"{'='*70}\n")
        
        if user.verify_otp(otp_code):
            user.email_verified = True
            user.otp_secret = None  # Clear OTP secret after verification
            user.otp_created_at = None
            user.save()  # Save to Firebase
            
            # Clear session
            session.pop('pending_verification_user_id', None)
            
            login_user(user, remember=True)
            flash('✅ Email verified successfully! Welcome to your dashboard.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('❌ Invalid or expired verification code! Please try again or request a new code.', 'error')
            return render_template('verify_email.html', user=user)
    
    return render_template('verify_email.html', user=user)


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """
    Resend OTP verification code
    """
    user_id = session.get('pending_verification_user_id') or (current_user.id if current_user.is_authenticated else None)
    
    if not user_id:
        flash('No pending verification found!', 'error')
        return redirect(url_for('auth.register'))
    
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.register'))
    
    if user.email_verified:
        flash('Email already verified!', 'info')
        return redirect(url_for('auth.login'))
    
    try:
        # Generate new OTP
        otp_code = user.generate_otp()
        user.save()  # Save to Firebase
        
        # Send OTP email
        send_otp_email_async(user.email, user.username, otp_code)
        flash('✅ New verification code is being sent to your email!', 'success')
    except Exception as e:
        flash(f'Error sending verification code: {str(e)}', 'error')
    
    return redirect(url_for('auth.verify_email'))


@auth_bp.route('/request-verification', methods=['GET', 'POST'])
@login_required
def request_verification():
    """
    Allow existing users to verify their email
    """
    if current_user.email_verified:
        flash('Your email is already verified!', 'info')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        try:
            # Generate OTP
            otp_code = current_user.generate_otp()
            current_user.save()  # Save to Firebase
            
            # Send OTP email
            send_otp_email_async(current_user.email, current_user.username, otp_code)
            flash('✅ Verification code is being sent to your email!', 'success')
            
            return redirect(url_for('auth.verify_email'))
        except Exception as e:
            flash(f'Error sending verification code: {str(e)}', 'error')
            return redirect(url_for('auth.request_verification'))
    
    return render_template('request_verification.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Forgot password - Request OTP for password reset
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Email address is required!', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        # Check if user exists in Firebase
        user = User.query_by_email(email)
        
        if not user:
            # Don't reveal if email exists or not (security)
            flash('If an account with this email exists, an OTP has been sent to reset your password.', 'info')
            return redirect(url_for('auth.login'))
        
        try:
            # Generate OTP
            otp_code = user.generate_otp()
            user.save()  # Save to Firebase
            
            # Store user_id in session for password reset
            session['reset_user_id'] = user.id
            
            # Send password reset email
            if send_password_reset_email(user.email, user.username, otp_code):
                flash('Password reset OTP sent to your email! Valid for 10 minutes.', 'success')
            else:
                flash('OTP generated! Check console in debug mode.', 'warning')
            
            return redirect(url_for('auth.reset_password'))
        except Exception as e:
            flash(f'Error generating reset code: {str(e)}', 'error')
            return redirect(url_for('auth.forgot_password'))
    
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """
    Reset password using OTP
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Check if reset session exists
    user_id = session.get('reset_user_id')
    if not user_id:
        flash('Please request a password reset first.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.get_by_id(user_id)
    if not user:
        session.pop('reset_user_id', None)
        flash('Invalid reset session. Please try again.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not otp_code or not new_password or not confirm_password:
            flash('All fields are required!', 'error')
            return redirect(url_for('auth.reset_password'))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return redirect(url_for('auth.reset_password'))
        
        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('auth.reset_password'))
        
        # Verify OTP
        if not user.verify_otp(otp_code):
            flash('Invalid or expired OTP code!', 'error')
            return redirect(url_for('auth.reset_password'))
        
        try:
            # Update password
            user.set_password(new_password)
            
            # Clear OTP data
            user.otp_secret = None
            user.otp_created_at = None
            
            user.save()  # Save to Firebase
            
            # Clear reset session
            session.pop('reset_user_id', None)
            
            flash('Password reset successfully! You can now login with your new password.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error resetting password: {str(e)}', 'error')
            return redirect(url_for('auth.reset_password'))
    
    return render_template('reset_password.html')


@auth_bp.route('/resend-reset-otp', methods=['GET'])
def resend_reset_otp():
    """
    Resend password reset OTP
    """
    user_id = session.get('reset_user_id')
    if not user_id:
        flash('Please request a password reset first.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.get_by_id(user_id)
    if not user:
        session.pop('reset_user_id', None)
        flash('Invalid reset session. Please try again.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    try:
        # Generate new OTP
        otp_code = user.generate_otp()
        user.save()  # Save to Firebase
        
        # Send email
        if send_password_reset_email(user.email, user.username, otp_code):
            flash('New password reset OTP sent to your email!', 'success')
        else:
            flash('New OTP generated! Check console in debug mode.', 'warning')
        
        return redirect(url_for('auth.reset_password'))
    except Exception as e:
        flash(f'Error resending OTP: {str(e)}', 'error')
        return redirect(url_for('auth.reset_password'))
