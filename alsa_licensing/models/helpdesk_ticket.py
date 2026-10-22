from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    alsa_active_license_ids = fields.Many2many(
        comodel_name="alsa.license",
        string="Licencias vigentes",
        compute="_compute_alsa_customer_assets",
    )
    alsa_available_equipment_ids = fields.Many2many(
        comodel_name="alsa.equipment",
        string="Equipos del cliente",
        compute="_compute_alsa_customer_assets",
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
    def _compute_alsa_customer_assets(self):
        today = fields.Date.context_today(self)
        License = self.env["alsa.license"]
        Equipment = self.env["alsa.equipment"]
        for ticket in self:
            licenses = License
            equipment = Equipment
            if ticket.partner_id:
                licenses = License.search(
                    [
                        ("partner_id", "=", ticket.partner_id.id),
                        ("expiration_date", ">=", today),
                    ]
                )
                equipment = Equipment.search(
                    [("partner_id", "=", ticket.partner_id.id)]
                )
            ticket.alsa_active_license_ids = licenses
            ticket.alsa_available_equipment_ids = equipment

    @api.onchange("partner_id")
    def _onchange_alsa_partner_id(self):
        if self.partner_id:
            self.alsa_equipment_ids = self.alsa_equipment_ids.filtered(
                lambda equipment: equipment.partner_id == self.partner_id
            )
        else:
            self.alsa_equipment_ids = False
