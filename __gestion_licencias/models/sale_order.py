# -*- coding: utf-8 -*-
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    licencia_id = fields.Many2one(
        'licencia.licencia',
        string='Licencia Contpaqi',
        domain="[('partner_id', '=', partner_id)]",
        help='Seleccione la licencia del cliente Contpaqi relacionada a este pedido.'
    )

    partner_licencia_ids = fields.One2many(
        related='partner_id.licencia_ids',
        string='Licencias del Cliente',
        readonly=True
    )

