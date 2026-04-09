from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    licencia_ids = fields.Many2many('licencia.contpaqi', string='Licencias')
    equipo_ids = fields.Many2many('licencia.linea', string='Equipos Instalados')

    @api.onchange('partner_id')
    def _onchange_partner_id_soporte(self):
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
            # mapped('linea_ids') obtiene todos los equipos de golpe
            equipos_ids = licencias.mapped('linea_ids').ids
            self.equipo_ids = [(6, 0, equipos_ids)]
        else:
            # Si se quita el cliente, limpiamos las tablas
            self.licencia_ids = [(5, 0, 0)]
            self.equipo_ids = [(5, 0, 0)]
