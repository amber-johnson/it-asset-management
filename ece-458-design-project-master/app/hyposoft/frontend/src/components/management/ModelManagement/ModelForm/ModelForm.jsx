import React from "react";
import { Formik } from "formik";
import { Form, Button } from "antd";
import ItemWithLabel from "../../../utility/formik/ItemWithLabel";
import * as Yup from "yup";
import AutoComplete from "../../../utility/formik/AutoComplete";
import ColorPicker from "./ColorPicker";
import NetworkPortLabelFormItem from "./NetworkPortLabel";
import SubmitButton from "../../../utility/formik/SubmitButton";
import InputNumber from "../../../utility/formik/InputNumber";
import Input from "../../../utility/formik/Input";
import TextArea from "../../../utility/formik/TextArea";
import { DisableContext, AuthContext } from "../../../../contexts/contexts";
import VSpace from "../../../utility/VSpace";
import {
  createModel,
  getVendors,
  getModel,
  updateModel,
  deleteModel,
} from "../../../../api/model";
import { useHistory } from "react-router-dom";
import useRedirectOnCPChange from "../../../utility/useRedirectOnCPChange";
import TypePicker from "./TypePicker";
import produce from "immer";

const COLOR_HEX_REGEX = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/g;

const schema = Yup.object()
  .shape({
    vendor: Yup.string().required(),
    model_number: Yup.string().required(),
    height: Yup.number()
      .min(1)
      .max(42)
      .required(),
    display_color: Yup.string()
      .matches(COLOR_HEX_REGEX)
      .required(),
    network_port_labels: Yup.array(
      Yup.string().required("This field is required"),
    ),
    power_ports: Yup.number()
      .min(0)
      .max(10),
    cpu: Yup.string().nullable(),
    memory: Yup.number().nullable(),
    storage: Yup.string().nullable(),
    comment: Yup.string().nullable(),
  })
  .default({
    vendor: "",
    model_number: "",
    type: "regular",
    height: 1,
    display_color: "#0ff",
    network_port_labels: [],
    power_ports: 0,
    cpu: "",
    memory: null,
    storage: "",
    comment: "",
  });

function ModelForm({ id }) {
  const history = useHistory();

  const [model, setModel] = React.useState(null);
  const [vendors, setVendors] = React.useState([]);

  React.useEffect(() => {
    if (id) {
      getModel(id).then(setModel);
    } else {
      setModel(schema.default());
    }
    getVendors().then(setVendors);
  }, []);

  useRedirectOnCPChange("/models");

  async function handleCreate(fields) {
    let fieldsForCreate = fields;
    if (fields.type === "blade") {
      fieldsForCreate = produce(fields, draft => {
        draft.height = 1;
        draft.network_port_labels = [];
        draft.power_ports = 0;
      });
    }

    await createModel(fieldsForCreate);
    history.push("/models");
  }

  function handleUpdate(fields) {
    let fieldsForUpdate = fields;
    if (fields.type === "blade") {
      fieldsForCreate = produce(fields, draft => {
        draft.height = 1;
        draft.network_port_labels = [];
        draft.power_ports = 0;
      });
    }

    updateModel(id, fieldsForUpdate);
  }

  async function handleDelete() {
    await deleteModel(id);
    history.push("/models");
  }

  return model ? (
    <Formik
      validationSchema={schema}
      initialValues={model}
      onSubmit={id ? handleUpdate : handleCreate}
    >
      {props => (
        <Form>
          <ItemWithLabel name="vendor" label="Vendor">
            <AutoComplete name="vendor" acList={vendors} />
          </ItemWithLabel>

          <ItemWithLabel name="model_number" label="Model #">
            <Input name="model_number" />
          </ItemWithLabel>

          <ItemWithLabel name="type" label="Type">
            <TypePicker name="type" />
          </ItemWithLabel>

          {props.values.type !== "blade" ? (
            <div>
              <ItemWithLabel name="height" label="Height">
                <InputNumber name="height" min={1} max={42} />
              </ItemWithLabel>
              <ItemWithLabel
                name="network_port_labels"
                label="Network Port Labels"
              >
                <NetworkPortLabelFormItem name="network_port_labels" />
              </ItemWithLabel>

              <ItemWithLabel name="power_ports" label="# of Power ports">
                <InputNumber name="power_ports" min={0} max={10} />
              </ItemWithLabel>
            </div>
          ) : null}

          <ItemWithLabel name="display_color" label="Display Color">
            <ColorPicker name="display_color" />
          </ItemWithLabel>

          <ItemWithLabel name="cpu" label="CPU">
            <Input name="cpu" />
          </ItemWithLabel>

          <ItemWithLabel name="memory" label="Memory">
            <InputNumber name="memory" />
          </ItemWithLabel>

          <ItemWithLabel name="storage" label="Storage">
            <Input name="storage" />
          </ItemWithLabel>

          <ItemWithLabel name="comment" label="Comment">
            <TextArea name="comment" rows={5} />
          </ItemWithLabel>

          <SubmitButton ghost type="primary" block>
            {id ? "Update" : "Create"}
          </SubmitButton>

          {id && (
            <>
              <VSpace height="16px" />
              <Button ghost type="danger" onClick={handleDelete} block>
                Delete
              </Button>
            </>
          )}
        </Form>
      )}
    </Formik>
  ) : null;
}

export default ModelForm;
