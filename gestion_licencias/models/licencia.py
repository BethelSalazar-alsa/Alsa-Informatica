# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LicenciaLicencia(models.Model):
    _name = 'licencia.licencia'
    _description = 'Licencia de Software'
    _order = 'expiracion_date desc, id desc'

    name = fields.Char(string='Clave/Serie de Licencia', required=True, copy=False)
    
    software_type = fields.Selection([
        ('contabilidad', 'CONTPAQi Contabilidad'),
        ('nominas', 'CONTPAQi Nóminas'),
        ('bancos', 'CONTPAQi Bancos'),
        ('comercial_premium', 'CONTPAQi Comercial Premium'),
        ('comercial_start', 'CONTPAQi Comercial Start'),
        ('comercial_pro', 'CONTPAQi Comercial Pro'),
        ('facturacion_electronica', 'CONTPAQi Facturación Electrónica'),
        ('xml_linea', 'CONTPAQi XML en Línea'),
        ('evalua_035', 'CONTPAQi Evalúa 035'),
        ('otros', 'Otros/Servicios')
    ], string='Software / Servicio', required=True)

    partner_id = fields.Many2one('res.partner', string='Cliente/Empresa', required=True, ondelete='restrict')
    
    adquisicion_date = fields.Date(string='Fecha de Adquisición', default=fields.Date.context_today)
    expiracion_date = fields.Date(string='Fecha de Expiración')
    
    status = fields.Selection([
        ('activo', 'Activo'),
        ('vencido', 'Vencido'),
        ('suspendido', 'Suspendido')
    ], string='Estado', default='activo', compute='_compute_status', store=True, readonly=False)

    equipo_ids = fields.One2many('licencia.equipo', 'licencia_id', string='Equipos Registrados')
    notes = fields.Text(string='Notas de Configuración / Servidor')

    @api.depends('expiracion_date')
    def _compute_status(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.expiracion_date and record.expiracion_date < today:
                record.status = 'vencido'
            elif record.status == 'vencido':
                record.status = 'activo'

    def name_get(self):
        result = []
        for record in self:
            software_label = dict(self._fields['software_type'].selection).get(record.software_type, '')
            name = f"{software_label} ({record.name})"
            result.append((record.id, name))
        return result
