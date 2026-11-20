/** @odoo-module **/
import {Component, onWillStart, useState} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {PrintStationChooseDialog} from "../choose_dialog/choose_dialog.esm";
import {registry} from "@web/core/registry";

export class PrintStationSystray extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.dialog = useService("dialog");
        this.state = useState({name: false});
        onWillStart(() => this.load());
        useBus(this.env.bus, "PRINT_STATION:CHANGED", () => this.load());
    }

    async load() {
        const result = await this.rpc("/printing/station/current", {});
        this.state.name = result.name;
    }

    openChooser() {
        if (!this.state.name) {
            this.dialog.add(PrintStationChooseDialog, {});
        }
    }
}

PrintStationSystray.template = "base_report_to_printer_station.PrintStationSystray";

registry
    .category("systray")
    .add(
        "base_report_to_printer_station.PrintStationSystray",
        {Component: PrintStationSystray},
        {sequence: 30}
    );
