# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _get_print_station(self):
        station = self.env["ir.http"]._get_print_station()
        if station is None:
            station = (
                self.env["printing.station"]
                .browse(self.env.context.get("printing_station_id"))
                .exists()
            )
        return station

    def behaviour(self):
        result = super().behaviour()
        if result.get("action") != "station_default":
            return result
        result.pop("printer_exception", None)
        station = self._get_print_station()
        if station:
            result.update(action="server", printer=station.printer_id, tray=False)
        else:
            result.update(
                action="client",
                printer=self.env["printing.printer"],
                station_missing=True,
            )
        return result

    @api.model
    def _check_print_station(self, behaviour):
        if behaviour.get("station_missing"):
            raise UserError(
                _(
                    "This computer is not registered as a print station. "
                    "Ask a supervisor to register it."
                )
            )

    @api.model
    def print_action_for_report_name(self, report_name):
        report = self._get_report_from_name(report_name)
        if report:
            self._check_print_station(report.behaviour())
        return super().print_action_for_report_name(report_name)

    def print_document_client_action(self, record_ids, data=None):
        station = self._get_print_station() or self.env["printing.station"]
        return super(
            IrActionsReport, self.with_context(printing_station_id=station.id)
        ).print_document_client_action(record_ids, data=data)

    def print_document(self, record_ids, data=None):
        self._check_print_station(self.behaviour())
        return super().print_document(record_ids, data=data)
