
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    licencia_ids = fields.One2many(
        'licencia.contpaqi', 
        'partner_id', 
        string='Licencias Contpaqi'
    )
    
    licencia_count = fields.Integer(compute='_compute_licencia_count', string='Número de Licencias')

    @api.depends('licencia_ids')
    def _compute_licencia_count(self):
        for partner in self:
            partner.licencia_count = len(partner.licencia_ids)

    def action_view_licencias(self):
        # Esta función define qué pasa al hacer clic en el botón
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Licencias Contpaqi',
            'view_mode': 'list,form',
            'res_model': 'licencia.contpaqi',
            'domain': [('id', 'in', self.licencia_ids.ids)],
            'context': {'default_partner_id': self.id},
        }
