/**
 * External Library Admin Management - Frontend JavaScript
 * Handles CRUD operations for external libraries
 */

class ExternalLibraryAdmin {
    constructor() {
        this.adminToken = 'admin-secret'; // In production, get from secure storage
        this.currentLibraries = [];
        this.editingLibraryId = null;
        
        this.init();
    }
    
    init() {
        // Initialize event listeners
        this.bindEvents();
        
        // Load initial data
        this.loadStatistics();
        this.loadLibraries();
    }
    
    bindEvents() {
        // Search functionality
        document.getElementById('search-input')?.addEventListener('input', 
            this.debounce(this.handleSearch.bind(this), 300));
        
        // Include deleted toggle
        document.getElementById('include-deleted')?.addEventListener('change', 
            this.loadLibraries.bind(this));
        
        // Form submission
        document.getElementById('libraryForm')?.addEventListener('submit', 
            this.handleFormSubmit.bind(this));
        
        // Modal events
        document.getElementById('libraryModal')?.addEventListener('hidden.bs.modal', 
            this.resetForm.bind(this));
    }
    
    debounce(func, wait) {
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
    
    async apiCall(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-Token': this.adminToken,
                'X-Admin-User': 'admin-ui'
            }
        };
        
        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(endpoint, finalOptions);
            
            if (!response.ok) {
                const error = await response.text();
                throw new Error(`API call failed: ${response.status} - ${error}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API call error:', error);
            this.showAlert('API Error: ' + error.message, 'danger');
            throw error;
        }
    }
    
    async loadStatistics() {
        try {
            const stats = await this.apiCall('/api/admin/libraries/stats');
            
            document.getElementById('total-libraries').textContent = stats.total_libraries;
            document.getElementById('active-libraries').textContent = stats.active_libraries;
            document.getElementById('deleted-libraries').textContent = stats.deleted_libraries;
            document.getElementById('total-users').textContent = stats.total_external_users;
        } catch (error) {
            console.error('Failed to load statistics:', error);
        }
    }
    
    async loadLibraries() {
        const container = document.getElementById('libraries-container');
        const loading = document.getElementById('loading-indicator');
        const emptyState = document.getElementById('empty-state');
        
        // Show loading
        loading.classList.remove('d-none');
        container.classList.add('d-none');
        emptyState.classList.add('d-none');
        
        try {
            const includeDeleted = document.getElementById('include-deleted')?.checked || false;
            const searchQuery = document.getElementById('search-input')?.value.trim();
            
            let url = `/api/admin/libraries?include_deleted=${includeDeleted}`;
            if (searchQuery) {
                url += `&search=${encodeURIComponent(searchQuery)}`;
            }
            
            const data = await this.apiCall(url);
            this.currentLibraries = data.libraries;
            
            this.renderLibraries(data.libraries);
            
            // Hide loading
            loading.classList.add('d-none');
            
            if (data.libraries.length === 0) {
                emptyState.classList.remove('d-none');
            } else {
                container.classList.remove('d-none');
            }
            
        } catch (error) {
            console.error('Failed to load libraries:', error);
            loading.classList.add('d-none');
            container.innerHTML = '<div class="col-12"><div class="alert alert-danger">Failed to load libraries</div></div>';
            container.classList.remove('d-none');
        }
    }
    
    renderLibraries(libraries) {
        const container = document.getElementById('libraries-container');
        
        if (libraries.length === 0) {
            container.innerHTML = '';
            return;
        }
        
        const html = libraries.map(library => this.renderLibraryCard(library)).join('');
        container.innerHTML = html;
    }
    
    renderLibraryCard(library) {
        const statusClass = library.status === 'active' ? 'success' : 'danger';
        const statusIcon = library.status === 'active' ? 'check-circle' : 'times-circle';
        
        const externalUsers = library.external_users.map(user => 
            `<span class="user-pill" title="${user.name}${user.organization ? ' - ' + user.organization : ''}">${user.email}</span>`
        ).join('');
        
        return `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card library-card h-100">
                    <div class="card-header d-flex justify-content-between align-items-start">
                        <h6 class="card-title mb-0">${this.escapeHtml(library.name)}</h6>
                        <span class="badge bg-${statusClass} status-badge">
                            <i class="fas fa-${statusIcon} me-1"></i>${library.status}
                        </span>
                    </div>
                    <div class="card-body">
                        <p class="text-muted small mb-2">
                            <i class="fas fa-link me-1"></i>
                            <a href="${library.url}" target="_blank" class="text-decoration-none">
                                ${this.truncateUrl(library.url)}
                            </a>
                        </p>
                        
                        ${library.description ? 
                            `<p class="card-text small">${this.escapeHtml(library.description)}</p>` : 
                            '<p class="card-text text-muted small"><em>No description</em></p>'
                        }
                        
                        ${library.external_users.length > 0 ? 
                            `<div class="mb-2">
                                <small class="text-muted">External Users:</small><br>
                                ${externalUsers}
                            </div>` : 
                            '<div class="mb-2"><small class="text-muted">No external users</small></div>'
                        }
                        
                        <div class="text-muted small">
                            <div>Created: ${this.formatDate(library.created_at)}</div>
                            ${library.updated_at !== library.created_at ? 
                                `<div>Updated: ${this.formatDate(library.updated_at)}</div>` : ''
                            }
                        </div>
                    </div>
                    <div class="card-footer">
                        <div class="library-actions">
                            <button class="btn btn-outline-primary btn-sm" onclick="editLibrary('${library.id}')">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            ${library.status === 'active' ? 
                                `<button class="btn btn-outline-danger btn-sm" onclick="deleteLibrary('${library.id}', '${this.escapeHtml(library.name)}')">
                                    <i class="fas fa-trash"></i> Delete
                                </button>` :
                                `<button class="btn btn-outline-success btn-sm" onclick="restoreLibrary('${library.id}')">
                                    <i class="fas fa-undo"></i> Restore
                                </button>`
                            }
                            <button class="btn btn-outline-info btn-sm" onclick="testConnection('${library.id}')">
                                <i class="fas fa-plug"></i> Test
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    handleSearch() {
        this.loadLibraries();
    }
    
    async handleFormSubmit(event) {
        event.preventDefault();
        
        const saveBtn = document.getElementById('save-library-btn');
        const originalText = saveBtn.innerHTML;
        
        // Show loading
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Saving...';
        saveBtn.disabled = true;
        
        try {
            const formData = this.collectFormData();
            
            if (this.editingLibraryId) {
                await this.updateLibrary(this.editingLibraryId, formData);
            } else {
                await this.createLibrary(formData);
            }
            
            // Close modal and refresh
            bootstrap.Modal.getInstance(document.getElementById('libraryModal')).hide();
            this.loadLibraries();
            this.loadStatistics();
            
            this.showAlert(`Library ${this.editingLibraryId ? 'updated' : 'created'} successfully!`, 'success');
            
        } catch (error) {
            console.error('Form submission error:', error);
        } finally {
            saveBtn.innerHTML = originalText;
            saveBtn.disabled = false;
        }
    }
    
    collectFormData() {
        const name = document.getElementById('library-name').value.trim();
        const url = document.getElementById('library-url').value.trim();
        const description = document.getElementById('library-description').value.trim();
        
        const external_users = [];
        const userContainers = document.querySelectorAll('.external-user-row');
        
        userContainers.forEach(container => {
            const email = container.querySelector('.user-email').value.trim();
            const name = container.querySelector('.user-name').value.trim();
            const organization = container.querySelector('.user-organization').value.trim();
            
            if (email && name) {
                external_users.push({ email, name, organization: organization || null });
            }
        });
        
        return {
            name,
            url,
            description: description || null,
            external_users
        };
    }
    
    async createLibrary(libraryData) {
        await this.apiCall('/api/admin/libraries', {
            method: 'POST',
            body: JSON.stringify(libraryData)
        });
    }
    
    async updateLibrary(libraryId, libraryData) {
        await this.apiCall(`/api/admin/libraries/${libraryId}`, {
            method: 'PUT',
            body: JSON.stringify(libraryData)
        });
    }
    
    async deleteLibrary(libraryId) {
        await this.apiCall(`/api/admin/libraries/${libraryId}`, {
            method: 'DELETE'
        });
    }
    
    async restoreLibrary(libraryId) {
        await this.apiCall(`/api/admin/libraries/${libraryId}/restore`, {
            method: 'POST'
        });
    }
    
    async testConnection(libraryId) {
        try {
            const result = await this.apiCall(`/api/admin/libraries/${libraryId}/test-connection`);
            
            const statusIcon = result.connection_status === 'success' ? 'check' : 'times';
            const statusClass = result.connection_status === 'success' ? 'success' : 'danger';
            
            this.showAlert(
                `<i class="fas fa-${statusIcon}"></i> Connection test ${result.connection_status}: ${result.library_name}`,
                statusClass
            );
        } catch (error) {
            this.showAlert('Connection test failed', 'danger');
        }
    }
    
    resetForm() {
        document.getElementById('libraryForm').reset();
        document.getElementById('external-users-container').innerHTML = '';
        this.editingLibraryId = null;
        document.getElementById('libraryModalTitle').textContent = 'Add External Library';
    }
    
    showAlert(message, type = 'info') {
        // Create alert element
        const alertId = 'alert-' + Date.now();
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
    
    // Utility methods
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    truncateUrl(url, maxLength = 40) {
        if (url.length <= maxLength) return url;
        return url.substring(0, maxLength) + '...';
    }
    
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }
}

// Global functions for button clicks
function editLibrary(libraryId) {
    window.libraryAdmin.editLibrary(libraryId);
}

function deleteLibrary(libraryId, libraryName) {
    window.libraryAdmin.showDeleteConfirmation(libraryId, libraryName);
}

function restoreLibrary(libraryId) {
    window.libraryAdmin.restoreLibraryConfirmed(libraryId);
}

function testConnection(libraryId) {
    window.libraryAdmin.testConnection(libraryId);
}

function showCreateLibraryModal() {
    window.libraryAdmin.showCreateModal();
}

function refreshLibraries() {
    window.libraryAdmin.loadLibraries();
    window.libraryAdmin.loadStatistics();
}

function addExternalUser() {
    window.libraryAdmin.addExternalUserRow();
}

// Extend the class with additional methods
ExternalLibraryAdmin.prototype.editLibrary = function(libraryId) {
    const library = this.currentLibraries.find(lib => lib.id === libraryId);
    if (!library) return;
    
    this.editingLibraryId = libraryId;
    
    // Populate form
    document.getElementById('library-name').value = library.name;
    document.getElementById('library-url').value = library.url;
    document.getElementById('library-description').value = library.description || '';
    
    // Populate external users
    const container = document.getElementById('external-users-container');
    container.innerHTML = '';
    
    library.external_users.forEach(user => {
        this.addExternalUserRow(user);
    });
    
    // Update modal title
    document.getElementById('libraryModalTitle').textContent = 'Edit External Library';
    
    // Show modal
    new bootstrap.Modal(document.getElementById('libraryModal')).show();
};

ExternalLibraryAdmin.prototype.showCreateModal = function() {
    this.resetForm();
    new bootstrap.Modal(document.getElementById('libraryModal')).show();
};

ExternalLibraryAdmin.prototype.showDeleteConfirmation = function(libraryId, libraryName) {
    document.getElementById('delete-library-name').textContent = libraryName;
    
    const confirmBtn = document.getElementById('confirm-delete-btn');
    confirmBtn.onclick = () => {
        this.deleteLibraryConfirmed(libraryId);
        bootstrap.Modal.getInstance(document.getElementById('deleteModal')).hide();
    };
    
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
};

ExternalLibraryAdmin.prototype.deleteLibraryConfirmed = async function(libraryId) {
    try {
        await this.deleteLibrary(libraryId);
        this.loadLibraries();
        this.loadStatistics();
        this.showAlert('Library deleted successfully!', 'success');
    } catch (error) {
        console.error('Delete error:', error);
    }
};

ExternalLibraryAdmin.prototype.restoreLibraryConfirmed = async function(libraryId) {
    try {
        await this.restoreLibrary(libraryId);
        this.loadLibraries();
        this.loadStatistics();
        this.showAlert('Library restored successfully!', 'success');
    } catch (error) {
        console.error('Restore error:', error);
    }
};

ExternalLibraryAdmin.prototype.addExternalUserRow = function(user = null) {
    const container = document.getElementById('external-users-container');
    const userIndex = container.children.length;
    
    const userHtml = `
        <div class="external-user-row border rounded p-3 mb-2">
            <div class="row">
                <div class="col-md-4">
                    <label class="form-label">Email *</label>
                    <input type="email" class="form-control user-email" required 
                           value="${user ? user.email : ''}" placeholder="user@example.com">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Name *</label>
                    <input type="text" class="form-control user-name" required 
                           value="${user ? user.name : ''}" placeholder="Full Name">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Organization</label>
                    <input type="text" class="form-control user-organization" 
                           value="${user && user.organization ? user.organization : ''}" placeholder="Optional">
                </div>
                <div class="col-md-1 d-flex align-items-end">
                    <button type="button" class="btn btn-outline-danger btn-sm" onclick="this.parentElement.parentElement.parentElement.remove()">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', userHtml);
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.libraryAdmin = new ExternalLibraryAdmin();
});