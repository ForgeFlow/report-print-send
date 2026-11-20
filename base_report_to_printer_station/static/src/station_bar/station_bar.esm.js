/** @odoo-module **/
import {Component, onWillStart, useState} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {PrintStationChooseDialog} from "../choose_dialog/choose_dialog.esm";

export class PrintStationBar extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.dialog = useService("dialog");
        this.state = useState({name: false});
        onWillStart(() => this.load());
        useBus(this.env.bus, "PRINT_STATION:CHANGED", () => this.load());
    }

    async load() {
        this.state.name = (await this.rpc("/printing/station/current", {})).name;
    }

    choose() {
        this.dialog.add(PrintStationChooseDialog, {});
    }

    async leave() {
        await this.rpc("/printing/station/leave", {});
        this.env.bus.trigger("PRINT_STATION:CHANGED");
    }
}

PrintStationBar.template = "base_report_to_printer_station.StationBar";
