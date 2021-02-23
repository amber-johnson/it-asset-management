import React, { useContext } from "react";
import styled from "styled-components";
import { Typography, Row } from "antd";
import { AuthContext } from "../../../contexts/contexts";

const FullDiv = styled("div")`
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  padding: 16px;
`;

const FullRow = styled(Row)`
  flex-grow: 10000;
`;

function LandingPage() {
  const { user } = useContext(AuthContext);

  return (
    <FullDiv>
      <Typography.Title level={3}>
        Test 12 Logged in as {user.username}
      </Typography.Title>
      <FullRow justify="center" align="middle">
        <img src="/static/favicon.ico" />
      </FullRow>
    </FullDiv>
  );
}
export default LandingPage;
