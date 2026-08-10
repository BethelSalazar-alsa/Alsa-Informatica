from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta Relacionada', 
                                      tracking=True, help='Para pre-cargar información de la venta')
    
    licencia_id = fields.Many2one('licencia.contpaqi', string='Licencia', tracking=True)
    
    # Campo relacionado para obtener automáticamente y en tiempo real todos los equipos de la licencia
    equipo_ids = fields.One2many('licencia.linea', related='licencia_id.linea_ids', 
                                  string='Equipos Instalados', readonly=True)

    # NUEVO: Vistas del Cliente Completo
    partner_licencia_ids = fields.One2many('licencia.contpaqi', related='partner_id.licencia_ids',
                                            string='Licencias del Cliente', readonly=True)

    partner_equipo_ids = fields.Many2many('licencia.linea', compute='_compute_partner_equipo_ids',
                                           string='Equipos del Cliente')

    # NUEVO: Selector de equipo específico y dominio dinámico
    equipo_id = fields.Many2one('licencia.linea', string='Equipo Específico', tracking=True)
    allowed_equipo_ids = fields.Many2many('licencia.linea', compute='_compute_allowed_equipo_ids')

    @api.depends('partner_id', 'partner_id.licencia_ids', 'partner_id.licencia_ids.linea_ids')
    def _compute_partner_equipo_ids(self):
        for ticket in self:
            if ticket.partner_id:
                ticket.partner_equipo_ids = ticket.partner_id.licencia_ids.mapped('linea_ids')
            else:
                ticket.partner_equipo_ids = self.env['licencia.linea']

    @api.depends('partner_id', 'licencia_id')
    def _compute_allowed_equipo_ids(self):
        for ticket in self:
            if ticket.licencia_id:
                ticket.allowed_equipo_ids = ticket.licencia_id.linea_ids
            elif ticket.partner_id:
                ticket.allowed_equipo_ids = ticket.partner_id.licencia_ids.mapped('linea_ids')
            else:
                ticket.allowed_equipo_ids = self.env['licencia.linea']

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
            if self.equipo_id and self.equipo_id.licencia_id.partner_id != self.partner_id:
                self.equipo_id = False
        else:
            self.licencia_id = False
            self.equipo_id = False

    @api.onchange('licencia_id')
    def _onchange_licencia_id(self):
        """Si cambia la licencia y el equipo específico no corresponde, lo limpia"""
        if self.licencia_id and self.equipo_id and self.equipo_id.licencia_id != self.licencia_id:
            self.equipo_id = False
