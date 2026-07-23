/** @odoo-module **/

function getErrorChainDetails(errorObj) {
    if (!errorObj) return '';
    var parts = [];
    var current = errorObj;
    var visited = typeof Set !== 'undefined' ? new Set() : null;
    var depth = 0;

    while (current && depth < 10) {
        if (visited) {
            if (visited.has(current)) break;
            visited.add(current);
        }

        try {
            if (typeof current === 'string') {
                parts.push(current);
            } else if (typeof current === 'object') {
                if (current.name) parts.push(String(current.name));
                if (current.message) parts.push(String(current.message));
                if (current.stack) parts.push(String(current.stack));
                parts.push(String(current));
            }
        } catch(e) {}

        // Traverse cause (ES2022 Error cause), error, or reason properties
        var next = null;
        try {
            next = current.cause || current.error || current.reason;
        } catch(e) {}

        current = next;
        depth++;
    }

    return parts.join(' --- ');
}

function isCrossOriginCleanupError(event) {
    if (!event) return false;
    try {
        var details = '';
        if (event.reason) details += ' ' + getErrorChainDetails(event.reason);
        if (event.error) details += ' ' + getErrorChainDetails(event.error);
        if (event.detail) details += ' ' + getErrorChainDetails(event.detail);
        if (event.message) details += ' ' + String(event.message);

        var hasRemoveListener = details.indexOf('removeEventListener') !== -1;
        var hasCrossOrigin = details.indexOf('cross-origin') !== -1 || details.indexOf('Permission denied') !== -1;
        var hasEarlyListener = details.indexOf('useEarlyExternalListener') !== -1;
        var hasOwlLifecycle = details.indexOf('owl lifecycle') !== -1 || details.indexOf('OwlError') !== -1;

        if (hasRemoveListener || 
            (hasCrossOrigin && hasEarlyListener) || 
            (hasCrossOrigin && hasRemoveListener) ||
            (hasOwlLifecycle && (hasCrossOrigin || hasRemoveListener || hasEarlyListener))) {
            return true;
        }
    } catch(e) {}
    return false;
}

// Interceptor global de errores cross-origin para evitar la ventana emergente de Owl al desmontar la vista previa iframe
window.addEventListener('unhandledrejection', function(event) {
    if (isCrossOriginCleanupError(event)) {
        event.preventDefault();
        if (event.stopImmediatePropagation) {
            event.stopImmediatePropagation();
        }
    }
}, true);

window.addEventListener('error', function(event) {
    if (isCrossOriginCleanupError(event)) {
        event.preventDefault();
        if (event.stopImmediatePropagation) {
            event.stopImmediatePropagation();
        }
    }
}, true);

