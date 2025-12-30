// Custom JavaScript functions for Business Suite Pro

// Utility function to show loading state
function showLoading(element) {
    element.innerHTML = '<div class="loading-spinner"></div>';
}

// Utility function for API error handling
function handleApiError(error, message = 'An error occurred') {
    console.error('API Error:', error);
    alert(`${message}: ${error.message || 'Please try again.'}`);
}

// Form validation helper
function validateForm(formData, requiredFields) {
    for (const field of requiredFields) {
        if (!formData[field] || formData[field].toString().trim() === '') {
            return { valid: false, field: field, message: `${field} is required` };
        }
    }
    return { valid: true };
}

// Currency formatting
function formatCurrency(amount, currency = 'KES') {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(amount);
}

// Date formatting
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-KE', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
