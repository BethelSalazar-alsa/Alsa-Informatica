import base64
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class CotizacionExpress(models.Model):
    _name = 'cotizacion.express'
    _description = 'Cotización Express'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Cotización', required=True, default=lambda self: self.env['ir.sequence'].next_by_code('cotizacion.express') or 'Nueva')
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True, tracking=True)
    partner_name = fields.Char(related='partner_id.name', string='Nombre del Cliente')
    partner_email = fields.Char(related='partner_id.email', string='Email')
    partner_phone = fields.Char(related='partner_id.phone', string='Teléfono')
    partner_address = fields.Char(related='partner_id.contact_address', string='Dirección')

    date = fields.Date(string='Fecha', default=fields.Date.today, required=True)
    city = fields.Char(string='Ciudad', default='Colima')
    state_location = fields.Char(string='Estado', default='Col.')

    user_id = fields.Many2one('res.users', string='Vendedor', default=lambda self: self.env.user, required=True)
    signature_id = fields.Many2one('seller.signature', string='Firma del Vendedor',
                                   domain="[('user_id', '=', user_id)]")

    option_ids = fields.One2many('cotizacion.express.option', 'cotizacion_id', string='Opciones')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviado al Cliente'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', tracking=True)

    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Moneda')
    crm_lead_id = fields.Many2one('crm.lead', string='Oportunidad CRM')
    notes = fields.Html(string='Notas / Términos')
    pdf_preview = fields.Binary(string='Vista Previa PDF', attachment=False)
    amount_total = fields.Monetary(string='Total', compute='_compute_amount_total', store=True)

    @api.depends('option_ids.total', 'option_ids.selected')
    def _compute_amount_total(self):
        for rec in self:
            selected_options = rec.option_ids.filtered('selected')
            if selected_options:
                rec.amount_total = sum(selected_options.mapped('total'))
            elif rec.option_ids:
                rec.amount_total = rec.option_ids[0].total
            else:
                rec.amount_total = 0.0

    def _generate_pdf_preview(self):
        """Método interno para renderizar el PDF y guardarlo en el campo binario"""
        for record in self:
            try:
                report_id = self.env.ref('cotizaciones_express.report_cotizacion_express')
                pdf_content, dummy = self.env['ir.actions.report']._render_qweb_pdf(report_id, res_ids=record.ids)
                # Usamos super().write() para evitar recursión infinita y guardar de forma silenciosa
                super(CotizacionExpress, record).write({'pdf_preview': pdf_content})
            except Exception as e:
                _logger.error("Error generating PDF preview: %s", e)

    @api.model_create_multi
    def create(self, vals_list):
        """Se ejecuta la primera vez que el usuario hace clic en Guardar"""
        records = super(CotizacionExpress, self).create(vals_list)
        records._generate_pdf_preview()
        return records

    def write(self, vals):
        """Se ejecuta cada vez que el usuario guarda cambios"""
        res = super(CotizacionExpress, self).write(vals)
        # Evitamos bucle infinito: solo regeneramos si el cambio NO viene del propio PDF
        if 'pdf_preview' not in vals:
            self._generate_pdf_preview()
        return res

    def action_send_to_client(self):
        self.ensure_one()
        self.state = 'sent'
        template = self.env.ref('cotizaciones_express.email_template_cotizacion', raise_if_not_found=False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = {
            'default_model': 'cotizacion.express',
            'default_res_ids': self.ids,
            'default_template_id': template.id if template else False,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'name': _('Enviar Correo Electrónico'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def action_confirm(self):
        self.state = 'confirmed'

    def action_confirm_sale_order(self):
        self.ensure_one()
        selected = self.option_ids.filtered('selected')
        if not selected:
            raise UserError(_('Debe seleccionar al menos una opción como "Seleccionada por el Cliente"'))
        if not self.crm_lead_id:
            lead = self.env['crm.lead'].create({
                'name': self.name,
                'partner_id': self.partner_id.id,
                'expected_revenue': sum(self.option_ids.mapped('total')),
                'description': self.notes or '',
                'user_id': self.user_id.id,
                'team_id': self.env['crm.team'].search([], limit=1).id if self.env['crm.team'].search_count([]) else False,
            })
            self.crm_lead_id = lead.id
        for option in selected:
            vals = {
                'partner_id': self.partner_id.id,
                'origin': self.name,
                'user_id': self.user_id.id,
                'team_id': self.crm_lead_id.team_id.id if self.crm_lead_id else False,
                'campaign_id': self.crm_lead_id.campaign_id.id if self.crm_lead_id else False,
                'medium_id': self.crm_lead_id.medium_id.id if self.crm_lead_id else False,
                'note': option.description or '',
                'order_line': [],
            }
            order = self.env['sale.order'].create(vals)
            for line in option.line_ids:
                product = self.env['product.product'].search([('name', '=', line.name)], limit=1)
                if not product:
                    product = self.env['product.product'].search([('name', '=', 'Concepto Cotización')], limit=1)
                if not product:
                    product = self.env['product.product'].create({
                        'name': 'Concepto Cotización',
                        'type': 'service',
                        'sale_ok': True,
                        'purchase_ok': False,
                    })
                order_line_vals = {
                    'order_id': order.id,
                    'product_id': product.id,
                    'name': line.name + ('\n' + line.description if line.description else ''),
                    'product_uom_qty': line.quantity,
                    'price_unit': line.price_unit,
                    'tax_ids': [(6, 0, self.env['account.tax'].search([
                        ('amount', '=', line.iva_percent),
                        ('type_tax_use', '=', 'sale'),
                    ], limit=1).ids)] if line.iva_percent else False,
                }
                self.env['sale.order.line'].create(order_line_vals)
            if self.crm_lead_id:
                self.crm_lead_id.write({'sale_order_id': order.id})
        self.state = 'confirmed'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('origin', '=', self.name)],
            'name': _('Órdenes de Venta'),
        }

    def action_cancel(self):
        self.state = 'cancelled'

    def action_draft(self):
        self.state = 'draft'


class CotizacionExpressOption(models.Model):
    _name = 'cotizacion.express.option'
    _description = 'Opción / Paquete de Cotización'
    _rec_name = 'name'

    cotizacion_id = fields.Many2one('cotizacion.express', string='Cotización', ondelete='cascade')
    name = fields.Char(string='Nombre de la Opción', required=True, default='Opción')
    description = fields.Html(string='Descripción de la Opción')
    line_ids = fields.One2many('cotizacion.express.option.line', 'option_id', string='Productos')
    selected = fields.Boolean(string='Seleccionada por el Cliente', default=False)
    sequence = fields.Integer(string='Secuencia', default=10)

    subtotal = fields.Monetary(string='Subtotal', compute='_compute_option_totals', store=True)
    iva_total = fields.Monetary(string='IVA Total', compute='_compute_option_totals', store=True)
    total = fields.Monetary(string='Total', compute='_compute_option_totals', store=True)
    currency_id = fields.Many2one('res.currency', related='cotizacion_id.currency_id')

    @api.depends('line_ids.subtotal', 'line_ids.iva_amount')
    def _compute_option_totals(self):
        for rec in self:
            rec.subtotal = sum(rec.line_ids.mapped('subtotal'))
            rec.iva_total = sum(rec.line_ids.mapped('iva_amount'))
            rec.total = rec.subtotal + rec.iva_total


class CotizacionExpressOptionLine(models.Model):
    _name = 'cotizacion.express.option.line'
    _description = 'Producto de Opción'
    _rec_name = 'name'

    option_id = fields.Many2one('cotizacion.express.option', string='Opción', ondelete='cascade')
    name = fields.Char(string='Producto', required=True)
    description = fields.Text(string='Descripción')
    quantity = fields.Float(string='Cantidad', default=1.0, required=True)
    price_unit = fields.Monetary(string='Precio Unitario', required=True)
    currency_id = fields.Many2one('res.currency', related='option_id.currency_id')
    iva_percent = fields.Float(string='IVA %', default=16.0)
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_line_totals', store=True)
    iva_amount = fields.Monetary(string='IVA', compute='_compute_line_totals', store=True)
    total = fields.Monetary(string='Total', compute='_compute_line_totals', store=True)
    sequence = fields.Integer(string='Secuencia', default=10)

    @api.depends('price_unit', 'quantity', 'iva_percent')
    def _compute_line_totals(self):
        for rec in self:
            rec.subtotal = rec.price_unit * rec.quantity
            rec.iva_amount = rec.subtotal * (rec.iva_percent / 100.0)
            rec.total = rec.subtotal + rec.iva_amount

    def action_open_line_form(self):
        self.ensure_one()
        return {
            'name': _('Editar Producto'),
            'type': 'ir.actions.act_window',
            'res_model': 'cotizacion.express.option.line',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
