// Middlebury SIC - Main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle (for slide-out menu)
    const mobileToggle = document.getElementById('mobileToggle');
    const navMenu = document.getElementById('navMenu');
    const body = document.body; // Reference to the body element
    
    // Create an overlay element
    const overlay = document.createElement('div');
    overlay.classList.add('side-menu-overlay');
    document.body.appendChild(overlay);

    function toggleSideMenu() {
        navMenu.classList.toggle('show');
        body.classList.toggle('side-menu-open'); // Toggle class on body for overflow
        const icon = mobileToggle.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        }
    }

    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', toggleSideMenu);
    }
    
    // Overlay click listener: This now works because pointer-events: auto; is set on the active overlay
    // allowing clicks on the dimmed area to close the menu.
    overlay.addEventListener('click', function() {
        if (navMenu && navMenu.classList.contains('show')) {
            toggleSideMenu(); // Use the common toggle function
        }
    });

    // New: Event listener for an optional "Close" button within the menu
    // (Ensure this button's HTML is uncommented in base.html if you want to use it)
    const closeMenuButton = document.getElementById('closeMenuButton');
    if (closeMenuButton) {
        closeMenuButton.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default link behavior if it's an <a> tag
            toggleSideMenu();
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Close side menu after click if it's open
                if (navMenu && navMenu.classList.contains('show')) {
                    toggleSideMenu(); // Use the common toggle function
                }
            }
        });
    });
    
    // Animation on scroll
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        // Add animation class when elements come into view
        const animateOnScroll = function() {
            animatedElements.forEach(element => {
                const elementTop = element.getBoundingClientRect().top;
                const windowHeight = window.innerHeight;
                
                if (elementTop < windowHeight - 50) {
                    element.classList.add('animated');
                }
            });
        };
        
        // Run once on load
        animateOnScroll();
        
        // Run on scroll
        window.addEventListener('scroll', animateOnScroll);
    }
    
    // Initialize any charts on the page
    if (typeof Chart !== 'undefined' && document.getElementById('portfolioChart')) {
        initializePortfolioChart();
    }
});

// Portfolio allocation chart (for Investment Approach page)
function initializePortfolioChart() {
    const ctx = document.getElementById('portfolioChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Technology', 'Healthcare', 'Consumer Staples', 'Financials', 'Industrials', 'Energy', 'Others'],
            datasets: [{
                data: [25, 20, 15, 15, 10, 5, 10],
                backgroundColor: [
                    '#0d395f', // Primary
                    '#1a5080', // Primary light
                    '#8ba3bc', // Secondary
                    '#c4b35a', // Accent
                    '#28a745', // Success
                    '#ffc107', // Warning
                    '#adb5bd'  // Gray
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.raw + '%';
                        }
                    }
                }
            }
        }
    });
}

// Performance chart (for Home page)
function initializePerformanceChart() {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    
    // Sample data - replace with actual performance data
    const years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024'];
    const sicReturns = [8.2, 9.7, -2.3, 18.6, -5.1, 12.4, 9.8];
    const benchmarkReturns = [7.5, 8.9, -4.1, 16.2, -6.3, 11.2, 8.5];
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'SIC Portfolio',
                    data: sicReturns,
                    borderColor: '#0d395f',
                    backgroundColor: 'rgba(13, 57, 95, 0.1)',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 3
                },
                {
                    label: 'Benchmark',
                    data: benchmarkReturns,
                    borderColor: '#c4b35a',
                    backgroundColor: 'rgba(196, 179, 90, 0.1)',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw + '%';
                        }
                    }
                }
            }
        }
    });
}

// For recruitment form validation
function validateRecruitmentForm() {
    const form = document.getElementById('recruitmentForm');
    if (!form) return true;
    
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error');
            
            // Add error message if not already present
            let errorMessage = field.nextElementSibling;
            if (!errorMessage || !errorMessage.classList.contains('error-message')) {
                errorMessage = document.createElement('div');
                errorMessage.className = 'error-message';
                errorMessage.textContent = 'This field is required';
                field.parentNode.insertBefore(errorMessage, field.nextSibling);
            }
        } else {
            field.classList.remove('error');
            
            // Remove error message if exists
            const errorMessage = field.nextElementSibling;
            if (errorMessage && errorMessage.classList.contains('error-message')) {
                errorMessage.remove();
            }
        }
    });
    
    return isValid;
}