/** @odoo-module **/

// Interceptor global de errores cross-origin para evitar la ventana emergente de Owl al desmontar la vista previa iframe
window.addEventListener('unhandledrejection', function(event) {
    try {
        var reason = event ? (event.reason || event) : '';
        var msg = (reason && reason.message) ? reason.message : String(reason);
        var stack = (reason && reason.stack) ? reason.stack : '';
        
        if (msg.indexOf('removeEventListener') !== -1 || 
            msg.indexOf('cross-origin') !== -1 || 
            stack.indexOf('useEarlyExternalListener') !== -1) {
            event.preventDefault();
            if (event.stopImmediatePropagation) {
                event.stopImmediatePropagation();
            }
        }
    } catch(e) {}
}, true);

window.addEventListener('error', function(event) {
    try {
        var msg = event ? String(event.message || event.error || '') : '';
        if (msg.indexOf('removeEventListener') !== -1 || msg.indexOf('cross-origin') !== -1) {
            event.preventDefault();
            if (event.stopImmediatePropagation) {
                event.stopImmediatePropagation();
            }
        }
    } catch(e) {}
}, true);
