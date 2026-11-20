/** @odoo-module **/
import {Component, onWillStart, useState} from "@odoo/owl";
import {Dialog} from "@web/core/dialog/dialog";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class PrintStationChooseDialog extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({stations: [], choosing: false});
        onWillStart(async () => {
            this.state.stations = await this.rpc("/printing/station/list", {});
        });
    }

    async choose(station) {
        this.state.choosing = true;
        try {
            await this.rpc("/printing/station/choose", {station_id: station.id});
        } catch (error) {
            this.state.choosing = false;
            this.state.stations = await this.rpc("/printing/station/list", {});
            throw error;
        }
        this.env.bus.trigger("PRINT_STATION:CHANGED");
        this.props.close();
        if (this.props.onChosen) {
            await this.props.onChosen();
        }
    }
}

PrintStationChooseDialog.template = "base_report_to_printer_station.ChooseDialog";
PrintStationChooseDialog.components = {Dialog};

async function choosePrintStation(env, action) {
    const params = action.params || {};
    env.services.dialog.add(PrintStationChooseDialog, {
        onChosen: async () => {
            if (!params.method) {
                return;
            }
            const result = await env.services.orm.call(
                params.res_model,
                params.method,
                [params.res_ids]
            );
            if (result && typeof result === "object") {
                return env.services.action.doAction(result);
            }
            return env.services.action.doAction("soft_reload");
        },
    });
}

registry.category("actions").add("printing_station_choose", choosePrintStation);
