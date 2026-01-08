"""
Layer 3: High-level convenience functions.

This module provides easy-to-use functions for common use cases,
built on top of the lower layers (core, types, state, execution).

Functions:
- quick_flow: Create FlowExecutor from simple dict list
- run_pipeline: Create linear pipeline from handler functions
- from_dict/to_dict: Flow serialization helpers
- from_langgraph: Convert LangGraph StateGraph to Flow

Example:
    ```python
    from fastflow.api import quick_flow, run_pipeline

    # Simple pipeline from dicts
    executor = quick_flow([
        {"id": "load", "handler": load_data},
        {"id": "process", "depends_on": ["load"], "handler": process},
        {"id": "save", "depends_on": ["process"], "handler": save},
    ])

    # Linear pipeline from functions
    executor = run_pipeline([load_data, preprocess, train, evaluate])

    @rt("/execute")
    async def execute():
        return EventStream(executor.run(context={"db": db}))
    ```
"""

from fastcore.meta import delegates
from typing import Optional, Callable, Any, Union

from .state import Flow, NodeData, EdgeData
from .execution import FlowExecutor, ExecutionStep
from .callbacks import SSECallback, LoggingCallback, TimingCallback, FlowCallback

__all__ = [
    "quick_flow",
    "run_pipeline",
    "from_dict",
    "to_dict",
    "from_langgraph",
    "flow_from_steps",
]


# =============================================================================
# Flow Executor Convenience Functions
# =============================================================================

@delegates(FlowExecutor.__init__)
def quick_flow(
    steps: list[dict],
    graph_id: str = "quick-flow",
    **kwargs
) -> FlowExecutor:
    """
    Create a FlowExecutor from a simple list of step dicts.

    This is the easiest way to create an executable flow when you
    have simple requirements.

    Args:
        steps: List of step dictionaries with keys:
            - id: Step identifier (required)
            - depends_on: List of dependency step IDs (optional)
            - handler: Async handler function (optional)
            - duration: Simulated duration in seconds (optional, default 1.0)
            - node: Typed FlowNode instance (optional)
        graph_id: Identifier for the flow
        **kwargs: Additional arguments passed to FlowExecutor

    Returns:
        Configured FlowExecutor instance

    Example:
        ```python
        async def load_data(context, inputs):
            return await context["db"].fetch_all()

        async def process(context, inputs):
            data = inputs["load"]
            return transform(data)

        executor = quick_flow([
            {"id": "load", "handler": load_data},
            {"id": "process", "depends_on": ["load"], "handler": process},
            {"id": "save", "depends_on": ["process"], "duration": 0.5},
        ])

        @rt("/execute")
        async def execute():
            return EventStream(executor.run(context={"db": db}))
        ```
    """
    exec_steps = []
    for s in steps:
        step = ExecutionStep(
            node_id=s["id"],
            node=s.get("node"),
            depends_on=s.get("depends_on", []),
            duration=s.get("duration", 1.0),
            handler=s.get("handler"),
        )
        exec_steps.append(step)

    return FlowExecutor(graph_id=graph_id, steps=exec_steps, **kwargs)


def run_pipeline(
    handlers: list[Callable],
    graph_id: str = "pipeline",
    callbacks: Optional[list[FlowCallback]] = None,
) -> FlowExecutor:
    """
    Create a linear pipeline from a list of handler functions.

    Each handler runs after the previous one completes. Handler names
    are used as node IDs.

    Args:
        handlers: List of async handler functions
        graph_id: Identifier for the flow
        callbacks: Optional list of callbacks

    Returns:
        Configured FlowExecutor instance

    Example:
        ```python
        async def load_data(context, inputs):
            return await fetch_data()

        async def preprocess(context, inputs):
            return clean(inputs["load_data"])

        async def train(context, inputs):
            return model.fit(inputs["preprocess"])

        async def evaluate(context, inputs):
            return model.evaluate(inputs["train"])

        executor = run_pipeline([load_data, preprocess, train, evaluate])
        ```
    """
    steps = []
    for i, handler in enumerate(handlers):
        # Use function name as node ID
        node_id = handler.__name__ if hasattr(handler, "__name__") else f"step_{i}"
        depends_on = [steps[-1].node_id] if steps else []
        steps.append(ExecutionStep(
            node_id=node_id,
            depends_on=depends_on,
            handler=handler
        ))

    return FlowExecutor(
        graph_id=graph_id,
        steps=steps,
        callbacks=callbacks or []
    )


# =============================================================================
# Flow Serialization Helpers
# =============================================================================

def from_dict(data: dict, flow_id: str = "", name: str = "Untitled") -> Flow:
    """
    Create Flow from a dictionary (e.g., loaded from JSON).

    Args:
        data: Dictionary with "nodes" and "edges" keys
        flow_id: Optional flow identifier
        name: Optional flow name

    Returns:
        Flow instance

    Example:
        ```python
        import json

        with open("flow.json") as f:
            data = json.load(f)

        flow = from_dict(data, flow_id="loaded-flow")
        ```
    """
    return Flow.from_x6(data, flow_id, name)


def to_dict(flow: Flow) -> dict:
    """
    Convert Flow to a dictionary (e.g., for JSON serialization).

    Args:
        flow: Flow instance

    Returns:
        Dictionary in X6 format

    Example:
        ```python
        import json

        flow = Flow(...)
        data = to_dict(flow)

        with open("flow.json", "w") as f:
            json.dump(data, f)
        ```
    """
    return flow.to_x6()


# =============================================================================
# LangGraph Integration
# =============================================================================

def from_langgraph(graph, flow_id: str = "", name: str = "LangGraph Flow") -> Flow:
    """
    Convert a LangGraph StateGraph to Fastflow Flow.

    This enables visualizing LangGraph workflows in Fastflow's editor.

    Args:
        graph: LangGraph StateGraph instance
        flow_id: Optional flow identifier
        name: Optional flow name

    Returns:
        Flow instance

    Example:
        ```python
        from langgraph.graph import StateGraph

        # Build LangGraph
        builder = StateGraph(State)
        builder.add_node("agent", agent_fn)
        builder.add_node("tools", tool_fn)
        builder.add_edge("__start__", "agent")
        builder.add_conditional_edges("agent", should_continue, {...})
        lg = builder.compile()

        # Convert to Fastflow
        flow = from_langgraph(lg, flow_id="my-agent")
        ```
    """
    nodes = []
    edges = []

    # Layout parameters
    start_y = 50
    y_spacing = 120
    x_center = 300

    # Extract nodes
    node_list = []
    if hasattr(graph, "nodes"):
        # Handle different LangGraph versions
        if isinstance(graph.nodes, dict):
            node_list = list(graph.nodes.keys())
        else:
            node_list = list(graph.nodes)

    # Create node positions
    for i, node_name in enumerate(node_list):
        # Determine node type based on name
        if node_name == "__start__":
            node_type = "start"
            label = "__start__"
            inputs, outputs = 0, 1
        elif node_name == "__end__":
            node_type = "end"
            label = "__end__"
            inputs, outputs = 1, 0
        else:
            # Guess type from name
            name_lower = node_name.lower()
            if "agent" in name_lower:
                node_type = "agent"
            elif "tool" in name_lower:
                node_type = "tool"
            elif "llm" in name_lower:
                node_type = "llm"
            else:
                node_type = "agent"  # Default to agent

            label = node_name
            inputs, outputs = 1, 1

        nodes.append(NodeData(
            id=node_name,
            x=x_center,
            y=start_y + i * y_spacing,
            label=label,
            node_type=node_type,
            inputs=inputs,
            outputs=outputs,
        ))

    # Extract edges
    if hasattr(graph, "edges"):
        edge_list = graph.edges if isinstance(graph.edges, list) else list(graph.edges)
        for edge in edge_list:
            # Handle different edge formats
            if hasattr(edge, "source") and hasattr(edge, "target"):
                source, target = edge.source, edge.target
            elif isinstance(edge, tuple) and len(edge) >= 2:
                source, target = edge[0], edge[1]
            else:
                continue

            # Get label if available
            label = ""
            if hasattr(edge, "label"):
                label = edge.label
            elif len(edge) > 2 and isinstance(edge, tuple):
                label = str(edge[2]) if edge[2] else ""

            edges.append(EdgeData(
                source=source,
                target=target,
                label=label,
            ))

    return Flow(
        id=flow_id,
        name=name,
        nodes=nodes,
        edges=edges,
    )


# =============================================================================
# Flow Builder Helper
# =============================================================================

def flow_from_steps(
    steps: list[dict],
    flow_id: str = "",
    name: str = "Flow",
    layout: str = "vertical",
) -> Flow:
    """
    Create a Flow from step definitions with automatic layout.

    This is useful for creating flows programmatically with
    automatic node positioning.

    Args:
        steps: List of step dicts with keys:
            - id: Node identifier (required)
            - label: Display label (optional, defaults to id)
            - node_type: Node type (optional, defaults to "process")
            - depends_on: List of dependency node IDs (optional)
        flow_id: Flow identifier
        name: Flow name
        layout: Layout direction ("vertical" or "horizontal")

    Returns:
        Flow instance with positioned nodes

    Example:
        ```python
        flow = flow_from_steps([
            {"id": "start", "node_type": "start"},
            {"id": "load", "depends_on": ["start"], "label": "Load Data"},
            {"id": "process", "depends_on": ["load"], "label": "Process"},
            {"id": "end", "node_type": "end", "depends_on": ["process"]},
        ])
        ```
    """
    nodes = []
    edges = []

    # Layout parameters
    if layout == "horizontal":
        x_start, y_start = 50, 200
        x_spacing, y_spacing = 200, 0
    else:  # vertical
        x_start, y_start = 200, 50
        x_spacing, y_spacing = 0, 120

    # Create nodes with positions
    for i, step in enumerate(steps):
        node_id = step["id"]
        node_type = step.get("node_type", "process")
        label = step.get("label", node_id)

        # Determine inputs/outputs based on type
        if node_type == "start":
            inputs, outputs = 0, 1
        elif node_type == "end":
            inputs, outputs = 1, 0
        else:
            inputs, outputs = 1, 1

        nodes.append(NodeData(
            id=node_id,
            x=x_start + i * x_spacing,
            y=y_start + i * y_spacing,
            label=label,
            node_type=node_type,
            inputs=inputs,
            outputs=outputs,
            data=step.get("data", {}),
        ))

        # Create edges from dependencies
        for dep in step.get("depends_on", []):
            edges.append(EdgeData(
                source=dep,
                target=node_id,
                label=step.get("edge_label", ""),
            ))

    return Flow(
        id=flow_id,
        name=name,
        nodes=nodes,
        edges=edges,
    )
