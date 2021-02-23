import React from "react";
import { Form, Input } from "antd";
import { MAX_ROW, MAX_COL } from "./RackManagementPage";
import { split, toIndex, indexToRow, indexToColNoZero } from "./GridUtils";

// setRange: ([r1, r2, c1, c2] | null) => ()
// range: [r1, r2, c1, c2] | null
function GridRangeSelector({ setRange, range }) {
  const [p1, setP1] = React.useState("");
  const [p2, setP2] = React.useState("");
  const [p1ErrMsg, setP1ErrMsg] = React.useState("");
  const [p2ErrMsg, setP2ErrMsg] = React.useState("");

  React.useEffect(() => {
    if (range) {
      setP1(indexToRow(range[0]) + indexToColNoZero(range[2]));
      setP2(indexToRow(range[1]) + indexToColNoZero(range[3]));
    } else {
      setP1("");
      setP2("");
    }
  }, [range]);

  return (
    <Form style={{ width: 350 }}>
      <Form.Item
        extra={p1ErrMsg}
        validateStatus={p1ErrMsg.length > 0 ? "error" : "success"}
      >
        <Input
          addonBefore={"Point 1"}
          placeholder="A2"
          value={p1}
          onChange={e => {
            const str = e.target.value;
            const res = validate(str);
            if (res != null) {
              setP1ErrMsg(res);
            } else {
              setP1ErrMsg("");
              if (validate(p2) === null) {
                setRange(destructure(str, p2));
              }
            }
            setP1(str);
          }}
        />
      </Form.Item>
      <Form.Item
        extra={p2ErrMsg}
        validateStatus={p2ErrMsg.length > 0 ? "error" : "success"}
      >
        <Input
          addonBefore={"Point 2"}
          placeholder="B20"
          value={p2}
          onChange={e => {
            const str = e.target.value;
            const res = validate(str);
            if (res != null) {
              setP2ErrMsg(res);
            } else {
              setP2ErrMsg("");
              if (validate(p1) === null) {
                setRange(destructure(p1, str));
              }
            }
            setP2(str);
          }}
        />
      </Form.Item>
    </Form>
  );
}

// these validation functions return an error string when there's a problem
// and returns null when there's not

function validate(s) {
  if (s.length < 2) return "";
  const [rStr, cStr] = split(s, 1);

  if (isNaN(cStr)) return "Use numbers to represent columns";

  const [r, c] = toIndex(rStr + cStr);

  if (r < 0 || r >= MAX_ROW) return "Row out of bounds";
  if (c < 0 || c >= MAX_COL) return "Column out of bounds";

  return null;
}

function destructure(p1, p2) {
  const [r1, c1] = toIndex(p1);
  const [r2, c2] = toIndex(p2);

  return [r1, r2, c1, c2];
}

export default GridRangeSelector;
