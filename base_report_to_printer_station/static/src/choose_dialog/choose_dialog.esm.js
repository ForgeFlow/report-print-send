/** @odoo-module **/
import {Component, onWillStart, useState} from "@odoo/owl";
import {deserializeDateTime, formatDateTime} from "@web/core/l10n/dates";
import {ConfirmationDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {Dialog} from "@web/core/dialog/dialog";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {sprintf} from "@web/core/utils/strings";
import {useService} from "@web/core/utils/hooks";

export class PrintStationChooseDialog extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.dialog = useService("dialog");
        this.state = useState({stations: [], canRelease: false, choosing: false});
        onWillStart(() => this.load());
    }

    async load() {
        const result = await this.rpc("/printing/station/list", {});
        this.state.stations = result.stations;
        this.state.canRelease = result.can_release;
    }

    lastSeen(station) {
        return station.last_seen
            ? formatDateTime(deserializeDateTime(station.last_seen))
            : "";
    }

    release(station) {
        this.dialog.add(ConfirmationDialog, {
            body: sprintf(
                _t(
                    "Release %s? The computer that uses it will have to choose a station again."
                ),
                station.name
            ),
            confirm: async () => {
                await this.rpc("/printing/station/release", {station_id: station.id});
                await this.load();
            },
            cancel: () => true,
        });
    }

    async choose(station) {
        this.state.choosing = true;
        try {
            await this.rpc("/printing/station/choose", {station_id: station.id});
        } catch (error) {
            this.state.choosing = false;
            await this.load();
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
