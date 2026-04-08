

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

    def action_crear_licencia_por_producto(self):
        """Crea licencias para cada producto que tenga número de serie y aún no tenga licencia registrada"""
        licencias_creadas = 0
        for line in self.order_line:
            if line.numero_serie and not self.env['licencia.contpaqi'].search([
                ('name', '=', line.numero_serie),
                ('sale_order_id', '=', self.id)
            ]):
                # Crear licencia para cada línea con número de serie
                self.env['licencia.contpaqi'].create({
                    'name': line.numero_serie,
                    'sale_order_id': self.id,
                    'partner_id': self.partner_id.id,
                    'product_id': line.product_id.id,
                    'software_type': 'contpaqi',
                    'vendedor_id': self.env.user.id,
                })
                licencias_creadas += 1
        
        if licencias_creadas > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Éxito',
                    'message': f'{licencias_creadas} licencia(s) creada(s) exitosamente',
                    'type': 'success',
                    'sticky': True,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Información',
                    'message': 'No hay productos con número de serie o ya tienen licencias registradas',
                    'type': 'info',
                    'sticky': True,
                }
            }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    numero_serie = fields.Char(
        string='Número de Serie/Licencia',
        help='Número de serie del producto (ej: ABC123XYZ)'
    )
