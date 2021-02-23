import * as Yup from "yup";

const COLOR_HEX_REGEX = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/g;

export const schema = Yup.object()
  .shape({
    asset_number: Yup.number()
      .min(100000)
      .max(999999)
      .nullable(),
    hostname: Yup.string(),
    itmodel: Yup.number().required(),

    display_color: Yup.string()
      .matches(COLOR_HEX_REGEX)
      .nullable(),
    cpu: Yup.string().nullable(),
    memory: Yup.number().nullable(),
    storage: Yup.string().nullable(),

    location: Yup.lazy(({ tag }) =>
      tag === "rack-mount"
        ? Yup.object({
            tag: Yup.string().matches(/^rack-mount$/),
            site: Yup.number().required(),
            rack: Yup.number().required(),
            rack_position: Yup.number()
              .typeError("Should be a number!")
              .required()
              .integer()
              .min(1)
              .max(42),
          })
        : tag === "chassis-mount"
        ? Yup.object({
            tag: Yup.string().matches(/^chassis-mount$/),
            site: Yup.number().required(),
            rack: Yup.number().required(),
            asset: Yup.number().required(),
            slot: Yup.number()
              .typeError("Should be a number!")
              .required()
              .integer()
              .min(1)
              .max(14),
          })
        : tag === "offline"
        ? Yup.object({
            tag: Yup.string().matches(/^offline$/),
            site: Yup.number().required(),
          })
        : null,
    ),
    /*power_connections: Yup.array(
      Yup.object({
        pdu_id: Yup.number().required(),
        plug: Yup.number().required(),
      }).nullable(),
    ),*/
    network_ports: Yup.array(
      Yup.object({
        label: Yup.string().required(),
        mac_address: Yup.string().nullable(),
        connection: Yup.number().nullable(),
      }),
    ),
    comment: Yup.string().nullable(),
    owner: Yup.number().nullable(),
  })
  .default({
    asset_number: null,
    hostname: "",
    itmodel: null,
    display_color: null,
    cpu: null,
    memory: null,
    storage: null,
    location: {
      tag: "rack-mount",
      site: null,
      rack: null,
      rack_position: null,
    },
    power_connections: [],
    network_ports: [],
    comment: "",
    owner: null,
  });
