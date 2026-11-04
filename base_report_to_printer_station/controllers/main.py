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
        return {"name": station.name if station else False}
