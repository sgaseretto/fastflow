"""
Layer 2: Type dispatch foundation for fastflow nodes.

This module provides typed node classes and type-dispatched operations,
enabling Julia-like multiple dispatch in Python via fastcore.

Key features:
- Typed node classes (StartNode, EndNode, AgentNode, ToolNode, etc.)
- Type-dispatched operations: render, execute, validate, to_x6, can_connect
- Two-parameter dispatch for edge validation

Example:
    ```python
    from fastflow.types import AgentNode, render, execute, can_connect

    # Create a typed node
    agent = AgentNode(id="agent1", model="gpt-4", temperature=0.7)

    # Type dispatch automatically routes to correct implementation
    html = render(agent)  # Uses AgentNode-specific renderer

    # Two-parameter dispatch for edge validation
    start = StartNode(id="start")
    allowed, reason = can_connect(start, agent)  # True, ""
    ```
"""

from plum import dispatch
from fastcore.basics import store_attr

# Alias for consistency with fastcore naming
typedispatch = dispatch
from dataclasses import dataclass, field
from typing import Any, Optional
from abc import ABC
from fasthtml.common import Div, Span, to_xml

from .core import to_x6_node, to_x6_edge

__all__ = [
    # Base class
    "FlowNode",
    # Node types
    "StartNode",
    "EndNode",
    "AgentNode",
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
    # Dispatched operations
    "render",
    "execute",
    "validate",
    "node_to_x6",
    "node_from_x6",
    "can_connect",
    "get_node_style",
    # Utilities
    "NODE_TYPE_MAP",
    "register_node_type",
]


# =============================================================================
# Base Node Class
# =============================================================================

@dataclass
class FlowNode(ABC):
    """
    Base class for all flow nodes. Enables type dispatch.

    All node types inherit from this class, allowing type-dispatched
    operations like `render(node)` to route to the correct implementation.

    Attributes:
        id: Unique identifier for the node
        x: X position in pixels
        y: Y position in pixels
        width: Node width in pixels
        height: Node height in pixels
        label: Display label
        data: Additional custom data
    """
    id: str
    x: float = 0
    y: float = 0
    width: int = 160
    height: int = 60
    label: str = ""
    data: dict = field(default_factory=dict)

    @property
    def node_type(self) -> str:
        """Get the node type string from the class name."""
        name = self.__class__.__name__
        if name.endswith("Node"):
            name = name[:-4]
        return name.lower()


# =============================================================================
# LangGraph-style Nodes
# =============================================================================

@dataclass
class StartNode(FlowNode):
    """Start node - entry point of flow. Has no inputs, one output."""
    label: str = "__start__"
    inputs: int = 0
    outputs: int = 1


@dataclass
class EndNode(FlowNode):
    """End node - exit point of flow. Has one input, no outputs."""
    label: str = "__end__"
    inputs: int = 1
    outputs: int = 0


@dataclass
class AgentNode(FlowNode):
    """
    Agent node for LLM/AI agent processing.

    Represents an autonomous agent that can reason, plan, and take actions.

    Attributes:
        model: Model identifier (e.g., "gpt-4", "claude-3")
        temperature: Sampling temperature (0-2)
        system_prompt: Optional system prompt for the agent
    """
    label: str = "Agent"
    model: str = "gpt-4"
    temperature: float = 0.7
    system_prompt: str = ""
    inputs: int = 1
    outputs: int = 1


@dataclass
class ToolNode(FlowNode):
    """
    Tool node for function/tool calls.

    Represents a tool that can be called by an agent.

    Attributes:
        tool_name: Name of the tool
        tool_description: Description of what the tool does
    """
    label: str = "Tool"
    tool_name: str = ""
    tool_description: str = ""
    inputs: int = 1
    outputs: int = 1


@dataclass
class LLMNode(FlowNode):
    """
    LLM node for direct language model calls.

    Unlike AgentNode, this is a simple one-shot LLM call without
    agent reasoning loops.

    Attributes:
        model: Model identifier
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
    """
    label: str = "LLM"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1024
    inputs: int = 1
    outputs: int = 1


@dataclass
class ConditionNode(FlowNode):
    """
    Condition node for branching logic.

    Routes to different outputs based on a condition.

    Attributes:
        condition: The condition expression to evaluate
    """
    label: str = "Condition"
    condition: str = ""
    inputs: int = 1
    outputs: int = 2  # True and False branches


# =============================================================================
# Data Processing Nodes
# =============================================================================

@dataclass
class InputNode(FlowNode):
    """Input node - data entry point."""
    label: str = "Input"
    source: str = ""  # e.g., "file", "api", "database"
    inputs: int = 0
    outputs: int = 1


@dataclass
class OutputNode(FlowNode):
    """Output node - data exit point."""
    label: str = "Output"
    destination: str = ""  # e.g., "file", "api", "database"
    inputs: int = 1
    outputs: int = 0


@dataclass
class FilterNode(FlowNode):
    """Filter node for data filtering."""
    label: str = "Filter"
    condition: str = ""
    inputs: int = 1
    outputs: int = 1


@dataclass
class JoinNode(FlowNode):
    """Join node for combining data streams."""
    label: str = "Join"
    join_type: str = "inner"  # inner, outer, left, right
    inputs: int = 2
    outputs: int = 1


@dataclass
class TransformNode(FlowNode):
    """Transform node for data transformation."""
    label: str = "Transform"
    transform_type: str = ""
    inputs: int = 1
    outputs: int = 1


# =============================================================================
# Flowchart Nodes
# =============================================================================

@dataclass
class ProcessNode(FlowNode):
    """Process node - standard flowchart process step."""
    label: str = "Process"
    description: str = ""
    inputs: int = 1
    outputs: int = 1


@dataclass
class DecisionNode(FlowNode):
    """Decision node - flowchart decision diamond."""
    label: str = "Decision"
    question: str = ""
    inputs: int = 1
    outputs: int = 2  # Yes and No branches


# =============================================================================
# Code/Execution Nodes
# =============================================================================

@dataclass
class CodeNode(FlowNode):
    """Code node for custom code execution."""
    label: str = "Code"
    language: str = "python"
    code: str = ""
    inputs: int = 1
    outputs: int = 1


# =============================================================================
# Node Type Registry
# =============================================================================

NODE_TYPE_MAP: dict[str, type[FlowNode]] = {
    "start": StartNode,
    "end": EndNode,
    "agent": AgentNode,
    "tool": ToolNode,
    "llm": LLMNode,
    "condition": ConditionNode,
    "input": InputNode,
    "output": OutputNode,
    "filter": FilterNode,
    "join": JoinNode,
    "transform": TransformNode,
    "process": ProcessNode,
    "decision": DecisionNode,
    "code": CodeNode,
}


def register_node_type(name: str, cls: type[FlowNode]) -> None:
    """
    Register a custom node type.

    Args:
        name: Type name (lowercase, e.g., "custom")
        cls: Node class that inherits from FlowNode

    Example:
        ```python
        @dataclass
        class MyCustomNode(FlowNode):
            custom_field: str = ""

        register_node_type("custom", MyCustomNode)
        ```
    """
    NODE_TYPE_MAP[name.lower()] = cls


# =============================================================================
# Node Styles (for rendering)
# =============================================================================

NODE_STYLES: dict[str, dict] = {
    # LangGraph-style nodes
    "start": {"fill": "#1e293b", "stroke": "#1e293b", "textColor": "#fff"},
    "end": {"fill": "#1e293b", "stroke": "#1e293b", "textColor": "#fff"},
    "agent": {"fill": "#dbeafe", "stroke": "#60a5fa", "textColor": "#1e40af"},
    "tool": {"fill": "#fce7f3", "stroke": "#f472b6", "textColor": "#9d174d"},
    "llm": {"fill": "#f3e8ff", "stroke": "#c084fc", "textColor": "#6b21a8"},
    "condition": {"fill": "#fef3c7", "stroke": "#fbbf24", "textColor": "#92400e"},
    # Data processing
    "input": {"fill": "#dcfce7", "stroke": "#4ade80", "textColor": "#166534"},
    "output": {"fill": "#fee2e2", "stroke": "#f87171", "textColor": "#991b1b"},
    "filter": {"fill": "#e0f2fe", "stroke": "#38bdf8", "textColor": "#0369a1"},
    "join": {"fill": "#fef3c7", "stroke": "#fbbf24", "textColor": "#92400e"},
    "transform": {"fill": "#e0f2fe", "stroke": "#38bdf8", "textColor": "#0369a1"},
    # Flowchart
    "process": {"fill": "#eff4ff", "stroke": "#5f95ff", "textColor": "#262626"},
    "decision": {"fill": "#eff4ff", "stroke": "#5f95ff", "textColor": "#262626"},
    # Code
    "code": {"fill": "#e6fffb", "stroke": "#08979c", "textColor": "#08979c"},
    # Default
    "default": {"fill": "#f1f5f9", "stroke": "#94a3b8", "textColor": "#334155"},
}


# =============================================================================
# Type-Dispatched Operations
# =============================================================================

@dispatch
def render(node: FlowNode) -> str:
    """
    Render a node to HTML string.

    This is type-dispatched, so each node type can have its own
    rendering implementation.

    Args:
        node: The node to render

    Returns:
        HTML string representation

    Example:
        ```python
        agent = AgentNode(id="agent1", model="gpt-4")
        html = render(agent)  # "<div class='node-agent'>...</div>"
        ```
    """
    style = NODE_STYLES.get(node.node_type, NODE_STYLES["default"])
    return to_xml(Div(
        Span(node.label, cls="node-label"),
        cls=f"node-{node.node_type}",
        style=f"color: {style['textColor']}"
    ))


@dispatch
def render(node: StartNode) -> str:
    return to_xml(Div(
        Span(node.label, cls="node-label"),
        cls="node-start",
        style="color: #fff; text-align: center;"
    ))


@dispatch
def render(node: EndNode) -> str:
    return to_xml(Div(
        Span(node.label, cls="node-label"),
        cls="node-end",
        style="color: #fff; text-align: center;"
    ))


@dispatch
def render(node: AgentNode) -> str:
    return to_xml(Div(
        Div(node.label, cls="node-title"),
        Div(f"Model: {node.model}", cls="node-subtitle", style="font-size: 10px; opacity: 0.8;"),
        cls="node-agent"
    ))


@dispatch
def render(node: ToolNode) -> str:
    return to_xml(Div(
        Div(node.label, cls="node-title"),
        Div(node.tool_name or "No tool", cls="node-subtitle", style="font-size: 10px; opacity: 0.8;"),
        cls="node-tool"
    ))


@dispatch
def render(node: LLMNode) -> str:
    return to_xml(Div(
        Div(node.label, cls="node-title"),
        Div(f"{node.model}", cls="node-subtitle", style="font-size: 10px; opacity: 0.8;"),
        cls="node-llm"
    ))


@dispatch
def render(node: ConditionNode) -> str:
    return to_xml(Div(
        Div(node.label, cls="node-title"),
        Div(node.condition or "?", cls="node-subtitle", style="font-size: 10px; opacity: 0.8;"),
        cls="node-condition"
    ))


@dispatch
def render(node: CodeNode) -> str:
    return to_xml(Div(
        Div(node.label, cls="node-title"),
        Div(f"({node.language})", cls="node-subtitle", style="font-size: 10px; opacity: 0.8;"),
        cls="node-code"
    ))


# =============================================================================
# Execute Operation
# =============================================================================

@dispatch
async def execute(node: FlowNode, context: dict, inputs: dict) -> Any:
    """
    Execute node logic.

    This is type-dispatched, so each node type can have its own
    execution implementation.

    Args:
        node: The node to execute
        context: Shared execution context
        inputs: Results from upstream nodes

    Returns:
        Node execution result

    Example:
        ```python
        result = await execute(agent_node, context={"llm": my_llm}, inputs={})
        ```
    """
    # Default implementation - just pass through
    return {"status": "completed", "node_id": node.id}


@dispatch
async def execute(node: StartNode, context: dict, inputs: dict) -> Any:
    """Start node just passes through any initial data."""
    return context.get("initial_data", {})


@dispatch
async def execute(node: EndNode, context: dict, inputs: dict) -> Any:
    """End node collects all inputs."""
    return {"final_results": inputs}


@dispatch
async def execute(node: AgentNode, context: dict, inputs: dict) -> Any:
    """
    Execute agent node.

    Looks for 'llm' or 'agent' in context to perform actual execution.
    """
    llm = context.get("llm") or context.get("agent")
    if llm and hasattr(llm, "__call__"):
        return await llm(
            inputs,
            model=node.model,
            temperature=node.temperature,
            system_prompt=node.system_prompt
        )
    # Placeholder if no LLM configured
    return {"status": "no_llm_configured", "node_id": node.id, "inputs": inputs}


@dispatch
async def execute(node: ToolNode, context: dict, inputs: dict) -> Any:
    """
    Execute tool node.

    Looks for the tool by name in context.
    """
    tools = context.get("tools", {})
    tool = tools.get(node.tool_name)
    if tool and callable(tool):
        return await tool(inputs) if callable(tool) else tool
    return {"status": "tool_not_found", "tool_name": node.tool_name}


@dispatch
async def execute(node: CodeNode, context: dict, inputs: dict) -> Any:
    """
    Execute code node.

    WARNING: Only execute code from trusted sources.
    """
    if not node.code:
        return {"status": "no_code", "node_id": node.id}

    # Create execution namespace
    namespace = {"inputs": inputs, "context": context, "result": None}

    if node.language == "python":
        exec(node.code, namespace)
        return namespace.get("result", {"status": "executed"})

    return {"status": "unsupported_language", "language": node.language}


# =============================================================================
# Validate Operation
# =============================================================================

@dispatch
def validate(node: FlowNode) -> list[str]:
    """
    Validate node configuration.

    Returns list of validation error messages (empty if valid).

    Args:
        node: The node to validate

    Returns:
        List of error messages

    Example:
        ```python
        errors = validate(agent)
        if errors:
            print("Validation failed:", errors)
        ```
    """
    errors = []
    if not node.id:
        errors.append("Node must have an id")
    return errors


@dispatch
def validate(node: AgentNode) -> list[str]:
    errors = []
    if not node.id:
        errors.append("Node must have an id")
    if not node.model:
        errors.append("AgentNode must specify a model")
    if not 0 <= node.temperature <= 2:
        errors.append("Temperature must be between 0 and 2")
    return errors


@dispatch
def validate(node: ToolNode) -> list[str]:
    errors = []
    if not node.id:
        errors.append("Node must have an id")
    if not node.tool_name:
        errors.append("ToolNode must specify a tool_name")
    return errors


@dispatch
def validate(node: CodeNode) -> list[str]:
    errors = []
    if not node.id:
        errors.append("Node must have an id")
    if node.language not in ("python", "javascript"):
        errors.append(f"Unsupported language: {node.language}")
    return errors


# =============================================================================
# Serialization Operations
# =============================================================================

@dispatch
def node_to_x6(node: FlowNode) -> dict:
    """
    Serialize node to X6 JSON format.

    Args:
        node: The node to serialize

    Returns:
        Dictionary in X6 format
    """
    # Get all fields that aren't in base FlowNode
    extra_data = {}
    base_fields = {"id", "x", "y", "width", "height", "label", "data"}
    for key, value in node.__dict__.items():
        if key not in base_fields and not key.startswith("_"):
            extra_data[key] = value

    return to_x6_node(
        node_id=node.id,
        x=node.x,
        y=node.y,
        width=node.width,
        height=node.height,
        label=node.label or node.id,
        node_type=node.node_type,
        inputs=getattr(node, "inputs", 1),
        outputs=getattr(node, "outputs", 1),
        data={**node.data, **extra_data},
    )


def node_from_x6(data: dict) -> FlowNode:
    """
    Deserialize node from X6 JSON format.

    Args:
        data: X6 node dictionary

    Returns:
        Appropriate FlowNode subclass instance
    """
    node_data = data.get("data", {})
    node_type = node_data.get("nodeType", "default")

    # Get the appropriate class
    cls = NODE_TYPE_MAP.get(node_type, FlowNode)

    # Build kwargs for the class
    kwargs = {
        "id": str(data.get("id", "")),
        "x": data.get("x", 0),
        "y": data.get("y", 0),
        "width": data.get("width", 160),
        "height": data.get("height", 60),
        "label": node_data.get("label", ""),
    }

    # Add type-specific fields from data
    type_specific_fields = {k: v for k, v in node_data.items()
                           if k not in ("label", "nodeType", "inputs", "outputs")}
    kwargs["data"] = type_specific_fields

    # Try to set known fields on the node class
    if cls != FlowNode:
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(cls)}
        for key, value in type_specific_fields.items():
            if key in field_names:
                kwargs[key] = value
                # Remove from data dict since it's a real field
                kwargs["data"] = {k: v for k, v in kwargs["data"].items() if k != key}

    return cls(**kwargs)


# =============================================================================
# Connection Validation (Two-Parameter Dispatch)
# =============================================================================

@dispatch
def can_connect(source: FlowNode, target: FlowNode) -> tuple[bool, str]:
    """
    Check if two nodes can be connected.

    This is two-parameter type dispatch - behavior depends on both
    source and target types.

    Args:
        source: Source node
        target: Target node

    Returns:
        Tuple of (allowed: bool, reason: str)

    Example:
        ```python
        allowed, reason = can_connect(start_node, agent_node)
        if not allowed:
            print(f"Cannot connect: {reason}")
        ```
    """
    return True, ""


@dispatch
def can_connect(source: StartNode, target: EndNode) -> tuple[bool, str]:
    """Cannot connect start directly to end."""
    return False, "Cannot connect start directly to end"


@dispatch
def can_connect(source: EndNode, target: FlowNode) -> tuple[bool, str]:
    """End node cannot have outgoing connections."""
    return False, "End node cannot have outgoing connections"


@dispatch
def can_connect(source: FlowNode, target: StartNode) -> tuple[bool, str]:
    """Start node cannot have incoming connections."""
    return False, "Start node cannot have incoming connections"


@dispatch
def can_connect(source: OutputNode, target: FlowNode) -> tuple[bool, str]:
    """Output node cannot have outgoing connections."""
    return False, "Output node cannot have outgoing connections"


@dispatch
def can_connect(source: FlowNode, target: InputNode) -> tuple[bool, str]:
    """Input node cannot have incoming connections."""
    return False, "Input node cannot have incoming connections"


# =============================================================================
# Style Helper
# =============================================================================

@dispatch
def get_node_style(node: FlowNode) -> dict:
    """
    Get the style dictionary for a node.

    Args:
        node: The node to get style for

    Returns:
        Style dictionary with fill, stroke, textColor
    """
    return NODE_STYLES.get(node.node_type, NODE_STYLES["default"])
