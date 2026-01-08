"""AI Model Training Pipeline tab."""

from fasthtml.common import *
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
from fastflow import FlowEditor, Node, Edge


# AI Pipeline Simulation Script
AI_SIMULATION_SCRIPT = Script("""
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
        btn.textContent = '\\u23f3 Training...';
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

        btn.textContent = '\\u25b6 Run Training';
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
""")


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
        AI_SIMULATION_SCRIPT,
        id="tab-ai-dag"
    )
