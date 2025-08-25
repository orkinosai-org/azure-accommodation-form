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
     * External User Management (Admin Functions)
     * These functions ensure all user management goes through the admin API
     */
    
    /**
     * Add an external user to a library (admin only)
     */
    async addExternalUser(libraryId, userData) {
        try {
            const response = await fetch(`/api/admin/libraries/${libraryId}/external-users`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Admin-Token': this.getAdminToken()
                },
                body: JSON.stringify(userData)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to add user');
            }
            
            const result = await response.json();
            
            // Refresh libraries to get updated data
            await this.loadAvailableLibraries();
            
            return result;
            
        } catch (error) {
            console.error('Error adding external user:', error);
            this.showError(`Failed to add user: ${error.message}`);
            throw error;
        }
    }
    
    /**
     * Remove an external user from a library (admin only)
     */
    async removeExternalUser(libraryId, userEmail) {
        try {
            const response = await fetch(`/api/admin/libraries/${libraryId}/external-users/${encodeURIComponent(userEmail)}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Admin-Token': this.getAdminToken()
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to remove user');
            }
            
            const result = await response.json();
            
            // Refresh libraries to get updated data
            await this.loadAvailableLibraries();
            
            return result;
            
        } catch (error) {
            console.error('Error removing external user:', error);
            this.showError(`Failed to remove user: ${error.message}`);
            throw error;
        }
    }
    
    /**
     * Get external users for a specific library (admin only)
     */
    async getLibraryExternalUsers(libraryId) {
        try {
            const response = await fetch(`/api/admin/libraries/${libraryId}/external-users`, {
                headers: {
                    'X-Admin-Token': this.getAdminToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`Failed to get users: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Error getting external users:', error);
            this.showError('Failed to load external users.');
            return [];
        }
    }
    
    /**
     * Check if a user has access to a specific library
     */
    async checkUserAccess(libraryId, userEmail) {
        try {
            const response = await fetch(`/api/admin/libraries/${libraryId}/external-users/check-access`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_email: userEmail })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to check access: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Error checking user access:', error);
            return {
                has_access: false,
                error: error.message
            };
        }
    }
    
    /**
     * Create an external user management interface for a library
     */
    createExternalUserManager(containerId, libraryId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }
        
        const library = this.getLibraryById(libraryId);
        if (!library) {
            console.error(`Library ${libraryId} not found`);
            return;
        }
        
        const managerId = `user-manager-${libraryId}`;
        
        container.innerHTML = `
            <div class="external-user-manager" id="${managerId}">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="mb-0">External Users for ${this.escapeHtml(library.name)}</h6>
                    <button class="btn btn-primary btn-sm" onclick="showAddUserModal('${libraryId}')">
                        <i class="fas fa-plus me-1"></i> Add User
                    </button>
                </div>
                
                <div class="external-users-list" id="users-list-${libraryId}">
                    ${this.renderExternalUsersList(library.external_users, libraryId)}
                </div>
                
                <!-- Add User Modal -->
                <div class="modal fade" id="addUserModal-${libraryId}" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Add External User</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="addUserForm-${libraryId}">
                                    <div class="mb-3">
                                        <label class="form-label">Email Address *</label>
                                        <input type="email" class="form-control" name="email" required>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Full Name *</label>
                                        <input type="text" class="form-control" name="name" required>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Organization</label>
                                        <input type="text" class="form-control" name="organization">
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary" onclick="addUserToLibrary('${libraryId}')">
                                    Add User
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        return managerId;
    }
    
    /**
     * Render external users list
     */
    renderExternalUsersList(users, libraryId) {
        if (!users || users.length === 0) {
            return '<div class="text-muted">No external users</div>';
        }
        
        return users.map(user => `
            <div class="d-flex justify-content-between align-items-center border rounded p-2 mb-2">
                <div>
                    <strong>${this.escapeHtml(user.name)}</strong>
                    <br>
                    <small class="text-muted">${this.escapeHtml(user.email)}</small>
                    ${user.organization ? `<br><small class="text-muted">${this.escapeHtml(user.organization)}</small>` : ''}
                </div>
                <button class="btn btn-danger btn-sm" onclick="removeUserFromLibrary('${libraryId}', '${user.email}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');
    }
    
    /**
     * Get admin token (should be implemented based on your auth system)
     */
    getAdminToken() {
        // In production, get from secure storage or authentication context
        return 'admin-secret'; // This should be replaced with proper token management
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
    },
    
    /**
     * Create external user manager interface for a library
     */
    async createExternalUserManager(containerId, libraryId, options = {}) {
        const integration = await this.init();
        return integration.createExternalUserManager(containerId, libraryId, options);
    },
    
    /**
     * Add external user to library (admin only)
     */
    async addExternalUser(libraryId, userData) {
        const integration = await this.init();
        return integration.addExternalUser(libraryId, userData);
    },
    
    /**
     * Remove external user from library (admin only)
     */
    async removeExternalUser(libraryId, userEmail) {
        const integration = await this.init();
        return integration.removeExternalUser(libraryId, userEmail);
    },
    
    /**
     * Get external users for a library (admin only)
     */
    async getLibraryExternalUsers(libraryId) {
        const integration = await this.init();
        return integration.getLibraryExternalUsers(libraryId);
    },
    
    /**
     * Check if user has access to library
     */
    async checkUserAccess(libraryId, userEmail) {
        const integration = await this.init();
        return integration.checkUserAccess(libraryId, userEmail);
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

// Global functions for external user management
async function showAddUserModal(libraryId) {
    const modal = new bootstrap.Modal(document.getElementById(`addUserModal-${libraryId}`));
    modal.show();
}

async function addUserToLibrary(libraryId) {
    if (!window.libraryIntegration) {
        console.error('Library integration not initialized');
        return;
    }
    
    const form = document.getElementById(`addUserForm-${libraryId}`);
    const formData = new FormData(form);
    
    const userData = {
        email: formData.get('email'),
        name: formData.get('name'),
        organization: formData.get('organization') || null
    };
    
    try {
        const result = await window.libraryIntegration.addExternalUser(libraryId, userData);
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById(`addUserModal-${libraryId}`));
        modal.hide();
        
        // Clear form
        form.reset();
        
        // Refresh user list
        await refreshUsersList(libraryId);
        
        // Show success message
        showSuccessMessage(`User ${userData.email} added successfully!`);
        
    } catch (error) {
        console.error('Error adding user:', error);
    }
}

async function removeUserFromLibrary(libraryId, userEmail) {
    if (!window.libraryIntegration) {
        console.error('Library integration not initialized');
        return;
    }
    
    if (!confirm(`Are you sure you want to remove ${userEmail} from this library?`)) {
        return;
    }
    
    try {
        const result = await window.libraryIntegration.removeExternalUser(libraryId, userEmail);
        
        // Refresh user list
        await refreshUsersList(libraryId);
        
        // Show success message
        showSuccessMessage(`User ${userEmail} removed successfully!`);
        
    } catch (error) {
        console.error('Error removing user:', error);
    }
}

async function refreshUsersList(libraryId) {
    if (!window.libraryIntegration) return;
    
    const library = window.libraryIntegration.getLibraryById(libraryId);
    if (!library) return;
    
    const usersList = document.getElementById(`users-list-${libraryId}`);
    if (usersList) {
        usersList.innerHTML = window.libraryIntegration.renderExternalUsersList(library.external_users, libraryId);
    }
}

function showSuccessMessage(message) {
    // Create a simple success alert
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 3000);
}

// Example of how to use in a form
document.addEventListener('DOMContentLoaded', async () => {
    // Example: Create a library selector in a form
    if (document.getElementById('library-selector-container')) {
        await window.externalLibraryAPI.createSelector('library-selector-container', {
            selectId: 'document-library',
            placeholder: 'Choose a document library...',
            onChange: (library, event) => {
                if (library) {
                    console.log('Library selected:', library.name);
                    // Handle library selection in your form
                }
            }
        });
    }
    
    // Example: Create a library grid
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
});