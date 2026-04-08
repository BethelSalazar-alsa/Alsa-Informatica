from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # NUEVO: Relación con la venta para pre-cargar datos
    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta Relacionada', 
                                      tracking=True, 
                                      ondelete='set null',
                                      help='Selecciona la orden de venta asociada. Se filtra automáticamente por cliente.')
    
    licencia_ids = fields.Many2many('licencia.contpaqi', string='Licencias')
    equipo_ids = fields.Many2many('licencia.linea', string='Equipos Instalados')

    @api.onchange('partner_id')
    def _onchange_partner_id_soporte(self):
        """Auto-carga licencias y equipos cuando cambia el cliente"""
        if self.partner_id:
            # CORRECCIÓN: Llamamos a los modelos por separado
            licencia_model = self.env['licencia.contpaqi']
            
            # Buscamos las licencias del cliente o de su grupo comercial
            licencias = licencia_model.search([
                ('partner_id', 'child_of', self.partner_id.commercial_partner_id.id)
            ])
            
            # Asignamos las licencias encontradas
            self.licencia_ids = [(6, 0, licencias.ids)]
            
            # Extraemos los equipos (líneas) vinculados a esas licencias
            equipos_ids = licencias.mapped('linea_ids').ids
            self.equipo_ids = [(6, 0, equipos_ids)]
            
            # Limpiar sale_order_id si cambia de cliente
            self.sale_order_id = False
        else:
            # Si se quita el cliente, limpiamos las tablas
            self.licencia_ids = [(5, 0, 0)]
            self.equipo_ids = [(5, 0, 0)]
            self.sale_order_id = False

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        """Cuando se selecciona una venta, pre-carga el cliente (si no está asignado) y sus licencias/equipos"""
        if self.sale_order_id:
            # Pre-cargar cliente de la venta (solo si no tiene cliente asignado)
            if not self.partner_id:
                self.partner_id = self.sale_order_id.partner_id
            
            # Pre-cargar licencias de la venta (incluyendo creadas desde esta venta)
            licencias_venta = self.sale_order_id.licencia_creada_ids  # Licencias creadas desde esta venta
            if licencias_venta:
                self.licencia_ids = [(6, 0, licencias_venta.ids)]
            else:
                # Si no hay licencias creadas, mostrar todas del cliente
                licencias = self.env['licencia.contpaqi'].search([
                    ('partner_id', 'child_of', self.sale_order_id.partner_id.commercial_partner_id.id)
                ])
                self.licencia_ids = [(6, 0, licencias.ids)]
            
            # Pre-cargar equipos relacionados
            equipos_ids = self.licencia_ids.mapped('id')
            if equipos_ids:
                equipos = self.env['licencia.linea'].search([('licencia_id', 'in', equipos_ids)])
                self.equipo_ids = [(6, 0, equipos.ids)]
