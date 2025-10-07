/* Change Password Page JavaScript */

function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const icon = document.getElementById(fieldId + '_icon');
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.className = 'bi bi-eye-slash';
    } else {
        field.type = 'password';
        icon.className = 'bi bi-eye';
    }
}

function validatePassword() {
    const password = document.getElementById('new_password').value;
    const requirements = document.getElementById('password_requirements');
    
    if (password.length > 0) {
        requirements.style.display = 'block';
        requirements.classList.add('fade-in-requirements', 'active');
    } else {
        requirements.style.display = 'none';
        requirements.classList.remove('active');
        return;
    }

    // Check length
    const lengthReq = document.getElementById('length_req');
    if (password.length >= 8) {
        lengthReq.innerHTML = '<i class="bi bi-check-circle text-success"></i> At least 8 characters';
        lengthReq.className = 'requirement-met';
    } else {
        lengthReq.innerHTML = '<i class="bi bi-x-circle text-danger"></i> At least 8 characters';
        lengthReq.className = 'requirement-unmet';
    }

    // Check uppercase
    const uppercaseReq = document.getElementById('uppercase_req');
    if (/[A-Z]/.test(password)) {
        uppercaseReq.innerHTML = '<i class="bi bi-check-circle text-success"></i> One uppercase letter (A-Z)';
        uppercaseReq.className = 'requirement-met';
    } else {
        uppercaseReq.innerHTML = '<i class="bi bi-x-circle text-danger"></i> One uppercase letter (A-Z)';
        uppercaseReq.className = 'requirement-unmet';
    }

    // Check lowercase
    const lowercaseReq = document.getElementById('lowercase_req');
    if (/[a-z]/.test(password)) {
        lowercaseReq.innerHTML = '<i class="bi bi-check-circle text-success"></i> One lowercase letter (a-z)';
        lowercaseReq.className = 'requirement-met';
    } else {
        lowercaseReq.innerHTML = '<i class="bi bi-x-circle text-danger"></i> One lowercase letter (a-z)';
        lowercaseReq.className = 'requirement-unmet';
    }

    // Check number
    const numberReq = document.getElementById('number_req');
    if (/\d/.test(password)) {
        numberReq.innerHTML = '<i class="bi bi-check-circle text-success"></i> One number (0-9)';
        numberReq.className = 'requirement-met';
    } else {
        numberReq.innerHTML = '<i class="bi bi-x-circle text-danger"></i> One number (0-9)';
        numberReq.className = 'requirement-unmet';
    }

    // Check special character
    const specialReq = document.getElementById('special_req');
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
        specialReq.innerHTML = '<i class="bi bi-check-circle text-success"></i> One special character (!@#$%^&*)';
        specialReq.className = 'requirement-met';
    } else {
        specialReq.innerHTML = '<i class="bi bi-x-circle text-danger"></i> One special character (!@#$%^&*)';
        specialReq.className = 'requirement-unmet';
    }

    validatePasswordMatch();
}

function validatePasswordMatch() {
    const password = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const matchDiv = document.getElementById('password_match');
    const submitBtn = document.getElementById('submitBtn');

    if (confirmPassword.length === 0) {
        matchDiv.innerHTML = '';
        submitBtn.disabled = true;
        return;
    }

    if (password === confirmPassword) {
        matchDiv.innerHTML = '<small class="text-success"><i class="bi bi-check-circle"></i> Passwords match</small>';
        
        // Check if password meets all requirements
        const isValid = password.length >= 8 && 
                       /[A-Z]/.test(password) && 
                       /[a-z]/.test(password) && 
                       /\d/.test(password) && 
                       /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
        
        submitBtn.disabled = !isValid;
    } else {
        matchDiv.innerHTML = '<small class="text-danger"><i class="bi bi-x-circle"></i> Passwords do not match</small>';
        submitBtn.disabled = true;
    }
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Show password requirements when user starts typing
    const newPasswordField = document.getElementById('new_password');
    if (newPasswordField) {
        newPasswordField.addEventListener('focus', function() {
            if (this.value.length === 0) {
                const requirements = document.getElementById('password_requirements');
                requirements.style.display = 'block';
                requirements.classList.add('fade-in-requirements');
            }
        });
        
        // Add input event listener for real-time validation
        newPasswordField.addEventListener('input', validatePassword);
    }
    
    // Add event listener for confirm password field
    const confirmPasswordField = document.getElementById('confirm_password');
    if (confirmPasswordField) {
        confirmPasswordField.addEventListener('input', validatePasswordMatch);
    }
});
