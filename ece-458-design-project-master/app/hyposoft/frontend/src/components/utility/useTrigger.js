import { useState } from "react";

function useTrigger() {
  const [v, setV] = useState(0);
  const trigger = () => setV(1 - v);
  return [v, trigger];
}

export default useTrigger;
