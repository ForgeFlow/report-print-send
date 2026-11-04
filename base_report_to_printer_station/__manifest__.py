# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Report to printer by print station",
    "summary": "Send reports to the printer of the computer's print station",
    "version": "16.0.1.0.0",
    "category": "Generic Modules/Base",
    "author": "ForgeFlow,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/report-print-send",
    "license": "AGPL-3",
    "depends": ["base_report_to_printer"],
    "data": [
        "security/ir.model.access.csv",
        "data/printing_data.xml",
        "views/printing_station_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "base_report_to_printer_station/static/src/systray/*",
        ],
    },
    "installable": True,
    "application": False,
}
