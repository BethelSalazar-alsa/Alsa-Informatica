# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    licencia_ids = fields.One2many('licencia.licencia', 'partner_id', string='Licencias Contpaqi')
    licencia_count = fields.Integer(string='Cantidad de Licencias', compute='_compute_licencia_count')

    @api.depends('licencia_ids')
    def _compute_licencia_count(self):
        for partner in self:
            partner.licencia_count = len(partner.licencia_ids)

    def action_view_licencias(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("gestion_licencias.action_licencia_licencia")
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {'default_partner_id': self.id}
        return action
