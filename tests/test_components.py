"""
Tests for Fastflow components.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_import():
    """Test that all exports are importable."""
    from fastflow import (
        FlowEditor,
        Node,
        Edge,
        NodePalette,
        PaletteItem,
        fastflow_headers,
        Flow,
        NodeData,
        EdgeData,
        NodeType,
        get_node_types,
        get_node_type,
    )

    assert FlowEditor is not None
    assert Node is not None
    assert Edge is not None


def test_node_creation():
    """Test Node component returns correct structure."""
    from fastflow import Node

    node = Node("test-node", x=100, y=200, inputs=1, outputs=2, node_type="agent")

    assert node["_type"] == "node"
    assert node["id"] == "test-node"
    assert node["x"] == 100
    assert node["y"] == 200
    assert node["inputs"] == 1
    assert node["outputs"] == 2
    assert node["node_type"] == "agent"


def test_edge_creation():
    """Test Edge component returns correct structure."""
    from fastflow import Edge

    edge = Edge(source="a", target="b", label="next", dashed=True)

    assert edge["_type"] == "edge"
    assert edge["source"] == "a"
    assert edge["target"] == "b"
    assert edge["label"] == "next"
    assert edge["dashed"] == True


def test_node_type_decorator():
    """Test NodeType decorator registration."""
    from fastflow import NodeType, get_node_type, clear_node_types
    from fasthtml.common import Div

    # Clear existing types
    clear_node_types()

    @NodeType("test-type", inputs=2, outputs=3, icon="🔧")
    def TestNode(label: str = "Test"):
        return Div(label)

    info = get_node_type("test-type")
    assert info is not None
    assert info.name == "test-type"
    assert info.inputs == 2
    assert info.outputs == 3
    assert info.icon == "🔧"


def test_flow_state():
    """Test Flow state class."""
    from fastflow import Flow, NodeData, EdgeData

    flow = Flow(
        id="test-flow",
        name="Test Flow",
        nodes=[
            NodeData(id="1", x=0, y=0, label="start", node_type="start"),
            NodeData(id="2", x=100, y=0, label="end", node_type="end"),
        ],
        edges=[
            EdgeData(source="1", target="2"),
        ],
    )

    assert len(flow.nodes) == 2
    assert len(flow.edges) == 1
    assert flow.get_node("1").label == "start"


def test_flow_topological_sort():
    """Test topological sorting of nodes."""
    from fastflow import Flow, NodeData, EdgeData

    flow = Flow(
        nodes=[
            NodeData(id="3", x=0, y=0, label="end", node_type="end"),
            NodeData(id="1", x=0, y=0, label="start", node_type="start"),
            NodeData(id="2", x=0, y=0, label="middle", node_type="agent"),
        ],
        edges=[
            EdgeData(source="1", target="2"),
            EdgeData(source="2", target="3"),
        ],
    )

    sorted_nodes = flow.topological_sort()
    labels = [n.label for n in sorted_nodes]

    # start should come before middle, middle before end
    assert labels.index("start") < labels.index("middle")
    assert labels.index("middle") < labels.index("end")


def test_flow_serialization():
    """Test Flow JSON serialization/deserialization."""
    from fastflow import Flow, NodeData, EdgeData

    flow = Flow(
        id="test",
        name="Test",
        nodes=[
            NodeData(id="1", x=10, y=20, label="a", node_type="start"),
            NodeData(id="2", x=30, y=40, label="b", node_type="end"),
        ],
        edges=[
            EdgeData(source="1", target="2", label="next"),
        ],
    )

    # Serialize to X6 format
    json_str = flow.to_json()
    assert "nodes" in json_str
    assert "edges" in json_str

    # Deserialize
    restored = Flow.from_json(json_str)
    assert len(restored.nodes) == 2
    assert restored.edges[0].label == "next"


def test_fastflow_headers():
    """Test headers generation."""
    from fastflow import fastflow_headers

    hdrs = fastflow_headers()

    assert isinstance(hdrs, tuple)
    assert len(hdrs) >= 2  # At least CSS link and JS script
