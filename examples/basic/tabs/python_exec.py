"""Python Execution tab - demonstrates callbacks and type dispatch."""

from fasthtml.common import *
import sys
from pathlib import Path
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
from fastflow import FlowEditor, Edge, DAGNode
from fastflow.types import InputNode, FilterNode, TransformNode, OutputNode
from fastflow.callbacks import FlowCallback, FlowState, TimingCallback, LoggingCallback, ProgressCallback
from fastflow.execution import FlowExecutor, ExecutionStep


# =============================================================================
# Custom Callback
# =============================================================================

class StatusUpdateCallback(FlowCallback):
    """
    Custom callback that demonstrates the two-way callback pattern.

    This callback:
    - Injects metadata into context before each node
    - Collects timing information after nodes
    - Can modify execution flow
    """
    order = 20  # Run after timing callback

    def __init__(self):
        self.step_count = 0

    def before_flow(self, state: FlowState):
        """Initialize flow metadata."""
        state.context["started_at"] = "now"
        state.context["step_logs"] = []
        self.step_count = 0

    def before_node(self, state: FlowState):
        """Inject step number before each node."""
        self.step_count += 1
        if state.current_node:
            node_id = state.current_node.id if hasattr(state.current_node, "id") else str(state.current_node)
            state.context["current_step"] = self.step_count
            state.context["step_logs"].append(f"Step {self.step_count}: Starting {node_id}")

    def after_node(self, state: FlowState):
        """Log completion with timing."""
        if state.current_node:
            node_id = state.current_node.id if hasattr(state.current_node, "id") else str(state.current_node)
            elapsed = state.node_times.get(node_id, 0)
            state.context["step_logs"].append(f"Step {self.step_count}: Completed {node_id} in {elapsed:.2f}s")


# =============================================================================
# Typed Nodes
# =============================================================================

load_node = InputNode(id="py_load", x=100, y=80, label="Load Data", source="csv")
filter_node = FilterNode(id="py_filter", x=300, y=80, label="Filter", condition="active=True")
transform_node = TransformNode(id="py_transform", x=500, y=80, label="Transform", transform_type="normalize")
output_node = OutputNode(id="py_output", x=700, y=80, label="Save", destination="database")


# =============================================================================
# Handler Functions
# =============================================================================

async def load_handler(context: dict, inputs: dict) -> dict:
    """Simulate loading data."""
    await asyncio.sleep(0.8)  # Simulate I/O
    return {"records": 1000, "source": "users.csv"}


async def filter_handler(context: dict, inputs: dict) -> dict:
    """Filter data based on condition."""
    await asyncio.sleep(0.5)
    input_data = inputs.get("py_load", {})
    records = input_data.get("records", 0)
    filtered = int(records * 0.7)  # 70% pass filter
    return {"records": filtered, "filtered_out": records - filtered}


async def transform_handler(context: dict, inputs: dict) -> dict:
    """Transform the filtered data."""
    await asyncio.sleep(0.6)
    input_data = inputs.get("py_filter", {})
    records = input_data.get("records", 0)
    return {"records": records, "transformed": True, "schema": "normalized"}


async def save_handler(context: dict, inputs: dict) -> dict:
    """Save results to destination."""
    await asyncio.sleep(0.4)
    input_data = inputs.get("py_transform", {})
    records = input_data.get("records", 0)
    return {"saved": records, "destination": "database", "status": "success"}


# =============================================================================
# FlowExecutor Instance
# =============================================================================

python_executor = FlowExecutor(
    graph_id="python-exec-flow",
    steps=[
        ExecutionStep(node_id="py_load", node=load_node, depends_on=[], handler=load_handler),
        ExecutionStep(node_id="py_filter", node=filter_node, depends_on=["py_load"], handler=filter_handler),
        ExecutionStep(node_id="py_transform", node=transform_node, depends_on=["py_filter"], handler=transform_handler),
        ExecutionStep(node_id="py_output", node=output_node, depends_on=["py_transform"], handler=save_handler),
    ],
    callbacks=[
        TimingCallback(),           # Track execution times
        LoggingCallback(),          # Log to console
        StatusUpdateCallback(),     # Our custom callback
        ProgressCallback(),         # Track progress percentage
        # SSECallback is auto-added
    ]
)


# =============================================================================
# JavaScript for SSE handling
# =============================================================================

PYTHON_EXEC_SCRIPT = Script("""
    let pythonExecRunning = false;
    let pythonEventSource = null;

    function setNodeStatusPython(graph, nodeId, status) {
        const node = graph.getCellById(nodeId);
        if (!node) return;

        const statusColors = {
            'success': '#52c41a',
            'running': '#1890ff',
            'pending': '#d9d9d9',
            'error': '#ff4d4f',
        };
        const statusSymbols = {
            'success': '\\u2713',
            'running': '\\u21bb',
            'pending': '',
            'error': '\\u2715',
        };
        const statusBgColors = {
            'success': '#f0fdf4',
            'running': '#eff6ff',
            'pending': '#f9fafb',
            'error': '#fef2f2',
        };

        const statusColor = statusColors[status] || '#d9d9d9';
        const statusSymbol = statusSymbols[status] || '';
        const statusBgColor = statusBgColors[status] || '#f9fafb';
        const data = node.getData() || {};
        const icon = data.icon || '\\u2699\\ufe0f';
        const labelText = data.label || nodeId;

        // Rebuild HTML content with new status
        let htmlContent = `<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 100%; height: 100%; display: flex; align-items: center; position: relative;">`;
        htmlContent += `<div style="position: absolute; left: 0; top: 0; width: 4px; height: 100%; background: ${statusColor}; border-radius: 2px 0 0 2px;"></div>`;
        htmlContent += `<div style="margin-left: 16px; font-size: 16px;">${icon}</div>`;
        htmlContent += `<div style="flex: 1; margin-left: 8px; font-size: 13px; color: #374151; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${labelText}</div>`;
        if (status !== 'pending') {
            htmlContent += `<div style="width: 20px; height: 20px; border-radius: 50%; background: ${statusBgColor}; border: 1.5px solid ${statusColor}; display: flex; align-items: center; justify-content: center; margin-right: 8px;">`;
            htmlContent += `<span style="font-size: 11px; font-weight: bold; color: ${statusColor};">${statusSymbol}</span>`;
            htmlContent += `</div>`;
        }
        htmlContent += `</div>`;

        node.setData({ ...data, status });
        node.attr('foBody/html', htmlContent);
    }

    function setEdgeStatusPython(graph, sourceId, targetId, status, animated) {
        const edges = graph.getEdges();
        for (const edge of edges) {
            if (edge.getSourceCellId() === sourceId && edge.getTargetCellId() === targetId) {
                const color = status === 'success' ? '#52c41a' :
                             status === 'running' ? '#1890ff' : '#94a3b8';
                edge.attr('line/stroke', color);
                if (animated) {
                    edge.attr('line/strokeDasharray', '5 5');
                    edge.attr('line/style/animation', 'ant-line 30s infinite linear');
                } else {
                    edge.attr('line/strokeDasharray', null);
                    edge.attr('line/style/animation', null);
                }
                break;
            }
        }
    }

    async function runPythonExecution() {
        if (pythonExecRunning) return;
        pythonExecRunning = true;

        const graph = window.fastflow?.['python-exec-flow'];
        if (!graph) {
            console.error('Graph not found');
            pythonExecRunning = false;
            return;
        }

        const btn = document.getElementById('run-python-exec');
        btn.textContent = '\\u23f3 Executing...';
        btn.disabled = true;

        const resultsDiv = document.getElementById('python-exec-results');
        resultsDiv.innerHTML = '<div style="color: #1890ff;">Starting Python execution...</div>';

        // Connect to SSE endpoint
        pythonEventSource = new EventSource('/execute/python-pipeline');

        // Handle named events (server sends event: nodeStatus, edgeStatus, complete, error)
        pythonEventSource.addEventListener('nodeStatus', function(event) {
            try {
                const data = JSON.parse(event.data);
                console.log('SSE nodeStatus:', data);
                setNodeStatusPython(graph, data.nodeId, data.status);
                resultsDiv.innerHTML += `<div>Node ${data.nodeId}: ${data.status}</div>`;
            } catch (e) {
                console.error('Error parsing nodeStatus:', e);
            }
        });

        pythonEventSource.addEventListener('edgeStatus', function(event) {
            try {
                const data = JSON.parse(event.data);
                console.log('SSE edgeStatus:', data);
                setEdgeStatusPython(graph, data.sourceId, data.targetId, data.status, data.animated);
            } catch (e) {
                console.error('Error parsing edgeStatus:', e);
            }
        });

        pythonEventSource.addEventListener('complete', function(event) {
            try {
                const data = JSON.parse(event.data);
                console.log('SSE complete:', data);
                resultsDiv.innerHTML += `<div style="color: #52c41a; font-weight: bold;">\\u2713 ${data.message || 'Completed!'}</div>`;
                if (data.results) {
                    resultsDiv.innerHTML += `<pre style="font-size: 10px; background: #f8fafc; padding: 8px; border-radius: 4px; margin-top: 8px;">${JSON.stringify(data.results, null, 2)}</pre>`;
                }
                showStatus('Python pipeline completed!');
                cleanup();
            } catch (e) {
                console.error('Error parsing complete:', e);
            }
        });

        pythonEventSource.addEventListener('error', function(event) {
            // Note: 'error' event can be either from SSE or from the server
            // If it's from the server, event.data will be set
            if (event.data) {
                try {
                    const data = JSON.parse(event.data);
                    console.log('SSE error:', data);
                    resultsDiv.innerHTML += `<div style="color: #ff4d4f;">\\u2715 Error: ${data.message}</div>`;
                    showStatus('Pipeline error: ' + data.message);
                } catch (e) {
                    console.error('Error parsing error event:', e);
                }
            }
            cleanup();
        });

        pythonEventSource.onerror = function(err) {
            console.error('SSE Connection Error:', err);
            // Only show connection error if we haven't received a complete event
            if (pythonExecRunning) {
                resultsDiv.innerHTML += '<div style="color: #ff4d4f;">Connection error</div>';
                cleanup();
            }
        };

        function cleanup() {
            if (pythonEventSource) {
                pythonEventSource.close();
                pythonEventSource = null;
            }
            btn.textContent = '\\u25b6 Run Python Pipeline';
            btn.disabled = false;
            pythonExecRunning = false;
        }
    }

    function resetPythonExecution() {
        const graph = window.fastflow?.['python-exec-flow'];
        if (!graph) return;

        const allNodes = ['py_load', 'py_filter', 'py_transform', 'py_output'];
        for (const nodeId of allNodes) {
            setNodeStatusPython(graph, nodeId, 'pending');
        }

        const edgePairs = [
            ['py_load', 'py_filter'],
            ['py_filter', 'py_transform'],
            ['py_transform', 'py_output']
        ];
        for (const [src, tgt] of edgePairs) {
            setEdgeStatusPython(graph, src, tgt, 'pending', false);
        }

        document.getElementById('python-exec-results').innerHTML = '';
        showStatus('Pipeline reset');
    }
""")


# =============================================================================
# Tab Function
# =============================================================================

def python_exec_tab():
    """Python-based execution with SSE and callbacks demonstration."""
    return Div(
        Div(
            Aside(
                H3("Python Execution", style="margin: 0 0 16px 0; font-size: 14px;"),
                P("This tab demonstrates Python-based flow execution with:",
                  style="font-size: 12px; color: #666; margin-bottom: 12px;"),
                Div(
                    P("* Type-dispatched nodes", style="margin: 0 0 4px 0; font-size: 11px; color: #64748b;"),
                    P("* Two-way callback system", style="margin: 0 0 4px 0; font-size: 11px; color: #64748b;"),
                    P("* Real-time SSE updates", style="margin: 0 0 4px 0; font-size: 11px; color: #64748b;"),
                    P("* Custom handlers", style="margin: 0; font-size: 11px; color: #64748b;"),
                    style="padding: 10px; background: #f8fafc; border-radius: 6px; border: 1px solid #e2e8f0; margin-bottom: 16px;"
                ),
                H4("Callbacks Active:", style="margin: 16px 0 8px 0; font-size: 12px; color: #64748b;"),
                Div(
                    P("✓ TimingCallback", style="margin: 0 0 4px 0; font-size: 11px; color: #52c41a;"),
                    P("✓ LoggingCallback", style="margin: 0 0 4px 0; font-size: 11px; color: #52c41a;"),
                    P("✓ StatusUpdateCallback", style="margin: 0 0 4px 0; font-size: 11px; color: #52c41a;"),
                    P("✓ ProgressCallback", style="margin: 0 0 4px 0; font-size: 11px; color: #52c41a;"),
                    P("✓ SSECallback", style="margin: 0; font-size: 11px; color: #52c41a;"),
                    style="padding: 10px; background: #f0fdf4; border-radius: 6px; border: 1px solid #bbf7d0;"
                ),
                Div(
                    Button("▶ Run Python Pipeline", id="run-python-exec", onclick="runPythonExecution()",
                           style="width: 100%; margin-top: 16px; padding: 10px; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;"),
                    Button("↺ Reset", id="reset-python-exec", onclick="resetPythonExecution()",
                           style="width: 100%; margin-top: 8px; padding: 8px; background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer;"),
                ),
                # Results display
                Div(
                    H4("Execution Results:", style="margin: 16px 0 8px 0; font-size: 12px; color: #64748b;"),
                    Div(id="python-exec-results", style="font-size: 11px; color: #374151; max-height: 150px; overflow-y: auto;"),
                    style="margin-top: 16px;"
                ),
                cls="sidebar"
            ),
            Main(
                FlowEditor(
                    # Use DAGNode for visual representation (typed nodes are for execution)
                    DAGNode("py_load", x=100, y=120, label="Load Data", node_type="input",
                           icon="📥", inputs=0, outputs=1,
                           port_positions={"inputs": "left", "outputs": "right"}),
                    DAGNode("py_filter", x=300, y=120, label="Filter", node_type="filter",
                           icon="🔍",
                           port_positions={"inputs": "left", "outputs": "right"}),
                    DAGNode("py_transform", x=500, y=120, label="Transform", node_type="transform",
                           icon="🔄",
                           port_positions={"inputs": "left", "outputs": "right"}),
                    DAGNode("py_output", x=700, y=120, label="Save", node_type="output",
                           icon="💾", inputs=1, outputs=0,
                           port_positions={"inputs": "left", "outputs": "right"}),
                    # Edges
                    Edge(source="py_load", target="py_filter", color="#94a3b8"),
                    Edge(source="py_filter", target="py_transform", color="#94a3b8"),
                    Edge(source="py_transform", target="py_output", color="#94a3b8"),
                    id="python-exec-flow",
                    on_change="/flow/changed",
                ),
                cls="editor-main"
            ),
            cls="app-container"
        ),
        PYTHON_EXEC_SCRIPT,
        id="tab-python-exec"
    )
