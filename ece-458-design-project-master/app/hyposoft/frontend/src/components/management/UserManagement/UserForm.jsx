import React from "react";
import { Formik } from "formik";
import Form from "antd/lib/form/Form";
import { getUser, createUser, updateUser, deleteUser } from "../../../api/user";
import * as Yup from "yup";
import ItemWithLabel from "../../utility/formik/ItemWithLabel";
import Input from "../../utility/formik/Input";
import Switch from "../../utility/formik/Switch";
import { Switch as $Switch } from "antd";
import { Divider, Button } from "antd";
import Select from "../../utility/formik/Select";
import { getSites } from "../../../api/site";
import SubmitButton from "../../utility/formik/SubmitButton";
import VSpace from "../../utility/VSpace";
import produce from "immer";
import { useHistory } from "react-router-dom";

function schema(isCreate) {
  return Yup.object({
    username: Yup.string().required(),
    ...(isCreate ? { password: Yup.string().required() } : {}),
    first_name: Yup.string().nullable(),
    last_name: Yup.string().nullable(),
    email: Yup.string().nullable(),
    permission: Yup.object({
      model_perm: Yup.boolean(),
      asset_perm: Yup.boolean(),
      power_perm: Yup.boolean(),
      audit_perm: Yup.boolean(),
      admin_perm: Yup.boolean(),
      site_perm: Yup.array(Yup.string()),
    }),
  }).default({
    username: "",
    ...(isCreate ? { password: "" } : {}),
    first_name: "",
    last_name: "",
    email: "",
    permission: {
      model_perm: false,
      asset_perm: false,
      power_perm: false,
      audit_perm: false,
      admin_perm: false,
      site_perm: [],
    },
  });
}

function UserForm({ id }) {
  const history = useHistory();
  const [sites, setSites] = React.useState([]);
  const [user, setUser] = React.useState(null);

  console.log(id);

  const s = schema(!id);

  React.useEffect(() => {
    (async () => {
      const sites = await getSites();
      setSites(sites);

      if (id) {
        const user = await getUser(id);
        user.permission.site_perm = user.permission?.site_perm
          ?.split(",")
          ?.map(abbr =>
            abbr == "Global"
              ? "Global"
              : sites.find(({ abbr: sabbr }) => abbr == sabbr)?.id,
          )
          ?.filter(id => !!id);
        setUser(user);
      } else {
        await setUser(s.default());
      }
    })();
  }, []);

  async function handleCreate(values) {
    const v = produce(values, draft => {
      draft.permission.site_perm = draft.permission.site_perm
        .map(id =>
          id == "Global"
            ? "Global"
            : sites.find(({ id: sid }) => sid == id).abbr,
        )
        .join(",");
    });
    await createUser(v);
    history.push("/users");
  }

  async function handleDelete() {
    await deleteUser(id);
    history.push("/users");
  }

  async function handleUpdate(values) {
    const v = produce(values, draft => {
      draft.permission.site_perm = draft.permission.site_perm
        .map(id =>
          id == "Global"
            ? "Global"
            : sites.find(({ id: sid }) => sid == id).abbr,
        )
        .join(",");
    });
    await updateUser(id, v);
    window.location.reload();
  }

  return (
    user && (
      <Formik
        validationSchema={s}
        initialValues={user}
        onSubmit={id ? handleUpdate : handleCreate}
      >
        {props => (
          <Form>
            <div>
              <ItemWithLabel name="username" label="Username">
                <Input name="username" />
              </ItemWithLabel>
              {!id && (
                <ItemWithLabel name="password" label="Password">
                  <Input name="password" type="password" />
                </ItemWithLabel>
              )}
              <ItemWithLabel name="first_name" label="First name">
                <Input name="first_name" />
              </ItemWithLabel>
              <ItemWithLabel name="last_name" label="Last name">
                <Input name="last_name" />
              </ItemWithLabel>
              <ItemWithLabel name="email" label="Email">
                <Input name="email" />
              </ItemWithLabel>

              <Divider>Permissions</Divider>

              <ItemWithLabel
                name="permission.admin_perm"
                label="Admin permission"
              >
                <Switch name="permission.admin_perm" />
              </ItemWithLabel>

              {!props.values.permission?.admin_perm && (
                <>
                  <ItemWithLabel
                    name="permission.model_perm"
                    label="Model permission"
                  >
                    <Switch name="permission.model_perm" />
                  </ItemWithLabel>
                  <ItemWithLabel
                    name="permission.asset_perm"
                    label="Asset permission"
                  >
                    <Switch name="permission.asset_perm" />
                  </ItemWithLabel>
                  <ItemWithLabel
                    name="permission.power_perm"
                    label="Power permission"
                  >
                    <Switch name="permission.power_perm" />
                  </ItemWithLabel>
                  <ItemWithLabel
                    name="permission.audit_perm"
                    label="Audit permission"
                  >
                    <Switch name="permission.audit_perm" />
                  </ItemWithLabel>
                  <ItemWithLabel
                    name="permission.site_perm"
                    label="Site Permission"
                  >
                    Global?:{" "}
                    <$Switch
                      defaultChecked={user.permission.site_perm.includes(
                        "Global",
                      )}
                      onChange={b => {
                        props.setFieldValue(
                          "permission.site_perm",
                          b ? ["Global"] : [],
                        );
                      }}
                    />
                    {!(
                      props.values.permission.site_perm.length == 1 &&
                      props.values.permission.site_perm[0] == "Global"
                    ) && (
                      <Select
                        name="permission.site_perm"
                        mode="multiple"
                        options={sites.map(({ id, abbr }) => {
                          return { value: id, text: abbr };
                        })}
                      />
                    )}
                  </ItemWithLabel>
                </>
              )}

              {id ? (
                <div>
                  <SubmitButton type="primary" block>
                    Update
                  </SubmitButton>
                  <VSpace height="16px" />
                  <Button type="danger" block onClick={handleDelete}>
                    Delete
                  </Button>
                </div>
              ) : (
                <SubmitButton block type="primary">
                  Create
                </SubmitButton>
              )}
            </div>
          </Form>
        )}
      </Formik>
    )
  );
}

export default UserForm;
