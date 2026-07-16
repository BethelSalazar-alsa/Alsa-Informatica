from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home
import json


class CotizacionExpressController(http.Controller):

    @http.route('/cotizacion/preview/<int:cotizacion_id>', type='http', auth='user', website=False)
    def preview_cotizacion(self, cotizacion_id):
        cotizacion = request.env['cotizacion.express'].browse(cotizacion_id)
        if not cotizacion.exists():
            return request.not_found()
        return request.render('cotizaciones_express.cotizacion_preview_template', {
            'doc': cotizacion,
            'company': request.env.company,
        })

    @http.route('/cotizacion/preview_html/<int:cotizacion_id>', type='http', auth='user', website=False)
    def preview_cotizacion_html(self, cotizacion_id):
        cotizacion = request.env['cotizacion.express'].browse(cotizacion_id)
        if not cotizacion.exists():
            return request.not_found()
        return request.render('cotizaciones_express.cotizacion_preview_template', {
            'doc': cotizacion,
            'company': request.env.company,
        })
