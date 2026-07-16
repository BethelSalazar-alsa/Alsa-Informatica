/** @odoo-module **/
var iframe = document.getElementById("cotizacion_preview_iframe");
if (iframe) {
    setInterval(function () {
        var form = iframe.closest(".o_form_view");
        if (form && form.dataset.recordId) {
            iframe.src = "/cotizacion/preview_html/" + form.dataset.recordId + "?t=" + Date.now();
        }
    }, 2000);
    document.addEventListener("change", function () {
        var form = iframe.closest(".o_form_view");
        if (form && form.dataset.recordId) {
            iframe.src = "/cotizacion/preview_html/" + form.dataset.recordId + "?t=" + Date.now();
        }
    }, true);
    document.addEventListener("input", function () {
        var form = iframe.closest(".o_form_view");
        if (form && form.dataset.recordId) {
            iframe.src = "/cotizacion/preview_html/" + form.dataset.recordId + "?t=" + Date.now();
        }
    }, true);
}
