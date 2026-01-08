"""
Fastflow - A Python library wrapping AntV X6 for FastHTML

Build visual workflow editors with Python using FastHTML-style components,
with fastcore patterns for extensibility (type dispatch, callbacks, @patch).

## Layered API

### Layer 0: Core Primitives (for advanced users)
```python
from fastflow.core import raw_node_status, raw_edge_status, raw_complete
```

### Layer 1: State Management
```python
from fastflow import Flow, NodeData, EdgeData
```

### Layer 2: Typed Nodes + Callbacks (main API)
```python
from fastflow.types import AgentNode, ToolNode, render, execute, can_connect
from fastflow.callbacks import FlowCallback, SSECallback, LoggingCallback
from fastflow import FlowExecutor, ExecutionStep
```

### Layer 3: Convenience Functions
```python
from fastflow.api import quick_flow, run_pipeline, from_langgraph
```

## Quick Start
```python
from fasthtml.common import *
from fastflow import FlowEditor, Node, Edge, fastflow_headers
from fastflow.execution import FlowExecutor, ExecutionStep
from fastflow.callbacks import SSECallback, LoggingCallback

app, rt = fast_app(hdrs=fastflow_headers())

@rt("/")
def get():
    return FlowEditor(
        Node("start", x=100, y=100, node_type="start"),
        Node("agent", x=300, y=200, node_type="agent"),
        Edge(source="start", target="agent"),
    )
```
"""

__version__ = "0.2.0"

# =============================================================================
# Layer 0: Core Primitives
# =============================================================================
from .core import (
    raw_node_status,
    raw_edge_status,
    raw_complete,
    raw_error,
    to_x6_node,
    to_x6_edge,
    from_x6_node,
    from_x6_edge,
)

# =============================================================================
# Layer 1: State Management
# =============================================================================
from .state import Flow, NodeData, EdgeData

# =============================================================================
# Layer 2: Typed Nodes (via types module)
# =============================================================================
from .types import (
    # Base class
    FlowNode,
    # Node types
    StartNode,
    EndNode,
    AgentNode as TypedAgentNode,  # Renamed to avoid conflict with component
    ToolNode,
    LLMNode,
    ConditionNode,
    InputNode,
    OutputNode,
    FilterNode,
    JoinNode,
    TransformNode,
    ProcessNode,
    DecisionNode,
    CodeNode,
    # Type-dispatched operations
    render,
    execute,
    validate,
    node_to_x6,
    node_from_x6,
    can_connect,
    get_node_style,
    # Registry
    NODE_TYPE_MAP,
    register_node_type,
)

# =============================================================================
# Layer 2: Callbacks
# =============================================================================
from .callbacks import (
    # State
    FlowState,
    # Exceptions
    CancelFlowException,
    SkipNodeException,
    RetryNodeException,
    # Base callback
    FlowCallback,
    # Built-in callbacks
    SSECallback,
    LoggingCallback,
    TimingCallback,
    RetryCallback,
    ProgressCallback,
    ValidationCallback,
)

# =============================================================================
# Layer 2: Execution
# =============================================================================
from .execution import (
    FlowExecutor,
    ExecutionStep,
    # Backward compat SSE helpers (also in core as raw_*)
    node_status,
    edge_status,
    execution_complete,
    execution_error,
    run_sequential,
)

# =============================================================================
# Layer 3: Convenience API
# =============================================================================
from .api import (
    quick_flow,
    run_pipeline,
    from_dict,
    to_dict,
    from_langgraph,
    flow_from_steps,
)

# =============================================================================
# UI Components (FT components for browser)
# =============================================================================
from .components import (
    FlowEditor,
    Node,
    Edge,
    NodePalette,
    PaletteItem,
    FlowControls,
    # Specialized components
    TableNode,
    PaletteGroup,
    StatusBadge,
    DAGNode,
    AgentNode,  # This is the FT component, not the typed node
    FlowchartNode,
    # Constants
    NODE_STYLES,
    # Type dispatch integration
    node_from_typed,
    nodes_from_typed,
    validate_typed_node,
)

# =============================================================================
# Headers
# =============================================================================
from .headers import fastflow_headers

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    # Version
    "__version__",

    # --- Layer 0: Core Primitives ---
    "raw_node_status",
    "raw_edge_status",
    "raw_complete",
    "raw_error",
    "to_x6_node",
    "to_x6_edge",
    "from_x6_node",
    "from_x6_edge",

    # --- Layer 1: State Management ---
    "Flow",
    "NodeData",
    "EdgeData",

    # --- Layer 2: Typed Nodes ---
    "FlowNode",
    "StartNode",
    "EndNode",
    "TypedAgentNode",
    "ToolNode",
    "LLMNode",
    "ConditionNode",
    "InputNode",
    "OutputNode",
    "FilterNode",
    "JoinNode",
    "TransformNode",
    "ProcessNode",
    "DecisionNode",
    "CodeNode",
    # Type dispatch operations
    "render",
    "execute",
    "validate",
    "node_to_x6",
    "node_from_x6",
    "can_connect",
    "get_node_style",
    "NODE_TYPE_MAP",
    "register_node_type",

    # --- Layer 2: Callbacks ---
    "FlowState",
    "CancelFlowException",
    "SkipNodeException",
    "RetryNodeException",
    "FlowCallback",
    "SSECallback",
    "LoggingCallback",
    "TimingCallback",
    "RetryCallback",
    "ProgressCallback",
    "ValidationCallback",

    # --- Layer 2: Execution ---
    "FlowExecutor",
    "ExecutionStep",
    "node_status",
    "edge_status",
    "execution_complete",
    "execution_error",
    "run_sequential",

    # --- Layer 3: Convenience API ---
    "quick_flow",
    "run_pipeline",
    "from_dict",
    "to_dict",
    "from_langgraph",
    "flow_from_steps",

    # --- UI Components ---
    "FlowEditor",
    "Node",
    "Edge",
    "NodePalette",
    "PaletteItem",
    "FlowControls",
    "TableNode",
    "PaletteGroup",
    "StatusBadge",
    "DAGNode",
    "AgentNode",
    "FlowchartNode",
    "NODE_STYLES",
    # Type dispatch integration
    "node_from_typed",
    "nodes_from_typed",
    "validate_typed_node",

    # --- Headers ---
    "fastflow_headers",
]
