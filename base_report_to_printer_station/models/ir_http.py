# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.http import request

COOKIE_NAME = "printing_station_token"
COOKIE_MAX_AGE = 400 * 24 * 60 * 60


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @api.model
    def _get_print_station_token(self):
        token = request.httprequest.cookies.get(COOKIE_NAME)
        if not token:
            return self.env["printing.station.token"]
        return self.env["printing.station.token"].sudo()._find_by_token(token)

    @api.model
    def _set_print_station_cookie(self, token):
        request.future_response.set_cookie(
            COOKIE_NAME,
            token,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            secure=request.httprequest.scheme == "https",
            samesite="Lax",
        )

    @api.model
    def _get_print_station(self):
        if not request:
            return None
        station_token = self._get_print_station_token()
        if not station_token:
            return self.env["printing.station"]
        station_token._touch()
        self._set_print_station_cookie(request.httprequest.cookies[COOKIE_NAME])
        return station_token.station_id.with_env(self.env)

    @api.model
    def _register_print_station(self, station):
        """A supervisor links this computer to the station, in place of the
        computer the station had."""
        Token = self.env["printing.station.token"]
        (self._get_print_station_token() | station.token_ids).action_revoke()
        Token.flush_model()
        self._set_print_station_cookie(Token._create_for_station(station))

    @api.model
    def _choose_print_station(self, station):
        """A user links this computer, which has no station yet, to a station
        no other computer uses."""
        current = self._get_print_station_token()
        if current:
            raise UserError(
                _(
                    "This computer already prints at %s.",
                    current.station_id.name,
                )
            )
        station = station.sudo()
        if not station.active or station.in_use:
            raise UserError(_("%s is in use on another computer.", station.name))
        try:
            with self.env.cr.savepoint():
                token = (
                    self.env["printing.station.token"]
                    .sudo()
                    ._create_for_station(station)
                )
                self.env["printing.station.token"].flush_model()
        except IntegrityError as error:
            raise UserError(
                _("%s is in use on another computer.", station.name)
            ) from error
        self._set_print_station_cookie(token)
