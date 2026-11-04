# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import secrets
from datetime import timedelta

from odoo import api, fields, models

LAST_SEEN_INTERVAL = timedelta(hours=1)


class PrintingStationToken(models.Model):
    _name = "printing.station.token"
    _description = "Print Station Registered Computer"
    _order = "last_seen desc, id desc"

    station_id = fields.Many2one(
        comodel_name="printing.station",
        required=True,
        ondelete="cascade",
        index=True,
    )
    token_hash = fields.Char(required=True, index=True, copy=False)
    registered_by_id = fields.Many2one(
        comodel_name="res.users", default=lambda self: self.env.user, readonly=True
    )
    last_seen = fields.Datetime(readonly=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("token_hash_uniq", "UNIQUE(token_hash)", "The token must be unique.")
    ]

    @api.model
    def _hash_token(self, token):
        return hashlib.sha256(token.encode()).hexdigest()

    @api.model
    def _create_for_station(self, station):
        token = secrets.token_urlsafe(32)
        self.create(
            {
                "station_id": station.id,
                "token_hash": self._hash_token(token),
                "last_seen": fields.Datetime.now(),
            }
        )
        return token

    @api.model
    def _find_by_token(self, token):
        return self.search(
            [
                ("token_hash", "=", self._hash_token(token)),
                ("station_id.active", "=", True),
            ],
            limit=1,
        )

    def _touch(self):
        now = fields.Datetime.now()
        stale = self.filtered(
            lambda token: not token.last_seen
            or now - token.last_seen > LAST_SEEN_INTERVAL
        )
        if stale:
            stale.write({"last_seen": now})

    def action_revoke(self):
        self.write({"active": False})
