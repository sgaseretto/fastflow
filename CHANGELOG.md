# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - Fastcore Refactor

### Added

#### Fastcore Integration & Type Dispatch System
- **Type Dispatch System**: Using `plum-dispatch` for multiple dispatch operations on typed nodes
- **Typed Node Classes**: `StartNode`, `EndNode`, `AgentNode`, `ToolNode`, `LLMNode`, `ConditionNode`, `InputNode`, `OutputNode`, `FilterNode`, `JoinNode`, `TransformNode`, `ProcessNode`, `DecisionNode`, `CodeNode`
- **Type-dispatched operations**:
  - `render(node)` - Generate HTML/FT representation for a node
  - `execute(node, context, inputs)` - Execute node logic
  - `validate(node)` - Validate node configuration
  - `can_connect(source, target)` - Check if two nodes can be connected
  - `get_node_style(node)` - Get CSS styling for a node
  - `node_to_x6(node)` / `node_from_x6(data, node_type)` - X6 serialization
- **Node Registry**: `NODE_TYPE_MAP` for looking up node classes by type string
- **Custom Node Registration**: `register_node_type()` to add custom node types

#### Two-Way Callback System (fastai-style)
- **`FlowCallback` base class** with lifecycle hooks:
  - `before_flow` / `after_flow` - Called at flow start/end
  - `before_node` / `after_node` - Called around each node execution
  - `before_edge` / `after_edge` - Called around edge traversal
  - `on_error` / `on_cancel` - Error and cancellation handling
- **`FlowState` dataclass** - Mutable execution state passed to callbacks
- **Built-in Callbacks**:
  - `SSECallback` - Server-Sent Events for browser updates
  - `LoggingCallback` - Structured logging with configurable logger
  - `TimingCallback` - Performance metrics and timing
  - `RetryCallback` - Automatic retry on failure
  - `ProgressCallback` - Progress percentage tracking
  - `ValidationCallback` - Pre-execution node validation
- **Control Flow Exceptions**:
  - `CancelFlowException` - Stop entire flow execution
  - `SkipNodeException` - Skip current node, continue flow
  - `RetryNodeException` - Retry current node

#### Layered API Architecture
- **Layer 0 (Core Primitives)**: `raw_node_status()`, `raw_edge_status()`, `raw_complete()`, `raw_error()`, `to_x6_node()`, `to_x6_edge()`
- **Layer 1 (State Management)**: `Flow`, `NodeData`, `EdgeData` with `store_attr` and `@patch` extensibility
- **Layer 2 (Main API)**: Typed nodes, callbacks, `FlowExecutor`
- **Layer 3 (Convenience)**: `quick_flow()`, `run_pipeline()`, `from_dict()`, `to_dict()`, `from_langgraph()`, `flow_from_steps()`

#### Convenience Functions
- **`quick_flow(steps)`** - Create `FlowExecutor` from list of step dictionaries
- **`run_pipeline(handlers)`** - Create linear pipeline from async handler functions
- **`flow_from_steps(steps)`** - Create `Flow` with automatic layout from step definitions
- **`from_dict()` / `to_dict()`** - Flow serialization helpers
- **`from_langgraph()`** - Convert LangGraph StateGraph to Flow (placeholder)

#### Fastcore Ergonomics
- **`store_attr()`** in `NodeData`, `EdgeData`, `Flow` - Eliminates `__init__` boilerplate
- **`@patch` extensions** - Add methods without subclassing:
  - `NodeData.validate()`, `NodeData.copy()`
  - `EdgeData.validate()`, `EdgeData.copy()`
  - `Flow.validate()`, `Flow.copy()`

### Changed
- **FlowExecutor** now accepts `callbacks` parameter for the callback system
- **Dependencies**: Added `fastcore>=1.5.0` and `plum-dispatch>=2.0.0`
- **Version**: Bumped to 0.2.0

### Removed
- **`@NodeType` decorator** - Use typed node classes from `fastflow.types` instead
- **`get_node_types()`** - Use `NODE_TYPE_MAP` instead
- **`get_node_type()`** - Use `NODE_TYPE_MAP` instead
- **`clear_node_types()`** - No longer needed with typed node classes
- **`compat.py`** - Backward compatibility module removed
- **`node_types.py`** - Legacy node type registry removed

### Migration Guide
Use typed node classes instead of the old `@NodeType` decorator:

```python
# Old (removed)
# @NodeType("agent", inputs=1, outputs=1)
# def MyAgent(model="gpt-4"):
#     return Div(model)

# New (recommended)
from dataclasses import dataclass
from fastflow.types import AgentNode, render

@dataclass
class MyAgent(AgentNode):
    custom_field: str = ""

@render.register
def _(node: MyAgent):
    return Div(node.model, node.custom_field)
```

---

## [Unreleased]

### Added

#### New Specialized Components
- **`TableNode`** - Create database table/entity nodes for ER diagrams with column definitions
- **`DAGNode`** - Create data processing DAG nodes with status indicators (input, filter, join, union, agg, output)
- **`AgentNode`** - Create agent workflow nodes (llm, code, branch, loop, kb, mcp, db)
- **`FlowchartNode`** - Create flowchart nodes with standard shapes (process, decision, data, connector)
- **`PaletteGroup`** - Collapsible groups for organizing palette items
- **`StatusBadge`** - Visual status indicator for nodes (success, error, running, pending)

#### Enhanced Node Features
- **`shape`** parameter - Node shape type ('rect', 'circle', 'polygon', 'diamond', 'ellipse')
- **`icon`** parameter - Icon emoji or URL displayed in node label
- **`status`** parameter - Visual status indicator with colored border ('success', 'error', 'running')
- **`port_positions`** parameter - Custom port positions (`{'inputs': 'left', 'outputs': 'right'}`)
- **Custom colors** - `fill`, `stroke`, `text_color` parameters to override default styling
- **Left/right port groups** - Support for horizontal connections (ER diagrams, data flows)

#### Enhanced Edge Features
- **`connector`** parameter - Edge connector type ('smooth', 'rounded', 'manhattan', 'normal')
- **`router`** parameter - Edge routing algorithm ('manhattan', 'orth', 'metro', 'er', 'normal')
- **`color`** parameter - Custom edge line color
- **`animated`** parameter - Animated dashed line for running state
- **`marker`** parameter - Arrow marker type ('block', 'classic', 'diamond', 'circle', 'arrow')
- **`relationship`** parameter - ER relationship label ('1:1', '1:N', 'N:1', 'N:N')

#### Extended Node Type Styles
- **Data Processing**: `input`, `output`, `filter`, `join`, `union`, `agg`, `transform`
- **Agent Flow**: `code`, `branch`, `loop`, `kb` (knowledge base), `mcp`, `db`
- **Flowchart**: `process`, `decision`, `data`, `connector`
- **ER Diagram**: `table`

#### Comprehensive Example Application
- **Tabbed interface** demonstrating 7 workflow types:
  1. **LangGraph Style** - Agent workflow like LangGraph Builder
  2. **ER Diagram** - Database entity-relationship diagram
  3. **Data Processing DAG** - Data pipeline visualization
  4. **AI Model DAG** - ML training pipeline with status indicators
  5. **Agent Flow** - Complex agent orchestration with LLM, code, KB, MCP nodes
  6. **Flowchart** - Traditional flowchart with standard shapes
  7. **Python Execution** - Python-based SSE execution with callbacks (NEW)

#### Python Execution Demo Tab
- **Full SSE-based execution** - Real-time Python pipeline execution streamed to browser
- **Custom callback example** - `StatusUpdateCallback` demonstrating two-way callback pattern
- **Typed nodes** - Uses `InputNode`, `FilterNode`, `TransformNode`, `OutputNode` from types.py
- **Multiple callbacks** - `TimingCallback`, `LoggingCallback`, `ProgressCallback`, `SSECallback` working together
- **Handler functions** - Real async Python handlers (`load_handler`, `filter_handler`, etc.) processing data

#### Type Dispatch Integration for UI Components
- **`node_from_typed(typed_node)`** - Convert typed FlowNode instances to UI Node components
- **`nodes_from_typed(typed_nodes)`** - Convert list of typed FlowNodes to UI components
- **`validate_typed_node(typed_node)`** - Validate typed node using type-dispatched `validate()`
- Provides seamless bridge between Layer 2 typed nodes and UI layer

#### Comprehensive Tutorials
- **6 step-by-step tutorials** in `docs/tutorials/`:
  1. [LangGraph-Style Workflow](docs/tutorials/langgraph-workflow.md) - Build AI agent workflows (Beginner)
  2. [ER Diagram Builder](docs/tutorials/er-diagram.md) - Create database diagrams with tables and relationships (Intermediate)
  3. [Data Processing DAG](docs/tutorials/data-processing-dag.md) - Build ETL pipelines with execution simulation (Intermediate)
  4. [AI/ML Training Pipeline](docs/tutorials/ai-model-dag.md) - Create ML workflows with conditional branches (Intermediate)
  5. [Agent Orchestration](docs/tutorials/agent-flow.md) - Complex agent flows with tools, KB, MCP (Advanced)
  6. [Traditional Flowchart](docs/tutorials/flowchart.md) - Classic flowcharts with standard shapes (Beginner)
- Each tutorial includes complete code examples and incremental building steps
- [Tutorial index](docs/tutorials/index.md) with prerequisites, difficulty levels, and quick reference

#### Interactive Editing Features
- **Keyboard delete**: Press `Delete` or `Backspace` to delete selected nodes/edges
- **Double-click to rename nodes**: Double-click any node to edit its label inline
- **Double-click to edit edge labels**: Double-click any edge to add/edit its label
- **Context menu**: Right-click on nodes/edges for quick actions (rename, delete, make dashed/solid)

#### Enhanced ER Diagram TableNode
- **Four-way port connections** - TableNode now supports ports on all four sides (top, bottom, left, right) for flexible relationship lines
- **Add column dialog** - Right-click a table → "Add Column" to add new columns with name, type, PK/FK options
- **Remove column dialog** - Right-click a table → "Remove Column" to see and remove existing columns
- **Dynamic table resizing** - Table nodes automatically resize when columns are added or removed
- **Visual styling matching X6 ER example**:
  - Gradient header background (`linear-gradient(135deg, #1890ff 0%, #096dd9 100%)`)
  - Gradient body background (`linear-gradient(135deg, #fff 0%, #f8f9fa 100%)`)
  - Drop shadow effect (`drop-shadow(0 4px 12px rgba(0, 0, 0, 0.1))`)
  - Different background colors for key types (PK: `#e6f7ff`, FK: `#fff7e6`)
  - Monospace font for column types
  - Ports hidden by default, visible on hover with smooth CSS transitions
  - Port circles styled with blue stroke and white fill
  - Port hover effect with enlarged circle and green highlight when connecting

#### New JavaScript API Functions
- `window.fastflow.deleteSelected(graphId)` - Delete selected cells
- `window.fastflow.deleteCell(graphId, cellId)` - Delete specific cell
- `window.fastflow.renameNode(graphId, nodeId, newLabel)` - Rename a node
- `window.fastflow.setEdgeLabel(graphId, edgeId, label)` - Set/remove edge label
- `window.fastflow.setEdgeDashed(graphId, edgeId, dashed)` - Toggle dashed style
- `window.fastflow.getNodes(graphId)` - Get all nodes
- `window.fastflow.getEdges(graphId)` - Get all edges

#### Table Column Management API
- `window.fastflow.addTableColumn(graphId, nodeId, column)` - Add a column to a table node
- `window.fastflow.removeTableColumn(graphId, nodeId, columnIndex)` - Remove a column by index
- `window.fastflow.getTableColumns(graphId, nodeId)` - Get all columns from a table node
- `window.fastflow.setTableColumns(graphId, nodeId, columns)` - Replace all columns in a table node

#### Python-Based Execution with SSE
- **`FlowExecutor` class** - Execute flows with topological ordering and real-time visual updates
- **`ExecutionStep` dataclass** - Define pipeline steps with dependencies and custom handlers
- **SSE helpers** - `node_status()`, `edge_status()`, `execution_complete()`, `execution_error()` for streaming updates
- **`run_sequential()` helper** - Simple helper for linear pipeline execution
- **Custom handlers** - Attach async Python functions to execute real logic at each step
- **Dependency management** - Automatic topological sorting based on step dependencies
- **Context sharing** - Pass shared context (database connections, configs) between handlers
- **Error handling** - Graceful error reporting with visual feedback

#### JavaScript SSE Execution API
- `window.fastflow.connectExecution(graphId, endpoint, options)` - Connect to SSE endpoint for execution updates
- `window.fastflow.disconnectExecution(graphId)` - Disconnect active SSE connection
- `window.fastflow.setNodeStatus(graphId, nodeId, status)` - Set node execution status
- `window.fastflow.setEdgeStatus(graphId, sourceId, targetId, status, animated)` - Set edge status
- `window.fastflow.resetAllStatus(graphId)` - Reset all nodes/edges to pending state
- `window.fastflow.isExecutionConnected(graphId)` - Check if execution SSE is connected

#### DAG Execution Simulation (JavaScript-based, legacy)
- **Data DAG simulation** - "Run Simulation" button that animates data pipeline execution step-by-step
- **AI Pipeline simulation** - "Run Training" button that simulates ML training pipeline with status updates
- **Real-time status updates** - Nodes transition through pending → running → success states
- **Animated edges** - Data flow visualization with animated dashed lines during execution
- **Reset functionality** - Reset buttons to restore initial state for re-running simulations

#### New Documentation
- **[Python Execution Guide](docs/how_it_works/python_execution.md)** - Comprehensive guide for Python-driven execution with SSE

#### Auto-Fit Content
- **`auto_fit` parameter** - FlowEditor now auto-fits content to viewport after initialization (enabled by default)
- Ensures all nodes and edges are visible regardless of canvas/container size
- Uses `zoomToFit` with 40px padding and max scale of 1 (won't zoom beyond 100%)

### Fixed
- **Fixed ER table node creation from palette** - Dragging a table from palette now creates proper ER table nodes with header, columns, and four-way ports (was creating empty rectangles with timestamp IDs)
- **Added Edit Column option to ER tables** - Right-click context menu now includes "Edit Column" option for modifying existing columns
- **Critical**: Fixed X6 CDN URL - X6 v2 uses ESM format which doesn't expose global variables via script tags. Now using X6 v1.x with proper UMD build from unpkg (`/dist/x6.js`)
- Fixed port group names in `fastflow.js` helper functions to match main initialization (`top`/`bottom` instead of `in`/`out`)
- Fixed node shape in helper functions to use built-in `rect` instead of unregistered `fastflow-node`
- Fixed keyboard shortcuts (Delete/Backspace) not working on macOS - added `keyboard: { enabled: true }` to X6 Graph config
- Fixed drag-and-drop positioning - nodes now appear where dropped instead of offset to the left (fixed `clientToLocal` coordinate conversion)
- **Fixed ER table node text rendering** - Text now appears correctly inside table cells using foreignObject with HTML content instead of SVG text elements
- **Fixed DAG node text rendering** - DAG nodes now use foreignObject with HTML for proper text positioning inside node boundaries
- **Fixed canvas/container height** - FlowEditor containers now properly fill their parent containers with `min-height: 600px`
- **Fixed white text on inline edit** - Inline edit inputs now have explicit `color: #333` to ensure text is always visible
- **Fixed content cutoff on wide diagrams** - Auto-fit now ensures all nodes are visible by zooming to fit content after initialization
- **Fixed hidden tab graph display** - Graphs in hidden tabs (like tabbed interfaces) now properly resize and fit content when the tab becomes visible. X6 graphs initialized while hidden couldn't calculate proper dimensions; now `resize()` and `zoomToFit()` are called when tabs are shown
- **Fixed TableNode border not extending fully** - Border now properly wraps around the entire table node with consistent stroke width

### Changed
- **BREAKING**: Migrated from Drawflow to AntV X6 for richer graph features
- **BREAKING**: `Node` API changes:
  - `name` parameter is now `id` internally
  - Added `label` parameter for display text
  - `type` parameter renamed to `node_type`
- **BREAKING**: `Edge` API changes:
  - `from_node`/`to_node` renamed to `source`/`target`
  - `from_output`/`to_input` renamed to `source_port`/`target_port`
  - Added `label` parameter for edge labels (pill badge style)
  - Added `dashed` parameter for conditional edges
- **BREAKING**: `EdgeData` class updated with new field names
- **BREAKING**: `NodeData` class simplified:
  - Removed `name`, `cls`, `html` fields
  - Added `label`, `node_type`, `width`, `height` fields
  - `inputs`/`outputs` are now integers (port counts) instead of dicts
- Serialization format changed from Drawflow's nested structure to X6's flat nodes/edges format
- `to_drawflow()`/`from_drawflow()` methods renamed to `to_x6()`/`from_x6()`

### Added
- LangGraph Builder-inspired styling with colored node types (start, end, agent, tool, llm, condition)
- Edge labels displayed as pill badges
- Dashed line support for conditional/optional edges
- Port-based connections with visual input/output handles
- Background grid and smooth panning
- JavaScript helper functions: `exportFlow`, `importFlow`, `addNode`, `addEdge`, `clearFlow`
- Zoom controls: `zoomIn`, `zoomOut`, `zoomToFit`, `centerContent`

### Removed
- Drawflow-specific options (`reroute`, `curvature`, `mode`)
- `Connection` dataclass (ports now managed internally by X6)
- `FlowEditor.module` field (X6 uses single canvas)

## [0.1.0] - Initial Release

### Added
- Initial project structure with `pyproject.toml` using `uv` for package management
- Core FastHTML components:
  - `FlowEditor` - Main flow editor container with X6 integration
  - `Node` - Define nodes in the flow with position, inputs/outputs, and data
  - `Edge` - Define connections between nodes with optional labels
  - `NodePalette` - Drag-and-drop palette for creating nodes
  - `PaletteItem` - Individual draggable items for the palette
  - `FlowControls` - Zoom and control buttons
- `fastflow_headers()` function for loading X6 JS from CDN
- JavaScript bridge (`fastflow.js`) for X6-HTMX integration
- State management classes:
  - `Flow` - Complete workflow state with serialization
  - `NodeData` - Individual node data with label and node_type
  - `EdgeData` - Connection data with label and dashed support
  - Support for topological sorting of nodes
- `@NodeType` decorator for registering custom node types
- Default CSS styles inspired by LangGraph Builder
- Basic example application demonstrating LangGraph-style workflow
- Documentation:
  - README with quick start guide and API reference
  - Getting started guide
  - Architecture documentation with Mermaid diagrams
- Test suite with pytest
