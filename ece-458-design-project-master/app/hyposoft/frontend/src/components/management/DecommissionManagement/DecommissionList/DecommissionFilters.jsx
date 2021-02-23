import React from "react";
import { Formik, Field } from "formik";
import { Form, Collapse, Row, Col, Calendar, DatePicker } from "antd";
import VSpace from "../../../utility/VSpace";
import RangeSlider from "../../../utility/formik/RangeSlider";
import ItemWithLabel from "../../../utility/formik/ItemWithLabel";
import Input from "../../../utility/formik/Input";
import FormDebugger from "../../../utility/formik/FormDebugger";
import moment from "moment";

// Props
/*
  initialFilterValues: {
    search: string,
    decommissioned_by: string,
    time_from: string,
    time_to: string,
  }
*/
// onChange: (an object with the same form as the initialFilterValues) => void

function DecommissionFilters({ initialFilterValues, onChange }) {
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
                <ItemWithLabel name="search" label="Search by keyword">
                  <Input name="search" />
                </ItemWithLabel>

                <VSpace height="8px" />

                <ItemWithLabel name="search" label="Search by decommissioner">
                  <Input name="decommissioned_by" />
                </ItemWithLabel>

                <VSpace height="8px" />

                <p style={{ fontWeight: "bold" }}>Decommissioned time range</p>
                <Field>
                  {({ form }) => (
                    <DatePicker.RangePicker
                      onChange={r => {
                        if (r) {
                          const [s, e] = r;
                          form.setValues({
                            time_from: s.toISOString(),
                            time_to: e.toISOString(),
                          });
                        } else {
                          form.setValues({
                            time_from: null,
                            time_to: null,
                          });
                        }
                      }}
                    />
                  )}
                </Field>

                <VSpace height="8px" />
              </Col>
            </Row>
          </Form>
        </Formik>
      </Collapse.Panel>
    </Collapse>
  );
}

export default DecommissionFilters;
