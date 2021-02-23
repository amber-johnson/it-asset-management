import React from "react";
import styled from "styled-components";
import * as Yup from "yup";
import { Formik } from "formik";
import { Form, Row, Col, Button, Typography, Divider } from "antd";
import { AuthContext } from "../../../contexts/contexts";
import ItemWithLabel from "../../utility/formik/ItemWithLabel";
import Input from "../../utility/formik/Input";
import SubmitButton from "../../utility/formik/SubmitButton";
import { login } from "../../../api/auth";
import VSpace from "../../utility/VSpace";

const { Title, Paragraph } = Typography;

const CenteringRow = styled(Row)`
  text-align: center;
  height: 100vh;
  padding: 16px;
`;

const schema = Yup.object({
  username: Yup.string().required(),
  password: Yup.string().required(),
});

function LoginPage() {
  const { setUser } = React.useContext(AuthContext);

  async function handleSubmit(username, password) {
    const user = await login(username, password);
    setUser(user);
  }

  function sso(e) {
    e.preventDefault();
    window.location.href = "/auth/shib_login";
  }

  return (
    <CenteringRow type="flex" align="middle" justify="center">
      <Col md={6}>
        <Title level={2}>Hyposoft</Title>
        <Paragraph>IT Asset Management System</Paragraph>
        <VSpace height="8px" />
        <Formik
          initialValues={{ username: "", password: "" }}
          validationSchema={schema}
          onSubmit={async ({ username, password }, actions) => {
            actions.setSubmitting(true);
            await handleSubmit(username, password);
            actions.setSubmitting(false);
          }}
        >
          {() => (
            <Form>
              <ItemWithLabel name="username" label="Username">
                <Input name="username" placeholder="john123" />
              </ItemWithLabel>

              <ItemWithLabel name="password" label="Password">
                <Input name="password" type="password" placeholder="Password" />
              </ItemWithLabel>

              <SubmitButton htmlType="submit" type="primary" block>
                Log in
              </SubmitButton>

              <Divider>or</Divider>

              <Button type="primary" onClick={sso} block>
                Duke SSO
              </Button>
            </Form>
          )}
        </Formik>
      </Col>
    </CenteringRow>
  );
}
export default LoginPage;
