# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from datetime import timedelta
from unittest import mock

from psycopg2 import IntegrityError

from odoo import fields
from odoo.tests import HttpCase, new_test_user, tagged
from odoo.tools import mute_logger

from odoo.addons.base_report_to_printer.models.ir_actions_report import (
    IrActionsReport as BaseIrActionsReport,
)

from ..models.ir_http import COOKIE_MAX_AGE, COOKIE_NAME


@tagged("post_install", "-at_install")
class TestPrintingStation(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Printer = cls.env["printing.printer"]
        cls.Station = cls.env["printing.station"]
        cls.server = cls.env["printing.server"].create({})
        cls.printer = cls._create_printer("Staging 1")
        cls.other_printer = cls._create_printer("Office")
        cls.station = cls.Station.create(
            {"name": "Single 1", "printer_id": cls.printer.id}
        )
        cls.station_action = cls.env.ref(
            "base_report_to_printer_station.printing_action_station"
        )
        cls.env["ir.ui.view"].create(
            {
                "name": "Station test",
                "type": "qweb",
                "key": "base_report_to_printer_station.test_text",
                "arch": '<t t-name="base_report_to_printer_station.test_text">'
                "Test</t>",
            }
        )
        cls.report = cls.env["ir.actions.report"].create(
            {
                "name": "Station Test",
                "model": "res.partner",
                "report_name": "base_report_to_printer_station.test_text",
                "report_type": "qweb-text",
                "property_printing_action_id": cls.station_action.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Order 1"})
        cls.picker = new_test_user(
            cls.env, login="picker", password="picker", groups="base.group_user"
        )
        cls.env.user.printing_printer_id = cls.other_printer
        cls._grant_report_read_as_mail_does()

    @classmethod
    def _grant_report_read_as_mail_does(cls):
        cls.env["ir.model.access"].create(
            {
                "name": "ir.actions.report user read",
                "model_id": cls.env.ref("base.model_ir_actions_report").id,
                "group_id": cls.env.ref("base.group_user").id,
                "perm_read": True,
            }
        )

    @classmethod
    def _create_printer(cls, name, **kwargs):
        vals = {
            "name": name,
            "system_name": name.replace(" ", "_"),
            "server_id": cls.server.id,
        }
        vals.update(kwargs)
        return cls.Printer.create(vals)

    def _register_computer(self):
        self.authenticate("admin", "admin")
        response = self.url_open(
            "/printing/station/%s/register" % self.station.id, allow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        return response.cookies[COOKIE_NAME]

    def _login_picker(self, token=None):
        self.authenticate("picker", "picker")
        if token:
            self.opener.cookies.set(COOKIE_NAME, token)

    def _call(self, method, args):
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "ir.actions.report",
                "method": method,
                "args": args,
                "kwargs": {},
            },
        }
        return self.url_open(
            "/web/dataset/call_kw",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

    def _current_station(self):
        return self.url_open(
            "/printing/station/current",
            data=json.dumps({"jsonrpc": "2.0", "method": "call", "params": {}}),
            headers={"Content-Type": "application/json"},
        ).json()["result"]["name"]

    def _assert_not_registered(self, response):
        error = response.json()["error"]["data"]
        self.assertEqual(error["name"], "odoo.exceptions.UserError")
        self.assertIn("not registered", error["message"])

    def _mock_printer(self):
        return mock.patch.object(
            type(self.Printer), "print_document", autospec=True, return_value=True
        )

    def test_registered_computer_prints_on_station_printer(self):
        token = self._register_computer()
        registration = self.station.token_ids
        self.assertEqual(len(registration), 1)
        self.assertEqual(registration.registered_by_id.login, "admin")
        self.assertNotEqual(registration.token_hash, token)
        registration.last_seen = fields.Datetime.now() - timedelta(days=2)
        self._login_picker(token)
        self.assertEqual(self._current_station(), "Single 1")
        self.assertGreater(
            registration.last_seen, fields.Datetime.now() - timedelta(minutes=5)
        )
        action = self._call(
            "print_action_for_report_name", [self.report.report_name]
        ).json()["result"]
        self.assertEqual(action["action"], "server")
        self.assertEqual(action["printer_name"], "Staging 1")
        with self._mock_printer() as print_document:
            response = self._call(
                "print_document_client_action", [[self.report.id], self.partner.ids]
            )
        print_document.assert_called_once()
        self.assertEqual(print_document.call_args.args[0], self.printer)
        renewed_cookie = response.headers["Set-Cookie"]
        self.assertIn("%s=%s" % (COOKIE_NAME, token), renewed_cookie)
        self.assertIn("Max-Age=%s" % COOKIE_MAX_AGE, renewed_cookie)
        self.assertIn("HttpOnly", renewed_cookie)
        self.assertIn("SameSite=Lax", renewed_cookie)
        with mock.patch.object(
            BaseIrActionsReport,
            "print_document_client_action",
            autospec=True,
            return_value=True,
        ) as threaded_print:
            self._call(
                "print_document_client_action", [[self.report.id], self.partner.ids]
            )
        self.assertEqual(
            threaded_print.call_args.args[0].env.context["printing_station_id"],
            self.station.id,
        )

    def test_unregistered_revoked_or_archived_computer_cannot_print(self):
        self._login_picker()
        self.assertFalse(self._current_station())
        with self._mock_printer() as print_document:
            self._assert_not_registered(
                self._call("print_action_for_report_name", [self.report.report_name])
            )
            self._assert_not_registered(
                self._call("print_document", [[self.report.id], self.partner.ids])
            )
            token = self._register_computer()
            self.station.token_ids.action_revoke()
            self._login_picker(token)
            self._assert_not_registered(
                self._call("print_document", [[self.report.id], self.partner.ids])
            )
            token = self._register_computer()
            self.station.active = False
            self._login_picker(token)
            self._assert_not_registered(
                self._call("print_document", [[self.report.id], self.partner.ids])
            )
        print_document.assert_not_called()

    def test_moving_a_computer_revokes_the_old_registration(self):
        self._register_computer()
        old_registration = self.station.token_ids
        new_station = self.Station.create(
            {"name": "Bulk 1", "printer_id": self.other_printer.id}
        )
        response = self.url_open(
            "/printing/station/%s/register" % new_station.id, allow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.assertFalse(old_registration.active)
        self.assertEqual(self._current_station(), "Bulk 1")

    def test_job_prints_with_station_in_context(self):
        self.report.property_printing_action_id = False
        self.env.user.printing_action = "station_default"
        report = self.report.with_context(printing_station_id=self.station.id)
        with self._mock_printer() as print_document:
            report.print_document(self.partner.ids)
            print_document.assert_called_once()
            self.assertEqual(print_document.call_args.args[0], self.printer)
            with self.assertRaisesRegex(Exception, "not registered"):
                self.report.print_document(self.partner.ids)
            content, _format = self.report._render_qweb_text(
                self.report.report_name, self.partner.ids
            )
        self.assertIn(b"Test", content)
        print_document.assert_called_once()

    def test_picker_cannot_register_a_computer(self):
        self._login_picker()
        response = self.url_open(
            "/printing/station/%s/register" % self.station.id, allow_redirects=False
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.station.token_ids)

    @mute_logger("odoo.sql_db")
    def test_printer_belongs_to_one_station(self):
        with self.assertRaises(IntegrityError):
            self.Station.create({"name": "Single 2", "printer_id": self.printer.id})
