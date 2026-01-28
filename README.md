# Smart Task & Expense Intelligence System

A comprehensive personal productivity and expense analytics system designed for students and freelancers.

## 🎯 Features

### 1. **Authentication Module**
- User Registration with validation
- Secure Login/Logout
- Password hashing with Werkzeug
- Session management with Flask-Login
- Remember me functionality

### 2. **Task Management (CRUD)**
Each task includes:
- **Title** - Task name
- **Description** - Detailed information
- **Priority** - Low, Medium, High
- **Category** - Work, Personal, Education, Health, Finance, Shopping, Other
- **Deadline** - Target completion date
- **Status** - Pending or Completed

Features:
- ✅ Create, Read, Update, Delete tasks
- ✅ Mark tasks as completed
- ✅ Automatic deadline detection
- ✅ Priority-based filtering
- ✅ Status-based filtering
- ✅ Overdue task warnings

### 3. **Expense Management (CRUD)**
Each expense includes:
- **Amount** - Expense value ($)
- **Category** - Food & Dining, Transportation, Shopping, Entertainment, etc.
- **Date** - Transaction date and time
- **Description** - Optional notes

Features:
- ✅ Record new expenses
- ✅ Edit or delete expenses
- ✅ Category-wise breakdown
- ✅ Monthly expense trends
- ✅ Average daily spending calculation
- ✅ High expense alerts

### 4. **Analytics Dashboard**
Visual representations using Chart.js:
- 📊 Tasks by Status (Doughnut Chart)
- 📊 Tasks by Priority (Bar Chart)
- 📊 Expenses by Category (Pie Chart)
- 📊 Monthly Expense Trend (Line Chart)
- 📈 Key Statistics Cards
- 📌 Upcoming Tasks Widget

### 5. **AI Insights & ML Module** (ml/insights.py)

#### Rule-Based Insights:
- **Task Insights:**
  - Detect overdue high-priority tasks
  - Calculate task completion rate
  - Identify pending high-priority tasks
  - Alert on tasks due soon

- **Expense Insights:**
  - Detect overspending (month-over-month comparison)
  - Identify highest spending categories
  - Flag large expenses (> $100)
  - Calculate average daily spending

- **Combined Analysis:**
  - Productivity vs. Financial health correlation
  - Overall performance assessment

#### Machine Learning Predictions:
- **Risk Level Prediction (Low/Medium/High):**
  - Factors: Overdue tasks + Spending trends
  - Rule-based scoring (viva-friendly & explainable)
  - Return insights with metrics

Example Output:
```
"High Risk Detected: 3 overdue tasks + High spending trend 
($1500/month avg). Recommend prioritizing task completion."
```

## 🛠️ Tech Stack

### Backend
- **Flask** 2.3.0 - Web framework
- **Flask-SQLAlchemy** 3.0.0 - ORM
- **Flask-Login** 0.6.2 - Authentication
- **Werkzeug** 2.3.0 - Security utilities
- **SQLite** - Default database (upgradable to MySQL)

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling (Blue-based theme)
- **Bootstrap 5** - Responsive framework
- **Chart.js** 3.9.1 - Data visualization
- **JavaScript** - Interactivity

### Machine Learning
- **scikit-learn** 1.2.0 - ML utilities
- **Rule-based logic** - Simple, explainable predictions

## 📂 Project Structure

```
smart_task_expense_system/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration settings
│
├── models/
│   ├── user.py                # User model (authentication)
│   ├── task.py                # Task model (CRUD)
│   └── expense.py             # Expense model (CRUD)
│
├── routes/
│   ├── auth.py                # Authentication routes
│   ├── tasks.py               # Task management routes
│   ├── expenses.py            # Expense management routes
│   └── dashboard.py           # Dashboard & analytics routes
│
├── ml/
│   └── insights.py            # AI insights generation
│
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── dashboard.html         # Dashboard with charts & insights
│   ├── tasks.html             # Task list view
│   ├── task_form.html         # Task creation/edit form
│   ├── expenses.html          # Expense list view
│   └── expense_form.html      # Expense creation/edit form
│
├── static/
│   ├── css/
│   │   └── style.css          # Custom styling
│   └── js/
│       └── charts.js          # Chart.js configurations
│
└── README.md                   # This file
```

## 🚀 How to Run

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- VS Code (recommended)

### Installation & Setup

1. **Clone/Extract the project:**
```bash
cd smart_task_expense_system
```

2. **Create a virtual environment (optional but recommended):**
```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python app.py
```

5. **Access the application:**
```
🌐 Open your browser and go to: http://localhost:5000
```

### Demo Credentials
- **Username:** `demo`
- **Password:** `demo123`

## 📝 Usage Guide

### 1. **Create Account**
- Go to Registration page
- Fill in username, email, and password
- Click "Register"

### 2. **Login**
- Use your credentials to login
- Check "Remember me" to stay logged in

### 3. **Add Tasks**
- Click "➕ Add Task" from Dashboard
- Fill in Title, Priority, Category, and Deadline
- Click "Create Task"

### 4. **Manage Tasks**
- View all tasks with filters (Status, Priority)
- Edit tasks to update details
- Mark tasks as completed
- Delete tasks as needed

### 5. **Record Expenses**
- Click "➕ Add Expense"
- Enter Amount, Category, and optional Description
- Click "Record Expense"

### 6. **View Analytics**
- Dashboard shows visual charts:
  - Task completion rates
  - Expense distribution by category
  - Monthly spending trends
- Read AI-generated insights and recommendations

### 7. **AI Insights**
- **Task Insights:** Alerts on overdue tasks, completion rates
- **Expense Insights:** Overspending alerts, category analysis
- **Risk Assessment:** Overall productivity and financial health score
- **Combined Analysis:** Correlations and recommendations

## 🤖 Machine Learning Features

### Insights Generation (ml/insights.py)

The ML module provides:

1. **Task Analysis:**
   - Completion rate calculation
   - Overdue task detection
   - High-priority task alerts
   - Upcoming deadline reminders

2. **Expense Analysis:**
   - Month-over-month spending comparison
   - Category-wise expense breakdown
   - Large expense detection
   - Daily spending average

3. **Risk Prediction:**
   - Scoring system: 0-4 points
   - Risk levels: Low, Medium, High
   - Explainable predictions with metrics
   - Actionable recommendations

### Example ML Logic:
```python
Risk Score = (overdue_tasks_count) + (spending_level)
- Risk Score >= 3: HIGH RISK
- Risk Score 1-2: MEDIUM RISK
- Risk Score 0: LOW RISK
```

## 🎨 UI/UX Features

- **Responsive Design:** Works on desktop, tablet, mobile
- **Blue-based Color Theme:** Professional and clean
- **Interactive Charts:** Real-time data visualization
- **Intuitive Navigation:** Easy access to all features
- **Form Validation:** Prevents invalid data entry
- **Success/Error Messages:** User feedback on actions
- **Accessibility:** WCAG compliance considerations

## 📊 Dashboard Components

1. **Key Statistics:**
   - Total Tasks, Completed, Pending, Overdue
   - Total Expenses, Current Month Total
   - Average Daily Spending

2. **Visual Charts:**
   - Task status distribution
   - Task priority breakdown
   - Expense category pie chart
   - Monthly expense trend line chart

3. **AI Insights Panel:**
   - Task management insights
   - Financial health insights
   - Combined productivity analysis
   - Risk assessment with metrics

4. **Upcoming Tasks Widget:**
   - Next 5 tasks by deadline
   - Priority indicators
   - Days remaining countdown

## 💾 Database Schema

### Users Table
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- first_name, last_name
- created_at, updated_at
```

### Tasks Table
```sql
- id (Primary Key)
- user_id (Foreign Key)
- title, description
- priority (Low/Medium/High)
- category
- deadline
- status (Pending/Completed)
- completed_at
- created_at, updated_at
```

### Expenses Table
```sql
- id (Primary Key)
- user_id (Foreign Key)
- amount
- category
- date
- description
- created_at, updated_at
```

## 🔐 Security Features

- Password hashing with Werkzeug
- SQL injection prevention (SQLAlchemy ORM)
- CSRF protection (Flask default)
- Session-based authentication
- User ownership verification (middleware)
- HttpOnly cookies
- SameSite cookie policy

## 🚀 Future Enhancements

- [ ] User profile customization
- [ ] Dark mode theme
- [ ] Email notifications
- [ ] Budget setting and alerts
- [ ] Recurring tasks/expenses
- [ ] Data export (CSV/PDF)
- [ ] Mobile app integration
- [ ] Advanced ML predictions (spending forecasting)
- [ ] Multi-user household management
- [ ] Integration with payment APIs
- [ ] Social sharing of insights
- [ ] API endpoints for mobile apps

## 🐛 Troubleshooting

### Database Errors
- Delete `task_expense.db` file and restart app
- Database will auto-initialize on first run

### Port Already in Use
- Change port in `app.py` (default: 5000)
- Or: `python app.py --port 5001`

### Import Errors
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python version: `python --version`

### Chart.js Not Loading
- Check browser console for errors
- Ensure CDN link is accessible
- Try clearing browser cache

## 📞 Support & Issues

- Check console logs for error messages
- Review Flask debug output
- Verify database file exists and is writable

## 📄 License

This project is created for academic purposes (Final Year Project).

## 👤 Author

Created as a Final Year Academic Project
- System Architecture: Flask + SQLAlchemy
- Frontend: Bootstrap 5 + Chart.js
- ML/AI: Rule-based insights (explainable)

## ✅ Viva-Safe Features

✓ Simple, readable code with comments
✓ Explainable ML logic (no black-box deep learning)
✓ Comprehensive documentation
✓ Demo data included
✓ Full CRUD operations implemented
✓ Professional UI/UX
✓ Database design follows best practices
✓ Error handling and validation
✓ Modular architecture

---

**Last Updated:** January 2026
**Version:** 1.0.0
**Status:** ✅ Fully Functional & Production Ready
