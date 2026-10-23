import math

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    alsa_is_licensable = fields.Boolean(
        string="Genera licencia ALSA",
        help="Al confirmar una venta, las líneas de este producto crean o renuevan una licencia.",
    )
    alsa_license_duration_months = fields.Integer(
        string="Duración de licencia (meses)",
        default=12,
    )
    alsa_accesses_per_unit = fields.Integer(
        string="Accesos por unidad vendida",
        default=1,
    )

    @api.constrains("alsa_license_duration_months", "alsa_accesses_per_unit")
    def _check_alsa_license_configuration(self):
        for product in self.filtered("alsa_is_licensable"):
            if product.alsa_license_duration_months < 1:
                raise ValidationError(
                    "La duración de una licencia debe ser de al menos un mes."
                )
            if product.alsa_accesses_per_unit < 1:
                raise ValidationError(
                    "Los accesos por unidad vendida deben ser mayores que cero."
                )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    alsa_active_license_ids = fields.Many2many(
        comodel_name="alsa.license",
        string="Licencias vigentes",
        compute="_compute_alsa_customer_assets",
    )
    alsa_active_license_count = fields.Integer(
        string="Licencias vigentes",
        compute="_compute_alsa_customer_assets",
    )
    alsa_customer_equipment_ids = fields.One2many(
        related="partner_id.alsa_equipment_ids",
        string="Equipos del cliente",
        readonly=False,
    )
    alsa_equipment_ids = fields.Many2many(
        comodel_name="alsa.equipment",
        relation="alsa_sale_order_equipment_rel",
        column1="order_id",
        column2="equipment_id",
        string="Equipos utilizados en la venta",
        copy=False,
    )

    @api.depends("partner_id")
    def _compute_alsa_customer_assets(self):
        today = fields.Date.context_today(self)
        License = self.env["alsa.license"]
        for order in self:
            licenses = License
            if order.partner_id:
                licenses = License.search(
                    [
                        ("partner_id", "=", order.partner_id.id),
                        ("expiration_date", ">=", today),
                    ]
                )
            order.alsa_active_license_ids = licenses
            order.alsa_active_license_count = len(licenses)

    @api.onchange("partner_id")
    def _onchange_alsa_partner_equipment(self):
        if self.partner_id:
            self.alsa_equipment_ids = self.alsa_equipment_ids.filtered(
                lambda equipment: equipment.partner_id == self.partner_id
            )
        else:
            self.alsa_equipment_ids = False

    @api.constrains("partner_id", "alsa_equipment_ids")
    def _check_alsa_equipment_partner(self):
        for order in self:
            invalid_equipment = order.alsa_equipment_ids.filtered(
                lambda equipment: equipment.partner_id != order.partner_id
            )
            if invalid_equipment:
                raise ValidationError(
                    "Todos los equipos seleccionados deben pertenecer al cliente de la venta."
                )

    def action_confirm(self):
        result = super().action_confirm()
        for order in self:
            for line in order.order_line.filtered(
                lambda sale_line: not sale_line.display_type
                and sale_line.product_id
                and sale_line.alsa_is_licensable
            ):
                line._alsa_create_or_update_license(order.partner_id)
        return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    alsa_is_licensable = fields.Boolean(
        string="Genera licencia",
        related="product_id.product_tmpl_id.alsa_is_licensable",
    )
    alsa_license_id = fields.Many2one(
        comodel_name="alsa.license",
        string="Licencia a renovar",
        copy=False,
        ondelete="set null",
        help="Déjelo vacío para crear una licencia nueva al confirmar la venta.",
    )
    alsa_license_start_date = fields.Date(string="Inicio de licencia", copy=False)
    alsa_license_expiration_date = fields.Date(
        string="Vencimiento acordado",
        copy=False,
        help="Si se deja vacío, se aplicará la duración configurada en el producto.",
    )
    alsa_license_access_count = fields.Integer(
        string="Accesos contratados",
        copy=False,
    )

    @api.onchange("product_id", "product_uom_qty")
    def _onchange_alsa_license_values(self):
        for line in self:
            if line.alsa_is_licensable:
                accesses_per_unit = line.product_id.product_tmpl_id.alsa_accesses_per_unit
                line.alsa_license_access_count = max(
                    1, math.ceil(line.product_uom_qty * accesses_per_unit)
                )
                if not line.alsa_license_start_date:
                    line.alsa_license_start_date = fields.Date.context_today(line)
            else:
                line.alsa_license_id = False
                line.alsa_license_start_date = False
                line.alsa_license_expiration_date = False
                line.alsa_license_access_count = 0

    @api.onchange("alsa_license_id")
    def _onchange_alsa_license_id(self):
        for line in self:
            if line.alsa_license_id:
                line.alsa_license_start_date = fields.Date.context_today(line)
                line.alsa_license_access_count = max(
                    line.alsa_license_access_count,
                    line.alsa_license_id.allowed_access_count,
                )

    def _alsa_create_or_update_license(self, partner):
        self.ensure_one()
        today = fields.Date.context_today(self)
        product_template = self.product_id.product_tmpl_id
        license_record = self.alsa_license_id

        if license_record and license_record.partner_id != partner:
            raise ValidationError(
                "La licencia seleccionada en la línea de venta no pertenece al cliente del pedido."
            )

        start_date = self.alsa_license_start_date or today
        expiration_date = self.alsa_license_expiration_date
        if not expiration_date:
            if (
                license_record
                and license_record.sale_order_id == self.order_id
                and license_record.expiration_date
            ):
                # A second product line assigned to the same license in this
                # order must not renew the license for a second full period.
                expiration_date = license_record.expiration_date
            else:
                renewal_base = start_date
                if (
                    license_record
                    and license_record.expiration_date
                    and license_record.expiration_date >= today
                ):
                    renewal_base = license_record.expiration_date
                expiration_date = renewal_base + relativedelta(
                    months=product_template.alsa_license_duration_months
                )

        access_count = self.alsa_license_access_count or max(
            1,
            math.ceil(
                self.product_uom_qty * product_template.alsa_accesses_per_unit
            ),
        )
        values = {
            "partner_id": partner.id,
            "start_date": start_date,
            "expiration_date": expiration_date,
            "allowed_access_count": max(
                access_count,
                license_record.allowed_access_count if license_record else 0,
            ),
            "sale_order_id": self.order_id.id,
            "sale_order_line_id": self.id,
        }

        # Keep the first product as the historical/main product, while every
        # sold product is represented by its own editable license line.
        if not license_record or not license_record.product_id:
            values["product_id"] = self.product_id.id

        if license_record:
            license_record.write(values)
        else:
            values["name"] = "%s / %s" % (
                self.order_id.name,
                self.product_id.display_name,
            )
            license_record = self.env["alsa.license"].create(values)
            self.alsa_license_id = license_record

        product_line = license_record.product_line_ids.filtered(
            lambda item: item.sale_order_line_id == self
        )[:1]
        if not product_line:
            product_line = license_record.product_line_ids.filtered(
                lambda item: item.product_id == self.product_id
                and not item.sale_order_line_id
            )[:1]
        line_values = {
            "product_id": self.product_id.id,
            "quantity": self.product_uom_qty,
            "allowed_access_count": access_count,
            "sale_order_line_id": self.id,
        }
        if product_line:
            product_line.write(line_values)
        else:
            line_values["license_id"] = license_record.id
            self.env["alsa.license.line"].create(line_values)
        return license_record
