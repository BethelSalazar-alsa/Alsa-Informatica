from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    licencia_creada_ids = fields.One2many('licencia.contpaqi', 'sale_order_id', 
                                          string='Licencias Creadas', 
                                          readonly=True, 
                                          help='Licencias registradas desde esta venta')
    
    licencia_count = fields.Integer(compute='_compute_licencia_count', string='Número de Licencias Creadas')

    @api.depends('licencia_creada_ids')
    def _compute_licencia_count(self):
        for order in self:
            order.licencia_count = len(order.licencia_creada_ids)

    def action_view_licencias_creadas(self):
        """Abre la lista de licencias creadas desde esta venta"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Licencias Creadas',
            'view_mode': 'list,form',
            'res_model': 'licencia.contpaqi',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {
                'default_sale_order_id': self.id,
                'default_partner_id': self.partner_id.id,
            },
        }

    def action_crear_licencia_rapida(self):
        """Abre el formulario para crear una licencia rápidamente desde la venta"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'licencia.contpaqi',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_partner_id': self.partner_id.id,
            }
        }
