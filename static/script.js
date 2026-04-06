/* ============================================================================
   AI Interview Platform - JavaScript
   Interactive Features, Animations, and Dynamic Functionality
   ============================================================================ */

/**
 * Smooth scroll behavior for internal links
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

/**
 * Page scroll animation for dashboard
 */
let scrolled = false;
window.addEventListener('scroll', () => {
    if (window.scrollY > 0 && !scrolled) {
        document.querySelector('.dashboard-main')?.classList.add('scrolled');
        scrolled = true;
    } else if (window.scrollY === 0) {
        document.querySelector('.dashboard-main')?.classList.remove('scrolled');
        scrolled = false;
    }
});

/**
 * Auto-expand textarea as user types
 */
const textareas = document.querySelectorAll('textarea');
textareas.forEach(textarea => {
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});

/**
 * Smooth number counter animation
 */
function animateNumber(element, target, duration = 1500) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const counter = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = Math.round(target);
            clearInterval(counter);
        } else {
            element.textContent = Math.round(current);
        }
    }, 16);
}

/**
 * Intersection Observer for fade-in animations
 */
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('in-view');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.results-card, .metric-card, .feature-card').forEach(el => {
    observer.observe(el);
});

/**
 * Ripple effect on button clicks
 */
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('mousedown', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = size + 'px';
        ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');

        this.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });
});

/**
 * Add ripple styles dynamically
 */
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }

    .ripple {
        position: absolute;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }

    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .in-view {
        animation: fadeInUp 0.6s ease-out forwards;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);

/**
 * Format time display (MM:SS)
 */
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

/**
 * Debounce helper for search/input
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
 * Throttle helper for scroll events
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Handle chart animation with gradient
 */
function createChartGradient(ctx) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.5)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');
    return gradient;
}

/**
 * Add visual feedback for page transitions
 */
let transitionInProgress = false;

function startPageTransition() {
    if (transitionInProgress) return;
    transitionInProgress = true;

    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(11, 14, 20, 0.8);
        backdrop-filter: blur(4px);
        z-index: 9999;
        animation: fadeOut 0.3s ease-out forwards;
        animation-delay: 300ms;
    `;

    document.body.appendChild(overlay);

    setTimeout(() => {
        overlay.remove();
        transitionInProgress = false;
    }, 600);
}

/**
 * Keyboard shortcuts
 */
document.addEventListener('keydown', (e) => {
    // Escape key to close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal[style*="flex"]').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    // Cmd/Ctrl + K for search (future feature)
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        console.log('Search activated');
    }

    // Enter to submit forms (context-dependent)
    if (e.key === 'Enter' && e.ctrlKey) {
        const submitBtn = document.querySelector('.btn-submit, .btn-primary');
        if (submitBtn && document.activeElement !== document.body) {
            submitBtn.click();
        }
    }
});

/**
 * Detect if user prefers reduced motion
 */
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (prefersReducedMotion) {
    document.body.style.setProperty('--transition-fast', '0ms');
    document.body.style.setProperty('--transition-base', '0ms');
    document.body.style.setProperty('--transition-slow', '0ms');
}

/**
 * Check internet connection status
 */
window.addEventListener('online', () => {
    console.log('Connection restored');
    // Could show a toast notification here
});

window.addEventListener('offline', () => {
    console.log('Connection lost');
    // Could show an offline indicator
});

/**
 * Auto-save form data to localStorage
 */
function autoSaveForm(formSelector) {
    const form = document.querySelector(formSelector);
    if (!form) return;

    const inputs = form.querySelectorAll('input, textarea, select');

    inputs.forEach(input => {
        input.addEventListener('change', () => {
            const data = new FormData(form);
            const obj = Object.fromEntries(data);
            localStorage.setItem(`form_${formSelector}`, JSON.stringify(obj));
        });
    });

    // Restore form data
    const saved = localStorage.getItem(`form_${formSelector}`);
    if (saved) {
        const obj = JSON.parse(saved);
        Object.entries(obj).forEach(([key, value]) => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) input.value = value;
        });
    }
}

/**
 * Add focus state visibility for accessibility
 */
document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-nav');
    }
});

document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-nav');
});

const accessibilityStyle = document.createElement('style');
accessibilityStyle.textContent = `
    body.keyboard-nav .btn:focus,
    body.keyboard-nav input:focus,
    body.keyboard-nav textarea:focus,
    body.keyboard-nav select:focus {
        outline: 2px solid var(--accent-primary);
        outline-offset: 2px;
    }
`;
document.head.appendChild(accessibilityStyle);

/**
 * Dark mode preference
 */
const darkModePreference = window.matchMedia('(prefers-color-scheme: dark)').matches;
if (darkModePreference) {
    document.body.classList.add('dark-mode');
}

/**
 * Scroll to top button
 */
function createScrollToTopButton() {
    const btn = document.createElement('button');
    btn.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="18 15 12 9 6 15"></polyline>
        </svg>
    `;
    btn.className = 'scroll-to-top';
    btn.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
        border: none;
        color: white;
        cursor: pointer;
        display: none;
        z-index: 995;
        transition: all 0.3s ease;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
    `;

    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    window.addEventListener('scroll', throttle(() => {
        if (window.scrollY > 300) {
            btn.style.display = 'flex';
            btn.style.alignItems = 'center';
            btn.style.justifyContent = 'center';
        } else {
            btn.style.display = 'none';
        }
    }, 500));

    document.body.appendChild(btn);
}

createScrollToTopButton();

/**
 * Export results as PDF-ready HTML
 */
function exportResultsAsHTML() {
    const content = document.querySelector('.results-container');
    if (!content) return;

    const html = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Interview Results</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: Arial, sans-serif; color: #333; line-height: 1.6; }
                .results-container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
                h1, h2, h3 { margin-top: 20px; margin-bottom: 10px; }
                .metric-card, .results-card { page-break-inside: avoid; margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }
                table { width: 100%; border-collapse: collapse; margin-top: 15px; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f5f5f5; font-weight: bold; }
            </style>
        </head>
        <body>
            ${content.innerHTML}
        </body>
        </html>
    `;

    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview-results-${new Date().toISOString().split('T')[0]}.html`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Performance monitoring
 */
if ('PerformanceObserver' in window) {
    try {
        const perfObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.duration > 3000) {
                    console.warn('Long task detected:', entry.name, entry.duration);
                }
            }
        });
        perfObserver.observe({ entryTypes: ['longtask'] });
    } catch (e) {
        // Longtask API may not be available
    }
}

/**
 * Fatal error handler
 */
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    // Could send to error tracking service
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    // Could send to error tracking service
});

/**
 * Initialize on DOM ready
 */
document.addEventListener('DOMContentLoaded', () => {
    // Any initialization code here
    console.log('Interview Platform loaded successfully');

    // Initialize tooltips if needed
    initializeTooltips();

    // Initialize animations
    initializeAnimations();
});

/**
 * Tooltip initialization
 */
function initializeTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = e.target.getAttribute('data-tooltip');
    tooltip.style.cssText = `
        position: absolute;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        white-space: nowrap;
        z-index: 1000;
        bottom: 105%;
        left: 50%;
        transform: translateX(-50%);
    `;
    e.target.parentElement.appendChild(tooltip);
}

function hideTooltip(e) {
    e.target.parentElement.querySelector('.tooltip')?.remove();
}

/**
 * Initialize animations on scroll
 */
function initializeAnimations() {
    const animateOnScroll = (selector, className) => {
        const elements = document.querySelectorAll(selector);
        const triggerObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add(className);
                }
            });
        }, { threshold: 0.1 });

        elements.forEach(el => triggerObserver.observe(el));
    };

    animateOnScroll('.results-card', 'slide-in');
    animateOnScroll('.metric-card', 'scale-in');
}

/* ============================================================================
   ADVANCED INTERACTIVE FEATURES
   ============================================================================ */

/**
 * Interview Timer System
 */
class InterviewTimer {
    constructor(durationMinutes = 10) {
        this.totalSeconds = durationMinutes * 60;
        this.remainingSeconds = this.totalSeconds;
        this.isRunning = false;
        this.timerElement = null;
    }

    start(elementId) {
        this.timerElement = document.getElementById(elementId);
        if (!this.timerElement) return;
        
        this.isRunning = true;
        this.interval = setInterval(() => this.tick(), 1000);
    }

    tick() {
        if (this.remainingSeconds <= 0) {
            this.stop();
            this.onTimeUp();
            return;
        }

        this.remainingSeconds--;
        this.updateDisplay();

        // Trigger warning at 1 minute
        if (this.remainingSeconds === 60 && this.timerElement) {
            this.timerElement.parentElement?.classList.add('warning');
        }
    }

    updateDisplay() {
        if (!this.timerElement) return;
        
        const minutes = Math.floor(this.remainingSeconds / 60);
        const seconds = this.remainingSeconds % 60;
        this.timerElement.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }

    stop() {
        this.isRunning = false;
        clearInterval(this.interval);
    }

    onTimeUp() {
        showNotification('Time\'s up! Submitting your interview...', 'info');
    }
}

/**
 * Progress Tracker
 */
class ProgressTracker {
    constructor(totalSteps) {
        this.totalSteps = totalSteps;
        this.currentStep = 0;
    }

    updateProgress(step) {
        this.currentStep = step;
        const percentage = (step / this.totalSteps) * 100;
        
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = percentage + '%';
        }

        const progressText = document.querySelector('.progress-text .current');
        if (progressText) {
            progressText.textContent = step;
        }
    }

    complete() {
        this.updateProgress(this.totalSteps);
        showNotification('Interview completed! Great job! 🎉', 'success');
    }
}

/**
 * Achievement System
 */
class AchievementSystem {
    constructor() {
        this.achievements = {
            'first_interview': { name: '🚀 First Step', description: 'Complete your first interview' },
            'five_interviews': { name: '⭐ Rising Star', description: 'Complete 5 interviews' },
            'perfect_score': { name: '🏆 Perfect Score', description: 'Score 100% on an interview' },
            'streak_five': { name: '🔥 On Fire', description: 'Maintain 5 interview streak' },
            'quick_responder': { name: '⚡ Quick Thinker', description: 'Average response time < 30 seconds' }
        };
    }

    unlock(achievementId) {
        const achievement = this.achievements[achievementId];
        if (achievement) {
            this.displayBadge(achievement);
        }
    }

    displayBadge(achievement) {
        const badge = document.createElement('div');
        badge.className = 'badge achievement';
        badge.innerHTML = `<span>${achievement.name}</span><span>${achievement.description}</span>`;
        badge.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1000;
        `;
        document.body.appendChild(badge);

        setTimeout(() => badge.remove(), 4000);
    }
}

/**
 * Performance Feedback System
 */
class PerformanceFeedback {
    static generateScore(depth, clarity, technical, reasoning, confidence) {
        return Math.round((depth + clarity + technical + reasoning + confidence) / 5);
    }

    static getScoreColor(score) {
        if (score >= 90) return '#14B8A6';
        if (score >= 80) return '#6366F1';
        if (score >= 70) return '#F97316';
        if (score >= 60) return '#FB923C';
        return '#EF4444';
    }

    static getScoreLabel(score) {
        if (score >= 90) return 'Excellent';
        if (score >= 80) return 'Great';
        if (score >= 70) return 'Good';
        if (score >= 60) return 'Fair';
        return 'Needs Improvement';
    }

    static generateFeedback(score) {
        const feedbackMap = {
            'Excellent': 'Outstanding performance! Keep maintaining this level.',
            'Great': 'Well done! You\'re on track for strong interviews.',
            'Good': 'Solid performance. Focus on depth to reach excellence.',
            'Fair': 'Room for improvement. Practice answering more comprehensively.',
            'Needs Improvement': 'Let\'s work on clarity and technical depth.'
        };

        const label = this.getScoreLabel(score);
        return feedbackMap[label] || '';
    }
}

/**
 * Enhanced Form Validation
 */
class FormValidator {
    static validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    static validatePassword(password) {
        return password.length >= 8;
    }

    static validateUsername(username) {
        return username.length >= 3 && username.length <= 20;
    }

    static showFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (!field) return;

        field.style.borderColor = '#EF4444';
        const errorMsg = document.createElement('div');
        errorMsg.className = 'error-message';
        errorMsg.textContent = message;
        errorMsg.style.cssText = `
            color: #EF4444;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        `;
        field.parentElement?.appendChild(errorMsg);
    }

    static clearFieldError(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return;

        field.style.borderColor = '';
        const errorMsg = field.parentElement?.querySelector('.error-message');
        if (errorMsg) errorMsg.remove();
    }
}

/**
 * Notification System
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 1rem;">
            <span class="status-indicator ${type === 'success' ? 'success' : type === 'error' ? 'error' : 'warning'}"></span>
            <span>${message}</span>
        </div>
    `;
    notification.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        z-index: 1000;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? 'rgba(20, 184, 166, 0.1)' : type === 'error' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(99, 102, 241, 0.1)'};
        border: 1px solid ${type === 'success' ? 'rgba(20, 184, 166, 0.3)' : type === 'error' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(99, 102, 241, 0.3)'};
        border-radius: 0.5rem;
        color: var(--text-primary);
        animation: slide-in-right 0.3s ease-out;
    `;
    document.body.appendChild(notification);

    setTimeout(() => notification.remove(), 4000);
}

/**
 * Initialize all advanced features
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize achievement system
    window.achievementSystem = new AchievementSystem();

    // Add real-time validation to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('input', (e) => {
            if (e.target.type === 'email') {
                if (FormValidator.validateEmail(e.target.value)) {
                    FormValidator.clearFieldError(e.target.id);
                }
            }
            if (e.target.type === 'password') {
                if (FormValidator.validatePassword(e.target.value)) {
                    FormValidator.clearFieldError(e.target.id);
                }
            }
        });
    });
});

/**
 * Export utility for analytics
 */
const AnalyticsExport = {
    exportJSON(data, filename = 'analytics.json') {
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    },

    exportCSV(data, filename = 'analytics.csv') {
        let csv = [];
        data.forEach(row => {
            csv.push(Object.values(row).join(','));
        });
        const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
};

window.AnalyticsExport = AnalyticsExport;

console.log('Interview Platform JavaScript loaded successfully');
