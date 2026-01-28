"""
Expense management routes with Firebase (CRUD operations)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models.firebase_models import Expense, User

# Create blueprint
expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@expenses_bp.route('/')
@login_required
def index():
    """
    Display all expenses for current user - Firebase version
    """
    # Get filter parameters
    category_filter = request.args.get('category', 'all')
    month_filter = request.args.get('month', '')
    
    # Get all expenses from Firebase
    expenses = Expense.query_by_user(current_user.id)
    
    # Apply filters
    if category_filter != 'all':
        expenses = [e for e in expenses if e.category == category_filter]
    
    if month_filter:
        try:
            year, month = map(int, month_filter.split('-'))
            expenses = [
                e for e in expenses
                if ((e.date if isinstance(e.date, datetime) else datetime.fromisoformat(e.date)).year == year and
                    (e.date if isinstance(e.date, datetime) else datetime.fromisoformat(e.date)).month == month)
            ]
        except (ValueError, AttributeError):
            pass
    
    # Order by date (newest first)
    expenses = sorted(expenses, key=lambda e: e.date, reverse=True)
    
    # Calculate statistics
    total_amount = sum(e.amount for e in expenses)
    current_user_data = User.get_by_id(current_user.id)
    balance_amount = current_user_data.balance_amount if current_user_data else 0
    
    # Category-wise totals
    category_totals = {}
    for expense in expenses:
        if expense.category not in category_totals:
            category_totals[expense.category] = 0
        category_totals[expense.category] += expense.amount
    
    return render_template(
        'expenses.html',
        expenses=expenses,
        total_amount=total_amount,
        balance_amount=balance_amount,
        category_totals=category_totals,
        category_filter=category_filter,
        month_filter=month_filter,
        Expense=Expense
    )

@expenses_bp.route('/update-balance', methods=['POST'])
@login_required
def update_balance():
    """Update user's balance amount manually - Firebase version"""
    amount_str = request.form.get('balance_amount', '').strip()
    try:
        amount = float(amount_str)
        current_user.balance_amount = amount
        current_user.save()
        flash(f'Balance updated to ₹{amount:.2f}', 'success')
    except ValueError:
        flash('Please enter a valid balance amount.', 'error')
    except Exception as e:
        flash(f'Error updating balance: {str(e)}', 'error')
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new expense - Firebase version
    """
    if request.method == 'POST':
        try:
            amount_str = request.form.get('amount', '').strip()
            category = request.form.get('category', 'Other').strip()
            date_str = request.form.get('date', '')
            description = request.form.get('description', '').strip()
            payment_method = request.form.get('payment_method', 'Cash')
            
            # Handle custom category
            if category == '__custom__':
                category = request.form.get('category_custom', 'Other').strip()
            
            # Validation
            if not amount_str:
                flash('Amount is required!', 'error')
                return redirect(url_for('expenses.create'))
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    flash('Amount must be greater than 0!', 'error')
                    return redirect(url_for('expenses.create'))
            except ValueError:
                flash('Please enter a valid amount!', 'error')
                return redirect(url_for('expenses.create'))
            
            # Parse date
            if not date_str:
                date_iso = datetime.utcnow().isoformat()
            else:
                try:
                    date_iso = datetime.fromisoformat(date_str).isoformat()
                except ValueError:
                    flash('Invalid date format!', 'error')
                    return redirect(url_for('expenses.create'))
            
            # Create expense in Firebase
            new_expense = Expense()
            new_expense.user_id = str(current_user.id)
            new_expense.amount = amount
            new_expense.category = category
            new_expense.date = date_iso
            new_expense.description = description
            new_expense.payment_method = payment_method
            new_expense.save()
            
            # Deduct from user balance
            current_user.balance_amount = (current_user.balance_amount or 0) - amount
            current_user.save()
            
            flash(f'Expense of ₹{amount:.2f} recorded successfully!', 'success')
            return redirect(url_for('expenses.index'))
        except Exception as e:
            flash(f'Error creating expense: {str(e)}', 'error')
            return redirect(url_for('expenses.create'))
    
    return render_template('expense_form.html', expense=None, Expense=Expense)

@expenses_bp.route('/<expense_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(expense_id):
    """Edit expense - Firebase version"""
    expense = Expense.get_by_id(expense_id)
    
    if not expense or str(expense.user_id) != str(current_user.id):
        flash('Expense not found!', 'error')
        return redirect(url_for('expenses.index'))
    
    if request.method == 'POST':
        try:
            amount_str = request.form.get('amount', '').strip()
            category = request.form.get('category', 'Other').strip()
            date_str = request.form.get('date', '')
            description = request.form.get('description', '').strip()
            payment_method = request.form.get('payment_method', 'Cash')
            
            # Handle custom category
            if category == '__custom__':
                category = request.form.get('category_custom', 'Other').strip()
            
            # Validation
            if not amount_str:
                flash('Amount is required!', 'error')
                return redirect(url_for('expenses.edit', expense_id=expense_id))
            
            try:
                new_amount = float(amount_str)
                if new_amount <= 0:
                    flash('Amount must be greater than 0!', 'error')
                    return redirect(url_for('expenses.edit', expense_id=expense_id))
            except ValueError:
                flash('Please enter a valid amount!', 'error')
                return redirect(url_for('expenses.edit', expense_id=expense_id))
            
            # Calculate difference for balance adjustment
            old_amount = expense.amount
            difference = new_amount - old_amount
            
            # Update expense
            expense.amount = new_amount
            expense.category = category
            expense.description = description
            expense.payment_method = payment_method
            
            if date_str:
                try:
                    expense.date = datetime.fromisoformat(date_str).isoformat()
                except ValueError:
                    flash('Invalid date format!', 'error')
                    return redirect(url_for('expenses.edit', expense_id=expense_id))
            
            expense.save()
            
            # Adjust balance by the difference
            current_user.balance_amount = (current_user.balance_amount or 0) - difference
            current_user.save()
            
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('expenses.index'))
        except Exception as e:
            flash(f'Error updating expense: {str(e)}', 'error')
            return redirect(url_for('expenses.edit', expense_id=expense_id))
    
    return render_template('expense_form.html', expense=expense, Expense=Expense)

@expenses_bp.route('/<expense_id>/delete', methods=['POST'])
@login_required
def delete(expense_id):
    """Delete expense - Firebase version"""
    expense = Expense.get_by_id(expense_id)
    
    if not expense or str(expense.user_id) != str(current_user.id):
        flash('Expense not found!', 'error')
        return redirect(url_for('expenses.index'))
    
    try:
        amount = expense.amount
        expense.delete()
        
        # Refund balance when deleting an expense
        current_user.balance_amount = (current_user.balance_amount or 0) + amount
        current_user.save()
        
        flash(f'Expense of ₹{amount:.2f} deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting expense: {str(e)}', 'error')
    
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/api/monthly-stats')
@login_required
def monthly_stats():
    """
    API endpoint to get monthly expense statistics
    Used by Chart.js for visualization - Firebase version
    """
    # Get all expenses for user
    expenses = Expense.query_by_user(current_user.id)
    
    monthly_data = {}
    for expense in expenses:
        try:
            # expense.date is already a datetime object after from_dict conversion
            expense_date = expense.date if isinstance(expense.date, datetime) else datetime.fromisoformat(expense.date)
            month_key = expense_date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += expense.amount
        except (ValueError, AttributeError):
            pass
    
    # Sort by month and get last 6
    sorted_months = sorted(monthly_data.keys())[-6:]
    
    return jsonify({
        'months': sorted_months,
        'amounts': [monthly_data.get(m, 0) for m in sorted_months]
    })

@expenses_bp.route('/api/category-stats')
@login_required
def category_stats():
    """
    API endpoint to get category-wise expense statistics
    Used by Chart.js for visualization - Firebase version
    """
    expenses = Expense.query_by_user(current_user.id)
    
    category_data = {}
    for expense in expenses:
        if expense.category not in category_data:
            category_data[expense.category] = 0
        category_data[expense.category] += expense.amount
    
    return jsonify({
        'categories': list(category_data.keys()),
        'amounts': list(category_data.values())
    })
