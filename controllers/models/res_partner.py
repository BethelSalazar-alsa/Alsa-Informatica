
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    licencia_ids = fields.One2many(
        'licencia.contpaqi', 
        'partner_id', 
        string='Licencias Contpaqi',
        # Cambiamos a store=True para permitir búsquedas y SQL
        store=True 
    )


    def _compute_licencia_ids(self):
        for partner in self:
            # Buscamos licencias donde el cliente sea el actual
            domain = [('partner_id', '=', partner.id)]
            
            # Si tiene padre, también incluimos las del padre
            if partner.parent_id:
                domain = ['|', ('partner_id', '=', partner.id), ('partner_id', '=', partner.parent_id.id)]
            
            # Si es una empresa, incluimos las de sus contactos hijos (reemplaza el dominio anterior si es empresa)
            if partner.is_company:
                domain = ['|', ('partner_id', '=', partner.id), ('partner_id', 'child_of', partner.id)]
            
            partner.licencia_ids = self.env['licencia.contpaqi'].search(domain)
    
    licencia_count = fields.Integer(compute='_compute_licencia_count', string='Número de Licencias')

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
