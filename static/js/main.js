// Common JavaScript functions for the Shop Management System

// Format currency
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Confirm action
function confirmAction(message) {
    return confirm(message);
}

// Initialize tooltips or other UI enhancements
document.addEventListener('DOMContentLoaded', function() {
    console.log('Shop Management System loaded');
});
