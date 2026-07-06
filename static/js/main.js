// Main JavaScript file for Цветочная Мафия Молдова CRM

// Global variables
let app = {
    flowers: [],
    categories: [],
    settings: {
        delivery_cost: 0,
        markup_percentage: 0
    }
};

// Document ready
$(document).ready(function() {
    // Initialize the application
    initializeApp();
    
    // Set up global event handlers
    setupGlobalEventHandlers();
    
    // Initialize page-specific functionality
    initializePageSpecific();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Load global data
    loadFlowersData();
    loadCategoriesData();
    loadGlobalSettings();
    
    // Set up form validation
    setupFormValidation();
    
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Set up auto-save functionality
    setupAutoSave();
}

/**
 * Load flowers data from API
 */
function loadFlowersData() {
    $.get('/api/flowers')
        .done(function(data) {
            console.log('Цветы загружены:', data);
            app.flowers = data; // API возвращает массив напрямую
            // Trigger custom event
            $(document).trigger('flowersLoaded', [app.flowers]);
        })
        .fail(function() {
            console.warn('Нет доступных цветов для загрузки');
            app.flowers = [];
        });
}

/**
 * Load categories data (simulated - in real app would be an API call)
 */
function loadCategoriesData() {
    // This would be an actual API call in a real application
    app.categories = [];
}

/**
 * Load global settings from API
 */
function loadGlobalSettings() {
    $.get('/api/settings')
        .done(function(data) {
            console.log('Настройки загружены:', data);
            app.settings = data;
            // Trigger custom event for components that depend on settings
            $(document).trigger('settingsLoaded', [app.settings]);
        })
        .fail(function() {
            console.warn('Не удалось загрузить настройки, используем значения по умолчанию');
            app.settings = {
                delivery_cost: 500,
                markup_percentage: 17
            };
        });
}

/**
 * Set up global event handlers
 */
function setupGlobalEventHandlers() {
    // Handle form submissions with loading states
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.html();
        
        // Add loading state
        submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>Saving...');
        submitBtn.prop('disabled', true);
        
        // Store original text for potential restoration
        submitBtn.data('original-text', originalText);
    });
    
    // Handle AJAX errors globally
    $(document).ajaxError(function(event, xhr, settings, error) {
        console.error('AJAX Error:', error);
        showNotification('An error occurred. Please try again.', 'error');
    });
    
    // Handle delete confirmations
    $('[data-action="delete"]').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
            return false;
        }
    });
    
    // Handle numeric input formatting
    $('input[type="number"]').on('blur', function() {
        const value = parseFloat($(this).val());
        if (!isNaN(value)) {
            const step = $(this).attr('step');
            const decimals = step && step.includes('.') ? step.split('.')[1].length : 0;
            $(this).val(value.toFixed(decimals));
        }
    });
}

/**
 * Initialize page-specific functionality
 */
function initializePageSpecific() {
    const page = $('body').data('page') || getCurrentPage();
    
    switch(page) {
        case 'bouquets-form':
            initializeBouquetForm();
            break;
        case 'flowers-index':
            initializeFlowersTable();
            break;
        case 'bouquets-index':
            initializeBouquetsTable();
            break;
        case 'dashboard':
            initializeDashboard();
            break;
        case 'export':
            initializeExport();
            break;
    }
}

/**
 * Get current page identifier
 */
function getCurrentPage() {
    const path = window.location.pathname;
    
    if (path === '/') return 'dashboard';
    if (path.includes('/flowers')) return 'flowers-index';
    if (path.includes('/bouquets/new') || path.includes('/bouquets/') && path.includes('/edit')) return 'bouquets-form';
    if (path.includes('/bouquets')) return 'bouquets-index';
    if (path.includes('/export')) return 'export';
    
    return 'general';
}

/**
 * Initialize bouquet form functionality
 */
function initializeBouquetForm() {
    // This is handled in the bouquet form template
    // Additional functionality can be added here
    
    // Listen for flowers loaded event
    $(document).on('flowersLoaded', function(event, flowers) {
        updateFlowerSelectOptions();
    });
    
    // Set up real-time price calculation
    setupPriceCalculation();
}

/**
 * Initialize flowers table
 */
function initializeFlowersTable() {
    // Add search and sort functionality if DataTables is available
    if ($.fn.DataTable && $('#flowersTable').length) {
        $('#flowersTable').DataTable({
            "pageLength": 25,
            "order": [[ 1, "asc" ]],
            "columnDefs": [
                { "orderable": false, "targets": -1 }
            ],
            "language": {
                "search": "Search flowers:",
                "lengthMenu": "Show _MENU_ flowers per page",
                "info": "Showing _START_ to _END_ of _TOTAL_ flowers",
                "emptyTable": "No flowers found"
            }
        });
    }
}

/**
 * Initialize bouquets table
 */
function initializeBouquetsTable() {
    if ($.fn.DataTable && $('#bouquetsTable').length) {
        $('#bouquetsTable').DataTable({
            "pageLength": 25,
            "order": [[ 0, "asc" ]],
            "columnDefs": [
                { "orderable": false, "targets": [3, -1] }
            ],
            "language": {
                "search": "Search bouquets:",
                "lengthMenu": "Show _MENU_ bouquets per page",
                "info": "Showing _START_ to _END_ of _TOTAL_ bouquets",
                "emptyTable": "No bouquets found"
            }
        });
    }
}

/**
 * Initialize dashboard functionality
 */
function initializeDashboard() {
    // Add any dashboard-specific functionality
    animateCounters();
}

/**
 * Initialize export functionality
 */
function initializeExport() {
    // Add export-specific functionality
    updateExportPreview();
}

/**
 * Set up form validation
 */
function setupFormValidation() {
    // Add custom validation for forms
    $('form').each(function() {
        $(this).on('submit', function(e) {
            let isValid = true;
            
            // Validate required fields
            $(this).find('input[required], select[required], textarea[required]').each(function() {
                if (!$(this).val().trim()) {
                    $(this).addClass('is-invalid');
                    isValid = false;
                } else {
                    $(this).removeClass('is-invalid');
                }
            });
            
            // Validate numeric fields
            $(this).find('input[type="number"]').each(function() {
                const value = parseFloat($(this).val());
                const min = parseFloat($(this).attr('min'));
                const max = parseFloat($(this).attr('max'));
                
                if (isNaN(value) || (min !== undefined && value < min) || (max !== undefined && value > max)) {
                    $(this).addClass('is-invalid');
                    isValid = false;
                } else {
                    $(this).removeClass('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showNotification('Please fix the errors in the form', 'error');
                return false;
            }
        });
    });
}

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        $('[data-bs-toggle="tooltip"]').each(function() {
            new bootstrap.Tooltip(this);
        });
        
        // Initialize popovers
        $('[data-bs-toggle="popover"]').each(function() {
            new bootstrap.Popover(this);
        });
    }
}

/**
 * Set up auto-save functionality
 */
function setupAutoSave() {
    // Auto-save draft data to localStorage
    $('form input, form select, form textarea').on('input change', debounce(function() {
        const form = $(this).closest('form');
        const formId = form.attr('id') || 'default-form';
        const formData = form.serialize();
        
        localStorage.setItem(`form-draft-${formId}`, formData);
    }, 1000));
    
    // Restore draft data on page load
    $('form').each(function() {
        const formId = $(this).attr('id') || 'default-form';
        const draftData = localStorage.getItem(`form-draft-${formId}`);
        
        if (draftData && !$(this).data('has-data')) {
            // Restore form data (implementation would depend on form structure)
        }
    });
}

/**
 * Set up real-time price calculation
 */
function setupPriceCalculation() {
    $(document).on('input change', '.flower-select, .quantity-input', debounce(function() {
        calculateBouquetPrice();
    }, 300));
}

/**
 * Calculate bouquet price
 */
function calculateBouquetPrice() {
    let totalFlowerCost = 0;
    
    $('.composition-row').each(function() {
        const flowerSelect = $(this).find('.flower-select');
        const quantityInput = $(this).find('.quantity-input');
        const subtotalDisplay = $(this).find('.subtotal');
        
        const selectedOption = flowerSelect.find('option:selected');
        const flowerPrice = parseFloat(selectedOption.data('price')) || 0;
        const quantity = parseInt(quantityInput.val()) || 0;
        const subtotal = flowerPrice * quantity;
        
        subtotalDisplay.text(formatCurrency(subtotal));
        totalFlowerCost += subtotal;
    });
    
    // Calculate final price with delivery and markup
    const deliveryCost = app.settings.delivery_cost;
    const markupPercent = app.settings.markup_percentage;
    const totalWithDelivery = totalFlowerCost + deliveryCost;
    const finalPrice = totalWithDelivery * (1 + markupPercent / 100);
    
    // Update display
    $('#flowersCost').text(formatCurrency(totalFlowerCost));
    $('#deliveryCost').text(formatCurrency(deliveryCost));
    $('#markupPercent').text(markupPercent + '%');
    $('#finalPrice').text(formatCurrency(finalPrice));
}

/**
 * Update flower select options
 */
function updateFlowerSelectOptions() {
    $('.flower-select').each(function() {
        const currentValue = $(this).val();
        $(this).empty();
        $(this).append('<option value="">Select a flower</option>');
        
        app.flowers.forEach(function(flower) {
            const selected = flower.id == currentValue ? 'selected' : '';
            $(this).append(`<option value="${flower.id}" data-price="${flower.price_per_unit}" ${selected}>${flower.name} - ${formatCurrency(flower.price_per_unit)}</option>`);
        }.bind(this));
    });
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : `alert-${type}`;
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Add to page (assumes there's a notifications container)
    if ($('#notifications').length) {
        $('#notifications').append(alertHtml);
    } else {
        $('main .container:first').prepend(alertHtml);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        $('.alert').not('.alert-permanent').fadeOut();
    }, 5000);
}

/**
 * Format currency value
 */
function formatCurrency(value) {
    return Math.round(parseFloat(value) / 10) * 10 + ' лей';
}

/**
 * Animate dashboard counters
 */
function animateCounters() {
    $('.card h2').each(function() {
        const target = parseInt($(this).text());
        const element = $(this);
        
        $({ counter: 0 }).animate({ counter: target }, {
            duration: 1500,
            easing: 'swing',
            step: function() {
                element.text(Math.ceil(this.counter));
            },
            complete: function() {
                element.text(target);
            }
        });
    });
}

/**
 * Update export preview
 */
function updateExportPreview() {
    $('#category_id').on('change', function() {
        // Update preview based on selected category
        // This would typically involve an AJAX call
    });
}

/**
 * Debounce function to limit function calls
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        
        if (callNow) func.apply(context, args);
    };
}

/**
 * Utility function to get CSRF token
 */
function getCSRFToken() {
    return $('meta[name=csrf-token]').attr('content');
}

/**
 * Handle responsive table functionality
 */
function handleResponsiveTables() {
    $(window).on('resize', function() {
        if ($(window).width() < 768) {
            $('.table-responsive').addClass('table-responsive-sm');
        } else {
            $('.table-responsive').removeClass('table-responsive-sm');
        }
    }).trigger('resize');
}

// Initialize responsive tables
$(document).ready(function() {
    handleResponsiveTables();
});

// Export to global scope for debugging
window.FlowerCRM = {
    app: app,
    calculateBouquetPrice: calculateBouquetPrice,
    showNotification: showNotification,
    formatCurrency: formatCurrency
};
