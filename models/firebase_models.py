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
                   'otp_created_at', 'last_login', 'completion_date', 'createdAt',
                   'creationTimestamp', 'created_on', 'createdDate']
    
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
        """Verify OTP code with extended time window"""
        if not self.otp_secret:
            print(f"⚠️ OTP Verification Failed: No OTP secret found")
            return False
            
        # Check OTP age (10 minute expiry)
        if self.otp_created_at:
            try:
                created_at = self.otp_created_at
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                if isinstance(created_at, datetime):
                    age_seconds = (datetime.utcnow() - created_at).total_seconds()
                    if age_seconds > 600:  # 10 minutes
                        print(f"⚠️ OTP Verification Failed: OTP expired ({age_seconds:.0f}s old, max 600s)")
                        return False
            except Exception as e:
                print(f"⚠️ OTP age check error: {str(e)}")
                pass
        
        # Verify OTP with window for time drift
        # window=10 allows codes from up to 5 minutes before/after (10 * 30 seconds)
        totp = pyotp.TOTP(self.otp_secret)
        
        # Try verification with extended window
        result = totp.verify(otp_code, valid_window=10)
        
        if result:
            print(f"✅ OTP Verification Successful: {otp_code}")
        else:
            print(f"❌ OTP Verification Failed: Invalid code '{otp_code}'")
            print(f"   Expected current code: {totp.now()}")
            print(f"   OTP Secret exists: {bool(self.otp_secret)}")
            if self.otp_created_at:
                created_at = self.otp_created_at
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                age = (datetime.utcnow() - created_at).total_seconds()
                print(f"   OTP age: {age:.0f} seconds")
        
        return result
    
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
    CATEGORIES = ['Work', 'Personal', 'Education', 'Health', 'Finance', 'Shopping', 'Other']
    
    def __init__(self):
        self.id = None
        self.user_id = None
        self.title = None
        self.description = None
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

    def _parse_date_value(self, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
            except (ValueError, TypeError):
                return None
        if isinstance(value, dict):
            seconds = value.get('seconds') or value.get('_seconds')
            if seconds is not None:
                try:
                    return datetime.utcfromtimestamp(seconds).date()
                except (ValueError, OSError):
                    return None
        if hasattr(value, 'timestamp'):
            try:
                return datetime.utcfromtimestamp(value.timestamp()).date()
            except (ValueError, OSError):
                return None
        return None

    def get_creation_date(self):
        candidates = [
            self.created_at,
            getattr(self, 'createdAt', None),
            getattr(self, 'creationTimestamp', None),
            getattr(self, 'created_on', None),
            getattr(self, 'createdDate', None)
        ]
        for value in candidates:
            parsed = self._parse_date_value(value)
            if parsed:
                return parsed
        return datetime.utcnow().date()
    
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
        if not self.deadline:
            try:
                created_at = self.created_at
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                if isinstance(created_at, datetime):
                    days_active = (datetime.utcnow().date() - created_at.date()).days + 1
                    days_active = max(days_active, 1)
                    total_completions = self.get_total_completions()
                    if total_completions >= days_active:
                        return 100
                    return min((self.current_streak / days_active) * 100, 100)
            except Exception:
                pass
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
    
    def get_calendar_data(self, year, month, creation_date=None):
        """
        Generate calendar data with completion status for each day.
        Handles Daily, Weekly, and Monthly habit types.
        Calendar timeline starts from habit creation date.
        
        Returns dict with calendar structure and day colors:
        - 'green': Completed for the required period
        - 'red': Missed for the required period
        - 'gray': Future dates
        - 'unavailable': Dates before habit creation
        """
        import calendar as cal
        from firebase_db import firebase_db as db_instance
        
        # Parse creation date if provided
        if creation_date is None:
            creation_date = self.get_creation_date()
        elif isinstance(creation_date, datetime):
            creation_date = creation_date.date()
        
        # Get all completions for this habit
        completions = db_instance.query(HabitCompletion.COLLECTION).where(
            'habit_id', '==', str(self.id)
        ).get()
        
        # Convert completion dates to date objects for easy lookup
        completion_dates = set()
        if completions:
            for completion in completions:
                try:
                    comp_date = completion.get('completion_date')
                    if isinstance(comp_date, str):
                        comp_date = datetime.fromisoformat(comp_date).date()
                    else:
                        comp_date = comp_date.date() if hasattr(comp_date, 'date') else None
                    
                    if comp_date:
                        completion_dates.add(comp_date)
                except Exception:
                    pass
        
        # Build calendar structure starting from creation date
        num_days = cal.monthrange(year, month)[1]
        calendar_days = []
        
        for day in range(1, num_days + 1):
            current_date = datetime(year, month, day).date()
            # Determine color based on creation date boundary
            color = self._get_day_color(current_date, completion_dates, creation_date)
            
            calendar_days.append({
                'day': day,
                'date': current_date.isoformat(),
                'color': color,  # 'green', 'red', 'gray', or 'unavailable'
                'completed': color == 'green'
            })
        
        return {
            'days': calendar_days,
            'month': month,
            'year': year,
            'month_name': datetime(year, month, 1).strftime('%B'),
            'week_start': 0,  # Monday
            'creation_date': creation_date.isoformat()
        }
    
    def _get_day_color(self, date, completion_dates, creation_date=None):
        """
        Determine color for a specific day based on habit frequency and completion status.
        
        Daily: Green if completed on that date, Red if not
        Weekly: Green if completed at least once in that week, Red if not
        Monthly: Green if completed at least once in that month, Red if not
        Gray: If date is in the future (not yet evaluable)
        Unavailable: If date is before habit creation date
        """
        from datetime import timedelta
        
        # Parse creation date if provided
        if creation_date is None:
            creation_date = self.get_creation_date()
        elif isinstance(creation_date, datetime):
            creation_date = creation_date.date()
        
        today = datetime.utcnow().date()
        
        # Dates before creation are unavailable (not in scope for this habit)
        if date < creation_date:
            return 'unavailable'
        
        # Future dates are gray (not yet evaluable)
        if date > today:
            return 'gray'
        
        # Handle Daily frequency
        if self.frequency == self.FREQUENCY_DAILY:
            if date in completion_dates:
                return 'green'
            else:
                return 'red'
        
        # Handle Weekly frequency
        # Green if completed at least once within the defined week (Mon-Sun)
        elif self.frequency == self.FREQUENCY_WEEKLY:
            # Get the start of the week (Monday)
            week_start = date - timedelta(days=date.weekday())
            week_end = week_start + timedelta(days=6)
            
            # Check if any completion exists in this week
            for comp_date in completion_dates:
                if week_start <= comp_date <= week_end:
                    return 'green'
            
            # If week is not fully past, show red only if week has ended
            if week_end <= today:
                return 'red'
            else:
                return 'gray'
        
        # Handle Monthly frequency
        # Green if completed at least once within the month
        elif self.frequency == self.FREQUENCY_MONTHLY:
            month_start = datetime(date.year, date.month, 1).date()
            # Last day of month
            if date.month == 12:
                month_end = datetime(date.year + 1, 1, 1).date() - timedelta(days=1)
            else:
                month_end = datetime(date.year, date.month + 1, 1).date() - timedelta(days=1)
            
            # Check if any completion exists in this month
            for comp_date in completion_dates:
                if month_start <= comp_date <= month_end:
                    return 'green'
            
            # If month has ended, show red; otherwise gray
            if month_end <= today:
                return 'red'
            else:
                return 'gray'
        
        return 'gray'
    
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
