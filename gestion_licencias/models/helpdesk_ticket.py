from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta Relacionada', 
                                      tracking=True, help='Para pre-cargar información de la venta')
    
    licencia_id = fields.Many2one('licencia.contpaqi', string='Licencia', tracking=True)
    equipo_id = fields.Many2one('licencia.linea', string='Equipo/Terminal', tracking=True)

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        """Al seleccionar una venta, pre-carga el cliente"""
        if self.sale_order_id:
            self.partner_id = self.sale_order_id.partner_id

    @api.onchange('partner_id')
    def _onchange_partner_id_licencia(self):
        """Limpia los campos si cambia el cliente y no coinciden"""
        if self.partner_id:
            if self.licencia_id and self.licencia_id.partner_id != self.partner_id:
                self.licencia_id = False
                self.equipo_id = False
        else:
            self.licencia_id = False
            self.equipo_id = False

    @api.onchange('licencia_id')
    def _onchange_licencia_id_equipo(self):
        """Limpia el equipo si cambia la licencia y no coincide"""
        if self.licencia_id:
            if self.equipo_id and self.equipo_id.licencia_id != self.licencia_id:
                self.equipo_id = False
        else:
            self.equipo_id = False
