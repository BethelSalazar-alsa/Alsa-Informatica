# -*- coding: utf-8 -*-
from odoo import models, fields

class LicenciaEquipo(models.Model):
    _name = 'licencia.equipo'
    _description = 'Equipo Vinculado a Licencia'
    _order = 'tipo asc, name asc'

    name = fields.Char(string='Nombre del Equipo / PC', required=True)
    
    tipo = fields.Selection([
        ('servidor', 'Servidor'),
        ('terminal', 'Terminal')
    ], string='Tipo de Rol', required=True, default='terminal')

    licencia_id = fields.Many2one('licencia.licencia', string='Licencia Asociada', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', related='licencia_id.partner_id', string='Cliente/Empresa', store=True, readonly=True)

    ip_address = fields.Char(string='Dirección IP / ID de Remoto', help='Dirección IP local, AnyDesk ID, TeamViewer ID, etc.')
    usuario_responsable = fields.Char(string='Usuario / Responsable')
    notes = fields.Text(string='Notas / Especificaciones')
