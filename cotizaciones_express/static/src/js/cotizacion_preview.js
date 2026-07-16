/** @odoo-module **/
(function () {
    function refreshPreview() {
        var iframe = document.getElementById("cotizacion_preview_iframe");
        if (!iframe) return;
        var form = iframe.closest(".o_form_view");
        if (form && form.dataset.recordId) {
            iframe.src = "/report/pdf/cotizaciones_express.report_cotizacion_express/"
                + form.dataset.recordId + "?t=" + Date.now();
        }
    }
    setInterval(refreshPreview, 3000);
    document.addEventListener("change", refreshPreview, true);
    document.addEventListener("input", refreshPreview, true);
})();
