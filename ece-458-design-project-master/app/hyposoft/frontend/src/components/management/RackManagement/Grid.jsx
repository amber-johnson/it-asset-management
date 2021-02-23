import React from "react";
import style from "./Grid.module.css";
import GridRangeSelector from "./GridRangeSelector";
import { Typography } from "antd";
import { GRID_COLOR_MAP } from "./RackManagementPage";

const CELL_WIDTH = 20;

// columns: string[]
// rows: string[]
// renderCell: (rowIdx, colIdx) => Node

const FULL = { width: "100%", height: "100%" };

function Grid({ columns, rows, colorMap, setRange, range }) {
  const isDragging = React.useRef(false);

  const headerRow = (
    <thead>
      <tr>
        <th className={style.tableElm}></th>
        {columns.map(column => (
          <th className={style.tableElm} key={column}>
            {column}
          </th>
        ))}
      </tr>
    </thead>
  );

  const body = (
    <tbody>
      {rows.map((row, rowIdx) => (
        <tr key={row + rowIdx}>
          <td className={style.tableElm}>{row}</td>
          {columns.map((col, colIdx) => {
            const cv = colorMap[rowIdx] && colorMap[rowIdx][colIdx];
            const backgroundColor = GRID_COLOR_MAP[cv ? cv : 0];
            return (
              <td
                className={style.tableElm}
                key={col + colIdx}
                onMouseDown={() => {
                  isDragging.current = true;
                  setRange([rowIdx, rowIdx, colIdx, colIdx]);
                }}
                onMouseEnter={() => {
                  if (isDragging.current) {
                    setRange([range[0], rowIdx, range[2], colIdx]);
                  }
                }}
                onMouseUp={() => {
                  isDragging.current = false;
                  setRange([range[0], rowIdx, range[2], colIdx]);
                }}
              >
                <div style={{ backgroundColor, ...FULL }} />
              </td>
            );
          })}
        </tr>
      ))}
    </tbody>
  );

  return (
    <div>
      <div className={style.horizontalScroll}>
        <table
          style={{ width: CELL_WIDTH * (columns.length + 1) }}
          className={style.table}
        >
          {headerRow}
          {body}
        </table>
      </div>

      <Typography.Title level={4} style={{ marginTop: 16 }}>
        Select range
      </Typography.Title>

      <GridRangeSelector
        setRange={r => {
          setRange(r);
        }}
        range={range}
      />
    </div>
  );
}

export default Grid;
