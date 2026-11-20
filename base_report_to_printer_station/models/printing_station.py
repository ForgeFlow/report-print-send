# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PrintingStation(models.Model):
    _name = "printing.station"
    _description = "Print Station"
    _order = "name, id"

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
    in_use = fields.Boolean(
        compute="_compute_in_use",
        help="A computer is linked to this station.",
    )

    _sql_constraints = [
        (
            "printer_id_uniq",
            "UNIQUE(printer_id)",
            "A printer can belong to one print station only.",
        )
    ]

    def _compute_in_use(self):
        for station in self:
            station.in_use = bool(station.sudo().token_ids)

    def action_register_computer(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/printing/station/%s/register" % self.id,
            "target": "self",
        }

    @api.model
    def _action_choose(self, records, method):
        """Ask the user for the station of this computer, then call `method`
        of `records` again from the browser."""
        return {
            "type": "ir.actions.client",
            "tag": "printing_station_choose",
            "params": {
                "res_model": records._name,
                "res_ids": records.ids,
                "method": method,
            },
        }
