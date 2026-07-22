from odoo import http
from odoo.http import request


class CotizacionExpressController(http.Controller):

    @http.route('/cotizacion/preview_html/<int:cotizacion_id>', type='http', auth='user', website=False)
    def preview_cotizacion_html(self, cotizacion_id, **kwargs):
        if cotizacion_id > 0:
            cotizacion = request.env['cotizacion.express'].browse(cotizacion_id)
            if not cotizacion.exists():
                cotizacion = request.env['cotizacion.express'].new({'name': 'Nueva'})
        else:
            cotizacion = request.env['cotizacion.express'].new({'name': 'Nueva'})

        response = request.render('cotizaciones_express.cotizacion_preview_template', {
            'docs': cotizacion,
            'preview_mode': True,
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    @http.route('/cotizacion/preview.js', type='http', auth='public', website=False)
    def preview_js(self, **kwargs):
        js = r"""(function() {
    try {
        var parentWin = null;
        var parentDoc = null;
        try {
            if (window.parent && window.parent !== window) {
                parentWin = window.parent;
                parentDoc = parentWin.document;
            }
        } catch (e) {
            return;
        }

        if (!parentDoc) return;

        var lastInputTime = 0;
        function onInput() { lastInputTime = Date.now(); }
        function onChange() { lastInputTime = 0; triggerReload(500); }

        try {
            parentDoc.addEventListener('input', onInput, true);
            parentDoc.addEventListener('change', onChange, true);
        } catch (e) {}

        window.addEventListener('unload', function() {
            try {
                if (parentDoc) {
                    parentDoc.removeEventListener('input', onInput, true);
                    parentDoc.removeEventListener('change', onChange, true);
                }
            } catch (e) {}
        });

        function getRecordId() {
            try {
                var formEl = parentDoc.querySelector('.o_form_view');
                if (formEl && formEl.dataset.recordId) {
                    var id = parseInt(formEl.dataset.recordId, 10);
                    if (id > 0) return id;
                }

                var pathname = parentWin.location.pathname;
                var match = pathname.match(/\/cotizacion\.express\/(\d+)/);
                if (match) return parseInt(match[1], 10);

                var hash = parentWin.location.hash;
                var hashMatch = hash.match(/[#&]id=(\d+)/);
                if (hashMatch) return parseInt(hashMatch[1], 10);
                
                var queryMatch = parentWin.location.search.match(/[?&]id=(\d+)/);
                if (queryMatch) return parseInt(queryMatch[1], 10);
            } catch(e) {}
            return 0;
        }

        var parentId = getRecordId();
        var currentUrlMatch = window.location.pathname.match(/\/preview_html\/(\d+)/);
        var currentId = currentUrlMatch ? parseInt(currentUrlMatch[1], 10) : 0;

        var pdfLink = parentDoc.getElementById('cotizacion_pdf_link');
        if (pdfLink) {
            if (parentId > 0) {
                pdfLink.href = "/report/pdf/cotizaciones_express.cotizacion_preview_template/" + parentId;
                pdfLink.style.display = "";
            } else {
                pdfLink.style.display = "none";
            }
        }

        if (currentId === 0 && parentId > 0) {
            window.location.href = "/cotizacion/preview_html/" + parentId + "?t=" + Date.now();
            return;
        }

        var reloadTimeout = null;
        function triggerReload(delay) {
            if (reloadTimeout) clearTimeout(reloadTimeout);
            reloadTimeout = setTimeout(function() {
                try {
                    var activeId = getRecordId();
                    if (activeId > 0 && activeId !== currentId) {
                        window.location.href = "/cotizacion/preview_html/" + activeId + "?t=" + Date.now();
                    } else if (activeId > 0) {
                        window.location.reload();
                    } else if (currentId > 0) {
                        window.location.href = "/cotizacion/preview_html/0?t=" + Date.now();
                    }
                } catch(e) {}
            }, delay || 1000);
        }

        setInterval(function() {
            try {
                var activeId = getRecordId();
                if (activeId !== currentId) {
                    triggerReload(100);
                } else if (activeId > 0 && (Date.now() - lastInputTime > 2000)) {
                    window.location.reload();
                }
            } catch(e) {}
        }, 2500);

    } catch (e) {
        console.warn("Preview iframe safe catch:", e);
    }
})();"""
        return request.make_response(js, [('Content-Type', 'application/javascript; charset=utf-8')])

    @http.route('/cotizacion/image/<string:model>/<int:record_id>/<string:field>', type='http', auth='user', website=False)
    def get_image(self, model, record_id, field, **kwargs):
        Model = request.env.get(model)
        if not Model:
            return request.not_found(description='Modelo no encontrado')
        record = Model.browse(record_id)
        if not record.exists():
            return request.not_found(description='Registro no encontrado')
        value = record[field]
        if not value:
            return request.not_found(description='Sin imagen')
        if isinstance(value, bytes):
            value = value.decode('ascii')
        import base64
        raw = base64.b64decode(value)
        return request.make_response(raw, [('Content-Type', 'image/png')])
