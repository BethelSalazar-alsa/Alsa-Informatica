/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { onMounted, onWillUnmount } from "@odoo/owl";

patch(FormController.prototype, "cotizaciones_express_preview", {
    setup() {
        this._super.apply(this, arguments);
        var resModel = this.props.model && this.props.model.resModel;
        if (resModel !== "cotizacion.express") return;

        var interval = null;

        function refreshPreview() {
            var iframe = document.getElementById("cotizacion_preview_iframe");
            if (!iframe) return;
            var form = iframe.closest(".o_form_view");
            if (!form) return;
            var pdfLink = document.getElementById("cotizacion_pdf_link");
            if (form.dataset.recordId) {
                var id = form.dataset.recordId;
                iframe.src = "/cotizacion/preview_html/" + id + "?t=" + Date.now();
                if (pdfLink) {
                    pdfLink.href = "/report/pdf/cotizaciones_express.report_cotizacion_express/" + id;
                }
            } else {
                iframe.src = "data:text/html;charset=utf-8,"
                    + encodeURIComponent('<html><body style="font-family:sans-serif;color:#999;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;"><p>Guarde la cotizaci\u00f3n para ver la vista previa</p></body></html>');
            }
        }

        onMounted(function () {
            refreshPreview();
            interval = setInterval(refreshPreview, 2000);
            document.addEventListener("change", refreshPreview, true);
            document.addEventListener("input", refreshPreview, true);
        });

        onWillUnmount(function () {
            if (interval) clearInterval(interval);
            document.removeEventListener("change", refreshPreview, true);
            document.removeEventListener("input", refreshPreview, true);
        });
    }
});
