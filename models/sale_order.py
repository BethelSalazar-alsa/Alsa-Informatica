

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # NUEVOS CAMPOS
    licencia_ids = fields.Many2many('licencia.contpaqi', string='Licencias del Cliente')
    # Campo inverso para ver licencias creadas desde esta venta
    licencia_creada_ids = fields.One2many('licencia.contpaqi', 'sale_order_id', 
                                          string='Licencias Creadas', 
                                          readonly=True, 
                                          help='Licencias registradas desde esta venta')

    @api.onchange('partner_id')
    def _onchange_partner_id_licencias(self):
        if self.partner_id:
            # Buscamos licencias del cliente o de su empresa padre
            domain = ['|', ('partner_id', '=', self.partner_id.id), 
                           ('partner_id', '=', self.partner_id.parent_id.id)]
            licencias = self.env['licencia.contpaqi'].search(domain)
            # El comando (6, 0, [ids]) reemplaza la lista actual con los nuevos IDs
            self.licencia_ids = [(6, 0, licencias.ids)]

    def action_crear_licencia_rapida(self):
        """Abre el formulario para crear una licencia rápidamente desde la venta"""
        # Pasar contexto con la venta pre-seleccionada
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'licencia.contpaqi',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',  # Abre en una ventana emergente
            'context': {
                'default_sale_order_id': self.id,
                'default_partner_id': self.partner_id.id,
            }
        }
