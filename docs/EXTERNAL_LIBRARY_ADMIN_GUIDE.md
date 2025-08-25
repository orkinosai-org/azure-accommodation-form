# External Library Admin List and Management - User Guide

## Overview

The External Library Admin List feature provides centralized management of external SharePoint libraries and their metadata for integration with the Azure Accommodation Form application. This feature allows administrators to manage which external libraries are available to users and control access through external user management.

## Features

### Core Functionality
- **Library Management**: Add, edit, and manage external SharePoint libraries
- **User Access Control**: Define external users who can access each library
- **Soft Delete**: Mark libraries as deleted while preserving audit trails
- **Status Management**: Track library status (active/deleted)
- **Connection Testing**: Test connectivity to external libraries
- **Search & Filter**: Find libraries quickly with search and filtering options

### Data Fields
Each external library record contains:
- **Library Name**: Descriptive name for the library
- **URL**: Complete SharePoint library URL
- **Info/Description**: Optional description of the library's purpose
- **Status**: Active or Deleted state
- **External Users**: List of users outside the organization with access
  - Email address
  - Full name
  - Organization (optional)
- **Audit Information**: Creation and modification timestamps and users

## Admin Interface

### Accessing the Admin Interface

1. Navigate to `/admin/libraries` in your web browser
2. Ensure you have admin authentication token configured
3. The interface will load with current library statistics and management tools

### Dashboard Overview

The admin dashboard displays:
- **Statistics Cards**: Total, active, deleted libraries, and external user count
- **Library Grid**: Visual cards showing all managed libraries
- **Control Panel**: Search, filtering, and action buttons

### Managing Libraries

#### Adding a New Library

1. Click **"Add Library"** button
2. Fill in the required information:
   - **Library Name**: Enter a descriptive name
   - **Library URL**: Enter the complete SharePoint URL
   - **Description**: Optional description of the library
   - **External Users**: Add users who need access
3. Click **"Save Library"**

#### Editing a Library

1. Find the library in the grid
2. Click **"Edit"** button on the library card
3. Modify the desired fields
4. Click **"Save Library"**

#### Deleting a Library

1. Find the library in the grid
2. Click **"Delete"** button on the library card
3. Confirm the deletion in the popup dialog

**Note**: Deletion is "soft" - the library is marked as deleted but preserved for audit purposes.

#### Restoring a Deleted Library

1. Enable **"Include deleted libraries"** toggle
2. Find the deleted library (marked with red status)
3. Click **"Restore"** button
4. The library will be reactivated

#### Testing Library Connectivity

1. Find the library in the grid
2. Click **"Test"** button
3. The system will attempt to connect to the library URL
4. Results will be displayed in a notification

### External User Management

#### Adding External Users

1. When creating or editing a library, scroll to **"External Users"** section
2. Click **"Add User"** button
3. Fill in user information:
   - **Email**: Required - user's email address
   - **Name**: Required - user's full name
   - **Organization**: Optional - user's organization
4. Repeat for additional users
5. Remove users by clicking the trash icon

#### User Access Control

External users defined in the library configuration represent users outside your organization who should have access to the library. This information can be used by:
- Access control systems
- Audit logs
- Permission management tools
- Integration with SharePoint permissions

### Search and Filtering

#### Search Functionality
- Use the search box to find libraries by name or description
- Search is case-insensitive and matches partial text
- Results update automatically as you type

#### Filtering Options
- **Include Deleted Libraries**: Toggle to show/hide deleted libraries
- **Status Filter**: Filter by active or deleted status

## API Integration

### Public Endpoint

The system provides a public endpoint for frontend applications to retrieve active libraries:

```
GET /api/admin/public/active-libraries
```

This endpoint returns only active libraries with essential information for frontend use.

### Admin Endpoints

Full CRUD operations are available through admin-authenticated endpoints:

- `GET /api/admin/libraries` - List libraries with pagination
- `POST /api/admin/libraries` - Create new library
- `GET /api/admin/libraries/{id}` - Get specific library
- `PUT /api/admin/libraries/{id}` - Update library
- `DELETE /api/admin/libraries/{id}` - Soft delete library
- `POST /api/admin/libraries/{id}/restore` - Restore deleted library
- `GET /api/admin/libraries/stats` - Get statistics
- `GET /api/admin/libraries/{id}/test-connection` - Test connectivity

### External User Management Endpoints

These endpoints ensure all external user operations go through the admin-managed system:

#### Add External User (Admin Only)
```
POST /api/admin/libraries/{library_id}/external-users
Content-Type: application/json
X-Admin-Token: your-admin-token

{
    "email": "user@example.com",
    "name": "User Name",
    "organization": "Company Name"
}
```

#### Remove External User (Admin Only)
```
DELETE /api/admin/libraries/{library_id}/external-users/{user_email}
X-Admin-Token: your-admin-token
```

#### Get External Users (Admin Only)
```
GET /api/admin/libraries/{library_id}/external-users
X-Admin-Token: your-admin-token
```

#### Check User Access (Public)
```
POST /api/admin/libraries/{library_id}/external-users/check-access
Content-Type: application/json

{
    "user_email": "user@example.com"
}
```

### Response Examples

#### Add User Response
```json
{
    "message": "User user@example.com added to library successfully",
    "library_id": "lib-123",
    "user": {
        "email": "user@example.com",
        "name": "User Name",
        "organization": "Company Name"
    },
    "total_users": 3
}
```

#### Check Access Response
```json
{
    "library_id": "lib-123",
    "library_name": "Project Documents",
    "user_email": "user@example.com",
    "has_access": true,
    "user_details": {
        "email": "user@example.com",
        "name": "User Name",
        "organization": "Company Name"
    },
    "total_external_users": 3
}
```

## Frontend Integration

### Loading Libraries in Web Parts

Web parts should load libraries from the admin-managed list instead of hardcoded sources:

```javascript
// Load active libraries for user selection
async function loadAvailableLibraries() {
    try {
        const response = await fetch('/api/admin/public/active-libraries');
        const libraries = await response.json();
        
        // Use libraries in your web part
        populateLibrarySelector(libraries);
    } catch (error) {
        console.error('Failed to load libraries:', error);
    }
}
```

### Respecting Library Status

Always check the library status and only show active libraries to end users:

```javascript
function filterActiveLibraries(libraries) {
    return libraries.filter(lib => lib.status === 'active');
}
```

### External User Management in Web Parts

**IMPORTANT:** All external user add/remove operations must go through the External Library Admin API. Web parts should never manage external users directly.

#### Using the External Library Integration API

```javascript
// Initialize the integration
await window.externalLibraryAPI.init();

// Create external user manager interface
await window.externalLibraryAPI.createExternalUserManager('container-id', 'library-id');

// Add external user (admin only)
await window.externalLibraryAPI.addExternalUser('library-id', {
    email: 'user@example.com',
    name: 'User Name',
    organization: 'Company Name'
});

// Remove external user (admin only)
await window.externalLibraryAPI.removeExternalUser('library-id', 'user@example.com');

// Check user access
const accessInfo = await window.externalLibraryAPI.checkUserAccess('library-id', 'user@example.com');
```

#### Web Part Best Practices

1. **Always use admin-managed lists**: Never hardcode external user lists in web parts
2. **Use API endpoints**: All external user operations must go through `/api/admin/libraries/{id}/external-users`
3. **Check permissions**: Validate user access using the admin list before granting access
4. **Handle errors gracefully**: Provide user-friendly error messages for failed operations
5. **Refresh data**: Reload library data after user management operations

#### Example Web Part Structure

```javascript
class ExternalUserWebPart {
    async init() {
        // Initialize external library integration
        await window.externalLibraryAPI.init();
        
        // Create library selector
        await this.createLibrarySelector();
        
        // Set up user management interface
        this.setupUserManagement();
    }
    
    async createLibrarySelector() {
        await window.externalLibraryAPI.createSelector('library-container', {
            onChange: (library) => this.onLibrarySelected(library)
        });
    }
    
    async onLibrarySelected(library) {
        // Create user management interface for selected library
        await window.externalLibraryAPI.createExternalUserManager(
            'user-management-container', 
            library.id
        );
    }
    
    async checkUserAccess(userEmail) {
        // Always check against admin-managed list
        return await window.externalLibraryAPI.checkUserAccess(
            this.selectedLibraryId, 
            userEmail
        );
    }
}
```

### Required Script Includes

Include the external library integration script in your web parts:

```html
<script src="/static/js/external-library-integration.js"></script>
```

## Security Considerations

### Admin Authentication

- Admin endpoints require proper authentication tokens
- In production, implement robust admin authentication
- Use HTTPS for all admin operations
- Regularly rotate admin tokens

### External User Data

- Store minimal user information required for access control
- Follow data protection regulations (GDPR, etc.)
- Audit access to user information
- Implement proper data retention policies

### Library URLs

- Validate SharePoint URLs before storing
- Test connectivity before activation
- Monitor for changes in library accessibility
- Implement proper error handling for inaccessible libraries

## Troubleshooting

### Common Issues

#### Library Not Appearing in Frontend
1. Check library status - ensure it's "active"
2. Verify the public endpoint is accessible
3. Check browser console for API errors
4. Ensure the frontend is calling the correct endpoint

#### Connection Test Failing
1. Verify the SharePoint URL is correct and accessible
2. Check network connectivity from the server
3. Ensure proper permissions on the SharePoint library
4. Check for firewall or proxy restrictions

#### Admin Interface Not Loading
1. Verify admin authentication token
2. Check browser console for JavaScript errors
3. Ensure all static assets are loading correctly
4. Verify the admin page route is accessible

### Monitoring and Logs

- Monitor API endpoint usage
- Track library creation and modification activities
- Log connection test results
- Monitor for failed authentication attempts

## Best Practices

### Library Management
- Use descriptive names for libraries
- Include meaningful descriptions
- Regularly test library connectivity
- Archive unused libraries instead of deleting
- Document library purposes and access requirements

### User Management
- Keep external user lists up to date
- Remove users who no longer need access
- Use organization field for better tracking
- Coordinate with SharePoint administrators for permissions

### System Maintenance
- Regular backups of library configuration
- Monitor system performance
- Update documentation when processes change
- Train multiple administrators on the system

## Support and Maintenance

### Regular Tasks
- Review and update library lists monthly
- Test library connectivity quarterly
- Audit external user access semi-annually
- Update documentation as needed

### Escalation Process
1. Check system logs for errors
2. Verify network connectivity
3. Contact SharePoint administrators if needed
4. Escalate to system administrators for application issues

This documentation should be reviewed and updated regularly as the system evolves and new features are added.