from odoo import models, fields

class SellerSignature(models.Model):
    _name = 'seller.signature'
    _description = 'Firma del Vendedor'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users', string='Vendedor', required=True, default=lambda self: self.env.user)
    signature_image = fields.Binary(string='Firma', required=True, attachment=True)
    signature_name = fields.Char(string='Nombre en Firma', required=True, default=lambda self: self.env.user.name)
    active = fields.Boolean(string='Activo', default=True)
