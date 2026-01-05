"""
State management classes for Fastflow.

Provides Python dataclasses that map to X6's data structures.
"""

from dataclasses import dataclass, field
from typing import Optional, Any
import json


@dataclass
class NodeData:
    """Represents a node in the flow."""
    id: str
    x: float
    y: float
    width: int = 160
    height: int = 60
    label: str = ""
    node_type: str = "default"
    inputs: int = 1
    outputs: int = 1
    data: dict[str, Any] = field(default_factory=dict)

    def to_x6(self) -> dict:
        """Convert to X6 node format."""
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "data": {
                "label": self.label or self.id,
                "nodeType": self.node_type,
                "inputs": self.inputs,
                "outputs": self.outputs,
                **self.data,
            },
        }

    @classmethod
    def from_x6(cls, data: dict) -> "NodeData":
        """Create NodeData from X6 format."""
        node_data = data.get("data", {})
        return cls(
            id=str(data["id"]),
            x=data.get("x", 0),
            y=data.get("y", 0),
            width=data.get("width", 160),
            height=data.get("height", 60),
            label=node_data.get("label", ""),
            node_type=node_data.get("nodeType", "default"),
            inputs=node_data.get("inputs", 1),
            outputs=node_data.get("outputs", 1),
            data={k: v for k, v in node_data.items()
                  if k not in ("label", "nodeType", "inputs", "outputs")},
        )


@dataclass
class EdgeData:
    """Represents a connection/edge between nodes."""
    source: str
    target: str
    source_port: str = "out_0"
    target_port: str = "in_0"
    label: str = ""
    dashed: bool = False
    data: dict[str, Any] = field(default_factory=dict)

    def to_x6(self) -> dict:
        """Convert to X6 edge format."""
        edge_data = {
            "source": self.source,
            "target": self.target,
            "sourcePort": self.source_port,
            "targetPort": self.target_port,
        }
        if self.label:
            edge_data["label"] = self.label
        if self.dashed:
            edge_data["dashed"] = True
        if self.data:
            edge_data["data"] = self.data
        return edge_data

    @classmethod
    def from_x6(cls, data: dict) -> "EdgeData":
        """Create EdgeData from X6 format."""
        # Handle labels - check both simple format and X6's array format
        label = data.get("label", "")

        # Also check X6's internal labels array format
        if not label:
            labels = data.get("labels", [])
            if labels and len(labels) > 0:
                label_data = labels[0]
                if isinstance(label_data, dict):
                    attrs = label_data.get("attrs", {})
                    text = attrs.get("text", {})
                    label = text.get("text", "")

        return cls(
            source=str(data.get("source", "")),
            target=str(data.get("target", "")),
            source_port=data.get("sourcePort", "out_0"),
            target_port=data.get("targetPort", "in_0"),
            label=label,
            dashed=data.get("dashed", False),
            data=data.get("data", {}),
        )


@dataclass
class Flow:
    """Complete workflow state."""
    id: str = ""
    name: str = "Untitled"
    nodes: list[NodeData] = field(default_factory=list)
    edges: list[EdgeData] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_node(self, node_id: str) -> Optional[NodeData]:
        """Get a node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def add_node(self, node: NodeData) -> None:
        """Add a node to the flow."""
        self.nodes.append(node)

    def remove_node(self, node_id: str) -> bool:
        """Remove a node by ID. Returns True if found and removed."""
        for i, node in enumerate(self.nodes):
            if node.id == node_id:
                self.nodes.pop(i)
                # Also remove any edges connected to this node
                self.edges = [
                    e for e in self.edges
                    if e.source != node_id and e.target != node_id
                ]
                return True
        return False

    def add_edge(self, edge: EdgeData) -> None:
        """Add an edge to the flow."""
        self.edges.append(edge)

    def remove_edge(self, source: str, target: str) -> bool:
        """Remove an edge. Returns True if found and removed."""
        for i, edge in enumerate(self.edges):
            if edge.source == source and edge.target == target:
                self.edges.pop(i)
                return True
        return False

    def get_incoming_edges(self, node_id: str) -> list[EdgeData]:
        """Get all edges pointing to a node."""
        return [e for e in self.edges if e.target == node_id]

    def get_outgoing_edges(self, node_id: str) -> list[EdgeData]:
        """Get all edges coming from a node."""
        return [e for e in self.edges if e.source == node_id]

    def topological_sort(self) -> list[NodeData]:
        """Return nodes in topological order (for execution)."""
        # Build adjacency and in-degree maps
        in_degree: dict[str, int] = {n.id: 0 for n in self.nodes}
        adj: dict[str, list[str]] = {n.id: [] for n in self.nodes}

        for edge in self.edges:
            if edge.source in adj and edge.target in in_degree:
                adj[edge.source].append(edge.target)
                in_degree[edge.target] += 1

        # Kahn's algorithm
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            nid = queue.pop(0)
            node = self.get_node(nid)
            if node:
                result.append(node)

            for neighbor in adj.get(nid, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result

    def to_x6(self) -> dict:
        """Convert to X6 export format."""
        return {
            "nodes": [node.to_x6() for node in self.nodes],
            "edges": [edge.to_x6() for edge in self.edges],
        }

    @classmethod
    def from_x6(
        cls,
        data: dict,
        flow_id: str = "",
        name: str = "Untitled"
    ) -> "Flow":
        """Parse X6 export format."""
        nodes = [NodeData.from_x6(n) for n in data.get("nodes", [])]
        edges = [EdgeData.from_x6(e) for e in data.get("edges", [])]

        return cls(
            id=flow_id,
            name=name,
            nodes=nodes,
            edges=edges,
        )

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_x6())

    @classmethod
    def from_json(cls, json_str: str, flow_id: str = "", name: str = "Untitled") -> "Flow":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_x6(data, flow_id, name)
