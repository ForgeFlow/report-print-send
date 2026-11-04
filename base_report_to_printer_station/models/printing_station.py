# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PrintingStation(models.Model):
    _name = "printing.station"
    _description = "Print Station"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    printer_id = fields.Many2one(
        comodel_name="printing.printer", required=True, ondelete="restrict"
    )
    token_ids = fields.One2many(
        comodel_name="printing.station.token",
        inverse_name="station_id",
        string="Registered Computers",
    )

    _sql_constraints = [
        (
            "printer_id_uniq",
            "UNIQUE(printer_id)",
            "A printer can belong to one print station only.",
        )
    ]

    def action_register_computer(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/printing/station/%s/register" % self.id,
            "target": "self",
        }
