from odoo import http
from odoo.http import request


class CotizacionExpressController(http.Controller):

    @http.route('/cotizacion/preview_html/<int:cotizacion_id>', type='http', auth='user', website=False)
    def preview_cotizacion_html(self, cotizacion_id, **kwargs):
        if cotizacion_id > 0:
            cotizacion = request.env['cotizacion.express'].browse(cotizacion_id)
            if not cotizacion.exists():
                cotizacion = request.env['cotizacion.express']
        else:
            cotizacion = request.env['cotizacion.express']

        response = request.render('cotizaciones_express.cotizacion_preview_template', {
            'docs': cotizacion,
            'preview_mode': True,
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    @http.route('/cotizacion/preview.js', type='http', auth='public', website=False)
    def preview_js(self):
        js = r"""(function(){function r(){try{var e=parent.location.hash.replace(/^#/,"").split("&");for(var t=0;t<e.length;t++){var n=e[t].split("=");if(n[0]==="id"&&decodeURIComponent(n[1])>0)return parseInt(decodeURIComponent(n[1]),10)}return null}catch(e){return null}}function u(t){fetch("/cotizacion/preview_html/"+t+"?t="+(new Date).getTime()).then(function(r){return r.text()}).then(function(t){document.open();document.write(t);document.close()}).catch(function(){})}function t(){var e=r();if(e&&e>0){u(e);setTimeout(t,3e3)}else{setTimeout(t,1500)}}t()})();"""
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
