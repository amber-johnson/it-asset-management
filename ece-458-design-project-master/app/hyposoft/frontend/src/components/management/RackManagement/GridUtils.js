const charCodeA = "A".charCodeAt(0);

export function split(s, index) {
  return [s.substring(0, index), s.substring(index)];
}

export function rowToIndex(row) {
  return row.charCodeAt(0) - charCodeA;
}

export function indexToRow(idx) {
  return String.fromCharCode(idx + charCodeA);
}

export function colToIndex(col) {
  return parseInt(col) - 1;
}

export function indexToCol(idx) {
  return (idx + 1).toString();
}

export function indexToColNoZero(idx) {
  const s = (idx + 1).toString();
  return s;
}

export function toIndex(rack) {
  const [row, col] = split(rack, 1);
  return [rowToIndex(row), colToIndex(col)];
}
