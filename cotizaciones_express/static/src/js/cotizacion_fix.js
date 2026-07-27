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

// --- MANEJO DE PLEGADO DE VISTAS (PDF Y CHATTER) ---
try {
    function updateButtonStates(form, pdfVisible, chatterVisible) {
        const pdfBtn = form.querySelector('.btn-toggle-pdf');
        const chatterBtn = form.querySelector('.btn-toggle-chatter');
        
        if (pdfBtn) {
            pdfBtn.setAttribute('data-tooltip', 'Mostrar/Ocultar PDF');
            if (pdfVisible) {
                pdfBtn.classList.remove('collapsed');
            } else {
                pdfBtn.classList.add('collapsed');
            }
        }
        
        if (chatterBtn) {
            chatterBtn.setAttribute('data-tooltip', 'Mostrar/Ocultar Chatter');
            if (chatterVisible) {
                chatterBtn.classList.remove('collapsed');
            } else {
                chatterBtn.classList.add('collapsed');
            }
        }
    }

    function initializeFormState(form) {
        // Por defecto, ambos ocultos (false) si no se han definido en localStorage
        const pdfVisible = localStorage.getItem('cotizacion_pdf_visible') === 'true';
        const chatterVisible = localStorage.getItem('cotizacion_chatter_visible') === 'true';
        
        if (!pdfVisible) {
            form.classList.add('hide-pdf');
        } else {
            form.classList.remove('hide-pdf');
        }
        
        if (!chatterVisible) {
            form.classList.add('hide-chatter');
        } else {
            form.classList.remove('hide-chatter');
        }
        
        updateButtonStates(form, pdfVisible, chatterVisible);
    }

    // Escuchar creación/inserción de formularios en el DOM mediante MutationObserver
    const formObserver = new MutationObserver(function(mutations) {
        const form = document.querySelector('.o_cotizacion_express_form');
        if (form && !form.dataset.viewInitialized) {
            form.dataset.viewInitialized = 'true';
            initializeFormState(form);
        }
    });

    function startObserving() {
        if (document.body) {
            formObserver.observe(document.body, { childList: true, subtree: true });
        } else {
            // Reintento en caso de carga temprana
            setTimeout(startObserving, 50);
        }
    }
    startObserving();

    // Manejo de eventos click con delegación en document
    document.addEventListener('click', function(e) {
        const pdfBtn = e.target.closest('.btn-toggle-pdf');
        if (pdfBtn) {
            const form = pdfBtn.closest('.o_cotizacion_express_form');
            if (form) {
                const isVisible = !form.classList.contains('hide-pdf');
                const newVisible = !isVisible;
                localStorage.setItem('cotizacion_pdf_visible', newVisible);
                if (newVisible) {
                    form.classList.remove('hide-pdf');
                } else {
                    form.classList.add('hide-pdf');
                }
                const chatterVisible = localStorage.getItem('cotizacion_chatter_visible') === 'true';
                updateButtonStates(form, newVisible, chatterVisible);
            }
            return;
        }
        
        const chatterBtn = e.target.closest('.btn-toggle-chatter');
        if (chatterBtn) {
            const form = chatterBtn.closest('.o_cotizacion_express_form');
            if (form) {
                const isVisible = !form.classList.contains('hide-chatter');
                const newVisible = !isVisible;
                localStorage.setItem('cotizacion_chatter_visible', newVisible);
                if (newVisible) {
                    form.classList.remove('hide-chatter');
                } else {
                    form.classList.add('hide-chatter');
                }
                const pdfVisible = localStorage.getItem('cotizacion_pdf_visible') === 'true';
                updateButtonStates(form, pdfVisible, newVisible);
            }
            return;
        }
    });
} catch (e) {
    console.error("Error in cotizacion_express UI controls:", e);
}

