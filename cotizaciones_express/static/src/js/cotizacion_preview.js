/** @odoo-module **/
(function () {
    function refreshPreview() {
        var iframe = document.getElementById("cotizacion_preview_iframe");
        var pdfLink = document.getElementById("cotizacion_pdf_link");
        if (!iframe) return;
        var form = iframe.closest(".o_form_view");
        if (form && form.dataset.recordId) {
            var id = form.dataset.recordId;
            iframe.src = "/cotizacion/preview_html/" + id + "?t=" + Date.now();
            if (pdfLink) {
                pdfLink.href = "/report/pdf/cotizaciones_express.report_cotizacion_express/" + id;
            }
        }
    }
    setInterval(refreshPreview, 2000);
    document.addEventListener("change", refreshPreview, true);
    document.addEventListener("input", refreshPreview, true);
})();
