"""
Node type registration and management.

Provides the @NodeType decorator for registering custom node types
that can be used in FlowEditor.
"""

from typing import Callable, Optional, Any
from dataclasses import dataclass, field
from functools import wraps


@dataclass
class NodeTypeInfo:
    """Information about a registered node type."""
    name: str
    func: Callable
    inputs: int = 0
    outputs: int = 0
    category: str = "default"
    icon: Optional[str] = None
    color: Optional[str] = None
    description: str = ""


# Global registry of node types
_node_type_registry: dict[str, NodeTypeInfo] = {}


def NodeType(
    name: str,
    inputs: int = 0,
    outputs: int = 0,
    category: str = "default",
    icon: Optional[str] = None,
    color: Optional[str] = None,
):
    """
    Decorator to register a custom node type.

    The decorated function should return an FT component that renders
    the node's content. It can accept keyword arguments that will be
    populated from the node's `data` dictionary.

    Args:
        name: Unique identifier for the node type
        inputs: Default number of input handles
        outputs: Default number of output handles
        category: Category for grouping in palette
        icon: Icon name (for palette display)
        color: Theme color for the node

    Example:
        ```python
        @NodeType("llm", inputs=1, outputs=1, icon="brain", color="purple")
        def LLMNode(model: str = "gpt-4", temperature: float = 0.7):
            return Div(
                Div("LLM", cls="node-title"),
                Label("Model:"),
                Select(Option(model), df_model=True),
                cls="llm-node"
            )
        ```
    """
    def decorator(func: Callable) -> Callable:
        # Extract description from docstring
        description = func.__doc__ or ""

        # Register the node type
        info = NodeTypeInfo(
            name=name,
            func=func,
            inputs=inputs,
            outputs=outputs,
            category=category,
            icon=icon,
            color=color,
            description=description.strip(),
        )
        _node_type_registry[name] = info

        @wraps(func)
        def wrapper(**kwargs):
            return func(**kwargs)

        # Attach metadata to the wrapper
        wrapper._node_type_info = info
        return wrapper

    return decorator


def get_node_types() -> dict[str, NodeTypeInfo]:
    """Get all registered node types."""
    return _node_type_registry.copy()


def get_node_type(name: str) -> Optional[NodeTypeInfo]:
    """Get a specific node type by name."""
    return _node_type_registry.get(name)


def render_node_html(node_type: str, data: Optional[dict] = None) -> str:
    """
    Render HTML for a node type with given data.

    Args:
        node_type: The registered node type name
        data: Data dictionary to pass to the node function

    Returns:
        HTML string for the node content
    """
    from fasthtml.common import to_xml

    info = get_node_type(node_type)
    if not info:
        return f"<div class='node-error'>Unknown type: {node_type}</div>"

    data = data or {}
    try:
        ft_component = info.func(**data)
        return to_xml(ft_component)
    except Exception as e:
        return f"<div class='node-error'>Error: {e}</div>"


def get_node_type_categories() -> dict[str, list[NodeTypeInfo]]:
    """Get node types grouped by category."""
    categories: dict[str, list[NodeTypeInfo]] = {}
    for info in _node_type_registry.values():
        if info.category not in categories:
            categories[info.category] = []
        categories[info.category].append(info)
    return categories


def clear_node_types() -> None:
    """Clear all registered node types (useful for testing)."""
    _node_type_registry.clear()


# Built-in basic node types
def _register_builtin_types():
    """Register basic built-in node types."""
    from fasthtml.common import Div

    @NodeType("default", inputs=1, outputs=1, category="basic")
    def DefaultNode(label: str = "Node"):
        """A basic default node."""
        return Div(
            Div(label, cls="node-title"),
            Div(cls="node-body"),
            cls="default-node"
        )


# Auto-register built-in types on import
_register_builtin_types()
