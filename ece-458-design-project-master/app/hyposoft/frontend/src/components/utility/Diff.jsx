import React from "react";
import styled from "styled-components";
import { Button } from "antd";

/*
  headers: string[]
  diff: {
    before: string[] | null
    after: string[] | null
    warning: string | null
    error: string | null
    action: {
      name: string
      onClick: () => void
    } | null,
  }[]
*/

const TH = styled("th")`
  border: 1px solid #ddd;
  padding: 8px;
`;

const TD = styled("td")`
  border: 1px solid #ddd;
  white-space: pre;
  padding: 8px;
`;

const TDD = styled("td")`
  border-left: 1px solid transparent;
  border-right: 1px solid transparent;
  padding: 4px;
`;

function Diff0({ messages }) {
  return (
    <table style={{ border: "1px solid black" }}>
      <tbody>
        {messages.map(({ diffType, message }, idx) => (
          <tr key={idx}>
            <td>{idx}</td>
            <td>{diffType}</td>
            <td>{message}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Diff({ headers, diff, beforeText = "Before", afterText = "After" }) {
  return (
    <div style={{ width: "100%", overflow: "auto" }}>
      <table style={{ border: "1px solid black" }}>
        <thead>
          <tr>
            <TH />
            {headers.map((header, idx) => (
              <TH key={idx}>{header}</TH>
            ))}
          </tr>
        </thead>
        <tbody>
          {diff.map(({ before, after, warning, error, action }, idx) => (
            <React.Fragment key={idx}>
              <tr>
                <TDD colSpan={headers.length + 1} />
              </tr>
              <tr>
                <TD key="before">{beforeText}</TD>
                {before != null ? (
                  before.map((field, idx) => <TD key={idx}>{field}</TD>)
                ) : (
                  <TD colSpan={headers.length}>(Non-existent)</TD>
                )}
              </tr>
              <tr key={"after" + idx}>
                <TD key="after">{afterText}</TD>
                {after != null ? (
                  after.map((field, idx) => <TD key={idx}>{field}</TD>)
                ) : (
                  <TD colSpan={headers.length}>(Non-existent)</TD>
                )}
              </tr>
              {warning && (
                <tr key={idx + "warning"} style={{ color: "orange" }}>
                  <TD>Warning</TD>
                  <TD colSpan={headers.length}>{warning}</TD>
                </tr>
              )}
              {error && (
                <tr key={idx + "error"} style={{ color: "red" }}>
                  <TD>Error</TD>
                  <TD colSpan={headers.length}>{error}</TD>
                </tr>
              )}
              {action && (
                <tr key={idx + "action"} style={{ textAlign: "center" }}>
                  <TD>Action</TD>
                  <TD colSpan={headers.length}>
                    <Button size="small" onClick={action.onClick}>
                      {action.name}
                    </Button>
                  </TD>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Diff;
