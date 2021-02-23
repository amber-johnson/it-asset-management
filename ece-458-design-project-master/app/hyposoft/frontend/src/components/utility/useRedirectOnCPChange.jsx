import { useRef, useContext, useEffect } from "react";
import { ChangePlanContext } from "../../contexts/contexts";
import { useHistory } from "react-router-dom";

function useRedirectOnCPChange(redirectTo) {
  const history = useHistory();
  const { changePlan } = useContext(ChangePlanContext);
  const initialCPID = useRef(changePlan?.id);

  useEffect(() => {
    if (changePlan?.id != initialCPID.current) {
      if (redirectTo) {
        history.replace(redirectTo);
      } else {
        window.location.reload();
      }
    }
  }, [changePlan?.id]);
}

export default useRedirectOnCPChange;
