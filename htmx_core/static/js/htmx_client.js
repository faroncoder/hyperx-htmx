/**
 * HTMX Content Management System
 * Works with Django HTMXContentMiddleware for seamless content updates
 * 
 * @version 2.0.0
 * @author S5 Portal Team
 */


// --- HyperXState Global State Management ---
window.HyperXState = {
    routeType: null,
    token: null,
    siteUser: null,
    sessionId: null,
    lastUpdated: null,

    // Initialize state from localStorage
    init() {
        const savedState = localStorage.getItem('HyperXState');
        if (savedState) {
            try {
                Object.assign(this, JSON.parse(savedState));
            } catch (e) {
                console.warn('Failed to restore HyperXState:', e);
            }
        }
    },

    // Save current state to localStorage
    save() {
        try {
            localStorage.setItem('HyperXState', JSON.stringify({
                routeType: this.routeType,
                token: this.token,
                siteUser: this.siteUser,
                sessionId: this.sessionId,
                lastUpdated: this.lastUpdated
            }));
        } catch (e) {
            console.warn('Failed to save HyperXState:', e);
        }
    },

    // Update state from HTMX response headers
    updateFromHeaders(xhr) {
        if (!xhr) return false;

        const token = xhr.getResponseHeader('X-One-Time-Token');
        const routeType = xhr.getResponseHeader('X-Route-Type');
        const siteUser = xhr.getResponseHeader('X-Site-User');
        const sessionId = xhr.getResponseHeader('X-Session-ID');

        if (token || routeType) {
            this.routeType = routeType;
            this.token = token;
            this.siteUser = siteUser;
            this.sessionId = sessionId;
            this.lastUpdated = new Date().toISOString();

            console.log('🔁 HyperXState updated:', this);
            document.dispatchEvent(new CustomEvent('hyperx:stateUpdated', { detail: this }));
            this.save();
            return true;
        }
        return false;
    }
};

// --- Global HTMX Utilities ---
window.HTMXUtils = {
    // Internal tracking
    _internalNavigation: false,
    _initialized: false,

    /**
     * Security & Navigation Management
     */

    // Enhanced direct access detection with configurable security modes
    checkDirectAccess(options = {}) {
        const strict = options.strict === true;
        const currentPath = window.location.pathname;
        const currentOrigin = window.location.origin;

        // 1️⃣ Detect if this load was a direct navigation (typed URL / bookmark)
        const navEntry = performance.getEntriesByType('navigation')[0];
        const isDirect = !!(
            navEntry &&
            navEntry.type === 'navigate' &&
            (!document.referrer || !document.referrer.startsWith(currentOrigin))
        );

        // 2️⃣ Collect all declared HTMX endpoints from DOM
        const htmxEls = document.querySelectorAll('[hx-get],[hx-post],[hx-put],[hx-patch],[hx-delete]');
        const endpointPaths = Array.from(htmxEls)
            .map(el => {
                for (const attr of ['hx-get', 'hx-post', 'hx-put', 'hx-patch', 'hx-delete']) {
                    const url = el.getAttribute(attr);
                    if (url && url.startsWith('/')) return url.split('?')[0];
                }
                return null;
            })
            .filter(Boolean);

        // 3️⃣ Create regex patterns for endpoint matching
        const endpointPatterns = endpointPaths.map(p => new RegExp(`^${p.replace(/\/$/, '')}/?$`));
        const isHTMXEndpoint = endpointPatterns.some(r => r.test(currentPath));

        // 4️⃣ Act only if strict + direct + HTMX-only path
        if (strict && isHTMXEndpoint && isDirect) {
            console.warn('🔒 Direct access to HTMX endpoint detected:', currentPath);
            this.showToast('Direct access not allowed – returning to dashboard', 'warning', 3000);

            // Graceful fallback with minimal delay
            setTimeout(() => {
                window.location.href = '/';
            }, 1200);
            return true;
        }

        // 5️⃣ Passive analytics / dev-mode logging
        if (isHTMXEndpoint && !strict) {
            console.info('ℹ️ HTMX endpoint loaded via internal navigation:', currentPath);
        }
        
        return false;
    },

    // Mark internal navigation to track user flow
    markInternalNavigation() {
        this._internalNavigation = true;
        setTimeout(() => {
            this._internalNavigation = false;
        }, 1000);
    },

        // --- Enhanced Loading Overlay ---
    addLoadingOverlay(targetSelector, message = "Loading...") {
        const target = typeof targetSelector === "string" ? document.querySelector(targetSelector) : targetSelector;
        if (!target) return;

        // Create overlay element
        const overlay = document.createElement("div");
        overlay.className = "htmx-overlay-loader position-absolute top-0 start-0 w-100 h-100 d-flex flex-column align-items-center justify-content-center bg-white bg-opacity-75";
        overlay.style.zIndex = "999";
        overlay.innerHTML = `
            <div class="spinner-border text-primary mb-2" role="status"></div>
            <span class="small text-muted">${message}</span>
        `;

        // Ensure target has relative positioning
        const currentPosition = getComputedStyle(target).position;
        if (currentPosition === "static") {
            target.style.position = "relative";
        }

        // Remove old overlay if any
        const existing = target.querySelector(".htmx-overlay-loader");
        if (existing) existing.remove();

        // Append new overlay
        target.appendChild(overlay);
    },

    removeLoadingOverlay(targetSelector) {
        const target = typeof targetSelector === "string" ? document.querySelector(targetSelector) : targetSelector;
        if (!target) return;
        const overlay = target.querySelector(".htmx-overlay-loader");
        if (overlay) overlay.remove();
    },




    /**
     * Core Initialization & Script Management
     */

    // Main initialization function
    init() {
        if (this._initialized) return;

        console.log('🚀 Initializing HTMX Client System');
        
        // Initialize state management
        window.HyperXState.init();
        
        // Initialize all components
        this.reinitializeScripts();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Apply security and configuration
        this.applySecurityConfig();
        
        this._initialized = true;
        console.log('✅ HTMX Client System initialized');
    },

    // Reinitialize scripts after HTMX content update
    reinitializeScripts(container = document) {
        console.log('🔄 Reinitializing scripts for container:', container);

        // Sync HyperXState headers into new elements
        this.syncStateHeaders(container);

        // Apply HTMX configuration
        this.setDefaultHtmxPushUrl(container);

        // Re-initialize UI components
        this.initBootstrapComponents(container);
        this.initCustomComponents(container);

        // Fire completion event
        container.dispatchEvent(new CustomEvent('htmx:scriptsReinitialized'));
    },

    // Sync HyperXState into HTMX headers
    syncStateHeaders(container = document) {
        const { token, sessionId } = window.HyperXState;
        if (!token && !sessionId) return;

        container.querySelectorAll('[hx-headers]').forEach(el => {
            let headers = {};
            try {
                headers = JSON.parse(el.getAttribute('hx-headers') || '{}');
            } catch (e) {
                console.warn('Invalid hx-headers JSON:', e);
            }
            
            if (token) headers['X-One-Time-Token'] = token;
            if (sessionId) headers['X-Session-ID'] = sessionId;
            
            el.setAttribute('hx-headers', JSON.stringify(headers));
        });
    },

    /**
     * UI Component Initialization
     */

    // Initialize Bootstrap components in container
    initBootstrapComponents(container = document) {
        if (typeof bootstrap === 'undefined') {
            console.warn('Bootstrap not available');
            return;
        }

        console.log('🎨 Initializing Bootstrap components');

        const components = [
            { selector: '[data-bs-toggle="tooltip"]:not(.tooltip-initialized)', 
              init: el => new bootstrap.Tooltip(el), 
              class: 'tooltip-initialized' },
            { selector: '[data-bs-toggle="popover"]:not(.popover-initialized)', 
              init: el => new bootstrap.Popover(el), 
              class: 'popover-initialized' },
            { selector: '.modal:not(.modal-initialized)', 
              init: el => new bootstrap.Modal(el), 
              class: 'modal-initialized' },
            { selector: '.dropdown-toggle:not(.dropdown-initialized)', 
              init: el => new bootstrap.Dropdown(el), 
              class: 'dropdown-initialized' },
            { selector: '[data-bs-toggle="collapse"]:not(.collapse-initialized)', 
              init: el => new bootstrap.Collapse(el), 
              class: 'collapse-initialized' }
        ];

        components.forEach(({ selector, init, class: className }) => {
            const elements = container.querySelectorAll(selector);
            elements.forEach(el => {
                try {
                    init(el);
                    el.classList.add(className);
                } catch (e) {
                    console.warn(`Failed to initialize ${className}:`, e);
                }
            });
        });

        // Special handling for sidebar menus
        this.fixSidebarMenu(container);
    },

    // Fix sidebar menu collapse functionality
    fixSidebarMenu(container = document) {
        const sidebarMenus = container.querySelectorAll('.sidebar-menu [data-bs-toggle="collapse"]');
        if (sidebarMenus.length > 0) {
            console.log('🔧 Fixing sidebar menu collapse functionality');
            sidebarMenus.forEach(el => {
                if (!el.classList.contains('collapse-fixed')) {
                    // Ensure collapse is properly initialized
                    if (!bootstrap.Collapse.getInstance(el)) {
                        new bootstrap.Collapse(el);
                    }
                    el.classList.add('collapse-fixed');
                }
            });
        }
    },

    // Initialize custom application components
    initCustomComponents(container = document) {
        console.log('🔧 Initializing custom components');
        
        this.initDataTables(container);
        this.initDatePickers(container);
        this.initFormComponents(container);
        this.initXTabs(container);
    },

    // Initialize DataTables
    initDataTables(container) {
        if (typeof $ === 'undefined' || !$.fn.DataTable) return;

        const tables = container.querySelectorAll('table.datatable:not(.dataTable)');
        tables.forEach(table => {
            try {
                if (!$(table).hasClass('dataTable')) {
                    $(table).DataTable({
                        responsive: true,
                        pageLength: 25,
                        order: [[0, 'desc']],
                        language: {
                            search: "Filter:",
                            lengthMenu: "Show _MENU_ entries"
                        }
                    });
                }
            } catch (e) {
                console.warn('Failed to initialize DataTable:', e);
            }
        });
    },

    // Initialize date pickers
    initDatePickers(container) {
        const datePickers = container.querySelectorAll('input[type="date"]:not(.date-initialized)');
        datePickers.forEach(el => {
            // Add future custom date picker initialization here
            el.classList.add('date-initialized');
        });
    },

    /**
     * Form Component Management
     */

    // Initialize enhanced form components
    initFormComponents(container = document) {
        this.initAutoSubmitForms(container);
        this.initFilePreview(container);
        this.initFormValidation(container);
    },

    // Auto-submit forms
    initAutoSubmitForms(container) {
        const autoSubmitForms = container.querySelectorAll('form[data-auto-submit]:not(.auto-submit-initialized)');
        autoSubmitForms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    setTimeout(() => {
                        if (form.checkValidity()) {
                            form.submit();
                        }
                    }, 100);
                });
            });
            form.classList.add('auto-submit-initialized');
        });
    },

    // Initialize file upload previews
    initFilePreview(container) {
        const fileInputs = container.querySelectorAll('input[type="file"][data-preview]:not(.preview-initialized)');
        fileInputs.forEach(input => {
            input.addEventListener('change', this.handleFilePreview.bind(this));
            input.classList.add('preview-initialized');
        });
    },

    // Initialize basic form validation
    initFormValidation(container) {
        const forms = container.querySelectorAll('form:not(.validation-initialized)');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.showToast('Please fill in all required fields', 'warning');
                }
                form.classList.add('was-validated');
            });
            form.classList.add('validation-initialized');
        });
    },

    // Handle file upload previews
    handleFilePreview(event) {
        const input = event.target;
        const previewId = input.dataset.preview;
        const preview = document.getElementById(previewId);

        if (!preview || !input.files || !input.files[0]) return;

        const file = input.files[0];
        const maxSize = 5 * 1024 * 1024; // 5MB limit

        if (file.size > maxSize) {
            this.showToast('File size must be less than 5MB', 'warning');
            input.value = '';
            return;
        }

        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.innerHTML = `
                    <div class="position-relative">
                        <img src="${e.target.result}" class="img-fluid rounded" style="max-height: 200px;">
                        <small class="text-muted d-block mt-1">${file.name} (${(file.size / 1024).toFixed(1)} KB)</small>
                    </div>
                `;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = `
                <div class="alert alert-info mb-0">
                    <i class="fas fa-file me-2"></i>${file.name}
                    <small class="text-muted d-block">${(file.size / 1024).toFixed(1)} KB</small>
                </div>
            `;
        }
    },

    /**
     * X-Tab Tabbed Interface Management
     */

    // Initialize X-Tab tabbed interfaces
    initXTabs(container = document) {
        console.log('🔧 Initializing X-Tab interfaces');
        
        // Find all X-Tab containers
        const xTabContainers = container.querySelectorAll('[data-x-tab-container]:not(.x-tab-initialized)');
        
        xTabContainers.forEach(tabContainer => {
            this.setupXTabContainer(tabContainer);
            tabContainer.classList.add('x-tab-initialized');
        });
        
        // Set up X-Tab click handlers (use event delegation for dynamic content)
        if (!container._xTabDelegated) {
            container.addEventListener('click', this.handleXTabClick.bind(this));
            container._xTabDelegated = true;
        }
        
        // Initialize dynamic reload for active tabs
        this.setupXTabDynamicReload(container);
    },

    // Set up an X-Tab container
    setupXTabContainer(container) {
        // Mark container as initialized
        if (container._xTabSetup) return;
        container._xTabSetup = true;

        // Store configuration
        const config = {
            defaultTab: container.dataset.defaultTab || 'overview',
            reloadInterval: parseInt(container.dataset.reloadInterval) || 0,
            autoReload: container.dataset.autoReload === 'true'
        };
        container._xTabConfig = config;

        console.log('📄 X-Tab container initialized:', config);
    },

    // Handle X-Tab navigation clicks
    handleXTabClick(event) {
        const tabLink = event.target.closest('[data-x-tab]');
        if (!tabLink) return;

        event.preventDefault();
        
        const tabId = tabLink.dataset.xTab;
        const targetUrl = window.location.href;
        const container = tabLink.closest('[data-x-tab-container]');
        
        if (!container) {
            console.warn('X-Tab link found outside container:', tabLink);
            return;
        }

        // Update active state in UI immediately for better UX
        this.updateXTabActiveState(container, tabId);
        
        // Show loading overlay
        const contentArea = container.querySelector('#x-tab-content') || container.querySelector('[data-x-tab-content]');
        if (contentArea) {
            this.addLoadingOverlay(contentArea, 'Loading tab content...');
        }

        // Make HTMX request with X-Tab header
        console.log(`🔄 Loading X-Tab: ${tabId}`);
        
        htmx.ajax('GET', targetUrl, {
            headers: {
                'X-Tab': tabId,
                'HX-Request': 'true'
            },
            target: contentArea || '#x-tab-content',
            swap: 'innerHTML'
        }).then(() => {
            // Remove loading overlay on success
            if (contentArea) {
                this.removeLoadingOverlay(contentArea);
            }
            
            // Reinitialize components in the new content
            this.reinitializeScripts(contentArea);
            
            // Set up dynamic reload if needed
            this.setupXTabDynamicReload(container);
            
        }).catch((error) => {
            console.error('X-Tab loading error:', error);
            if (contentArea) {
                this.removeLoadingOverlay(contentArea);
            }
            this.showToast('Failed to load tab content', 'error', 5000);
        });
    },

    // Update active tab state in UI
    updateXTabActiveState(container, activeTabId) {
        // Remove active class from all tabs in this container
        const allTabs = container.querySelectorAll('[data-x-tab]');
        allTabs.forEach(tab => {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        });
        
        // Add active class to current tab
        const activeTab = container.querySelector(`[data-x-tab="${activeTabId}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
            activeTab.setAttribute('aria-selected', 'true');
        }
        
        // Update container state
        container.dataset.activeTab = activeTabId;
    },

    // Set up dynamic reload for tabs that support it
    setupXTabDynamicReload(container = document) {
        const reloadTabs = container.querySelectorAll('[data-reload-interval]:not(.reload-setup)');
        
        reloadTabs.forEach(tab => {
            const interval = parseInt(tab.dataset.reloadInterval);
            if (interval > 0) {
                // Clear any existing interval
                if (tab._reloadTimer) {
                    clearInterval(tab._reloadTimer);
                }
                
                // Set up new interval for active tabs only
                tab._reloadTimer = setInterval(() => {
                    if (tab.classList.contains('active') && document.contains(tab)) {
                        console.log(`🔄 Auto-reloading X-Tab: ${tab.dataset.xTab}`);
                        tab.click();
                    }
                }, interval);
                
                tab.classList.add('reload-setup');
                
                // Clean up on element removal
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'childList') {
                            mutation.removedNodes.forEach((node) => {
                                if (node === tab && tab._reloadTimer) {
                                    clearInterval(tab._reloadTimer);
                                    observer.disconnect();
                                }
                            });
                        }
                    });
                });
                
                observer.observe(document.body, { childList: true, subtree: true });
            }
        });
    },

    // Manually trigger X-Tab navigation (programmatic API)
    switchToXTab(containerId, tabId) {
        const container = document.querySelector(`#${containerId}, [data-x-tab-container="${containerId}"]`);
        if (!container) {
            console.warn(`X-Tab container not found: ${containerId}`);
            return;
        }
        
        const tabLink = container.querySelector(`[data-x-tab="${tabId}"]`);
        if (!tabLink) {
            console.warn(`X-Tab not found: ${tabId} in container ${containerId}`);
            return;
        }
        
        tabLink.click();
    },

    /**
     * Loading State Management
     */

    // Show loading state on element
    showLoading(element, message = 'Loading...') {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (!el) return;

        el.classList.add('htmx-loading');
        el.setAttribute('data-loading-message', message);
        
        // Add spinner if not present
        if (!el.querySelector('.loading-spinner')) {
            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner d-flex align-items-center justify-content-center p-3';
            spinner.innerHTML = `
                <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
                <span>${message}</span>
            `;
            el.prepend(spinner);
        }
    },

    // Hide loading state on element
    hideLoading(element) {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (!el) return;

        el.classList.remove('htmx-loading');
        el.removeAttribute('data-loading-message');
        
        // Remove spinner
        const spinner = el.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    },

    /**
     * Notification Management
     */

    // Show toast notification with enhanced features
    showToast(message, type = 'info', duration = 5000) {
        if (typeof bootstrap === 'undefined') {
            console.warn('Bootstrap not available for toasts, using console:', message);
            return;
        }

        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0 shadow-sm" 
                 role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body d-flex align-items-center">
                        <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                        <span>${this.escapeHtml(message)}</span>
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                            data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);

        const toastElement = document.getElementById(toastId);
        if (toastElement) {
            const toast = new bootstrap.Toast(toastElement, { 
                delay: duration,
                autohide: duration > 0 
            });
            
            toast.show();

            // Clean up after hiding
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        }
    },

    // Escape HTML to prevent XSS
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // Create toast container if it doesn't exist
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        container.setAttribute('role', 'region');
        container.setAttribute('aria-label', 'Notifications');
        document.body.appendChild(container);
        return container;
    },

    // Get icon for toast type
    getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'info': 'info-circle', 
            'warning': 'exclamation-triangle',
            'danger': 'times-circle',
            'error': 'times-circle',
            'primary': 'star',
            'secondary': 'gear'
        };
        return icons[type] || 'info-circle';
    },

    /**
     * Modal & Dialog Management
     */

    // Enhanced confirm action with better UX
    confirmAction(message, callback, options = {}) {
        if (typeof bootstrap === 'undefined') {
            // Fallback to native confirm
            if (window.confirm(message)) {
                callback?.();
            }
            return;
        }

        const modalId = `confirm-modal-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const icon = options.icon || (options.variant === 'danger' ? 'exclamation-triangle' : 'question-circle');
        
        const modalHtml = `
            <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}-title" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header border-0 pb-0">
                            <h5 class="modal-title" id="${modalId}-title">
                                <i class="fas fa-${icon} me-2 text-${options.variant || 'primary'}"></i>
                                ${this.escapeHtml(options.title || 'Confirm Action')}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body pt-2">
                            <p class="mb-0">${this.escapeHtml(message)}</p>
                        </div>
                        <div class="modal-footer border-0">
                            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                                ${options.cancelText || 'Cancel'}
                            </button>
                            <button type="button" class="btn btn-${options.variant || 'primary'}" id="${modalId}-confirm">
                                <i class="fas fa-check me-1"></i>
                                ${options.confirmText || 'Confirm'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        const modalElement = document.getElementById(modalId);
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement, {
            backdrop: 'static',
            keyboard: false
        });

        // Handle confirm button
        const confirmBtn = document.getElementById(`${modalId}-confirm`);
        confirmBtn?.addEventListener('click', () => {
            modal.hide();
            callback?.();
        });

        // Handle keyboard events
        modalElement.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.tagName !== 'BUTTON') {
                confirmBtn?.click();
            }
        });

        // Clean up after hiding
        modalElement.addEventListener('hidden.bs.modal', () => {
            modalElement.remove();
        });

        modal.show();
        
        // Focus confirm button after animation
        modalElement.addEventListener('shown.bs.modal', () => {
            confirmBtn?.focus();
        });
    },

    /**
     * HTMX Configuration Management
     */

    // Apply security and HTMX configuration
    applySecurityConfig(container = document) {
        this.setDefaultHtmxPushUrl(container);
        
        // Check direct access - use strict mode only if explicitly enabled
        // Default: passive monitoring mode (no redirects per settings)
        const strictMode = window.HTMXSecurityConfig?.strictDirectAccess || false;
        this.checkDirectAccess({ strict: strictMode });
    },

    // Set default hx-push-url="false" for all HTMX elements (no URL changes allowed)
    setDefaultHtmxPushUrl(container = document) {
        const htmxElements = container.querySelectorAll('[hx-get], [hx-post], [hx-put], [hx-patch], [hx-delete]');
        htmxElements.forEach(element => {
            element.setAttribute('hx-push-url', 'false');
        });
        
        if (htmxElements.length > 0) {
            console.log(`🔒 Applied hx-push-url="false" to ${htmxElements.length} HTMX elements`);
        }
    },

    /**
     * Event Handling Setup
     */

    // Set up all event listeners
    setupEventListeners() {
        // State management
        window.addEventListener('beforeunload', () => {
            window.HyperXState.save();
        });

        // HTMX state updates
        document.body.addEventListener('htmx:afterRequest', (event) => {
            window.HyperXState.updateFromHeaders(event.detail.xhr);
        });

        // Track internal navigation
        document.body.addEventListener('click', (event) => {
            const link = event.target.closest('a');
            if (link?.href?.startsWith(window.location.origin)) {
                this.markInternalNavigation();
            }
        });

        // HTMX request configuration
        document.body.addEventListener('htmx:configRequest', (event) => {
            event.detail.headers['HX-Push-Url'] = 'false';
        });

        // HTMX request lifecycle
        this.setupHTMXEventHandlers();

        // Confirmation dialogs
        this.setupConfirmationHandlers();
    },

    // Set up HTMX-specific event handlers
    setupHTMXEventHandlers() {
        // Before request
        document.body.addEventListener('htmx:beforeRequest', (event) => {
            this.markInternalNavigation();

            const targetSelector = event.target.getAttribute('hx-target');
            if (!targetSelector) return;

            const target = document.querySelector(targetSelector);
            if (!target) return;

            // Clear existing content and add overlay
            target.innerHTML = '';
            this.addLoadingOverlay(target, 'Loading...');
        });

        // After request
        document.body.addEventListener('htmx:afterRequest', (event) => {
            const targetSelector = event.target.getAttribute('hx-target');
            if (targetSelector) {
                this.removeLoadingOverlay(targetSelector);
            }

            if (event.detail.failed) {
                this.showToast('Request failed. Please try again.', 'danger');
            }
        });

        // Response errors
        document.body.addEventListener('htmx:responseError', (event) => {
            console.error('HTMX Response Error:', event.detail);
            this.showToast(`Server error (${event.detail.xhr.status}). Please try again.`, 'danger');
        });

        // Content updated
        document.body.addEventListener('htmx:contentUpdated', (event) => {
            this.reinitializeScripts(event.target);

            // Handle middleware events
            if (event.detail?.redirectConverted) {
                this.showToast('Navigation completed', 'success', 2000);
            }
        });

        // Custom events
        document.body.addEventListener('redirectConverted', (event) => {
            console.log('Redirect converted to render:', event.detail);
            this.showToast('Page updated', 'info', 1500);
        });

        document.body.addEventListener('redirectRenderError', (event) => {
            console.error('Redirect conversion failed:', event.detail);
            this.showToast('Navigation failed, using fallback', 'warning', 3000);
        });
    },

    // Set up confirmation dialog handlers
    setupConfirmationHandlers() {
        document.body.addEventListener('click', (event) => {
            const element = event.target.closest('[data-confirm]');
            if (!element) return;

            event.preventDefault();
            event.stopPropagation();

            const message = element.getAttribute('data-confirm');
            const variant = element.dataset.confirmVariant || 'danger';
            const title = element.dataset.confirmTitle || 'Confirm Action';

            this.confirmAction(message, () => {
                // Execute the intended action
                if (element.hasAttribute('hx-get') || 
                    element.hasAttribute('hx-post') ||
                    element.hasAttribute('hx-put') || 
                    element.hasAttribute('hx-delete')) {
                    htmx.trigger(element, 'click');
                } else if (element.href) {
                    window.location.href = element.href;
                } else if (element.form) {
                    element.form.submit();
                }
            }, { variant, title });
        });
    }
};

// --- Global API Setup ---

// Make reinitializeScripts available globally for middleware compatibility
window.reinitializeScripts = function (container) {
    return window.HTMXUtils.reinitializeScripts(container);
};

// Make key methods available globally for external scripts
window.showToast = function(message, type, duration) {
    return window.HTMXUtils.showToast(message, type, duration);
};

window.confirmAction = function(message, callback, options) {
    return window.HTMXUtils.confirmAction(message, callback, options);
};

// --- Application Initialization ---

document.addEventListener('DOMContentLoaded', function () {
    console.log('🎯 DOM Content Loaded - Starting HTMX Client initialization');
    
    // Initialize the complete system
    window.HTMXUtils.init();
    
    console.log('🎉 HTMX Client System ready');
});

// --- Performance & Debug Helpers ---

// Performance monitoring
if (window.performance && window.performance.mark) {
    window.performance.mark('htmx-client-loaded');
}

// Debug mode helper
window.HTMXDebug = {
    getState() {
        return {
            HyperXState: window.HyperXState,
            initialized: window.HTMXUtils._initialized,
            internalNavigation: window.HTMXUtils._internalNavigation
        };
    },
    
    reinitialize() {
        window.HTMXUtils._initialized = false;
        window.HTMXUtils.init();
    },
    
    testToast(type = 'info') {
        window.HTMXUtils.showToast(`Test ${type} notification`, type, 3000);
    }
};

// --- Module Export Support ---

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        HTMXUtils: window.HTMXUtils,
        HyperXState: window.HyperXState,
        HTMXDebug: window.HTMXDebug
    };
}