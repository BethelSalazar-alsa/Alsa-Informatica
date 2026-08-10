from odoo import http
from odoo.http import request

class WebsiteLicencia(http.Controller):
    @http.route('/registrar-licencia', type='http', auth="public", website=True)
    def licencia_form(self, **kwargs):
        # Este nombre debe coincidir con el ID de tu template XML
        return request.render("gestion_licencias.license_registration_form")
