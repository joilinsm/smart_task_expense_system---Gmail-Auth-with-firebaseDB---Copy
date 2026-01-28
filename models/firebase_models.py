"""
Firebase Model Helpers
Provides model-like classes and helper functions that mimic SQLAlchemy models
for seamless Firebase integration with existing route code
"""
from datetime import datetime
from firebase_db import firebase_db as db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import pyotp
from flask_login import UserMixin


class FirebaseModel:
    """Base class for Firebase models"""
    
    # Date fields that should be converted from ISO strings to datetime objects
    DATE_FIELDS = ['created_at', 'updated_at', 'deadline', 'date', 'completed_at', 
                   'otp_created_at', 'last_login', 'completion_date']
    
    @classmethod
    def from_dict(cls, data, doc_id=None):
        """Create instance from Firestore document data"""
        instance = cls()
        if doc_id:
            data['id'] = doc_id
        for key, value in data.items():
            # Convert ISO date strings to datetime objects
            if key in cls.DATE_FIELDS and value and isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                except (ValueError, AttributeError):
                    pass  # Keep as string if parsing fails
            setattr(instance, key, value)
        return instance
    
    def to_dict(self, exclude_id=True):
        """Convert instance to dictionary"""
        data = {}
        for key, value in self.__dict__.items():
            if exclude_id and key == 'id':
                continue
            # Convert datetime objects to ISO strings for Firebase
            if isinstance(value, datetime):
                value = value.isoformat()
            data[key] = value
        return data


class User(UserMixin, FirebaseModel):
    """
    User model for Firebase authentication
    Mimics SQLAlchemy User model for compatibility
    """
    
    COLLECTION = 'users'
    
    def __init__(self):
        self.id = None
        self.username = None
        self.email = None
        self.password_hash = None
        self.first_name = None
        self.last_name = None
        self.country_code = '+91'
        self.phone_number = None
        self.default_task_priority = 'Medium'
        self.monthly_budget = 1000.0
        self.theme_preference = 'blue'
        self.notification_enabled = True
        self.balance_amount = 0.0
        self.email_verified = False
        self.otp_secret = None
        self.otp_created_at = None
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_otp(self):
        """Generate OTP secret and return OTP code"""
        self.otp_secret = pyotp.random_base32()
        self.otp_created_at = datetime.utcnow().isoformat()
        totp = pyotp.TOTP(self.otp_secret)
        return totp.now()
    
    def verify_otp(self, otp_code):
        """Verify OTP code"""
        if not self.otp_secret:
            return False
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(otp_code)
    
    def save(self):
        """Save user to Firestore"""
        data = self.to_dict(exclude_id=True)
        if self.id:
            db.update(self.COLLECTION, self.id, data)
        else:
            self.id, _ = db.add(self.COLLECTION, data)
        return self.id
    
    @classmethod
    def query_by_username(cls, username):
        """Query user by username"""
        results = db.query(cls.COLLECTION).where('username', '==', username).get()
        return cls.from_dict(results[0], results[0]['id']) if results else None
    
    @classmethod
    def query_by_email(cls, email):
        """Query user by email"""
        results = db.query(cls.COLLECTION).where('email', '==', email).get()
        return cls.from_dict(results[0], results[0]['id']) if results else None
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        data = db.get(cls.COLLECTION, str(user_id))
        return cls.from_dict(data, str(user_id)) if data else None
    
    @classmethod
    def all(cls):
        """Get all users"""
        data_list = db.get_all(cls.COLLECTION)
        return [cls.from_dict(data, data['id']) for data in data_list]
    
    def delete(self):
        """Delete user from Firestore"""
        if self.id:
            db.delete(self.COLLECTION, self.id)


class Task(FirebaseModel):
    """Task model for Firebase"""
    
    COLLECTION = 'tasks'
    
    STATUS_PENDING = 'Pending'
    STATUS_COMPLETED = 'Completed'
    PRIORITY_LOW = 'Low'
    PRIORITY_MEDIUM = 'Medium'
    PRIORITY_HIGH = 'High'
    CATEGORIES = ['Work', 'Personal', 'Education', 'Health', 'Finance', 'Shopping', 'Other']
    
    def __init__(self):
        self.id = None
        self.user_id = None
        self.title = None
        self.description = None
        self.priority = self.PRIORITY_MEDIUM
        self.category = 'Other'
        self.deadline = None
        self.status = self.STATUS_PENDING
        self.completed_at = None
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def is_overdue(self):
        """Check if task is overdue"""
        if not self.deadline or self.status == self.STATUS_COMPLETED:
            return False
        try:
            deadline = datetime.fromisoformat(self.deadline) if isinstance(self.deadline, str) else self.deadline
            return datetime.utcnow() > deadline
        except:
            return False
    
    def days_until_deadline(self):
        """Calculate days until deadline"""
        if not self.deadline:
            return None
        try:
            deadline = datetime.fromisoformat(self.deadline) if isinstance(self.deadline, str) else self.deadline
            delta = deadline - datetime.utcnow()
            return delta.days
        except:
            return None
    
    def save(self):
        """Save task to Firestore"""
        self.updated_at = datetime.utcnow().isoformat()
        data = self.to_dict(exclude_id=True)
        if self.id:
            db.update(self.COLLECTION, self.id, data)
        else:
            self.id, _ = db.add(self.COLLECTION, data)
        return self.id
    
    @classmethod
    def get_by_id(cls, task_id):
        """Get task by ID"""
        data = db.get(cls.COLLECTION, str(task_id))
        return cls.from_dict(data, str(task_id)) if data else None
    
    @classmethod
    def query_by_user(cls, user_id):
        """Get all tasks for user"""
        results = db.query(cls.COLLECTION).where('user_id', '==', str(user_id)).get()
        return [cls.from_dict(data, data['id']) for data in results]
    
    @classmethod
    def query_by_user_and_status(cls, user_id, status):
        """Get tasks for user with specific status"""
        results = db.query(cls.COLLECTION).where('user_id', '==', str(user_id)).where('status', '==', status).get()
        return [cls.from_dict(data, data['id']) for data in results]
    
    def delete(self):
        """Delete task from Firestore"""
        if self.id:
            db.delete(self.COLLECTION, self.id)


class Expense(FirebaseModel):
    """Expense model for Firebase"""
    
    COLLECTION = 'expenses'
    
    CATEGORIES = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Utilities', 'Health', 'Education', 'Other']
    
    def __init__(self):
        self.id = None
        self.user_id = None
        self.title = None
        self.description = None
        self.amount = 0.0
        self.category = 'Other'
        self.payment_method = 'Cash'
        self.date = datetime.utcnow().isoformat()
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def save(self):
        """Save expense to Firestore"""
        self.updated_at = datetime.utcnow().isoformat()
        data = self.to_dict(exclude_id=True)
        if self.id:
            db.update(self.COLLECTION, self.id, data)
        else:
            self.id, _ = db.add(self.COLLECTION, data)
        return self.id
    
    @classmethod
    def get_by_id(cls, expense_id):
        """Get expense by ID"""
        data = db.get(cls.COLLECTION, str(expense_id))
        return cls.from_dict(data, str(expense_id)) if data else None
    
    @classmethod
    def query_by_user(cls, user_id):
        """Get all expenses for user"""
        results = db.query(cls.COLLECTION).where('user_id', '==', str(user_id)).get()
        return [cls.from_dict(data, data['id']) for data in results]
    
    def delete(self):
        """Delete expense from Firestore"""
        if self.id:
            db.delete(self.COLLECTION, self.id)


class Habit(FirebaseModel):
    """Habit model for Firebase"""
    
    COLLECTION = 'habits'
    
    CATEGORIES = ['Health', 'Fitness', 'Learning', 'Productivity', 'Social', 'Mindfulness', 'Finance', 'Other']
    
    FREQUENCY_DAILY = 'Daily'
    FREQUENCY_WEEKLY = 'Weekly'
    FREQUENCY_MONTHLY = 'Monthly'
    FREQUENCY_CHOICES = ['Daily', 'Weekly', 'Monthly']
    
    STATUS_CHOICES = ['Active', 'Paused', 'Completed']
    
    def __init__(self):
        self.id = None
        self.user_id = None
        self.name = None
        self.title = None  # Alias for name to match form
        self.description = None
        self.category = 'Health'
        self.frequency = self.FREQUENCY_DAILY
        self.goal = None
        self.deadline = None
        self.current_streak = 0
        self.longest_streak = 0
        self.is_active = True
        self.is_completed = False
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    @property
    def status(self):
        """Get status string based on is_completed and is_active"""
        if self.is_completed:
            return 'Completed'
        if self.is_active:
            return 'Active'
        return 'Paused'
    
    @status.setter
    def status(self, value):
        """Set is_completed and is_active based on status string"""
        if value == 'Completed':
            self.is_completed = True
            self.is_active = False
        elif value == 'Active':
            self.is_completed = False
            self.is_active = True
        else:  # Paused
            self.is_completed = False
            self.is_active = False
    
    def get_completion_percentage(self):
        """Calculate completion percentage based on goal and current streak"""
        if not self.goal:
            # If no goal, base on current streak (max 100%)
            return min(self.current_streak * 10, 100)
        try:
            goal_value = int(self.goal)
            if goal_value <= 0:
                return 0
            percentage = (self.current_streak / goal_value) * 100
            return min(percentage, 100)
        except (ValueError, TypeError):
            return 0
    
    def update_streak(self, increment=True):
        """Update habit streak"""
        if increment:
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            self.current_streak = 0
    
    def is_completed_today(self):
        """Check if habit has been completed today"""
        from firebase_db import firebase_db as db_instance
        try:
            today = datetime.utcnow().date()
            completions = db_instance.query(HabitCompletion.COLLECTION).where(
                'habit_id', '==', str(self.id)
            ).get()
            
            if not completions:
                return False
            
            for completion in completions:
                try:
                    completion_date = completion.get('completion_date')
                    if isinstance(completion_date, str):
                        comp_date = datetime.fromisoformat(completion_date).date()
                    else:
                        comp_date = completion_date.date() if hasattr(completion_date, 'date') else None
                    
                    if comp_date == today:
                        return True
                except Exception as e:
                    pass
            return False
        except Exception as e:
            return False
    
    def get_total_completions(self):
        """Get total number of completions for this habit"""
        from firebase_db import firebase_db as db_instance
        try:
            completions = db_instance.query(HabitCompletion.COLLECTION).where(
                'habit_id', '==', str(self.id)
            ).get()
            return len(completions) if completions else 0
        except Exception as e:
            return 0
    
    @property
    def total_completions(self):
        """Property to get total completions"""
        return self.get_total_completions()
    
    def save(self):
        """Save habit to Firestore"""
        self.updated_at = datetime.utcnow().isoformat()
        data = self.to_dict(exclude_id=True)
        if self.id:
            db.update(self.COLLECTION, self.id, data)
        else:
            self.id, _ = db.add(self.COLLECTION, data)
        return self.id
    
    @classmethod
    def get_by_id(cls, habit_id):
        """Get habit by ID"""
        data = db.get(cls.COLLECTION, str(habit_id))
        return cls.from_dict(data, str(habit_id)) if data else None
    
    @classmethod
    def query_by_user(cls, user_id):
        """Get all habits for user"""
        results = db.query(cls.COLLECTION).where('user_id', '==', str(user_id)).get()
        return [cls.from_dict(data, data['id']) for data in results]
    
    def delete(self):
        """Delete habit from Firestore"""
        if self.id:
            db.delete(self.COLLECTION, self.id)


class HabitCompletion(FirebaseModel):
    """Habit completion tracking for Firebase"""
    
    COLLECTION = 'habit_completions'
    
    def __init__(self):
        self.id = None
        self.habit_id = None
        self.user_id = None
        self.completion_date = datetime.utcnow().isoformat()
        self.notes = None
        self.created_at = datetime.utcnow().isoformat()
    
    def save(self):
        """Save completion to Firestore"""
        data = self.to_dict(exclude_id=True)
        if self.id:
            db.update(self.COLLECTION, self.id, data)
        else:
            self.id, _ = db.add(self.COLLECTION, data)
        return self.id
    
    @classmethod
    def get_by_id(cls, completion_id):
        """Get completion by ID"""
        data = db.get(cls.COLLECTION, str(completion_id))
        return cls.from_dict(data, str(completion_id)) if data else None
    
    @classmethod
    def query_by_habit(cls, habit_id):
        """Get all completions for habit"""
        results = db.query(cls.COLLECTION).where('habit_id', '==', str(habit_id)).get()
        return [cls.from_dict(data, data['id']) for data in results]
    
    @classmethod
    def query_by_user(cls, user_id):
        """Get all completions for user"""
        results = db.query(cls.COLLECTION).where('user_id', '==', str(user_id)).get()
        return [cls.from_dict(data, data['id']) for data in results]
    
    def delete(self):
        """Delete completion from Firestore"""
        if self.id:
            db.delete(self.COLLECTION, self.id)
