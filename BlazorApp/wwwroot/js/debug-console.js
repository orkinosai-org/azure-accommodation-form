// Debug console helper for Azure Accommodation Form
// This script provides JavaScript interop functions for debug logging to browser console
// DEBUG: This entire file is for debugging purposes (production: remove this file)

window.debugConsole = {
    log: function (message, level = 'log') {
        // Add timestamp and prefix to all debug messages
        const timestamp = new Date().toISOString();
        const prefixedMessage = `[DEBUG ${timestamp}] ${message}`;
        
        // Use the appropriate console method based on level
        switch (level.toLowerCase()) {
            case 'error':
                console.error(prefixedMessage);
                break;
            case 'warn':
            case 'warning':
                console.warn(prefixedMessage);
                break;
            case 'info':
                console.info(prefixedMessage);
                break;
            case 'debug':
                console.debug(prefixedMessage);
                break;
            default:
                console.log(prefixedMessage);
                break;
        }
    },
    
    group: function (groupName) {
        const timestamp = new Date().toISOString();
        const prefixedGroupName = `[DEBUG ${timestamp}] ${groupName}`;
        console.group(prefixedGroupName);
    },
    
    groupEnd: function () {
        console.groupEnd();
    },
    
    // Helper method to log objects with proper formatting
    logObject: function (label, obj) {
        const timestamp = new Date().toISOString();
        const prefixedLabel = `[DEBUG ${timestamp}] ${label}`;
        console.log(prefixedLabel, obj);
    },
    
    // Helper method to log formatted key-value pairs
    logKeyValue: function (key, value) {
        const timestamp = new Date().toISOString();
        console.log(`[DEBUG ${timestamp}] ${key}: ${value}`);
    }
};