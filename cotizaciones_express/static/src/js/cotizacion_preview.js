/** @odoo-module **/
import { registry } from "@web/core/registry";

const previewService = {
    start() {
        var interval;
        function refreshPreview() {
            var iframe = document.getElementById("cotizacion_preview_iframe");
            if (!iframe) return;
            var form = iframe.closest(".o_form_view");
            if (!form) return;
            if (form.dataset.recordId) {
                var id = form.dataset.recordId;
                iframe.src = "/cotizacion/preview_html/" + id + "?t=" + Date.now();
                var pdfLink = document.getElementById("cotizacion_pdf_link");
                if (pdfLink) {
                    pdfLink.href = "/report/pdf/cotizaciones_express.report_cotizacion_express/" + id;
                }
            } else {
                iframe.src = "data:text/html;charset=utf-8,"
                    + encodeURIComponent('<html><body style="font-family:sans-serif;color:#999;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;"><p>Guarde la cotizaci\u00f3n para ver la vista previa</p></body></html>');
            }
        }
        refreshPreview();
        interval = setInterval(refreshPreview, 2000);
        document.addEventListener("change", refreshPreview, true);
        document.addEventListener("input", refreshPreview, true);
        return {
            stop() {
                clearInterval(interval);
            }
        };
    }
};

registry.category("services").add("cotizacion_preview", previewService);
