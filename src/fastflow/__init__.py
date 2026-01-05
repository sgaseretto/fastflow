"""
Fastflow - A Python library wrapping AntV X6 for FastHTML

Build visual workflow editors with Python using FastHTML-style components.
"""

from .components import (
    FlowEditor,
    Node,
    Edge,
    NodePalette,
    PaletteItem,
    FlowControls,
    # New specialized components
    TableNode,
    PaletteGroup,
    StatusBadge,
    DAGNode,
    AgentNode,
    FlowchartNode,
    # Constants
    NODE_STYLES,
)
from .headers import fastflow_headers
from .state import Flow, NodeData, EdgeData
from .node_types import NodeType, get_node_types, get_node_type, clear_node_types
from .execution import (
    FlowExecutor,
    ExecutionStep,
    node_status,
    edge_status,
    execution_complete,
    execution_error,
    run_sequential,
)

__version__ = "0.1.0"

__all__ = [
    # Core Components
    "FlowEditor",
    "Node",
    "Edge",
    "NodePalette",
    "PaletteItem",
    "FlowControls",
    # Specialized Node Components
    "TableNode",
    "DAGNode",
    "AgentNode",
    "FlowchartNode",
    # Utility Components
    "PaletteGroup",
    "StatusBadge",
    # Constants
    "NODE_STYLES",
    # Headers
    "fastflow_headers",
    # State
    "Flow",
    "NodeData",
    "EdgeData",
    # Node Types
    "NodeType",
    "get_node_types",
    "get_node_type",
    "clear_node_types",
    # Execution (SSE-based)
    "FlowExecutor",
    "ExecutionStep",
    "node_status",
    "edge_status",
    "execution_complete",
    "execution_error",
    "run_sequential",
]
