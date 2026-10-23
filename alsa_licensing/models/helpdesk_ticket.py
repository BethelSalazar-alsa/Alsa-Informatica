from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    alsa_active_license_ids = fields.Many2many(
        comodel_name="alsa.license",
        string="Licencias vigentes",
        compute="_compute_alsa_active_licenses",
    )
    alsa_customer_equipment_ids = fields.One2many(
        related="partner_id.alsa_equipment_ids",
        string="Equipos del cliente",
        readonly=False,
    )
    alsa_equipment_ids = fields.Many2many(
        comodel_name="alsa.equipment",
        relation="alsa_helpdesk_ticket_equipment_rel",
        column1="ticket_id",
        column2="equipment_id",
        string="Equipos atendidos",
        copy=False,
    )

    @api.depends("partner_id")
    def _compute_alsa_active_licenses(self):
        today = fields.Date.context_today(self)
        License = self.env["alsa.license"]
        for ticket in self:
            licenses = License
            if ticket.partner_id:
                licenses = License.search(
                    [
                        ("partner_id", "=", ticket.partner_id.id),
                        ("expiration_date", ">=", today),
                    ]
                )
            ticket.alsa_active_license_ids = licenses

    @api.onchange("partner_id")
    def _onchange_alsa_partner_id(self):
        if self.partner_id:
            self.alsa_equipment_ids = self.alsa_equipment_ids.filtered(
                lambda equipment: equipment.partner_id == self.partner_id
            )
        else:
            self.alsa_equipment_ids = False

    @api.constrains("partner_id", "alsa_equipment_ids")
    def _check_alsa_equipment_partner(self):
        for ticket in self:
            invalid_equipment = ticket.alsa_equipment_ids.filtered(
                lambda equipment: equipment.partner_id != ticket.partner_id
            )
            if invalid_equipment:
                raise ValidationError(
                    "Todos los equipos seleccionados deben pertenecer al cliente del ticket."
                )
