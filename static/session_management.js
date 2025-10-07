// Session Management JavaScript
// Handles session timeout, logout functionality, and session persistence

let sessionStartTime = null;
let loginUrl = '/login';
let logoutUrl = '/logout';

// Initialize session management
function initSessionManagement(loginUrlParam, logoutUrlParam) {
    loginUrl = loginUrlParam || '/login';
    logoutUrl = logoutUrlParam || '/logout';
    
    console.log('Session management initialized', { loginUrl, logoutUrl });
    
    // Set up periodic session check
    setInterval(checkSessionHealth, 60000); // Check every minute
    
    // Initial session check
    checkSessionHealth();
}

// Check if session is still valid
async function checkSessionHealth() {
    try {
        const response = await fetch('/api/session-check', {
            credentials: 'same-origin',
            method: 'GET'
        });
        
        if (response.status === 401) {
            // Session expired, redirect to login
            console.log('Session expired, redirecting to login');
            handleSessionExpired();
        } else if (response.ok) {
            const data = await response.json();
            if (data.valid === false) {
                handleSessionExpired();
            }
        }
    } catch (error) {
        console.warn('Session check failed:', error);
        // Don't redirect on network errors, just log them
    }
}

// Handle session expiration
function handleSessionExpired() {
    // Clear any stored session data
    clearStoredData();
    
    // Show a user-friendly message
    alert('Your session has expired. Please log in again.');
    
    // Redirect to login page
    window.location.href = loginUrl;
}

// Clear stored data on logout or session expiration
function clearStoredData() {
    localStorage.removeItem('currentSessionId');
    localStorage.removeItem('sidebarCollapsed');
    sessionStorage.clear();
}

// Logout function
async function logout() {
    try {
        // Clear stored data first
        clearStoredData();
        
        // Call logout endpoint
        await fetch(logoutUrl, {
            method: 'POST',
            credentials: 'same-origin'
        });
        
        // Redirect to login
        window.location.href = loginUrl;
    } catch (error) {
        console.error('Logout error:', error);
        // Still redirect even if logout call fails
        window.location.href = loginUrl;
    }
}

// Export functions for global use
window.initSessionManagement = initSessionManagement;
window.logout = logout;
window.clearStoredData = clearStoredData;