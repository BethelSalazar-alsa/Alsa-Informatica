import html
import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AlsaEquipment(models.Model):
    _name = "alsa.equipment"
    _description = "Equipo de cliente"
    _order = "partner_id, name"

    name = fields.Char(string="Nombre del equipo", required=True, index=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente",
        required=True,
        index=True,
        ondelete="restrict",
    )
    equipment_type = fields.Selection(
        selection=[("terminal", "Terminal"), ("server", "Servidor")],
        string="Tipo de equipo",
        required=True,
        default="terminal",
        index=True,
    )
    specifications = fields.Html(
        string="Características / Especificaciones técnicas",
        sanitize=True,
    )
    specifications_summary = fields.Char(
        string="Resumen de características",
        compute="_compute_specifications_summary",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Producto / Servicio relacionado",
        ondelete="restrict",
    )
    license_id = fields.Many2one(
        comodel_name="alsa.license",
        string="Licencia asociada",
        ondelete="set null",
    )

    @api.depends("specifications")
    def _compute_specifications_summary(self):
        for equipment in self:
            plain_text = re.sub(r"<[^>]+>", " ", equipment.specifications or "")
            plain_text = " ".join(html.unescape(plain_text).split())
            equipment.specifications_summary = (
                plain_text[:97] + "..." if len(plain_text) > 100 else plain_text
            )

    @api.model_create_multi
    def create(self, vals_list):
        prepared_values = []
        for values in vals_list:
            values = dict(values)
            license_id = values.get("license_id")
            if license_id and not values.get("partner_id"):
                license_record = self.env["alsa.license"].browse(license_id).exists()
                if license_record:
                    values["partner_id"] = license_record.partner_id.id
            prepared_values.append(values)
        return super().create(prepared_values)

    def write(self, values):
        values = dict(values)
        license_id = values.get("license_id")
        if license_id and "partner_id" not in values:
            license_record = self.env["alsa.license"].browse(license_id).exists()
            if license_record:
                values["partner_id"] = license_record.partner_id.id
        return super().write(values)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.license_id and self.license_id.partner_id != self.partner_id:
            self.license_id = False
        return {
            "domain": {
                "license_id": [("partner_id", "=", self.partner_id.id)]
                if self.partner_id
                else []
            }
        }

    @api.onchange("license_id")
    def _onchange_license_id(self):
        if self.license_id:
            self.partner_id = self.license_id.partner_id
            if not self.product_id:
                self.product_id = self.license_id.product_id

    @api.constrains("partner_id", "license_id")
    def _check_license_partner(self):
        for equipment in self:
            if (
                equipment.license_id
                and equipment.partner_id != equipment.license_id.partner_id
            ):
                raise ValidationError(
                    "La licencia asociada debe pertenecer al mismo cliente que el equipo."
                )
