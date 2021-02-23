import React from "react";
import ImportPage from "./ImportPage";
import { importModels } from "../../../api/bulk";

function ModelImportPage() {
  return <ImportPage title="Import Models" importData={importModels} />;
}

export default ModelImportPage;
