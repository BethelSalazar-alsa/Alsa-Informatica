

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    licencia_ids = fields.Many2many('licencia.contpaqi', string='Licencias del Cliente')

    @api.onchange('partner_id')
    def _onchange_partner_id_licencias(self):
        if self.partner_id:
            # Buscamos licencias del cliente o de su empresa padre
            domain = ['|', ('partner_id', '=', self.partner_id.id), 
                           ('partner_id', '=', self.partner_id.parent_id.id)]
            licencias = self.env['licencia.contpaqi'].search(domain)
            # El comando (6, 0, [ids]) reemplaza la lista actual con los nuevos IDs
            self.licencia_ids = [(6, 0, licencias.ids)]
