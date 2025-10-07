/**
 * SPA Navigation - Single Page Application navigation without full page refresh
 */

(function() {
    'use strict';

    // Track current page to avoid unnecessary reloads
    let currentPage = window.location.pathname;

    /**
     * Load content into main area via AJAX
     */
    function loadPage(url, pushState = true) {
        // Show loading indicator
        const mainContent = document.querySelector('main');
        if (!mainContent) return;

        // Add loading class
        mainContent.style.opacity = '0.5';
        mainContent.style.pointerEvents = 'none';

        // Fetch the page
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            // Parse the HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Extract the main content
            const newContent = doc.querySelector('main');
            if (newContent) {
                mainContent.innerHTML = newContent.innerHTML;
                
                // Execute scripts in the new content
                const scripts = mainContent.querySelectorAll('script');
                scripts.forEach(script => {
                    const newScript = document.createElement('script');
                    if (script.src) {
                        newScript.src = script.src;
                    } else {
                        newScript.textContent = script.textContent;
                    }
                    document.body.appendChild(newScript);
                    script.remove();
                });
                
                // Update active state in sidebar
                updateActiveNavLink(url);
                
                // Update browser history
                if (pushState) {
                    history.pushState({ page: url }, '', url);
                    currentPage = url;
                }
            }
            
            // Remove loading state
            mainContent.style.opacity = '1';
            mainContent.style.pointerEvents = 'auto';
        })
        .catch(error => {
            console.error('Error loading page:', error);
            mainContent.style.opacity = '1';
            mainContent.style.pointerEvents = 'auto';
            alert('Failed to load page. Please try again.');
        });
    }

    /**
     * Update active state in sidebar navigation
     */
    function updateActiveNavLink(url) {
        const navLinks = document.querySelectorAll('.sidebar .nav-link');
        navLinks.forEach(link => {
            if (link.getAttribute('href') === url) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    /**
     * Handle link clicks
     */
    function handleLinkClick(event) {
        const link = event.target.closest('a');
        if (!link) return;

        const href = link.getAttribute('href');
        
        // Only handle internal navigation links
        if (href && 
            !href.startsWith('http') && 
            !href.startsWith('#') &&
            !link.hasAttribute('data-no-spa')) {
            
            event.preventDefault();
            
            // Don't reload if already on this page
            if (href === currentPage) {
                return;
            }
            
            loadPage(href, true);
        }
    }

    /**
     * Handle browser back/forward buttons
     */
    function handlePopState(event) {
        if (event.state && event.state.page) {
            loadPage(event.state.page, false);
        }
    }

    /**
     * Initialize SPA navigation
     */
    function init() {
        // Add click handlers to sidebar
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.addEventListener('click', handleLinkClick);
        }

        // Add click handler to navbar logo
        const navbarBrand = document.querySelector('.navbar-brand a');
        if (navbarBrand) {
            navbarBrand.addEventListener('click', handleLinkClick);
        }

        // Handle browser back/forward
        window.addEventListener('popstate', handlePopState);

        // Set initial state
        history.replaceState({ page: currentPage }, '', currentPage);

        console.log('SPA navigation initialized');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
