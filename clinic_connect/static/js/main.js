/* ==========================================================================
   ClinicConnect: Core JS Utilities
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Theme
    const savedTheme = localStorage.getItem('clinic-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // 2. Initialize Language
    const savedLang = localStorage.getItem('clinic-lang') || 'en';
    applyLanguage(savedLang);

    // 3. Auto Dismiss Alerts after 4 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s, transform 0.5s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100px)';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });
});

// ==========================================================================
// Theme Toggler (Light / Dark)
// ==========================================================================
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('clinic-theme', newTheme);
}

// ==========================================================================
// Client-Side Bilingual Localization (EN / HI)
// ==========================================================================
function toggleLanguage() {
    const currentLang = localStorage.getItem('clinic-lang') || 'en';
    const newLang = currentLang === 'en' ? 'hi' : 'en';
    applyLanguage(newLang);
}

function applyLanguage(lang) {
    document.querySelectorAll('.trn').forEach(el => {
        const text = el.getAttribute('data-' + lang);
        if (text) {
            // Support inputs with placeholder translations
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.placeholder = text;
            } else {
                el.textContent = text;
            }
        }
    });
    
    localStorage.setItem('clinic-lang', lang);
    const label = document.getElementById('current-lang-label');
    if (label) label.textContent = lang.toUpperCase();
}

// ==========================================================================
// Active Role Switcher
// ==========================================================================
function changeActiveRole(role) {
    fetch('/auth/switch-role', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role: role })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        }
    })
    .catch(err => console.error("Error switching roles: ", err));
}

// ==========================================================================
// Network status mock toggler
// ==========================================================================
function toggleNetworkStatus() {
    fetch('/auth/toggle-network', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        }
    })
    .catch(err => console.error("Error toggling network: ", err));
}
