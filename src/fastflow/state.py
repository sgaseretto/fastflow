"""
State management classes for Fastflow.

Provides Python classes that map to X6's data structures, using fastcore
ergonomics (store_attr, @patch) for cleaner code and extensibility.

Key features:
- NodeData, EdgeData, Flow classes with store_attr
- Extensible via @patch without subclassing
- Bidirectional X6 JSON serialization
- Topological sort for execution ordering

Example:
    ```python
    from fastflow.state import Flow, NodeData, EdgeData

    flow = Flow(
        id="my-flow",
        name="Data Pipeline",
        nodes=[
            NodeData(id="load", x=100, y=100, label="Load"),
            NodeData(id="process", x=300, y=100, label="Process"),
        ],
        edges=[
            EdgeData(source="load", target="process"),
        ]
    )

    # Extend via @patch
    from fastcore.basics import patch

    @patch
    def to_mermaid(self: Flow) -> str:
        '''Convert flow to Mermaid diagram.'''
        lines = ["graph LR"]
        for edge in self.edges:
            lines.append(f"    {edge.source} --> {edge.target}")
        return "\\n".join(lines)
    ```
"""

from fastcore.basics import store_attr, patch
from typing import Optional, Any
import json

from .core import to_x6_node, to_x6_edge, from_x6_node, from_x6_edge

__all__ = [
    "NodeData",
    "EdgeData",
    "Flow",
]


# =============================================================================
# NodeData
# =============================================================================

class NodeData:
    """
    Represents a node in the flow.

    Uses store_attr for reduced boilerplate. All attributes are set
    from __init__ parameters automatically.

    Attributes:
        id: Unique node identifier
        x: X position in pixels
        y: Y position in pixels
        width: Node width in pixels
        height: Node height in pixels
        label: Display label
        node_type: Node type for styling (e.g., "agent", "tool", "start")
        inputs: Number of input ports
        outputs: Number of output ports
        data: Additional custom data dictionary

    Example:
        ```python
        node = NodeData(
            id="agent1",
            x=100, y=200,
            label="ChatBot",
            node_type="agent",
            data={"model": "gpt-4"}
        )
        ```
    """

    def __init__(
        self,
        id: str,
        x: float = 0,
        y: float = 0,
        width: int = 160,
        height: int = 60,
        label: str = "",
        node_type: str = "default",
        inputs: int = 1,
        outputs: int = 1,
        data: Optional[dict] = None,
    ):
        store_attr()
        self.data = data if data is not None else {}

    def to_x6(self) -> dict:
        """Convert to X6 node format."""
        return to_x6_node(
            node_id=self.id,
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
            label=self.label or self.id,
            node_type=self.node_type,
            inputs=self.inputs,
            outputs=self.outputs,
            data=self.data,
        )

    @classmethod
    def from_x6(cls, data: dict) -> "NodeData":
        """Create NodeData from X6 format."""
        parsed = from_x6_node(data)
        return cls(
            id=parsed["id"],
            x=parsed["x"],
            y=parsed["y"],
            width=parsed["width"],
            height=parsed["height"],
            label=parsed["label"],
            node_type=parsed["node_type"],
            inputs=parsed["inputs"],
            outputs=parsed["outputs"],
            data=parsed["data"],
        )

    def __repr__(self) -> str:
        return f"NodeData(id={self.id!r}, label={self.label!r}, node_type={self.node_type!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, NodeData):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


# =============================================================================
# EdgeData
# =============================================================================

class EdgeData:
    """
    Represents a connection/edge between nodes.

    Uses store_attr for reduced boilerplate.

    Attributes:
        source: Source node ID
        target: Target node ID
        source_port: Source port name (default: "out_0")
        target_port: Target port name (default: "in_0")
        label: Optional edge label
        dashed: Whether to render as dashed line
        data: Additional custom data dictionary

    Example:
        ```python
        edge = EdgeData(
            source="load",
            target="process",
            label="next",
            dashed=False
        )
        ```
    """

    def __init__(
        self,
        source: str,
        target: str,
        source_port: str = "out_0",
        target_port: str = "in_0",
        label: str = "",
        dashed: bool = False,
        data: Optional[dict] = None,
    ):
        store_attr()
        self.data = data if data is not None else {}

    def to_x6(self) -> dict:
        """Convert to X6 edge format."""
        return to_x6_edge(
            source=self.source,
            target=self.target,
            source_port=self.source_port,
            target_port=self.target_port,
            label=self.label if self.label else None,
            dashed=self.dashed,
            data=self.data if self.data else None,
        )

    @classmethod
    def from_x6(cls, data: dict) -> "EdgeData":
        """Create EdgeData from X6 format."""
        parsed = from_x6_edge(data)
        return cls(
            source=parsed["source"],
            target=parsed["target"],
            source_port=parsed["source_port"],
            target_port=parsed["target_port"],
            label=parsed["label"],
            dashed=parsed["dashed"],
            data=parsed["data"],
        )

    def __repr__(self) -> str:
        label_str = f", label={self.label!r}" if self.label else ""
        return f"EdgeData(source={self.source!r}, target={self.target!r}{label_str})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, EdgeData):
            return False
        return self.source == other.source and self.target == other.target

    def __hash__(self) -> int:
        return hash((self.source, self.target))


# =============================================================================
# Flow
# =============================================================================

class Flow:
    """
    Complete workflow state.

    Contains all nodes and edges, with methods for manipulation
    and serialization.

    Attributes:
        id: Flow identifier
        name: Human-readable flow name
        nodes: List of NodeData instances
        edges: List of EdgeData instances
        metadata: Additional metadata dictionary

    Example:
        ```python
        flow = Flow(
            id="pipeline-1",
            name="Data Pipeline",
            nodes=[
                NodeData(id="start", x=100, y=100, node_type="start"),
                NodeData(id="end", x=300, y=100, node_type="end"),
            ],
            edges=[
                EdgeData(source="start", target="end"),
            ]
        )

        # Serialize to JSON
        json_str = flow.to_json()

        # Load from JSON
        flow2 = Flow.from_json(json_str)
        ```
    """

    def __init__(
        self,
        id: str = "",
        name: str = "Untitled",
        nodes: Optional[list[NodeData]] = None,
        edges: Optional[list[EdgeData]] = None,
        metadata: Optional[dict] = None,
    ):
        store_attr()
        self.nodes = nodes if nodes is not None else []
        self.edges = edges if edges is not None else []
        self.metadata = metadata if metadata is not None else {}

    # =========================================================================
    # Node Operations
    # =========================================================================

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
        """
        Remove a node by ID.

        Also removes any edges connected to this node.

        Returns:
            True if node was found and removed, False otherwise
        """
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

    def update_node(self, node_id: str, **kwargs) -> bool:
        """
        Update node attributes.

        Args:
            node_id: ID of node to update
            **kwargs: Attributes to update

        Returns:
            True if node was found and updated

        Example:
            ```python
            flow.update_node("agent1", label="Updated Label", x=200)
            ```
        """
        node = self.get_node(node_id)
        if node is None:
            return False
        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)
        return True

    # =========================================================================
    # Edge Operations
    # =========================================================================

    def add_edge(self, edge: EdgeData) -> None:
        """Add an edge to the flow."""
        self.edges.append(edge)

    def remove_edge(self, source: str, target: str) -> bool:
        """
        Remove an edge.

        Returns:
            True if edge was found and removed
        """
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

    def get_predecessors(self, node_id: str) -> list[str]:
        """Get IDs of all nodes that have edges pointing to this node."""
        return [e.source for e in self.get_incoming_edges(node_id)]

    def get_successors(self, node_id: str) -> list[str]:
        """Get IDs of all nodes that this node has edges pointing to."""
        return [e.target for e in self.get_outgoing_edges(node_id)]

    # =========================================================================
    # Graph Operations
    # =========================================================================

    def topological_sort(self) -> list[NodeData]:
        """
        Return nodes in topological order (for execution).

        Uses Kahn's algorithm.

        Returns:
            List of nodes in execution order

        Raises:
            ValueError: If there's a cycle in the graph
        """
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

        if len(result) != len(self.nodes):
            raise ValueError("Cycle detected in flow graph")

        return result

    def is_valid(self) -> tuple[bool, list[str]]:
        """
        Check if the flow is valid.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check for duplicate node IDs
        node_ids = [n.id for n in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            errors.append("Duplicate node IDs found")

        # Check that all edge endpoints exist
        for edge in self.edges:
            if edge.source not in node_ids:
                errors.append(f"Edge source '{edge.source}' not found in nodes")
            if edge.target not in node_ids:
                errors.append(f"Edge target '{edge.target}' not found in nodes")

        # Check for cycles
        try:
            self.topological_sort()
        except ValueError:
            errors.append("Cycle detected in flow graph")

        return len(errors) == 0, errors

    # =========================================================================
    # Serialization
    # =========================================================================

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
    def from_json(
        cls,
        json_str: str,
        flow_id: str = "",
        name: str = "Untitled"
    ) -> "Flow":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_x6(data, flow_id, name)

    def __repr__(self) -> str:
        return f"Flow(id={self.id!r}, name={self.name!r}, nodes={len(self.nodes)}, edges={len(self.edges)})"

    def __len__(self) -> int:
        return len(self.nodes)


# =============================================================================
# Extension Points via @patch
# =============================================================================

# Users can extend these classes without subclassing:
#
# @patch
# def validate(self: NodeData) -> list[str]:
#     '''Custom validation logic.'''
#     errors = []
#     if not self.id:
#         errors.append("Node must have an id")
#     return errors
#
# @patch
# def to_langgraph(self: Flow):
#     '''Convert to LangGraph format.'''
#     ...
#
# @patch(as_prop=True)
# def is_start(self: NodeData) -> bool:
#     return self.node_type == "start"


# Built-in extensions

@patch
def validate(self: NodeData) -> list[str]:
    """Validate node data. Returns list of errors."""
    errors = []
    if not self.id:
        errors.append("Node must have an id")
    if self.x < 0 or self.y < 0:
        errors.append("Node position must be non-negative")
    if self.width <= 0 or self.height <= 0:
        errors.append("Node dimensions must be positive")
    return errors


@patch
def validate(self: EdgeData) -> list[str]:
    """Validate edge data. Returns list of errors."""
    errors = []
    if not self.source:
        errors.append("Edge must have a source")
    if not self.target:
        errors.append("Edge must have a target")
    if self.source == self.target:
        errors.append("Edge cannot connect a node to itself")
    return errors


@patch
def validate(self: Flow) -> list[str]:
    """Validate entire flow. Returns list of errors."""
    errors = []

    # Validate all nodes
    for node in self.nodes:
        node_errors = node.validate()
        errors.extend([f"Node '{node.id}': {e}" for e in node_errors])

    # Validate all edges
    for edge in self.edges:
        edge_errors = edge.validate()
        errors.extend([f"Edge '{edge.source}→{edge.target}': {e}" for e in edge_errors])

    # Check graph validity
    _, graph_errors = self.is_valid()
    errors.extend(graph_errors)

    return errors


@patch
def copy(self: NodeData) -> "NodeData":
    """Create a copy of this node."""
    return NodeData(
        id=self.id,
        x=self.x,
        y=self.y,
        width=self.width,
        height=self.height,
        label=self.label,
        node_type=self.node_type,
        inputs=self.inputs,
        outputs=self.outputs,
        data=self.data.copy(),
    )


@patch
def copy(self: EdgeData) -> "EdgeData":
    """Create a copy of this edge."""
    return EdgeData(
        source=self.source,
        target=self.target,
        source_port=self.source_port,
        target_port=self.target_port,
        label=self.label,
        dashed=self.dashed,
        data=self.data.copy(),
    )


@patch
def copy(self: Flow) -> "Flow":
    """Create a deep copy of this flow."""
    return Flow(
        id=self.id,
        name=self.name,
        nodes=[n.copy() for n in self.nodes],
        edges=[e.copy() for e in self.edges],
        metadata=self.metadata.copy(),
    )
