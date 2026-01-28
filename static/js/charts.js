/*
   Smart Task & Expense Intelligence System
   JavaScript for Charts and Interactions
   Uses Chart.js for visualizations
*/

// Utility function to format currency
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

// Chart color palette
const chartColors = {
    primary: '#007bff',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    info: '#17a2b8',
    secondary: '#6c757d',
    light: '#e9ecef'
};

// Default Chart.js options
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.plugins.legend.labels.font.size = 12;
Chart.defaults.plugins.legend.labels.font.weight = '600';
Chart.defaults.plugins.legend.labels.padding = 15;

// Task Toggle Status Function
function toggleTaskStatus(taskId) {
    const url = `/tasks/${taskId}/toggle`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            showNotification(data.message, 'success');
            
            // Reload page or update UI
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred', 'error');
    });
}

// Show notification function
function showNotification(message, type = 'info') {
    const alertClass = `alert-${type === 'error' ? 'danger' : type}`;
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; max-width: 400px;" 
             role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const alertContainer = document.createElement('div');
    alertContainer.innerHTML = alertHtml;
    document.body.appendChild(alertContainer.firstElementChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.position-fixed.alert');
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

// Initialize charts when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all charts
    initializeDashboardCharts();
    
    // Add event listeners
    setupEventListeners();
});

function initializeDashboardCharts() {
    // Check if task chart exists (dashboard page)
    const taskChartElement = document.getElementById('taskChart');
    if (taskChartElement) {
        // Charts are already initialized in the template
        // This is just a placeholder for future enhancements
    }
}

function setupEventListeners() {
    // Setup form validations
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Setup delete confirmations
    const deleteButtons = document.querySelectorAll('button[onclick*="confirm"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
}

// Export chart as image (optional enhancement)
function downloadChart(canvasId, filename = 'chart.png') {
    const canvas = document.getElementById(canvasId);
    if (canvas) {
        const link = document.createElement('a');
        link.href = canvas.toDataURL();
        link.download = filename;
        link.click();
    }
}

// Print specific section
function printSection(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const printWindow = window.open('', '', 'width=800,height=600');
        printWindow.document.write(element.innerHTML);
        printWindow.document.close();
        printWindow.print();
    }
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Calculate days until deadline
function daysUntilDeadline(deadlineString) {
    const deadline = new Date(deadlineString);
    const today = new Date();
    const diffTime = deadline - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

// Update real-time statistics
function updateStats() {
    // This function can be called periodically to update statistics
    const dashboardUrl = '/dashboard/api/task-stats';
    
    fetch(dashboardUrl)
        .then(response => response.json())
        .then(data => {
            const taskStatsElement = document.getElementById('taskStats');
            if (taskStatsElement) {
                taskStatsElement.innerHTML = `
                    Completed: ${data.completed} | Pending: ${data.pending}
                `;
            }
        })
        .catch(error => console.error('Error updating stats:', error));
}

// Search functionality
function filterExpensesByCategory(category) {
    const rows = document.querySelectorAll('table tbody tr');
    rows.forEach(row => {
        if (category === 'all' || row.textContent.includes(category)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Validation helpers
function isValidAmount(amount) {
    return !isNaN(amount) && parseFloat(amount) > 0;
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Initialize tooltips (if using Bootstrap tooltips)
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Local storage helpers for preferences
function saveUserPreference(key, value) {
    try {
        localStorage.setItem(`task_expense_${key}`, JSON.stringify(value));
    } catch (e) {
        console.warn('Could not save preference:', e);
    }
}

function getUserPreference(key, defaultValue = null) {
    try {
        const value = localStorage.getItem(`task_expense_${key}`);
        return value ? JSON.parse(value) : defaultValue;
    } catch (e) {
        console.warn('Could not retrieve preference:', e);
        return defaultValue;
    }
}

// Theme management (for future enhancement)
function setTheme(theme = 'light') {
    document.documentElement.setAttribute('data-theme', theme);
    saveUserPreference('theme', theme);
}

function getTheme() {
    return getUserPreference('theme', 'light');
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = getTheme();
    if (savedTheme) {
        setTheme(savedTheme);
    }
});

// Responsive behavior
window.addEventListener('resize', function() {
    // Adjust charts if window is resized
    Chart.helpers.each(Chart.instances, function(instance) {
        instance.chart.update();
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl+S or Cmd+S to save forms
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        const form = document.querySelector('form');
        if (form) {
            form.submit();
        }
    }
    
    // Escape to go back
    if (event.key === 'Escape') {
        // Can be customized based on page context
    }
});

// Console logging (development)
console.log('Smart Task & Expense Intelligence System - JS Loaded');
