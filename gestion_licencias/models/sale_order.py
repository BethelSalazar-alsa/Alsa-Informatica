from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    licencia_ids = fields.Many2many('licencia.contpaqi', string='Licencias Relacionadas')

    @api.onchange('partner_id')
    def _onchange_partner_id_licencias(self):
        if self.partner_id:
            domain = ['|', ('partner_id', '=', self.partner_id.id), 
                           ('partner_id', '=', self.partner_id.parent_id.id)]
            licencias = self.env['licencia.contpaqi'].search(domain)
            self.licencia_ids = [(6, 0, licencias.ids)]

    def action_sync_licenses_to_lines(self):
        """ Sincroniza el número de serie/licencia a la descripción del producto en las líneas de venta """
        for order in self:
            for licencia in order.licencia_ids:
                if licencia.product_id:
                    # Buscar la línea que coincida con el producto
                    line = order.order_line.filtered(lambda l: l.product_id == licencia.product_id)
                    for l in line:
                        desc = l.name or ""
                        if licencia.name not in desc:
                            l.name = f"{desc}\n[Licencia/Serie: {licencia.name}]"
