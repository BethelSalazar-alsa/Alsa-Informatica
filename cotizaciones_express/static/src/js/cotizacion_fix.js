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

// --- TOGGLES ---
function movePdfToChatterPosition(form) {
    var rightCol = form.querySelector('.o_cotizacion_right_column');
    var sheetBg = form.querySelector('.o_form_sheet_bg');
    if (rightCol && sheetBg) {
        sheetBg.after(rightCol);
    }
}

function movePdfToOriginalPosition(form) {
    var rightCol = form.querySelector('.o_cotizacion_right_column');
    var flexContainer = form.querySelector('.o_cotizacion_flex_container');
    if (rightCol && flexContainer) {
        flexContainer.appendChild(rightCol);
    }
}

function repositionPdf(form) {
    if (form.classList.contains('hide-pdf')) return;
    if (!form.classList.contains('hide-chatter')) {
        movePdfToOriginalPosition(form);
    } else {
        movePdfToChatterPosition(form);
    }
}

document.addEventListener('click', function(e) {
    var form = e.target.closest('.o_cotizacion_express_form');
    if (!form) return;

    var pdfBtn = e.target.closest('.btn-toggle-pdf');
    if (pdfBtn) {
        form.classList.toggle('hide-pdf');
        pdfBtn.classList.toggle('collapsed');
        repositionPdf(form);
        return;
    }

    var chatterBtn = e.target.closest('.btn-toggle-chatter');
    if (chatterBtn) {
        form.classList.toggle('hide-chatter');
        chatterBtn.classList.toggle('collapsed');
        repositionPdf(form);
        return;
    }
});
