# Getting Started with Fastflow

This guide will help you create your first visual workflow editor with Fastflow and FastHTML.

## Installation

```bash
# Using uv (recommended)
uv add fastflow

# Or with pip
pip install fastflow
```

## Your First Flow Editor

Create a new file `app.py`:

```python
from fasthtml.common import *
from fastflow import FlowEditor, Node, Edge, fastflow_headers

# Create app with fastflow headers
app, rt = fast_app(hdrs=fastflow_headers())

@rt
def index():
    return Titled("My First Workflow",
        FlowEditor(
            # Create nodes (like LangGraph Builder style)
            Node("__start__", x=300, y=50, label="__start__", node_type="start",
                 inputs=0, outputs=1),
            Node("process", x=300, y=180, label="process", node_type="agent",
                 inputs=1, outputs=1),
            Node("__end__", x=300, y=310, label="__end__", node_type="end",
                 inputs=1, outputs=0),
            # Connect them with optional labels
            Edge(source="__start__", target="process"),
            Edge(source="process", target="__end__", label="done"),
        )
    )

serve()
```

Run it:

```bash
uv run python app.py
```

Open http://localhost:5001 to see your flow editor!

## Adding a Node Palette

Let users drag and drop nodes:

```python
from fastflow import NodePalette, PaletteItem

@rt
def index():
    return Titled("Workflow Builder",
        Div(
            # Sidebar with palette
            Aside(
                NodePalette(
                    PaletteItem("input", "Input", icon="📥", outputs=1),
                    PaletteItem("process", "Process", icon="⚙️", inputs=1, outputs=1),
                    PaletteItem("output", "Output", icon="📤", inputs=1),
                    target_editor="my-editor"
                ),
                style="width: 200px; padding: 16px;"
            ),
            # Main editor
            Main(
                FlowEditor(id="my-editor"),
                style="flex: 1;"
            ),
            style="display: flex; height: 100vh;"
        )
    )
```

## Handling Flow Changes

Receive events when the flow is modified:

```python
import json

@rt
def index():
    return Titled("Workflow",
        FlowEditor(
            id="editor",
            on_change="/flow/update",  # HTMX endpoint
        ),
        Div(id="status")
    )

@rt("/flow/update")
def post(event: str, data: str, flow: str):
    # Parse the event
    event_data = json.loads(data) if data else {}
    flow_data = json.loads(flow) if flow else {}

    # Log or process
    print(f"Event: {event}, Data: {event_data}")
    print(f"Flow has {len(flow_data.get('nodes', []))} nodes")

    # Return feedback to user
    return Div(f"Flow updated: {event}", id="status")
```

## Edge Labels and Dashed Lines

Add labels to edges (like LangGraph Builder's conditional edges):

```python
FlowEditor(
    Node("agent", x=300, y=100, label="agent", node_type="agent"),
    Node("tools", x=500, y=200, label="tools", node_type="tool"),
    Node("end", x=300, y=300, label="__end__", node_type="end"),
    # Solid edge with label
    Edge(source="agent", target="end", label="end"),
    # Dashed edge for conditional paths
    Edge(source="agent", target="tools", label="continue", dashed=True),
)
```

## Custom Node Types

Create reusable node types with the `@NodeType` decorator:

```python
from fastflow import NodeType

@NodeType("llm", inputs=1, outputs=1, icon="🧠")
def LLMNode(model: str = "gpt-4", temperature: float = 0.7):
    """An LLM processing node."""
    return Div(
        Div("🧠 LLM", cls="node-title"),
        Div(
            Label("Model"),
            Select(
                Option("gpt-4", selected=model == "gpt-4"),
                Option("gpt-3.5-turbo"),
                Option("claude-3"),
                name="model"
            ),
            Label("Temperature"),
            Input(type="range", min="0", max="2", step="0.1",
                  value=str(temperature), name="temperature"),
            cls="node-body"
        )
    )

# Use it
Node("my-llm", x=200, y=100, label="LLM", node_type="llm",
     data={"model": "gpt-4"})
```

## Working with Flow State

Use Python dataclasses to manipulate flows:

```python
from fastflow import Flow, NodeData, EdgeData

# Parse incoming flow JSON
@rt("/flow/save")
def post(flow: str):
    # Parse from X6 JSON format
    flow_obj = Flow.from_json(flow)

    # Access nodes
    for node in flow_obj.nodes:
        print(f"Node {node.id}: {node.node_type} at ({node.x}, {node.y})")

    # Access edges
    for edge in flow_obj.edges:
        print(f"Edge: {edge.source} -> {edge.target} ({edge.label})")

    # Execute in topological order
    for node in flow_obj.topological_sort():
        execute_node(node)

    # Save to database
    db.insert(name="My Flow", data=flow)

    return Div("Saved!")
```

## Next Steps

### Step-by-Step Tutorials

Follow our detailed tutorials to build different types of workflow editors:

| Tutorial | Description | Difficulty |
|----------|-------------|------------|
| [LangGraph-Style Workflow](tutorials/langgraph-workflow.md) | AI agent workflows like LangGraph Builder | Beginner |
| [ER Diagram Builder](tutorials/er-diagram.md) | Database entity-relationship diagrams | Intermediate |
| [Data Processing DAG](tutorials/data-processing-dag.md) | ETL pipelines with execution simulation | Intermediate |
| [AI/ML Training Pipeline](tutorials/ai-model-dag.md) | ML workflows with conditional branches | Intermediate |
| [Agent Orchestration](tutorials/agent-flow.md) | Complex agent flows with tools | Advanced |
| [Traditional Flowchart](tutorials/flowchart.md) | Classic flowcharts with standard shapes | Beginner |

### More Resources

- Check out the [examples](../examples/) directory for complete applications
- Read the [Architecture Guide](how_it_works/architecture.md) to understand internals
- See the [API Reference](../README.md#api-reference) for all components
