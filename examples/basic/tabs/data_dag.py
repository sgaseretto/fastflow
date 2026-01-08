"""Data Processing DAG tab for pipeline visualization."""

from fasthtml.common import *
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
from fastflow import (
    FlowEditor, Edge, NodePalette, PaletteItem, PaletteGroup, DAGNode,
)


# DAG Simulation Script
DAG_SIMULATION_SCRIPT = Script("""
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
            'success': '\\u2713',
            'running': '\\u21bb',
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
        btn.textContent = '\\u23f3 Running...';
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

        btn.textContent = '\\u25b6 Run Simulation';
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
""")


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
                           icon="��", inputs=0, outputs=1,
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
        DAG_SIMULATION_SCRIPT,
        id="tab-data-dag"
    )
