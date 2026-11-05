# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Reuse an Ask the user action created by hand instead of a duplicate"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    xmlid = "base_report_to_printer_select.printing_action_select"
    if env.ref(xmlid, raise_if_not_found=False):
        return
    action = env["printing.action"].search(
        [("action_type", "=", "select")], order="id", limit=1
    )
    if action:
        env["ir.model.data"].create(
            {
                "module": "base_report_to_printer_select",
                "name": "printing_action_select",
                "model": "printing.action",
                "res_id": action.id,
                "noupdate": True,
            }
        )
