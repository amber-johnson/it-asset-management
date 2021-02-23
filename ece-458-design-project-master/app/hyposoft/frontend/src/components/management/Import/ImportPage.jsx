import React from "react";
import { Typography, Row, Col, Button, Divider, message, Alert } from "antd";
import VSpace from "../../utility/VSpace";
import { UploadOutlined } from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";

function ImportPage({ title, importData }) {
  const history = useHistory();

  const origin = new URLSearchParams(useLocation().search).get("origin");

  const fileInputRef = React.useRef(null);
  const [diff, setDiff] = React.useState(null);
  const [errors, setErrors] = React.useState([]);
  const formData = React.useRef(null);

  function handleImport() {
    fileInputRef.current.click();
  }

  function onFileChange(e) {
    const fd = new FormData();
    fd.append("file", e.target.files[0]);
    formData.current = fd;

    importData(fd, false).then(({ status, diff, errors }) => {
      if (status === "diff") {
        setErrors([]);
        setDiff(diff);
      } else if (status === "error") {
        setErrors(errors.map(({ errors }) => errors));
      } else {
        setErrors([]);
      }
    });

    e.target.value = null;
  }

  function forceUpload() {
    message.loading("Importing...");
    importData(formData.current, true).then(({ errors }) => {
      if (errors) {
        setErrors(errors);
      } else {
        message.loading("In progress...");
        history.push(origin);
      }
    });
  }

  const displayForce = errors.length == 0 && formData.current;

  return (
    <div style={{ padding: "16px" }}>
      <Typography.Title level={3}>{title}</Typography.Title>
      <VSpace height="16px" />
      <Row>
        <Col md={8}>
          <Button block onClick={handleImport}>
            <UploadOutlined />
            Upload CSV
          </Button>
          <Divider />
        </Col>
      </Row>

      <VSpace height="16px" />

      <VSpace height="16px" />

      {diff && (
        <table style={{ border: "1pt solid black" }}>
          <thead>
            <tr>
              {diff.headers.map((header, idx) => (
                <th key={idx} style={{ border: "1pt solid black", padding: 4 }}>
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {diff.data.map((row, idx) => (
              <tr key={idx}>
                {row.map((d, idx) => (
                  <td
                    key={idx}
                    dangerouslySetInnerHTML={{ __html: d }}
                    style={{ border: "1pt solid black", padding: 4 }}
                  />
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <VSpace height="16px" />

      {errors.length > 0 && (
        <Alert type="error" message={<pre>{errors.join("\n")}</pre>} />
      )}

      <VSpace height="16px" />

      {displayForce && (
        <Row>
          <Col md={8}>
            <Button block type="primary" onClick={forceUpload}>
              Confirm changes
            </Button>
          </Col>
        </Row>
      )}

      <input
        accept=".csv"
        type="file"
        hidden
        ref={fileInputRef}
        onChange={onFileChange}
      />
    </div>
  );
}

export default ImportPage;
