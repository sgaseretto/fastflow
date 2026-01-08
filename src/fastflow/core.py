"""
Layer 0: Raw primitives for X6 and SSE.

This module provides the lowest-level building blocks for fastflow:
- Raw SSE message constructors for browser communication
- X6 JSON format converters

These primitives are used by higher layers but can also be used directly
by advanced users who need fine-grained control.

Example:
    ```python
    from fastflow.core import raw_node_status, raw_complete

    async def custom_execution():
        yield raw_node_status("step1", "running")
        await do_work()
        yield raw_node_status("step1", "success")
        yield raw_complete("Done!")
    ```
"""

from fasthtml.common import sse_message
from typing import Optional, Any, Literal
import json

__all__ = [
    # SSE primitives
    "raw_node_status",
    "raw_edge_status",
    "raw_complete",
    "raw_error",
    # X6 JSON helpers
    "to_x6_node",
    "to_x6_edge",
    "from_x6_node",
    "from_x6_edge",
]

# Type aliases
NodeStatus = Literal["pending", "running", "success", "error", "warning"]
EdgeStatus = Literal["pending", "running", "success", "error"]


# =============================================================================
# SSE Message Primitives
# =============================================================================

def raw_node_status(
    node_id: str,
    status: NodeStatus,
    *,
    graphId: Optional[str] = None,
    message: Optional[str] = None,
    **extra: Any,
) -> str:
    """
    Create a raw SSE message for node status update.

    This is the lowest-level function for sending node status updates.
    Higher-level APIs like callbacks use this internally.

    Args:
        node_id: The ID of the node to update
        status: The new status ('pending', 'running', 'success', 'error', 'warning')
        graphId: Optional graph ID (uses default if not specified)
        message: Optional message to display
        **extra: Additional data to include in the message

    Returns:
        SSE message string ready to yield from an async generator

    Example:
        ```python
        yield raw_node_status("load_data", "running")
        yield raw_node_status("load_data", "success", message="Loaded 1000 rows")
        ```
    """
    data = {"nodeId": node_id, "status": status, **extra}
    if graphId is not None:
        data["graphId"] = graphId
    if message is not None:
        data["message"] = message
    return sse_message(json.dumps(data), event="nodeStatus")


def raw_edge_status(
    source_id: str,
    target_id: str,
    status: EdgeStatus,
    *,
    animated: bool = False,
    graphId: Optional[str] = None,
    **extra: Any,
) -> str:
    """
    Create a raw SSE message for edge status update.

    Args:
        source_id: Source node ID
        target_id: Target node ID
        status: The new status ('pending', 'running', 'success', 'error')
        animated: Whether to animate the edge (typically for 'running')
        graphId: Optional graph ID
        **extra: Additional data to include

    Returns:
        SSE message string ready to yield from an async generator

    Example:
        ```python
        yield raw_edge_status("load", "process", "running", animated=True)
        yield raw_edge_status("load", "process", "success")
        ```
    """
    data = {
        "sourceId": source_id,
        "targetId": target_id,
        "status": status,
        "animated": animated,
        **extra,
    }
    if graphId is not None:
        data["graphId"] = graphId
    return sse_message(json.dumps(data), event="edgeStatus")


def raw_complete(
    message: Optional[str] = None,
    results: Optional[dict] = None,
    **extra: Any,
) -> str:
    """
    Create a raw SSE message signaling execution completion.

    Args:
        message: Optional completion message
        results: Optional results dictionary
        **extra: Additional data to include

    Returns:
        SSE message string ready to yield from an async generator

    Example:
        ```python
        yield raw_complete(
            message="Pipeline completed successfully!",
            results={"rows_processed": 1000}
        )
        ```
    """
    data = {"completed": True, **extra}
    if message is not None:
        data["message"] = message
    if results is not None:
        data["results"] = results
    return sse_message(json.dumps(data), event="complete")


def raw_error(
    message: str,
    *,
    nodeId: Optional[str] = None,
    details: Optional[dict] = None,
    **extra: Any,
) -> str:
    """
    Create a raw SSE message for execution error.

    Args:
        message: Error message
        nodeId: Optional node ID where error occurred
        details: Optional error details dictionary
        **extra: Additional data to include

    Returns:
        SSE message string ready to yield from an async generator

    Example:
        ```python
        yield raw_error("Connection failed", nodeId="db_connect", details={"code": 500})
        ```
    """
    data = {"error": True, "message": message, **extra}
    if nodeId is not None:
        data["nodeId"] = nodeId
    if details is not None:
        data["details"] = details
    return sse_message(json.dumps(data), event="error")


# =============================================================================
# X6 JSON Format Helpers
# =============================================================================

def to_x6_node(
    node_id: str,
    x: float,
    y: float,
    *,
    width: int = 160,
    height: int = 60,
    label: Optional[str] = None,
    node_type: str = "default",
    inputs: int = 1,
    outputs: int = 1,
    data: Optional[dict] = None,
    **extra: Any,
) -> dict:
    """
    Convert node parameters to X6 JSON format.

    Args:
        node_id: Unique node identifier
        x: X position in pixels
        y: Y position in pixels
        width: Node width in pixels
        height: Node height in pixels
        label: Display label (defaults to node_id)
        node_type: Node type for styling
        inputs: Number of input ports
        outputs: Number of output ports
        data: Additional custom data
        **extra: Extra top-level X6 properties

    Returns:
        Dictionary in X6 node format

    Example:
        ```python
        node = to_x6_node("step1", 100, 200, label="Load Data", node_type="input")
        ```
    """
    node_data = {
        "label": label or node_id,
        "nodeType": node_type,
        "inputs": inputs,
        "outputs": outputs,
        **(data or {}),
    }
    return {
        "id": node_id,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "data": node_data,
        **extra,
    }


def to_x6_edge(
    source: str,
    target: str,
    *,
    source_port: str = "out_0",
    target_port: str = "in_0",
    label: Optional[str] = None,
    dashed: bool = False,
    data: Optional[dict] = None,
    **extra: Any,
) -> dict:
    """
    Convert edge parameters to X6 JSON format.

    Args:
        source: Source node ID
        target: Target node ID
        source_port: Source port name
        target_port: Target port name
        label: Optional edge label
        dashed: Whether to render as dashed line
        data: Additional custom data
        **extra: Extra top-level X6 properties

    Returns:
        Dictionary in X6 edge format

    Example:
        ```python
        edge = to_x6_edge("load", "process", label="next")
        ```
    """
    result = {
        "source": source,
        "target": target,
        "sourcePort": source_port,
        "targetPort": target_port,
        **extra,
    }
    if label is not None:
        result["label"] = label
    if dashed:
        result["dashed"] = True
    if data is not None:
        result["data"] = data
    return result


def from_x6_node(data: dict) -> dict:
    """
    Parse X6 node format to a normalized dictionary.

    Args:
        data: X6 node dictionary

    Returns:
        Normalized node dictionary with flat structure

    Example:
        ```python
        x6_data = {"id": "n1", "x": 100, "y": 200, "data": {"label": "Node 1"}}
        node = from_x6_node(x6_data)
        # {'id': 'n1', 'x': 100, 'y': 200, 'label': 'Node 1', ...}
        ```
    """
    node_data = data.get("data", {})
    return {
        "id": str(data.get("id", "")),
        "x": data.get("x", 0),
        "y": data.get("y", 0),
        "width": data.get("width", 160),
        "height": data.get("height", 60),
        "label": node_data.get("label", ""),
        "node_type": node_data.get("nodeType", "default"),
        "inputs": node_data.get("inputs", 1),
        "outputs": node_data.get("outputs", 1),
        "data": {k: v for k, v in node_data.items()
                 if k not in ("label", "nodeType", "inputs", "outputs")},
    }


def from_x6_edge(data: dict) -> dict:
    """
    Parse X6 edge format to a normalized dictionary.

    Args:
        data: X6 edge dictionary

    Returns:
        Normalized edge dictionary with flat structure

    Example:
        ```python
        x6_data = {"source": "n1", "target": "n2", "label": "next"}
        edge = from_x6_edge(x6_data)
        # {'source': 'n1', 'target': 'n2', 'label': 'next', ...}
        ```
    """
    # Handle label from both simple format and X6's array format
    label = data.get("label", "")
    if not label:
        labels = data.get("labels", [])
        if labels and len(labels) > 0:
            label_data = labels[0]
            if isinstance(label_data, dict):
                attrs = label_data.get("attrs", {})
                text = attrs.get("text", {})
                label = text.get("text", "")

    return {
        "source": str(data.get("source", "")),
        "target": str(data.get("target", "")),
        "source_port": data.get("sourcePort", "out_0"),
        "target_port": data.get("targetPort", "in_0"),
        "label": label,
        "dashed": data.get("dashed", False),
        "data": data.get("data", {}),
    }
