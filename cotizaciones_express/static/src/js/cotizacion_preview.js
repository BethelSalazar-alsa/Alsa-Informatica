odoo.define('cotizaciones_express.cotizacion_preview', function (require) {
    "use strict";

    var iframe = document.getElementById('cotizacion_preview_iframe');
    if (!iframe) return;

    function updateSrc() {
        var form = iframe.closest('.o_form_view');
        if (form && form.dataset.recordId) {
            iframe.src = '/cotizacion/preview_html/' + form.dataset.recordId;
        }
    }

    var form = iframe.closest('.o_form_view');
    if (form) {
        var observer = new MutationObserver(updateSrc);
        observer.observe(form, {
            attributes: true,
            attributeFilter: ['data-record-id'],
            childList: false,
            subtree: false,
        });
    }

    document.addEventListener('change', function () {
        if (iframe.src) {
            iframe.src = iframe.src;
        }
    });
});
