import React, {useContext, useState} from "react";
import {useHistory} from "react-router-dom";
import {Layout, Menu, Col, Button, Select, Row} from "antd";
import {
    EyeInvisibleOutlined,
    LogoutOutlined,
    AppstoreOutlined,
    DatabaseOutlined,
    DisconnectOutlined,
    BuildOutlined,
    TableOutlined,
    BookOutlined,
    BarsOutlined,
    UserOutlined,
    InboxOutlined,
    PullRequestOutlined,
    DeliveredProcedureOutlined,
} from "@ant-design/icons";
import {
    AuthContext,
    ChangePlanContext,
    SiteContext,
} from "../../contexts/contexts";
import HGreed from "../utility/HGreed";
import {getChangePlanList} from "../../api/changeplan";
import {logout} from "../../api/auth";
import {getSites} from "../../api/site";
import ConfigureUserPermissions from "../utility/ConfigurePermissions";

const {Header, Content, Sider} = Layout;

function ManagementPageFrame({children}) {
    const history = useHistory();
    const {user} = useContext(AuthContext);
    const {site, setSiteByID, refreshTrigger: siteRefreshTrigger} = useContext(
        SiteContext,
    );
    const {
        changePlan,
        setChangePlan,
        refreshTrigger: cpRefreshTrigger,
    } = useContext(ChangePlanContext);

    const [changePlans, setChangePlans] = useState([]);
    const [sites, setSites] = useState([]);

    React.useEffect(() => {
        let isMobile = window.matchMedia("only screen and (max-width: 600px)")
            .matches;

        if (isMobile) {
            history.push("/scanner");
        }
    }, []);

    React.useEffect(() => {
        getSites().then(setSites);
    }, [siteRefreshTrigger]);

    React.useEffect(() => {
        getChangePlanList().then(cps => {
            setChangePlans(
                cps
                    .filter(({executed_at}) => !executed_at)
                    .map(({id, name}) => {
                        return {id, name};
                    }),
            );
        });
    }, [cpRefreshTrigger]);

    const selectedSiteID = site?.id ?? -1;

    async function onLogout() {
        const {redirectTo} = await logout();
        window.location.href = redirectTo ?? "/";
    }

    return (
        <Layout style={{minHeight: "100vh"}}>
            <Header style={{padding: 0}}>
                <Row>
                    <Col style={{paddingLeft: 24}}>
                        <h1
                            style={{
                                fontSize: 24,
                                color: "#ddd",
                                marginRight: "auto",
                                marginBottom: 0,
                            }}
                        >
                            IT Asset Management System
                        </h1>
                    </Col>
                    <HGreed/>
                    <Col style={{paddingRight: 24}}>
                        <Select
                            value={
                                changePlan
                                    ? JSON.stringify({
                                        id: changePlan.id.toString(),
                                        name: changePlan.name,
                                    })
                                    : "null"
                            }
                            onChange={v => {
                                setChangePlan(JSON.parse(v));
                            }}
                            style={{width: 250, marginRight: 8}}
                        >
                            <Select.Option value="null">Live Data</Select.Option>
                            {changePlans.map(({id, name}, idx) => (
                                <Select.Option
                                    key={idx}
                                    value={JSON.stringify({id: id.toString(), name})}
                                >
                                    {name}
                                </Select.Option>
                            ))}
                        </Select>
                        <Select
                            value={selectedSiteID}
                            onChange={setSiteByID}
                            style={{width: 250, marginRight: 8}}
                        >
                            <Select.Option value={-1}>Global</Select.Option>
                            {sites.map((ds, idx) => (
                                <Select.Option
                                    key={idx}
                                    value={ds.id}
                                >{`${ds.name} (${ds.abbr})`}</Select.Option>
                            ))}
                        </Select>
                        <Button ghost onClick={onLogout}>
                            <LogoutOutlined/>
                            Logout
                        </Button>
                    </Col>
                </Row>
            </Header>
            <Layout>
                <Sider width={160} theme="light" collapsible>
                    <Sidebar/>
                </Sider>
                <Layout style={{padding: "0 16px 16px"}}>
                    <Content style={{backgroundColor: "white"}}>{children}</Content>
                </Layout>
            </Layout>
        </Layout>
    );
}

const EXTERNAL_LINKS = {
    "/import": "/static/bulk_format_proposal.pdf",
};

function Sidebar() {
    const history = useHistory();

    const {user} = useContext(AuthContext);
    const isAdmin = !!user?.permission?.admin_perm;
    const config = ConfigureUserPermissions();
    console.log(config);

    function handleClick(e) {
        const key = e.key;
        const ext = EXTERNAL_LINKS[key];
        if (ext) {
            window.open(ext, "_blank");
        } else {
            history.push(e.key);
        }
    }

    return (
        <Menu onClick={handleClick} selectedKeys={[]} mode="inline">
            <Menu.Item key="/">
                <AppstoreOutlined/>
                <span>Overview</span>
            </Menu.Item>

            <Menu.Item key="/models">
                <InboxOutlined/>
                <span>Models</span>
            </Menu.Item>

            <Menu.Item key="/assets">
                <DatabaseOutlined/>
                <span>Assets</span>
            </Menu.Item>

            <Menu.Item key="/decommission">
                <DisconnectOutlined/>
                <span>Decommission</span>
            </Menu.Item>

            <Menu.Item key="/offline_assets">
                <DeliveredProcedureOutlined/>
                <span>Offline</span>
            </Menu.Item>

            <Menu.Item key="/sites">
                <BuildOutlined/>
                <span>Sites</span>
            </Menu.Item>

            <Menu.Item key="/racks">
                <TableOutlined/>
                <span>Racks</span>
            </Menu.Item>

            <Menu.Item key="/reports">
                <BookOutlined/>
                <span>Reports</span>
            </Menu.Item>

            {config.canLogView ? (
                <Menu.Item key="/logs">
                    <BarsOutlined/>
                    <span>Logs</span>
                </Menu.Item>
            ) : null}

            {config.canChangePlan ? (
                <Menu.Item key="/changeplan">
                    <PullRequestOutlined/>
                    <span>Change Plans</span>
                </Menu.Item>
            ) : null}

            {isAdmin ? (
                <Menu.Item key="/users">
                    <UserOutlined/>
                    <span>Users</span>
                </Menu.Item>
            ) : null}
        </Menu>
    );
}

export default ManagementPageFrame;
