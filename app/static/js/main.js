/**
 * RentHive JavaScript
 * Version: 7.0
 */

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    initAutoHideAlerts();
    
    // Initialize tooltips if Bootstrap is available
    initTooltips();
    
    // Form validation enhancements
    initFormValidation();
    
    // Confirm dialogs for destructive actions
    initConfirmDialogs();
    
    // Number formatting
    formatCurrency();
    
    // Initialize date inputs with today's date as max
    initDateInputs();
});


/**
 * Auto-hide alerts after 5 seconds
 */
function initAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}


/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}


/**
 * Form validation enhancements
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}


/**
 * Confirm dialogs for delete/destructive actions
 */
function initConfirmDialogs() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}


/**
 * Format currency values
 */
function formatCurrency() {
    const currencyElements = document.querySelectorAll('.currency');
    
    currencyElements.forEach(element => {
        const value = parseFloat(element.textContent);
        if (!isNaN(value)) {
            element.textContent = '₹' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
        }
    });
}


/**
 * Initialize date inputs
 */
function initDateInputs() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        if (input.hasAttribute('max-today')) {
            input.setAttribute('max', today);
        }
    });
}


/**
 * Calculate bill total (for bill creation form)
 */
function calculateBillTotal() {
    const rent = parseFloat(document.getElementById('rent_amount')?.value) || 0;
    const electricityUnits = parseFloat(document.getElementById('electricity_units')?.value) || 0;
    const electricityRate = parseFloat(document.getElementById('electricity_rate')?.value) || 0;
    const water = parseFloat(document.getElementById('water_amount')?.value) || 0;
    const maintenance = parseFloat(document.getElementById('maintenance_amount')?.value) || 0;
    const other = parseFloat(document.getElementById('other_charges')?.value) || 0;
    
    const electricityAmount = electricityUnits * electricityRate;
    const total = rent + electricityAmount + water + maintenance + other;
    
    // Display total if element exists
    const totalElement = document.getElementById('total_amount_display');
    if (totalElement) {
        totalElement.textContent = '₹' + total.toFixed(2);
    }
    
    return total;
}


/**
 * Show loading state on button
 */
function setButtonLoading(button, loading = true) {
    if (loading) {
        button.classList.add('btn-loading');
        button.disabled = true;
    } else {
        button.classList.remove('btn-loading');
        button.disabled = false;
    }
}


/**
 * Show notification toast
 */
function showToast(message, type = 'info') {
    // Create toast element
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    // Add to container
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '11';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove after hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}


/**
 * Validate phone number
 */
function validatePhone(phone) {
    const phoneRegex = /^[6-9]\d{9}$/;
    return phoneRegex.test(phone);
}


/**
 * Validate email
 */
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}


/**
 * Format date to DD-MM-YYYY
 */
function formatDate(date) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}-${month}-${year}`;
}


/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}


/**
 * Search/filter table rows
 */
function filterTable(searchInput, tableId) {
    const filter = searchInput.value.toUpperCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 1; i < rows.length; i++) {
        let found = false;
        const cells = rows[i].getElementsByTagName('td');
        
        for (let j = 0; j < cells.length; j++) {
            const cell = cells[j];
            if (cell) {
                const textValue = cell.textContent || cell.innerText;
                if (textValue.toUpperCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
        }
        
        rows[i].style.display = found ? '' : 'none';
    }
}


/**
 * Export table to CSV
 */
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let row of rows) {
        const cells = row.querySelectorAll('td, th');
        const rowData = Array.from(cells).map(cell => {
            return '"' + cell.textContent.replace(/"/g, '""') + '"';
        });
        csv.push(rowData.join(','));
    }
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}


/**
 * Print content
 */
function printContent(elementId) {
    const content = document.getElementById(elementId).innerHTML;
    const printWindow = window.open('', '', 'height=600,width=800');
    
    printWindow.document.write('<html><head><title>Print</title>');
    printWindow.document.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">');
    printWindow.document.write('</head><body>');
    printWindow.document.write(content);
    printWindow.document.write('</body></html>');
    
    printWindow.document.close();
    printWindow.print();
}


// Make functions available globally
window.RentHive = {
    calculateBillTotal,
    setButtonLoading,
    showToast,
    validatePhone,
    validateEmail,
    formatDate,
    debounce,
    filterTable,
    exportTableToCSV,
    printContent
};
