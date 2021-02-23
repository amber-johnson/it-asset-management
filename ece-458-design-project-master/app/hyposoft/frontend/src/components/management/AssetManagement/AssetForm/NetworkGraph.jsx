import React from "react";
import { Typography } from "antd";
import Graph from "react-graph-vis";

const options = {
  layout: {
    hierarchical: false,
  },
  edges: {
    color: "#000000",
    arrows: {
      to: {
        enabled: false,
      },
    },
  },
  height: "500px",
  physics: {
    enabled: false,
  },
  interaction: {
    hoverConnectedEdges: false,
    selectConnectedEdges: false,
    zoomView: false,
  },
};

const events = {
  select: ({ nodes }) => {
    const node = nodes[0];
    if (node) {
      window.location.href = `/#/assets/${node}`;
      window.location.reload();
    }
  },
};

function process(assetID, rawGraph) {
  const { verticies, edges } = rawGraph;
  function mapVertex(v) {
    const isMain = v.id == assetID;

    return {
      id: v.id,
      label: v.label + (isMain ? " ☆" : ""),
      color: isMain ? "#0ff" : "#eee",
    };
  }

  function mapEdge(e) {
    return {
      from: e[0],
      to: e[1],
    };
  }

  return {
    nodes: verticies.map(mapVertex),
    edges: edges.map(mapEdge),
  };
}

function NetworkGraph({ assetID, networkGraph }) {
  const [graph, setGraph] = React.useState(null);
  React.useEffect(() => {
    setGraph(process(assetID, networkGraph));
  }, [assetID, networkGraph]);

  return (
    <div>
      {graph ? <Graph options={options} graph={graph} events={events} /> : null}
    </div>
  );
}

export default NetworkGraph;
