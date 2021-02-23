import React from "react";
import { Formik } from "formik";
import { Form, Collapse, Row, Col } from "antd";
import VSpace from "../../../utility/VSpace";
import RangeSlider from "../../../utility/formik/RangeSlider";
import ItemWithLabel from "../../../utility/formik/ItemWithLabel";
import Input from "../../../utility/formik/Input";
import ResetButton from "../../../utility/formik/ResetButton";

// Props
// initialFilterValues: { search: string, height: [number, number], network_ports: [number, number], power_ports: [number, number]}
// onChange: (an object with the same form as the initialFilterValues) => void

function ModelFilters({ initialFilterValues, onChange }) {
  return (
    <Collapse>
      <Collapse.Panel header="Filters">
        <Formik
          initialValues={initialFilterValues}
          validateOnChange
          validate={onChange} // sigh
        >
          <Form>
            <Row>
              <Col md={8}>
                <ItemWithLabel name="search" label="Keyword search">
                  <Input name="search" />
                </ItemWithLabel>

                <VSpace height="8px" />

                <ItemWithLabel name="height" label="Height">
                  <RangeSlider name="height" />
                </ItemWithLabel>

                <VSpace height="8px" />

                <ItemWithLabel name="network_ports" label="# of network ports">
                  <RangeSlider name="network_ports" />
                </ItemWithLabel>

                <VSpace height="8px" />

                <ItemWithLabel name="power_ports" label="# of power ports">
                  <RangeSlider name="power_ports" />
                </ItemWithLabel>

                <ResetButton block>Reset</ResetButton>
              </Col>
            </Row>
          </Form>
        </Formik>
      </Collapse.Panel>
    </Collapse>
  );
}

export default ModelFilters;
