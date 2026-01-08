# Fastflow

**Build visual workflow editors with Python and FastHTML**

Fastflow is a Python library that wraps [AntV X6](https://x6.antv.antgroup.com/en) for use with [FastHTML](https://fastht.ml/), enabling you to create node-based visual editors like LangGraph Builder, Open Agent Builder, and data pipeline designers.

## Features

- **FastHTML-style API**: Use familiar FT components like `FlowEditor()`, `Node()`, `Edge()`
- **Python-Based Execution**: Run workflows entirely in Python with SSE for real-time visual updates
- **Type Dispatch System**: Define typed nodes with multiple-dispatch operations (render, execute, validate)
- **Two-Way Callbacks**: fastai-style callbacks that can read AND modify execution state
- **Layered API**: From raw primitives to convenience functions - use the right level of abstraction
- **Multiple Workflow Types**: LangGraph agents, ER diagrams, data pipelines, flowcharts
- **Specialized Components**: `TableNode`, `DAGNode`, `AgentNode`, `FlowchartNode`
- **Rich Node Styling**: 25+ built-in node types with icons and status indicators
- **Enhanced Edges**: Custom routers, connectors, relationship labels (1:N, N:N)
- **Drag-and-Drop**: Built-in `NodePalette` with groupable items (`PaletteGroup`)
- **HTMX Integration**: Automatic event handling via HTMX for server-side logic
- **Interactive Editing**: Double-click to rename, right-click context menus, keyboard shortcuts
- **Extensible via @patch**: Add methods to existing classes without subclassing
- **Serialization**: Import/export workflows as JSON

## Installation

```bash
# Using uv (recommended)
uv add fastflow

# Or with pip
pip install fastflow
```

## Quick Start

```python
from fasthtml.common import *
from fastflow import FlowEditor, Node, Edge, NodePalette, PaletteItem, fastflow_headers

# Create app with fastflow headers
app, rt = fast_app(hdrs=fastflow_headers())

@rt
def index():
    return Titled("My Workflow",
        FlowEditor(
            # Define nodes (LangGraph Builder style)
            Node("__start__", x=300, y=50, label="__start__", node_type="start",
                 inputs=0, outputs=1),
            Node("agent", x=300, y=180, label="agent", node_type="agent",
                 inputs=1, outputs=1),
            Node("tools", x=500, y=300, label="tools", node_type="tool",
                 inputs=1, outputs=1),
            Node("__end__", x=300, y=450, label="__end__", node_type="end",
                 inputs=1, outputs=0),
            # Define connections with labels
            Edge(source="__start__", target="agent"),
            Edge(source="agent", target="tools", label="continue", dashed=True),
            Edge(source="agent", target="__end__", label="end"),
            Edge(source="tools", target="agent"),
            # Configuration
            id="my-flow",
            on_change="/flow/changed",
        )
    )

@rt("/flow/changed")
def post(flow: str):
    # Handle flow changes
    print(f"Flow updated: {flow}")
    return ""

serve()
```

## Node Palette

Add a drag-and-drop palette for creating nodes:

```python
NodePalette(
    PaletteItem("input", "Input", icon="📥", outputs=1),
    PaletteItem("llm", "LLM", icon="🧠", inputs=1, outputs=1),
    PaletteItem("output", "Output", icon="📤", inputs=1),
    target_editor="my-flow"  # ID of the FlowEditor
)

# With collapsible groups
NodePalette(
    PaletteGroup(
        PaletteItem("input", "INPUT", inputs=0, outputs=1),
        PaletteItem("output", "OUTPUT", inputs=1, outputs=0),
        title="I/O"
    ),
    PaletteGroup(
        PaletteItem("filter", "FILTER", inputs=1, outputs=1),
        PaletteItem("join", "JOIN", inputs=2, outputs=1),
        title="Transform"
    ),
    target_editor="my-flow"
)
```

## Python-Based Execution with SSE

Run workflow execution entirely in Python with real-time visual updates using Server-Sent Events:

```python
from fasthtml.common import *
from fastflow import (
    FlowEditor, Node, Edge, fastflow_headers,
    FlowExecutor, ExecutionStep,
)

app, rt = fast_app(hdrs=fastflow_headers())

# Define execution pipeline with dependencies
executor = FlowExecutor(
    graph_id="my-pipeline",
    steps=[
        ExecutionStep("load", duration=1.0),
        ExecutionStep("process", depends_on=["load"], duration=0.5),
        ExecutionStep("save", depends_on=["process"], duration=0.5),
    ]
)

@rt
def index():
    return Titled("Pipeline",
        FlowEditor(
            Node("load", x=100, y=100, label="Load", node_type="input"),
            Node("process", x=100, y=200, label="Process", node_type="transform"),
            Node("save", x=100, y=300, label="Save", node_type="output"),
            Edge(source="load", target="process"),
            Edge(source="process", target="save"),
            id="my-pipeline",
        ),
        Button("Run",
            onclick="window.fastflow.connectExecution('my-pipeline', '/execute')"
        ),
    )

@rt("/execute")
async def execute():
    """SSE endpoint - all execution logic is in Python!"""
    return EventStream(executor.run())

serve()
```

### Custom Handlers

Add real Python logic to each step:

```python
async def load_data(context, inputs):
    import pandas as pd
    df = pd.read_csv(context["path"])
    return {"data": df}

async def process_data(context, inputs):
    df = inputs["load"]["data"]
    return {"processed": df.dropna()}

executor = FlowExecutor(
    graph_id="my-pipeline",
    steps=[
        ExecutionStep("load", handler=load_data),
        ExecutionStep("process", depends_on=["load"], handler=process_data),
        ExecutionStep("save", depends_on=["process"]),
    ]
)

@rt("/execute")
async def execute():
    return EventStream(executor.run_with_results(context={"path": "data.csv"}))
```

See the [Python Execution Guide](docs/how_it_works/python_execution.md) for more details.

## Callback System

Add callbacks to FlowExecutor for logging, timing, retries, and custom behavior:

```python
from fastflow import FlowExecutor, ExecutionStep
from fastflow.callbacks import SSECallback, LoggingCallback, TimingCallback, RetryCallback

executor = FlowExecutor(
    graph_id="my-pipeline",
    steps=[
        ExecutionStep("load", handler=load_data),
        ExecutionStep("process", depends_on=["load"], handler=process_data),
        ExecutionStep("save", depends_on=["process"], handler=save_data),
    ],
    callbacks=[
        SSECallback(),         # Real-time browser updates
        LoggingCallback(),     # Structured logging
        TimingCallback(),      # Performance metrics
        RetryCallback(max_retries=3),  # Auto-retry on failure
    ]
)

@rt("/execute")
async def execute():
    return EventStream(executor.run(context={"path": "data.csv"}))
```

### Custom Callbacks

Create your own callbacks by subclassing `FlowCallback`:

```python
from fastflow.callbacks import FlowCallback, FlowState, SkipNodeException

class ConditionalCallback(FlowCallback):
    def before_node(self, state: FlowState):
        # Skip certain nodes based on context
        if state.current_step.node_id == "optional":
            if not state.context.get("run_optional"):
                raise SkipNodeException("Skipping optional step")

    def after_node(self, state: FlowState):
        # Modify results
        node_id = state.current_step.node_id
        state.results[node_id]["processed_at"] = time.time()
```

## Typed Nodes (Advanced)

Define custom node types with type dispatch for render, execute, and validate operations:

```python
from dataclasses import dataclass
from fastflow.types import FlowNode, render, execute, validate, register_node_type

@dataclass
class MyAgentNode(FlowNode):
    node_type: str = "my-agent"
    model: str = "gpt-4"
    temperature: float = 0.7

# Register for string-based lookup
register_node_type("my-agent", MyAgentNode)

# Type-dispatched render
@render.register
def _(node: MyAgentNode):
    return Div(f"🤖 {node.model} (temp={node.temperature})")

# Type-dispatched execute
@execute.register
async def _(node: MyAgentNode, context: dict, inputs: dict):
    return await call_llm(node.model, node.temperature, inputs)

# Type-dispatched validation
@validate.register
def _(node: MyAgentNode) -> list[str]:
    errors = []
    if node.temperature < 0 or node.temperature > 2:
        errors.append("Temperature must be between 0 and 2")
    return errors
```

## Specialized Components

### ER Diagram Tables

```python
from fastflow import TableNode, Edge

TableNode("users", x=100, y=100, label="users", columns=[
    {"name": "id", "type": "int", "pk": True},
    {"name": "name", "type": "varchar(255)"},
    {"name": "email", "type": "varchar(255)"},
])

TableNode("orders", x=400, y=100, label="orders", columns=[
    {"name": "id", "type": "int", "pk": True},
    {"name": "user_id", "type": "int", "fk": "users.id"},
])

# ER relationship edge
Edge(source="users", target="orders", relationship="1:N", router="er")
```

### Data Processing DAG

```python
from fastflow import DAGNode

DAGNode("input1", x=50, y=100, label="INPUT", node_type="input", status="success")
DAGNode("filter1", x=200, y=100, label="FILTER", node_type="filter", status="running")
DAGNode("join1", x=350, y=150, label="JOIN", node_type="join", inputs=2, outputs=1)
DAGNode("output1", x=500, y=150, label="OUTPUT", node_type="output")
```

### Agent Workflow

```python
from fastflow import AgentNode

AgentNode("llm1", x=200, y=100, label="LLM Router", node_type="llm")
AgentNode("code1", x=150, y=200, label="Code Exec", node_type="code")
AgentNode("kb1", x=350, y=200, label="Query KB", node_type="kb")
AgentNode("db1", x=250, y=300, label="Save to DB", node_type="db")
```

### Flowchart

```python
from fastflow import FlowchartNode

FlowchartNode("start", x=100, y=50, label="Start", node_type="start")
FlowchartNode("process", x=100, y=150, label="Process", node_type="process")
FlowchartNode("decision", x=100, y=250, label="Valid?", node_type="decision")
FlowchartNode("end", x=100, y=350, label="End", node_type="end")
```

## Node Types

Fastflow includes 25+ built-in node types:

| Category | Types |
|----------|-------|
| **LangGraph** | `start`, `end`, `agent`, `tool`, `llm`, `condition` |
| **Data Processing** | `input`, `output`, `filter`, `join`, `union`, `agg`, `transform` |
| **Agent Flow** | `code`, `branch`, `loop`, `kb`, `mcp`, `db` |
| **Flowchart** | `process`, `decision`, `data`, `connector` |
| **ER Diagram** | `table` |

## API Reference

### `FlowEditor`

Main container component for the flow editor.

```python
FlowEditor(
    *children,                    # Node and Edge components
    id: str = "flowgraph",        # Container ID
    grid: bool = True,            # Show background grid
    on_change: str = None,        # HTMX endpoint for changes
    on_node_select: str = None,   # HTMX endpoint for selection
    height: str = "600px",        # Container height
)
```

### `Node`

Define a node in the flow.

```python
Node(
    name: str,                    # Unique identifier
    x: int = 0,                   # X position
    y: int = 0,                   # Y position
    label: str = None,            # Display label (defaults to name)
    node_type: str = "default",   # Node style (see Node Types table)
    inputs: int = 1,              # Number of input ports
    outputs: int = 1,             # Number of output ports
    data: dict = None,            # Node configuration data
    # Enhanced features
    shape: str = "rect",          # Shape: 'rect', 'circle', 'polygon', 'diamond'
    icon: str = None,             # Icon emoji displayed in label
    status: str = None,           # Status: 'success', 'error', 'running' (colored border)
    port_positions: dict = None,  # {'inputs': 'top'|'left', 'outputs': 'bottom'|'right'}
    fill: str = None,             # Custom fill color
    stroke: str = None,           # Custom stroke color
    text_color: str = None,       # Custom text color
)
```

### `Edge`

Define a connection between nodes.

```python
Edge(
    source: str,                  # Source node ID
    target: str,                  # Target node ID
    label: str = None,            # Optional edge label (pill badge style)
    dashed: bool = False,         # Use dashed line (for conditional edges)
    # Enhanced features
    connector: str = "rounded",   # 'smooth', 'rounded', 'manhattan', 'normal'
    router: str = "manhattan",    # 'manhattan', 'orth', 'metro', 'er', 'normal'
    color: str = None,            # Custom line color
    animated: bool = False,       # Animated dashed line (for running state)
    marker: str = "block",        # Arrow: 'block', 'classic', 'diamond', 'circle'
    relationship: str = None,     # ER relationship: '1:1', '1:N', 'N:N'
)
```

## State Management

Fastflow provides dataclasses for working with flow state:

```python
from fastflow import Flow, NodeData, EdgeData

# Parse flow from X6 JSON
flow = Flow.from_json(flow_json)

# Access nodes and edges
for node in flow.nodes:
    print(f"Node: {node.id} ({node.node_type}) at ({node.x}, {node.y})")

for edge in flow.edges:
    print(f"Edge: {edge.source} -> {edge.target} ({edge.label})")

# Topological sort for execution
for node in flow.topological_sort():
    execute_node(node)

# Export back to JSON
json_str = flow.to_json()
```

## Interactive Editing

Fastflow supports rich interactive editing out of the box:

### Keyboard Shortcuts
- **Delete / Backspace**: Delete selected nodes or edges
- **Ctrl + Mouse Wheel**: Zoom in/out
- **Click + Drag**: Pan the canvas

### Mouse Interactions
- **Double-click node**: Edit node label inline
- **Double-click edge**: Add or edit edge label
- **Right-click node**: Context menu (Rename, Delete)
- **Right-click edge**: Context menu (Edit Label, Make Solid/Dashed, Delete)
- **Drag from port**: Create new connections between nodes

## JavaScript API

Access the X6 graph from JavaScript:

```javascript
// Export flow data
const data = window.fastflow.exportFlow('my-flow');

// Import flow data
window.fastflow.importFlow('my-flow', data);

// Add nodes programmatically
window.fastflow.addNode('my-flow', {
    name: 'new-node',
    label: 'New Node',
    nodeType: 'agent',
    x: 200,
    y: 100,
    inputs: 1,
    outputs: 1,
});

// Rename a node
window.fastflow.renameNode('my-flow', 'node-id', 'New Label');

// Edit edge labels
window.fastflow.setEdgeLabel('my-flow', 'edge-id', 'my label');
window.fastflow.setEdgeLabel('my-flow', 'edge-id', '');  // Remove label

// Toggle dashed/solid edge style
window.fastflow.setEdgeDashed('my-flow', 'edge-id', true);   // Dashed
window.fastflow.setEdgeDashed('my-flow', 'edge-id', false);  // Solid

// Delete operations
window.fastflow.deleteSelected('my-flow');              // Delete selected
window.fastflow.deleteCell('my-flow', 'cell-id');       // Delete specific

// Get all nodes/edges
const nodes = window.fastflow.getNodes('my-flow');
const edges = window.fastflow.getEdges('my-flow');

// Zoom controls
window.fastflow.zoomIn('my-flow');
window.fastflow.zoomOut('my-flow');
window.fastflow.zoomToFit('my-flow');

// Clear all nodes
window.fastflow.clearFlow('my-flow');
```

## Tutorials

Step-by-step guides to build different types of workflow editors:

| Tutorial | Description | Difficulty |
|----------|-------------|------------|
| [LangGraph-Style Workflow](docs/tutorials/langgraph-workflow.md) | AI agent workflows like LangGraph Builder | Beginner |
| [ER Diagram Builder](docs/tutorials/er-diagram.md) | Database entity-relationship diagrams | Intermediate |
| [Data Processing DAG](docs/tutorials/data-processing-dag.md) | ETL pipelines with execution simulation | Intermediate |
| [AI/ML Training Pipeline](docs/tutorials/ai-model-dag.md) | ML workflows with conditional branches | Intermediate |
| [Agent Orchestration](docs/tutorials/agent-flow.md) | Complex agent flows with tools | Advanced |
| [Traditional Flowchart](docs/tutorials/flowchart.md) | Classic flowcharts with standard shapes | Beginner |

See the full [tutorial index](docs/tutorials/index.md) for more details.

## Examples

See the `examples/` directory for complete examples:

- **basic/app.py**: Comprehensive tabbed demo with 7 workflow types:
  1. **LangGraph Style** - Agent workflow like LangGraph Builder
  2. **ER Diagram** - Database entity-relationship diagram
  3. **Data Processing DAG** - Data pipeline visualization
  4. **AI Model DAG** - ML training pipeline with status indicators
  5. **Agent Flow** - Complex agent orchestration
  6. **Flowchart** - Traditional flowchart with standard shapes
  7. **Python Execution** - Real-time SSE execution with callbacks and typed nodes

## Development

```bash
# Clone the repository
git clone https://github.com/sgaseretto/fastflow
cd fastflow

# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run example
uv run python examples/basic/app.py
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [AntV X6](https://x6.antv.antgroup.com/en) - The underlying JavaScript diagramming library
- [FastHTML](https://fastht.ml/) - Python web framework
- [HTMX](https://htmx.org/) - HTML-over-the-wire
- [LangGraph Builder](https://github.com/langchain-ai/langgraph) - Design inspiration

## Roadmap

- [ ] Database persistence with fastlite
- [ ] Undo/redo support
- [ ] Minimap component
- [ ] Custom edge routing
- [ ] Sub-flows / grouping
- [ ] Real-time collaboration
- [ ] More example applications
