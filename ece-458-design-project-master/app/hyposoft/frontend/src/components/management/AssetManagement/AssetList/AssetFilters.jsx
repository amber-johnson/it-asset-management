import React from "react";
import { Formik } from "formik";
import { Form, Collapse, Row, Col } from "antd";
import VSpace from "../../../utility/VSpace";
import RangeSlider from "../../../utility/formik/RangeSlider";
import ItemWithLabel from "../../../utility/formik/ItemWithLabel";
import Input from "../../../utility/formik/Input";
import ResetButton from "../../../utility/formik/ResetButton";

// Props
/* 
  initialFilterValues: { 
    search: string,
    rack_from: string,
    rack_to: string,
    rack_position: [number, number],
  }
*/
// onChange: (an object with the same form as the initialFilterValues) => void

function AssetFilters({ initialFilterValues, onChange, forOffline }) {
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

                {!forOffline && (
                  <>
                    <ItemWithLabel name="rack_from" label="Rack from">
                      <Input name="rack_from" />
                    </ItemWithLabel>

                    <VSpace height="8px" />

                    <ItemWithLabel name="rack_to" label="Rack to">
                      <Input name="rack_to" />
                    </ItemWithLabel>

                    <VSpace height="8px" />

                    <ItemWithLabel name="rack_position" label="Rack position">
                      <RangeSlider name="rack_position" />
                    </ItemWithLabel>
                  </>
                )}

                <ResetButton block>Reset</ResetButton>
              </Col>
            </Row>
          </Form>
        </Formik>
      </Collapse.Panel>
    </Collapse>
  );
}

export default AssetFilters;
