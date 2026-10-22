from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AlsaLicense(models.Model):
    _name = "alsa.license"
    _description = "Licencia de cliente"
    _order = "expiration_date desc, name"

    name = fields.Char(string="Licencia / Código", required=True, index=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente",
        required=True,
        index=True,
        ondelete="restrict",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Producto / Servicio",
        required=True,
        index=True,
        ondelete="restrict",
    )
    start_date = fields.Date(
        string="Fecha de inicio",
        required=True,
        default=fields.Date.context_today,
    )
    expiration_date = fields.Date(
        string="Fecha de vencimiento",
        required=True,
        index=True,
    )
    state = fields.Selection(
        selection=[("active", "Activa"), ("expired", "Expirada")],
        string="Estado",
        compute="_compute_state",
        search="_search_state",
    )
    allowed_access_count = fields.Integer(
        string="Accesos / Usuarios permitidos",
        required=True,
        default=1,
    )
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Último pedido de venta",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Última línea de venta",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    equipment_ids = fields.One2many(
        comodel_name="alsa.equipment",
        inverse_name="license_id",
        string="Equipos",
    )

    @api.depends("expiration_date")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for license_record in self:
            license_record.state = (
                "active"
                if license_record.expiration_date
                and license_record.expiration_date >= today
                else "expired"
            )

    @api.model
    def _search_state(self, operator, value):
        today = fields.Date.context_today(self)
        active_domain = [("expiration_date", ">=", today)]
        expired_domain = [("expiration_date", "<", today)]

        if operator in ("=", "=="):
            if value == "active":
                return active_domain
            if value == "expired":
                return expired_domain
        elif operator == "!=":
            if value == "active":
                return expired_domain
            if value == "expired":
                return active_domain
        elif operator in ("in", "not in"):
            values = set(value or [])
            if operator == "not in":
                values = {"active", "expired"} - values
            if values == {"active", "expired"}:
                return []
            if values == {"active"}:
                return active_domain
            if values == {"expired"}:
                return expired_domain
            if not values:
                return [("id", "=", 0)]
        return NotImplemented

    @api.constrains("start_date", "expiration_date")
    def _check_dates(self):
        for license_record in self:
            if (
                license_record.start_date
                and license_record.expiration_date
                and license_record.expiration_date < license_record.start_date
            ):
                raise ValidationError(
                    "La fecha de vencimiento no puede ser anterior a la fecha de inicio."
                )

    @api.constrains("allowed_access_count")
    def _check_allowed_access_count(self):
        for license_record in self:
            if license_record.allowed_access_count < 1:
                raise ValidationError(
                    "La cantidad de accesos o usuarios permitidos debe ser mayor que cero."
                )
