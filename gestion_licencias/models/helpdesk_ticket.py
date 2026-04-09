from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    licencia_ids = fields.Many2many('licencia.contpaqi', string='Licencias')
    equipo_ids = fields.Many2many('licencia.linea', string='Equipos Instalados')

    @api.onchange('partner_id', 'product_id')
    def _onchange_partner_and_product_soporte(self):
        if self.partner_id:
            domain = [('partner_id', 'child_of', self.partner_id.commercial_partner_id.id)]
            if self.product_id:
                domain.append(('product_id', '=', self.product_id.id))
            
            licencias = self.env['licencia.contpaqi'].search(domain)
            self.licencia_ids = [(6, 0, licencias.ids)]
            
            equipos_ids = licencias.mapped('linea_ids').ids
            self.equipo_ids = [(6, 0, equipos_ids)]
        else:
            self.licencia_ids = [(5, 0, 0)]
            self.equipo_ids = [(5, 0, 0)]
