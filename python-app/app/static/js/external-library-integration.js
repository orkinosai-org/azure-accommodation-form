/**
 * External Library Integration for Form Components
 * This demonstrates how to integrate with the External Library Admin system
 */

class ExternalLibraryIntegration {
    constructor() {
        this.libraries = [];
        this.loadingLibraries = false;
    }
    
    /**
     * Load available external libraries from the admin-managed list
     */
    async loadAvailableLibraries() {
        if (this.loadingLibraries) return;
        
        this.loadingLibraries = true;
        
        try {
            const response = await fetch('/api/admin/public/active-libraries');
            
            if (!response.ok) {
                throw new Error(`Failed to load libraries: ${response.status}`);
            }
            
            this.libraries = await response.json();
            console.log(`Loaded ${this.libraries.length} external libraries`);
            
            return this.libraries;
            
        } catch (error) {
            console.error('Error loading external libraries:', error);
            this.showError('Failed to load external libraries. Please try again.');
            return [];
        } finally {
            this.loadingLibraries = false;
        }
    }
    
    /**
     * Filter libraries by criteria
     */
    filterLibraries(criteria = {}) {
        let filtered = [...this.libraries];
        
        // Filter by search term
        if (criteria.search) {
            const searchTerm = criteria.search.toLowerCase();
            filtered = filtered.filter(lib => 
                lib.name.toLowerCase().includes(searchTerm) ||
                (lib.description && lib.description.toLowerCase().includes(searchTerm))
            );
        }
        
        // Filter by external user access
        if (criteria.userEmail) {
            filtered = filtered.filter(lib =>
                lib.external_users.some(user => 
                    user.email.toLowerCase() === criteria.userEmail.toLowerCase()
                )
            );
        }
        
        return filtered;
    }
    
    /**
     * Create a library selector dropdown
     */
    createLibrarySelector(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }
        
        const selectElement = document.createElement('select');
        selectElement.className = 'form-control';
        selectElement.id = options.selectId || 'library-selector';
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = options.placeholder || 'Select a library...';
        selectElement.appendChild(defaultOption);
        
        // Add library options
        this.libraries.forEach(library => {
            const option = document.createElement('option');
            option.value = library.id;
            option.textContent = library.name;
            option.title = library.description || library.name;
            selectElement.appendChild(option);
        });
        
        // Add change event listener if provided
        if (options.onChange) {
            selectElement.addEventListener('change', (event) => {
                const selectedLibrary = this.getLibraryById(event.target.value);
                options.onChange(selectedLibrary, event);
            });
        }
        
        container.appendChild(selectElement);
        return selectElement;
    }
    
    /**
     * Create a library grid display
     */
    createLibraryGrid(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }
        
        container.innerHTML = '';
        
        if (this.libraries.length === 0) {
            container.innerHTML = '<p class="text-muted">No external libraries available.</p>';
            return;
        }
        
        const grid = document.createElement('div');
        grid.className = 'row';
        
        this.libraries.forEach(library => {
            const col = document.createElement('div');
            col.className = 'col-md-6 col-lg-4 mb-3';
            
            const card = this.createLibraryCard(library, options);
            col.appendChild(card);
            grid.appendChild(col);
        });
        
        container.appendChild(grid);
    }
    
    /**
     * Create a single library card
     */
    createLibraryCard(library, options = {}) {
        const card = document.createElement('div');
        card.className = 'card h-100';
        
        const externalUsers = library.external_users.length > 0 ? 
            `<small class="text-muted">${library.external_users.length} external user(s)</small>` :
            '<small class="text-muted">No external users</small>';
        
        card.innerHTML = `
            <div class="card-body">
                <h6 class="card-title">${this.escapeHtml(library.name)}</h6>
                ${library.description ? 
                    `<p class="card-text text-muted small">${this.escapeHtml(library.description)}</p>` :
                    ''
                }
                <div class="mb-2">
                    <small class="text-muted">
                        <i class="fas fa-link me-1"></i>
                        <a href="${library.url}" target="_blank" class="text-decoration-none">
                            View Library
                        </a>
                    </small>
                </div>
                <div>${externalUsers}</div>
            </div>
            ${options.showActions ? `
                <div class="card-footer">
                    <button class="btn btn-primary btn-sm" onclick="selectLibrary('${library.id}')">
                        Select Library
                    </button>
                </div>
            ` : ''}
        `;
        
        return card;
    }
    
    /**
     * Get library by ID
     */
    getLibraryById(libraryId) {
        return this.libraries.find(lib => lib.id === libraryId);
    }
    
    /**
     * Check if user has access to library
     */
    userHasAccess(library, userEmail) {
        if (!library || !userEmail) return false;
        
        return library.external_users.some(user => 
            user.email.toLowerCase() === userEmail.toLowerCase()
        );
    }
    
    /**
     * Get libraries accessible by user
     */
    getLibrariesForUser(userEmail) {
        if (!userEmail) return this.libraries;
        
        return this.libraries.filter(library => 
            this.userHasAccess(library, userEmail)
        );
    }
    
    /**
     * Utility methods
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }
    
    showError(message) {
        // Create a simple error alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of body
        document.body.insertBefore(alert, document.body.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
    
    /**
     * Initialize external library integration
     */
    async init() {
        try {
            await this.loadAvailableLibraries();
            console.log('External library integration initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize external library integration:', error);
            return false;
        }
    }
}

// Example usage functions that can be called from forms
window.externalLibraryAPI = {
    /**
     * Initialize the library integration system
     */
    async init() {
        if (!window.libraryIntegration) {
            window.libraryIntegration = new ExternalLibraryIntegration();
            await window.libraryIntegration.init();
        }
        return window.libraryIntegration;
    },
    
    /**
     * Create a library selector in the specified container
     */
    async createSelector(containerId, options = {}) {
        const integration = await this.init();
        return integration.createLibrarySelector(containerId, options);
    },
    
    /**
     * Create a library grid in the specified container
     */
    async createGrid(containerId, options = {}) {
        const integration = await this.init();
        return integration.createLibraryGrid(containerId, options);
    },
    
    /**
     * Get all available libraries
     */
    async getLibraries() {
        const integration = await this.init();
        return integration.libraries;
    },
    
    /**
     * Get libraries for a specific user
     */
    async getLibrariesForUser(userEmail) {
        const integration = await this.init();
        return integration.getLibrariesForUser(userEmail);
    }
};

// Global function for library selection (can be called from buttons)
async function selectLibrary(libraryId) {
    if (window.libraryIntegration) {
        const library = window.libraryIntegration.getLibraryById(libraryId);
        if (library) {
            console.log('Selected library:', library);
            
            // Trigger custom event for other components to listen to
            const event = new CustomEvent('librarySelected', {
                detail: { library }
            });
            document.dispatchEvent(event);
            
            // You can add more logic here, such as:
            // - Opening the library in a new window
            // - Storing the selection in the form
            // - Updating UI components
            
            return library;
        }
    }
    return null;
}

// Example of how to use in a form
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize global library integration instance
    if (!window.libraryIntegration) {
        window.libraryIntegration = new ExternalLibraryIntegration();
    }
    
    // Example: Create a library selector in a form (if container exists)
    if (document.getElementById('library-selector-container')) {
        console.log('Library selector container found, will be initialized by form');
    }
    
    // Example: Create a library grid (if container exists)
    if (document.getElementById('library-grid-container')) {
        await window.externalLibraryAPI.createGrid('library-grid-container', {
            showActions: true
        });
    }
    
    // Example: Listen for library selection events
    document.addEventListener('librarySelected', (event) => {
        const library = event.detail.library;
        console.log('Library selected event:', library);
        // Handle the selection in your application
    });
    
    console.log('External library integration initialized');
});