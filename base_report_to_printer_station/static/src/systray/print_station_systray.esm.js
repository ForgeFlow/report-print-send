/** @odoo-module **/
import {Component, onWillStart, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class PrintStationSystray extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({name: false});
        onWillStart(async () => {
            const result = await this.rpc("/printing/station/current", {});
            this.state.name = result.name;
        });
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
