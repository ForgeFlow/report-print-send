# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import Forbidden, NotFound

from odoo import http
from odoo.http import request


class PrintingStationController(http.Controller):
    @http.route(
        "/printing/station/<int:station_id>/register",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def register_computer(self, station_id, **kwargs):
        if not request.env.user.has_group(
            "base_report_to_printer.printing_group_manager"
        ):
            raise Forbidden()
        station = request.env["printing.station"].browse(station_id).exists()
        if not station:
            raise NotFound()
        request.env["ir.http"]._register_print_station(station)
        return request.redirect(
            "/web#id=%s&model=printing.station&view_type=form" % station.id
        )

    @http.route("/printing/station/current", type="json", auth="user")
    def current_station(self):
        station = request.env["ir.http"]._get_print_station()
        return {"name": station.sudo().name if station else False}

    @http.route("/printing/station/list", type="json", auth="user")
    def list_stations(self):
        current = request.env["ir.http"]._get_print_station()
        return [
            {
                "id": station.id,
                "name": station.name,
                "printer": station.printer_id.name,
                "current": station == current,
                "in_use": station.in_use and station != current,
            }
            for station in request.env["printing.station"].sudo().search([])
        ]

    @http.route("/printing/station/choose", type="json", auth="user")
    def choose_station(self, station_id):
        station = request.env["printing.station"].sudo().browse(int(station_id))
        if not station.exists():
            raise NotFound()
        request.env["ir.http"]._choose_print_station(station)
        return {"name": station.name}
