/**
 * rebornApp Authentication JavaScript
 * Handles login/register form interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // ======================
    // 1. FORM VALIDATION
    // ======================
    const registerForm = document.querySelector('form[action*="register"]');
    const loginForm = document.querySelector('form[action*="login"]');

    // Password match validation
    if (registerForm) {
        const password1 = registerForm.querySelector('input[name="password1"]');
        const password2 = registerForm.querySelector('input[name="password2"]');
        const errorDisplay = document.createElement('div');
        errorDisplay.className = 'password-error';
        errorDisplay.style.color = '#c62828';
        errorDisplay.style.fontSize = '14px';
        errorDisplay.style.marginTop = '5px';
        password2.parentNode.appendChild(errorDisplay);

        password2.addEventListener('input', function() {
            if (password1.value !== password2.value) {
                errorDisplay.textContent = 'Passwords do not match!';
                password2.style.borderColor = '#c62828';
            } else {
                errorDisplay.textContent = '';
                password2.style.borderColor = '#ddd';
            }
        });
    }

    // ======================
    // 2. ROLE SELECTION UI
    // ======================
    const roleSelect = document.querySelector('.role-select select');
    if (roleSelect) {
        roleSelect.addEventListener('change', function() {
            // Visual feedback when role changes
            this.style.backgroundColor = this.value === 'seller' 
                ? '#fff8e1' 
                : '#f5f5f5';
        });
    }

    // ======================
    // 3. FORM SUBMISSION HANDLING
    // ======================
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            // Client-side validation
            if (password1 && password2 && password1.value !== password2.value) {
                e.preventDefault();
                errorDisplay.textContent = 'Please fix password mismatch before submitting';
                errorDisplay.style.display = 'block';
                password2.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            // Add loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Logging in...';
        });
    }

    // ======================
    // 4. UI ENHANCEMENTS
    // ======================
    // Focus first form field
    const firstInput = document.querySelector('form input');
    if (firstInput) {
        firstInput.focus();
    }

    // Show/hide password toggle
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        const toggle = document.createElement('span');
        toggle.className = 'password-toggle';
        toggle.innerHTML = '👁️';
        toggle.style.cursor = 'pointer';
        toggle.style.marginLeft = '-30px';
        toggle.style.verticalAlign = 'middle';
        
        field.parentNode.appendChild(toggle);
        
        toggle.addEventListener('click', function() {
            if (field.type === 'password') {
                field.type = 'text';
                this.innerHTML = '👁️‍🗨️';
            } else {
                field.type = 'password';
                this.innerHTML = '👁️';
            }
        });
    });

    // ======================
    // 5. ERROR DISPLAY HANDLING
    // ======================
    const errorAlerts = document.querySelectorAll('.alert-error');
    errorAlerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// ======================
// HELPER FUNCTIONS
// ======================
function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}