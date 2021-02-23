import React, {useContext, useState} from "react";
import Grid from "../RackManagement/Grid";
import {Typography, Button, Select, Alert} from "antd";
import {toIndex, indexToRow} from "./GridUtils";
import {getRackList, createRack, deleteRacks} from "../../../api/rack";
import {AuthContext, SiteContext} from "../../../contexts/contexts";
import {getSites} from "../../../api/site";
import VSpace from "../../utility/VSpace";
import useRedirectOnCPChange from "../../utility/useRedirectOnCPChange";
import ConfigureUserPermissions, {
    CheckSitePermissions,
} from "../../utility/ConfigurePermissions";

const {Option} = Select;

function range(start, end) {
    return Array(end - start)
        .fill()
        .map((_, idx) => start + idx);
}

const RED = 1;
const GRAY = 2;
const DARKRED = 3;

export const GRID_COLOR_MAP = {
    0: "white",
    [RED]: "red",
    [GRAY]: "gray",
    [DARKRED]: "darkred",
};

export const MAX_ROW = 26;
export const MAX_COL = 99;

const ROWS = range(0, MAX_ROW).map(indexToRow);
const COLS = range(0, MAX_COL).map(v => (v + 1).toString());

function isInside([r1, r2, c1, c2], r, c) {
    return r1 <= r && r <= r2 && c1 <= c && c <= c2;
}

function showRacks(racks) {
    const idStr = racks.map(r => r.id).join(",");
    window.open("/#/racks/print_view?ids=" + idStr);
}

function LegendItem({color, text}) {
    return (
        <div style={{display: "flex", alignItems: "center"}}>
            <div
                style={{
                    width: 20,
                    height: 20,
                    backgroundColor: color,
                    display: "inline-block",
                }}
            />
            <span style={{marginLeft: 5}}>{text}</span>
        </div>
    );
}

function Legend() {
    return (
        <div style={{margin: 5}}>
            <LegendItem color="darkred" text="Selected racks"/>
            <LegendItem color="gray" text="Racks"/>
            <LegendItem color="red" text="Selection"/>
        </div>
    );
}

function RackManagementPage() {
    const {site} = useContext(SiteContext);

    //configure permissions
    const config = ConfigureUserPermissions();
    const doDisplay = config.canRackCUD;
    console.log("canRackCUD", doDisplay);

    const [racks, setRacks] = useState([]);
    const [sites, setSites] = useState([]);
    const [selectedSite, setSelectedSite] = useState(null);

    const [warnings, setWarnings] = useState([]);
    const [errors, setErrors] = useState([]);

    const finalSelectedSite = site ?? selectedSite;

    const [range, setRange] = React.useState(null);
    const clear = () => setRange(null);

    useRedirectOnCPChange();

    React.useEffect(() => {
        getSites().then(sites =>
            setSites(sites.filter(s => s.type === "datacenter")),
        );

        rehydrate();
        const listener = ({keyCode}) => {
            if (keyCode === 27) {
                // esc
                setRange(null);
            }
        };
        window.addEventListener("keydown", listener);
        return () => window.removeEventListener("keydown", listener);
    }, []);

    React.useEffect(() => {
        rehydrate();
    }, [finalSelectedSite]);


    function rehydrate() {
        const id = finalSelectedSite?.id;
        if (id) {
            getRackList(id).then(setRacks);
        } else {
            setRacks([]);
        }
    }

    function create([r1, r2, c1, c2]) {
        const id = finalSelectedSite?.id;
        if (id) {
            createRack(id, r1, r2, c1, c2)
                .then(({warn, err}) => {
                    setWarnings(warn);
                    setErrors(err);
                })
                .then(clear)
                .then(rehydrate);
        }
    }

    function remove([r1, r2, c1, c2]) {
        const id = finalSelectedSite?.id;
        if (id && confirm(`Are you sure about this?`)) {
            deleteRacks(id, r1, r2, c1, c2)
                .then(({warn, err}) => {
                    setWarnings(warn);
                    setErrors(err);
                })
                .then(clear)
                .then(rehydrate);
        }
    }

    const arrangedRange = range && [
        Math.min(range[0], range[1]),
        Math.max(range[0], range[1]),
        Math.min(range[2], range[3]),
        Math.max(range[2], range[3]),
    ];

    const selectedRacks = arrangedRange
        ? racks.filter(rack => isInside(arrangedRange, ...toIndex(rack.rack)))
        : [];

    function createColorMap() {
        const grid = {};
        if (arrangedRange) {
            const [r1, r2, c1, c2] = arrangedRange;
            for (let r = r1; r <= r2; r++) {
                for (let c = c1; c <= c2; c++) {
                    if (!grid[r]) grid[r] = {};
                    grid[r][c] = RED;
                }
            }
        }
        racks.forEach(rack => {
            const [r, c] = toIndex(rack.rack);
            if (!grid[r]) grid[r] = {};
            grid[r][c] = grid[r][c] === RED ? DARKRED : GRAY;
        });
        return grid;
    }

    const colorMap = createColorMap();

    return (
        <div style={{padding: 16}}>
            <Typography.Title level={3}>Racks</Typography.Title>
            <span>Site: </span>
            {!site ? (
                <Select
                    value={selectedSite?.id}
                    onChange={id => {
                        setSelectedSite(sites.find(s => s.id == id) ?? null);
                    }}
                    style={{width: 300}}
                >
                    {Object.values(sites).map((ds, idx) => (
                        <Option key={idx} value={ds.id}>
                            {`${ds.name} (${ds.abbr})`}
                        </Option>
                    ))}
                </Select>
            ) : (
                <span>{site.abbr}</span>
            )}
            {finalSelectedSite?.type === "offline-storage" && (
                <span style={{color: "red", marginLeft: 4}}>
          This site is offline storage and contains no racks.
        </span>
            )}
            {finalSelectedSite && finalSelectedSite?.type === "datacenter" } (
                <>
                    <Legend/>
                    <Grid
                        rows={ROWS}
                        columns={COLS}
                        colorMap={colorMap}
                        setRange={setRange}
                        range={range}
                    />
                    <div style={{marginTop: 16}}>
                        {doDisplay && CheckSitePermissions(finalSelectedSite?.abbr) ? (
                            <Button
                                disabled={!range}
                                type="primary"
                                style={{marginRight: 8}}
                                onClick={() => create(range)}
                            >
                                Create
                            </Button>
                        ) : null}
                        {console.log("finalSelectedSite", finalSelectedSite)}
                        {doDisplay && CheckSitePermissions(finalSelectedSite?.abbr) ?  (
                            <Button
                                disabled={!range}
                                type="danger"
                                style={{marginRight: 8}}
                                onClick={() => remove(range)}
                            >
                                Delete
                            </Button>
                        ) : null}

                        <Button
                            disabled={selectedRacks.length == 0}
                            type="default"
                            onClick={() => showRacks(selectedRacks)}
                        >
                            View
                        </Button>
                        {warnings.length > 0 && (
                            <>
                                <VSpace height="16px"/>
                                <Alert
                                    closable
                                    type="warning"
                                    message={
                                        <div>
                                            {warnings.map((warn, idx) => (
                                                <p key={idx}>{warn}</p>
                                            ))}
                                        </div>
                                    }
                                />
                            </>
                        )}
                        {errors.length > 0 && (
                            <>
                                <VSpace height="16px"/>
                                <Alert
                                    closable
                                    type="error"
                                    message={
                                        <div>
                                            {errors.map((err, idx) => (
                                                <p key={idx}>{err}</p>
                                            ))}
                                        </div>
                                    }
                                />
                            </>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}

export default RackManagementPage;
