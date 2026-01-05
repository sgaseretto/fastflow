"""
Fastflow Examples - Comprehensive Demo

A tabbed interface showing various workflow types you can build with Fastflow:
1. LangGraph Style - Agent workflow like LangGraph Builder
2. ER Diagram - Database entity-relationship diagram
3. Data Processing DAG - Data pipeline visualization
4. AI Model DAG - ML training pipeline with status
5. Agent Flow - Complex agent orchestration
6. Flowchart - Traditional flowchart shapes

Run with: uv run python examples/basic/app.py
"""

from fasthtml.common import *
import sys
from pathlib import Path

# Import fastflow components
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from fastflow import (
    FlowEditor, Node, Edge, NodePalette, PaletteItem, FlowControls,
    PaletteGroup, TableNode, DAGNode, AgentNode, FlowchartNode,
    fastflow_headers, NodeType
)

# Create app with fastflow headers
app, rt = fast_app(hdrs=fastflow_headers())


# =============================================================================
# Tab 1: LangGraph Style (Original Example)
# =============================================================================
def langgraph_tab():
    """LangGraph-style agent workflow."""
    return Div(
        Div(
            Aside(
                H3("Node Types", style="margin: 0 0 16px 0; font-size: 14px;"),
                NodePalette(
                    PaletteItem("start", "__start__", icon="", inputs=0, outputs=1),
                    PaletteItem("end", "__end__", icon="", inputs=1, outputs=0),
                    PaletteItem("agent", "Agent", icon="", inputs=1, outputs=1),
                    PaletteItem("tool", "Tool", icon="", inputs=1, outputs=1),
                    PaletteItem("llm", "LLM", icon="", inputs=1, outputs=1),
                    PaletteItem("condition", "Condition", icon="", inputs=1, outputs=2),
                    target_editor="langgraph-flow"
                ),
                cls="sidebar"
            ),
            Main(
                FlowEditor(
                    Node("__start__", x=300, y=50, label="__start__", node_type="start",
                         inputs=0, outputs=1),
                    Node("agent", x=300, y=180, label="agent", node_type="agent",
                         inputs=1, outputs=1),
                    Node("tools", x=500, y=300, label="tools", node_type="tool",
                         inputs=1, outputs=1),
                    Node("__end__", x=300, y=450, label="__end__", node_type="end",
                         inputs=1, outputs=0),
                    Edge(source="__start__", target="agent"),
                    Edge(source="agent", target="tools", label="continue", dashed=True),
                    Edge(source="agent", target="__end__", label="end"),
                    Edge(source="tools", target="agent"),
                    id="langgraph-flow",
                    on_change="/flow/changed",
                ),
                cls="editor-main"
            ),
            cls="app-container"
        ),
        id="tab-langgraph"
    )


# =============================================================================
# Tab 2: ER Diagram
# =============================================================================
def er_diagram_tab():
    """Database entity-relationship diagram."""
    return Div(
        Div(
            Aside(
                H3("Tables", style="margin: 0 0 16px 0; font-size: 14px;"),
                P("Drag tables to the canvas. Connect with relationship lines.",
                  style="font-size: 12px; color: #666; margin-bottom: 12px;"),
                NodePalette(
                    PaletteItem("table", "Table", icon="", inputs=1, outputs=1),
                    target_editor="er-flow"
                ),
                H4("Tips", style="margin: 20px 0 8px 0; font-size: 12px; color: #64748b;"),
                Div(
                    P("• Right-click table → Add/Remove columns", style="margin: 0 0 4px 0; font-size: 11px; color: #64748b;"),
                    P("• Connect from any side (top, bottom, left, right)", style="margin: 0 0 4px 0; font-size: 11px; color: #64748b;"),
                    P("• Double-click to rename tables", style="margin: 0; font-size: 11px; color: #64748b;"),
                    style="padding: 10px; background: #f8fafc; border-radius: 6px; border: 1px solid #e2e8f0;"
                ),
                cls="sidebar"
            ),
            Main(
                FlowEditor(
                    # Users table
                    TableNode("users", x=50, y=50, label="users", columns=[
                        {"name": "id", "type": "bigint", "pk": True},
                        {"name": "name", "type": "varchar(255)"},
                        {"name": "email", "type": "varchar(255)"},
                        {"name": "created_at", "type": "timestamp"},
                    ]),
                    # Orders table
                    TableNode("orders", x=400, y=50, label="orders", columns=[
                        {"name": "id", "type": "bigint", "pk": True},
                        {"name": "user_id", "type": "bigint", "fk": "users.id"},
                        {"name": "total", "type": "decimal(10,2)"},
                        {"name": "status", "type": "varchar(50)"},
                    ]),
                    # Products table
                    TableNode("products", x=50, y=280, label="products", columns=[
                        {"name": "id", "type": "bigint", "pk": True},
                        {"name": "name", "type": "varchar(255)"},
                        {"name": "price", "type": "decimal(10,2)"},
                        {"name": "stock", "type": "int"},
                        {"name": "count", "type": "int"},
                    ]),
                    # Order Items table
                    TableNode("order_items", x=400, y=280, label="order_items", columns=[
                        {"name": "id", "type": "bigint", "pk": True},
                        {"name": "order_id", "type": "bigint", "fk": "orders.id"},
                        {"name": "product_id", "type": "bigint", "fk": "products.id"},
                        {"name": "quantity", "type": "int"},
                    ]),
                    # Relationships - demonstrating both horizontal and vertical connections
                    Edge(source="users", target="orders", relationship="1:N", router="er",
                         source_port="port_right", target_port="port_left"),  # horizontal
                    Edge(source="orders", target="order_items", relationship="1:N", router="er",
                         source_port="port_bottom", target_port="port_top"),  # vertical
                    Edge(source="products", target="order_items", relationship="1:N", router="er",
                         source_port="port_right", target_port="port_left"),  # horizontal
                    id="er-flow",
                    on_change="/flow/changed",
                ),
                cls="editor-main"
            ),
            cls="app-container"
        ),
        id="tab-er"
    )


# =============================================================================
# Tab 3: Data Processing DAG
# =============================================================================
def data_dag_tab():
    """Data processing pipeline visualization."""
    return Div(
        Div(
            Aside(
                H3("Data Nodes", style="margin: 0 0 16px 0; font-size: 14px;"),
                NodePalette(
                    PaletteGroup(
                        PaletteItem("input", "INPUT", icon="📥", inputs=0, outputs=1),
                        PaletteItem("output", "OUTPUT", icon="📤", inputs=1, outputs=0),
                        title="I/O"
                    ),
                    PaletteGroup(
                        PaletteItem("filter", "FILTER", icon="🔍", inputs=1, outputs=1),
                        PaletteItem("transform", "TRANSFORM", icon="🔄", inputs=1, outputs=1),
                        PaletteItem("agg", "AGGREGATE", icon="∑", inputs=1, outputs=1),
                        title="Transform"
                    ),
                    PaletteGroup(
                        PaletteItem("join", "JOIN", icon="🔗", inputs=2, outputs=1),
                        PaletteItem("union", "UNION", icon="⊕", inputs=2, outputs=1),
                        title="Combine"
                    ),
                    target_editor="data-dag-flow"
                ),
                Div(
                    H4("Status Legend", style="margin: 20px 0 8px 0; font-size: 12px; color: #64748b;"),
                    Div(
                        Div("✓ Success", style="color: #52c41a; font-size: 12px;"),
                        Div("↻ Running", style="color: #1890ff; font-size: 12px;"),
                        Div("✕ Error", style="color: #ff4d4f; font-size: 12px;"),
                        style="padding: 8px 12px; background: #f8fafc; border-radius: 6px;"
                    ),
                ),
                Div(
                    Button("▶ Run Simulation", id="run-dag-sim", onclick="runDAGSimulation()",
                           style="width: 100%; margin-top: 16px; padding: 10px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;"),
                    Button("↺ Reset", id="reset-dag-sim", onclick="resetDAGSimulation()",
                           style="width: 100%; margin-top: 8px; padding: 8px; background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer;"),
                ),
                cls="sidebar"
            ),
            Main(
                FlowEditor(
                    # Input sources (left-to-right flow using port_positions)
                    DAGNode("input1", x=50, y=80, label="Users CSV", node_type="input",
                           icon="📥", inputs=0, outputs=1,
                           port_positions={"inputs": "left", "outputs": "right"}),
                    DAGNode("input2", x=50, y=200, label="Orders DB", node_type="input",
                           icon="🗄️", inputs=0, outputs=1,
                           port_positions={"inputs": "left", "outputs": "right"}),
                    # Processing nodes
                    DAGNode("filter1", x=250, y=80, label="Filter Active", node_type="filter",
                           icon="🔍",
                           port_positions={"inputs": "left", "outputs": "right"}),
                    DAGNode("filter2", x=250, y=200, label="Filter Recent", node_type="filter",
                           icon="🔍",
                           port_positions={"inputs": "left", "outputs": "right"}),
                    DAGNode("join1", x=450, y=140, label="Join Data", node_type="join",
                           icon="🔗", inputs=2, outputs=1,
                           port_positions={"inputs": "left", "outputs": "right"}),
                    DAGNode("agg1", x=650, y=140, label="Aggregate", node_type="agg",
                           icon="∑",
                           port_positions={"inputs": "left", "outputs": "right"}),
                    # Output
                    DAGNode("output1", x=850, y=140, label="Export CSV", node_type="output",
                           icon="📤", inputs=1, outputs=0,
                           port_positions={"inputs": "left", "outputs": "right"}),
                    # Connections with green color for data flow
                    Edge(source="input1", target="filter1", color="#94a3b8"),
                    Edge(source="input2", target="filter2", color="#94a3b8"),
                    Edge(source="filter1", target="join1", target_port=0, color="#94a3b8"),
                    Edge(source="filter2", target="join1", target_port=1, color="#94a3b8"),
                    Edge(source="join1", target="agg1", color="#94a3b8"),
                    Edge(source="agg1", target="output1", color="#94a3b8"),
                    id="data-dag-flow",
                    on_change="/flow/changed",
                ),
                cls="editor-main"
            ),
            cls="app-container"
        ),
        # DAG Simulation Script
        Script("""
            let dagSimRunning = false;

            // Execute order for the DAG simulation
            const dagExecutionOrder = [
                { nodes: ['input1', 'input2'], edges: [] },
                { nodes: ['filter1', 'filter2'], edges: ['input1-filter1', 'input2-filter2'] },
                { nodes: ['join1'], edges: ['filter1-join1', 'filter2-join1'] },
                { nodes: ['agg1'], edges: ['join1-agg1'] },
                { nodes: ['output1'], edges: ['agg1-output1'] },
            ];

            function setNodeStatus(graph, nodeId, status) {
                const node = graph.getCellById(nodeId);
                if (!node) return;

                const statusColors = {
                    'success': '#52c41a',
                    'running': '#1890ff',
                    'pending': '#d9d9d9',
                };
                const statusSymbols = {
                    'success': '✓',
                    'running': '↻',
                    'pending': '',
                };
                const statusBgColors = {
                    'success': '#f0fdf4',
                    'running': '#eff6ff',
                    'pending': '#f9fafb',
                };

                const statusColor = statusColors[status] || '#d9d9d9';
                const statusSymbol = statusSymbols[status] || '';
                const statusBgColor = statusBgColors[status] || '#f9fafb';
                const data = node.getData() || {};
                const icon = data.icon || '⚙️';
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

            function setEdgeAnimated(graph, sourceId, targetId, animated, color) {
                const edges = graph.getEdges();
                for (const edge of edges) {
                    if (edge.getSourceCellId() === sourceId && edge.getTargetCellId() === targetId) {
                        if (animated) {
                            edge.attr('line/stroke', color || '#52c41a');
                            edge.attr('line/strokeDasharray', '5 5');
                            edge.attr('line/style/animation', 'ant-line 30s infinite linear');
                        } else {
                            edge.attr('line/stroke', color || '#52c41a');
                            edge.attr('line/strokeDasharray', null);
                            edge.attr('line/style/animation', null);
                        }
                        break;
                    }
                }
            }

            async function runDAGSimulation() {
                if (dagSimRunning) return;
                dagSimRunning = true;

                const graph = window.fastflow?.['data-dag-flow'];
                if (!graph) {
                    console.error('Graph not found');
                    dagSimRunning = false;
                    return;
                }

                const btn = document.getElementById('run-dag-sim');
                btn.textContent = '⏳ Running...';
                btn.disabled = true;

                // Reset all nodes to pending first
                const allNodes = ['input1', 'input2', 'filter1', 'filter2', 'join1', 'agg1', 'output1'];
                for (const nodeId of allNodes) {
                    setNodeStatus(graph, nodeId, 'pending');
                }

                // Reset all edges to gray
                const edgePairs = [
                    ['input1', 'filter1'], ['input2', 'filter2'],
                    ['filter1', 'join1'], ['filter2', 'join1'],
                    ['join1', 'agg1'], ['agg1', 'output1']
                ];
                for (const [src, tgt] of edgePairs) {
                    setEdgeAnimated(graph, src, tgt, false, '#94a3b8');
                }

                await new Promise(r => setTimeout(r, 500));

                // Execute each step
                for (let i = 0; i < dagExecutionOrder.length; i++) {
                    const step = dagExecutionOrder[i];

                    // Set nodes to running
                    for (const nodeId of step.nodes) {
                        setNodeStatus(graph, nodeId, 'running');
                    }

                    // Animate incoming edges
                    for (const edgeKey of step.edges) {
                        const [src, tgt] = edgeKey.split('-');
                        setEdgeAnimated(graph, src, tgt, true, '#52c41a');
                    }

                    // Wait for "processing"
                    await new Promise(r => setTimeout(r, 1000));

                    // Set nodes to success
                    for (const nodeId of step.nodes) {
                        setNodeStatus(graph, nodeId, 'success');
                    }

                    // Stop edge animation
                    for (const edgeKey of step.edges) {
                        const [src, tgt] = edgeKey.split('-');
                        setEdgeAnimated(graph, src, tgt, false, '#52c41a');
                    }

                    await new Promise(r => setTimeout(r, 300));
                }

                btn.textContent = '▶ Run Simulation';
                btn.disabled = false;
                dagSimRunning = false;
                showStatus('Pipeline execution completed!');
            }

            function resetDAGSimulation() {
                const graph = window.fastflow?.['data-dag-flow'];
                if (!graph) return;

                const allNodes = ['input1', 'input2', 'filter1', 'filter2', 'join1', 'agg1', 'output1'];
                for (const nodeId of allNodes) {
                    setNodeStatus(graph, nodeId, 'pending');
                }

                const edgePairs = [
                    ['input1', 'filter1'], ['input2', 'filter2'],
                    ['filter1', 'join1'], ['filter2', 'join1'],
                    ['join1', 'agg1'], ['agg1', 'output1']
                ];
                for (const [src, tgt] of edgePairs) {
                    setEdgeAnimated(graph, src, tgt, false, '#94a3b8');
                }

                showStatus('Pipeline reset');
            }
        """),
        id="tab-data-dag"
    )


# =============================================================================
# Tab 4: AI Model DAG (Training Pipeline)
# =============================================================================
def ai_model_dag_tab():
    """AI model training pipeline with status indicators."""
    return Div(
        Div(
            Aside(
                H3("ML Pipeline", style="margin: 0 0 16px 0; font-size: 14px;"),
                P("Training pipeline with status indicators",
                  style="font-size: 12px; color: #666; margin-bottom: 16px;"),
                Div(
                    Span("●", style="color: #52c41a;"), " Success",
                    Br(),
                    Span("●", style="color: #1890ff;"), " Running",
                    Br(),
                    Span("●", style="color: #ff4d4f;"), " Failed",
                    style="font-size: 12px; margin-top: 20px; padding: 10px; background: #f8f8f8; border-radius: 6px;"
                ),
                Div(
                    Button("▶ Run Training", id="run-ai-sim", onclick="runAISimulation()",
                           style="width: 100%; margin-top: 16px; padding: 10px; background: #8b5cf6; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;"),
                    Button("↺ Reset", id="reset-ai-sim", onclick="resetAISimulation()",
                           style="width: 100%; margin-top: 8px; padding: 8px; background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer;"),
                ),
                cls="sidebar"
            ),
            Main(
                FlowEditor(
                    # Data preparation
                    Node("data_load", x=100, y=50, label="Load Data", node_type="input",
                         inputs=0, outputs=1, width=130, height=50),
                    Node("preprocess", x=100, y=150, label="Preprocess", node_type="transform",
                         width=130, height=50),
                    Node("split", x=100, y=250, label="Train/Test Split", node_type="transform",
                         width=130, height=50),
                    # Model training branch
                    Node("train_model", x=300, y=200, label="Train Model", node_type="llm",
                         width=130, height=50),
                    Node("validate", x=300, y=300, label="Validate", node_type="agent",
                         width=130, height=50),
                    # Evaluation
                    Node("evaluate", x=500, y=250, label="Evaluate", node_type="condition",
                         width=130, height=50, outputs=2),
                    Node("deploy", x=650, y=150, label="Deploy", node_type="output",
                         inputs=1, outputs=0, width=130, height=50),
                    Node("retrain", x=650, y=350, label="Retrain", node_type="tool",
                         width=130, height=50),
                    # Connections
                    Edge(source="data_load", target="preprocess"),
                    Edge(source="preprocess", target="split"),
                    Edge(source="split", target="train_model"),
                    Edge(source="train_model", target="validate"),
                    Edge(source="validate", target="evaluate"),
                    Edge(source="evaluate", target="deploy", label="pass", source_port=0),
                    Edge(source="evaluate", target="retrain", label="fail", source_port=1, dashed=True),
                    Edge(source="retrain", target="train_model", dashed=True),
                    id="ai-dag-flow",
                    on_change="/flow/changed",
                ),
                cls="editor-main"
            ),
            cls="app-container"
        ),
        # AI Pipeline Simulation Script
        Script("""
            let aiSimRunning = false;

            // Execute order for the AI pipeline simulation
            const aiExecutionOrder = [
                { nodes: ['data_load'], edges: [] },
                { nodes: ['preprocess'], edges: ['data_load-preprocess'] },
                { nodes: ['split'], edges: ['preprocess-split'] },
                { nodes: ['train_model'], edges: ['split-train_model'] },
                { nodes: ['validate'], edges: ['train_model-validate'] },
                { nodes: ['evaluate'], edges: ['validate-evaluate'] },
                { nodes: ['deploy'], edges: ['evaluate-deploy'] },
            ];

            function setAINodeStatus(graph, nodeId, status) {
                const node = graph.getCellById(nodeId);
                if (!node) return;

                const statusColors = {
                    'success': '#52c41a',
                    'running': '#1890ff',
                    'error': '#ff4d4f',
                    'pending': '#d9d9d9',
                };
                const data = node.getData() || {};
                node.setData({ ...data, status });

                // Update border stroke based on status
                if (status === 'pending') {
                    node.attr('body/strokeWidth', 2);
                } else {
                    node.attr('body/stroke', statusColors[status]);
                    node.attr('body/strokeWidth', status === 'running' ? 3 : 2);
                }
            }

            function setAIEdgeAnimated(graph, sourceId, targetId, animated, color) {
                const edges = graph.getEdges();
                for (const edge of edges) {
                    if (edge.getSourceCellId() === sourceId && edge.getTargetCellId() === targetId) {
                        if (animated) {
                            edge.attr('line/stroke', color || '#8b5cf6');
                            edge.attr('line/strokeDasharray', '5 5');
                            edge.attr('line/style/animation', 'ant-line 30s infinite linear');
                        } else {
                            edge.attr('line/stroke', color || '#94a3b8');
                            edge.attr('line/strokeDasharray', null);
                            edge.attr('line/style/animation', null);
                        }
                        break;
                    }
                }
            }

            async function runAISimulation() {
                if (aiSimRunning) return;
                aiSimRunning = true;

                const graph = window.fastflow?.['ai-dag-flow'];
                if (!graph) {
                    console.error('AI Graph not found');
                    aiSimRunning = false;
                    return;
                }

                const btn = document.getElementById('run-ai-sim');
                btn.textContent = '⏳ Training...';
                btn.disabled = true;

                // Reset all nodes to pending first
                const allNodes = ['data_load', 'preprocess', 'split', 'train_model', 'validate', 'evaluate', 'deploy', 'retrain'];
                for (const nodeId of allNodes) {
                    setAINodeStatus(graph, nodeId, 'pending');
                }

                await new Promise(r => setTimeout(r, 500));

                // Execute each step
                for (let i = 0; i < aiExecutionOrder.length; i++) {
                    const step = aiExecutionOrder[i];

                    // Set nodes to running
                    for (const nodeId of step.nodes) {
                        setAINodeStatus(graph, nodeId, 'running');
                    }

                    // Animate incoming edges
                    for (const edgeKey of step.edges) {
                        const [src, tgt] = edgeKey.split('-');
                        setAIEdgeAnimated(graph, src, tgt, true, '#8b5cf6');
                    }

                    // Wait for "processing"
                    const waitTime = step.nodes.includes('train_model') ? 2000 : 800;
                    await new Promise(r => setTimeout(r, waitTime));

                    // Set nodes to success
                    for (const nodeId of step.nodes) {
                        setAINodeStatus(graph, nodeId, 'success');
                    }

                    // Stop edge animation and set to success color
                    for (const edgeKey of step.edges) {
                        const [src, tgt] = edgeKey.split('-');
                        setAIEdgeAnimated(graph, src, tgt, false, '#52c41a');
                    }

                    await new Promise(r => setTimeout(r, 200));
                }

                btn.textContent = '▶ Run Training';
                btn.disabled = false;
                aiSimRunning = false;
                showStatus('Model training completed successfully!');
            }

            function resetAISimulation() {
                const graph = window.fastflow?.['ai-dag-flow'];
                if (!graph) return;

                const allNodes = ['data_load', 'preprocess', 'split', 'train_model', 'validate', 'evaluate', 'deploy', 'retrain'];
                for (const nodeId of allNodes) {
                    setAINodeStatus(graph, nodeId, 'pending');
                }

                // Reset edges to default gray
                const edgePairs = [
                    ['data_load', 'preprocess'], ['preprocess', 'split'],
                    ['split', 'train_model'], ['train_model', 'validate'],
                    ['validate', 'evaluate'], ['evaluate', 'deploy'],
                    ['evaluate', 'retrain'], ['retrain', 'train_model']
                ];
                for (const [src, tgt] of edgePairs) {
                    setAIEdgeAnimated(graph, src, tgt, false, '#94a3b8');
                }

                showStatus('Pipeline reset');
            }
        """),
        id="tab-ai-dag"
    )


# =============================================================================
# Tab 5: Agent Flow
# =============================================================================
def agent_flow_tab():
    """Complex agent orchestration workflow."""
    return Div(
        Div(
            Aside(
                H3("Agent Nodes", style="margin: 0 0 16px 0; font-size: 14px;"),
                NodePalette(
                    PaletteGroup(
                        PaletteItem("llm", "LLM", icon="", inputs=1, outputs=1),
                        PaletteItem("code", "Code", icon="", inputs=1, outputs=1),
                        title="Processing"
                    ),
                    PaletteGroup(
                        PaletteItem("branch", "Branch", icon="", inputs=1, outputs=2),
                        PaletteItem("loop", "Loop", icon="", inputs=1, outputs=1),
                        title="Control Flow"
                    ),
                    PaletteGroup(
                        PaletteItem("kb", "Knowledge Base", icon="", inputs=1, outputs=1),
                        PaletteItem("mcp", "MCP Server", icon="", inputs=1, outputs=1),
                        PaletteItem("db", "Database", icon="", inputs=1, outputs=1),
                        title="Data Sources"
                    ),
                    target_editor="agent-flow"
                ),
                cls="sidebar"
            ),
            Main(
                FlowEditor(
                    # Start
                    Node("start", x=400, y=30, label="Start", node_type="start",
                         inputs=0, outputs=1),
                    # LLM Router
                    AgentNode("llm_router", x=400, y=120, label="LLM Router", node_type="llm"),
                    # Branch
                    Node("branch1", x=400, y=220, label="Route", node_type="branch",
                         inputs=1, outputs=3),
                    # Code execution path
                    AgentNode("code1", x=150, y=330, label="Code Exec", node_type="code"),
                    # Knowledge base path
                    AgentNode("kb1", x=400, y=330, label="Query KB", node_type="kb"),
                    # MCP/Tool path
                    AgentNode("mcp1", x=650, y=330, label="MCP Tools", node_type="mcp"),
                    # Database
                    AgentNode("db1", x=400, y=430, label="Save to DB", node_type="db"),
                    # Loop back to LLM
                    Node("loop1", x=550, y=430, label="Loop", node_type="loop"),
                    # End
                    Node("end", x=400, y=530, label="End", node_type="end",
                         inputs=1, outputs=0),
                    # Connections
                    Edge(source="start", target="llm_router"),
                    Edge(source="llm_router", target="branch1"),
                    Edge(source="branch1", target="code1", label="code", source_port=0),
                    Edge(source="branch1", target="kb1", label="query", source_port=1),
                    Edge(source="branch1", target="mcp1", label="tool", source_port=2),
                    Edge(source="code1", target="db1"),
                    Edge(source="kb1", target="db1"),
                    Edge(source="mcp1", target="loop1"),
                    Edge(source="loop1", target="llm_router", dashed=True),
                    Edge(source="db1", target="end"),
                    id="agent-flow",
                    on_change="/flow/changed",
                ),
                cls="editor-main"
            ),
            cls="app-container"
        ),
        id="tab-agent"
    )


# =============================================================================
# Tab 6: Flowchart
# =============================================================================
def flowchart_tab():
    """Traditional flowchart with standard shapes."""
    return Div(
        Div(
            Aside(
                H3("Flowchart Shapes", style="margin: 0 0 16px 0; font-size: 14px;"),
                NodePalette(
                    PaletteGroup(
                        PaletteItem("start", "Start/End", icon="⬭", inputs=0, outputs=1),
                        PaletteItem("process", "Process", icon="▭", inputs=1, outputs=1),
                        title="Basic"
                    ),
                    PaletteGroup(
                        PaletteItem("decision", "Decision", icon="◇", inputs=1, outputs=2),
                        PaletteItem("data", "Data", icon="▱", inputs=1, outputs=1),
                        title="Flow Control"
                    ),
                    PaletteGroup(
                        PaletteItem("connector", "Connector", icon="○", inputs=1, outputs=1),
                        title="Connectors"
                    ),
                    target_editor="flowchart-flow"
                ),
                cls="sidebar"
            ),
            Main(
                FlowEditor(
                    # Start - ellipse shape
                    Node("fc_start", x=300, y=30, label="Start", node_type="start",
                         shape="ellipse", width=100, height=50, inputs=0, outputs=1),
                    # Input data - parallelogram shape
                    Node("fc_input", x=300, y=110, label="Get Input", node_type="data",
                         shape="parallelogram", width=120, height=50),
                    # Process - rectangle
                    Node("fc_process1", x=300, y=190, label="Process Data", node_type="process",
                         width=140, height=50),
                    # Decision - diamond shape
                    Node("fc_decision", x=300, y=280, label="Valid?", node_type="decision",
                         shape="diamond", width=120, height=80, inputs=1, outputs=2),
                    # Yes path - rectangle
                    Node("fc_process2", x=120, y=400, label="Save Result", node_type="process",
                         width=120, height=50),
                    # No path - rectangle
                    Node("fc_error", x=480, y=400, label="Log Error", node_type="process",
                         width=120, height=50),
                    # Connector - circle shape
                    Node("fc_connector", x=300, y=500, label="", node_type="connector",
                         shape="circle", width=50, height=50),
                    # Output - parallelogram
                    Node("fc_output", x=300, y=580, label="Output", node_type="data",
                         shape="parallelogram", width=120, height=50),
                    # End - ellipse shape
                    Node("fc_end", x=300, y=670, label="End", node_type="end",
                         shape="ellipse", width=100, height=50, inputs=1, outputs=0),
                    # Connections
                    Edge(source="fc_start", target="fc_input"),
                    Edge(source="fc_input", target="fc_process1"),
                    Edge(source="fc_process1", target="fc_decision"),
                    Edge(source="fc_decision", target="fc_process2", label="Yes", source_port=0),
                    Edge(source="fc_decision", target="fc_error", label="No", source_port=1),
                    Edge(source="fc_process2", target="fc_connector"),
                    Edge(source="fc_error", target="fc_connector"),
                    Edge(source="fc_connector", target="fc_output"),
                    Edge(source="fc_output", target="fc_end"),
                    id="flowchart-flow",
                    height="800px",
                    on_change="/flow/changed",
                ),
                cls="editor-main"
            ),
            cls="app-container"
        ),
        id="tab-flowchart"
    )


# =============================================================================
# Main Page
# =============================================================================
@rt
def index():
    """Main page with tabbed interface."""
    return Titled("Fastflow Examples",
        # Tab navigation
        Div(
            Button("LangGraph", cls="tab-btn active", onclick="showTab('langgraph')"),
            Button("ER Diagram", cls="tab-btn", onclick="showTab('er')"),
            Button("Data DAG", cls="tab-btn", onclick="showTab('data-dag')"),
            Button("AI Pipeline", cls="tab-btn", onclick="showTab('ai-dag')"),
            Button("Agent Flow", cls="tab-btn", onclick="showTab('agent')"),
            Button("Flowchart", cls="tab-btn", onclick="showTab('flowchart')"),
            cls="tab-nav"
        ),
        # Tab content
        Div(
            langgraph_tab(),
            er_diagram_tab(),
            data_dag_tab(),
            ai_model_dag_tab(),
            agent_flow_tab(),
            flowchart_tab(),
            cls="tab-content"
        ),
        # Status bar
        Div(id="status", cls="status-bar"),
        # Export modal
        Div(
            Div(
                H3("Exported Flow Data"),
                Pre(id="export-data", style="max-height: 400px; overflow: auto;"),
                Button("Close", onclick="closeModal()"),
                cls="modal-content"
            ),
            id="export-modal",
            cls="modal",
            style="display: none;"
        ),
        # Styles
        Style("""
            .tab-nav {
                display: flex;
                gap: 8px;
                padding: 16px 20px;
                background: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
            }
            .tab-btn {
                padding: 8px 16px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background: white;
                cursor: pointer;
                font-size: 13px;
                color: #64748b;
                transition: all 0.2s;
            }
            .tab-btn:hover {
                background: #f1f5f9;
                color: #334155;
            }
            .tab-btn.active {
                background: #3b82f6;
                color: white;
                border-color: #3b82f6;
            }
            .tab-content > div {
                display: none;
            }
            .tab-content > div:first-child {
                display: block;
            }
            .app-container {
                display: flex;
                gap: 20px;
                padding: 20px;
                height: calc(100vh - 150px);
                min-height: 600px;
            }
            .sidebar {
                width: 220px;
                flex-shrink: 0;
                overflow-y: auto;
            }
            .editor-main {
                flex: 1;
                height: 100%;
                min-height: 600px;
            }
            /* Ensure FlowEditor fills its container */
            .editor-main .fastflow-container {
                width: 100%;
                height: 100%;
                min-height: 600px;
            }
            .status-bar {
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: #22c55e;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
                opacity: 0;
                transition: opacity 0.3s;
            }
            .status-bar.show {
                opacity: 1;
            }
            .modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }
            .modal-content {
                background: white;
                padding: 24px;
                border-radius: 12px;
                max-width: 600px;
                width: 90%;
            }
            .palette-group {
                margin-bottom: 12px;
            }
            .palette-group-header {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                background: #f1f5f9;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 600;
                color: #64748b;
            }
            .palette-group-header:hover {
                background: #e2e8f0;
            }
            .group-arrow {
                font-size: 10px;
            }
            .palette-group-content {
                padding: 8px 0 0 0;
            }
            /* Status badge styles */
            .status-badge {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-right: 4px;
            }
            /* Fix inline edit text color - prevent white text */
            .fastflow-inline-edit {
                color: #333 !important;
                background: white !important;
            }
        """),
        # Tab switching script
        Script("""
            function showTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content > div').forEach(tab => {
                    tab.style.display = 'none';
                });
                // Show selected tab
                const selectedTab = document.getElementById('tab-' + tabName);
                if (selectedTab) {
                    selectedTab.style.display = 'block';
                }
                // Update button states
                document.querySelectorAll('.tab-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                event.target.classList.add('active');

                // Map tab names to graph IDs
                const graphIdMap = {
                    'langgraph': 'langgraph-flow',
                    'er': 'er-flow',
                    'data-dag': 'data-dag-flow',
                    'ai-dag': 'ai-dag-flow',
                    'agent': 'agent-flow',
                    'flowchart': 'flowchart-flow'
                };

                // Resize and fit graph after tab becomes visible
                const graphId = graphIdMap[tabName];
                if (graphId && window.fastflow && window.fastflow[graphId]) {
                    const graph = window.fastflow[graphId];
                    // Small delay to ensure the tab is fully visible before resizing
                    setTimeout(() => {
                        const container = document.getElementById(graphId);
                        if (container) {
                            // Resize graph to match container
                            graph.resize(container.clientWidth, container.clientHeight);
                            // Fit content to view
                            graph.zoomToFit({ padding: 40, maxScale: 1 });
                        }
                    }, 50);
                }
            }

            function closeModal() {
                document.getElementById('export-modal').style.display = 'none';
            }

            function showStatus(message) {
                const status = document.getElementById('status');
                status.textContent = message;
                status.classList.add('show');
                setTimeout(() => status.classList.remove('show'), 2000);
            }
        """)
    )


@rt("/flow/changed")
def post(event: str = "", data: str = "", flow: str = ""):
    """Handle flow change events."""
    import json

    try:
        event_data = json.loads(data) if data else {}
        print(f"Flow event: {event}")
        print(f"Event data: {event_data}")
        return Script(f"showStatus('Flow updated: {event}')")
    except Exception as e:
        print(f"Error processing flow event: {e}")
        return Script(f"showStatus('Error: {e}')")


if __name__ == "__main__":
    serve()
