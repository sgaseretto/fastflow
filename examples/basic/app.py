"""
Fastflow Examples - Comprehensive Demo

A tabbed interface showing various workflow types you can build with Fastflow:
1. LangGraph Style - Agent workflow like LangGraph Builder
2. ER Diagram - Database entity-relationship diagram
3. Data Processing DAG - Data pipeline visualization
4. AI Model DAG - ML training pipeline with status
5. Agent Flow - Complex agent orchestration
6. Flowchart - Traditional flowchart shapes
7. Python Execution - Python-based SSE execution with callbacks

Run with: uv run python examples/basic/app.py
"""

from fasthtml.common import *
import sys
from pathlib import Path
import json

# Import fastflow components
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from fastflow import fastflow_headers

# Import tab modules
from tabs import (
    langgraph_tab,
    er_diagram_tab,
    data_dag_tab,
    ai_model_dag_tab,
    agent_flow_tab,
    flowchart_tab,
    python_exec_tab,
    python_executor,
)

# Create app with fastflow headers
app, rt = fast_app(hdrs=fastflow_headers())


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
            Button("Python Exec", cls="tab-btn", onclick="showTab('python-exec')", style="background: #10b981; color: white; border-color: #10b981;"),
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
            python_exec_tab(),
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
        Style(APP_STYLES),
        # Tab switching script
        Script(TAB_SCRIPT)
    )


# =============================================================================
# Routes
# =============================================================================
@rt("/flow/changed")
def post(event: str = "", data: str = "", flow: str = ""):
    """Handle flow change events."""
    try:
        event_data = json.loads(data) if data else {}
        print(f"Flow event: {event}")
        print(f"Event data: {event_data}")
        return Script(f"showStatus('Flow updated: {event}')")
    except Exception as e:
        print(f"Error processing flow event: {e}")
        return Script(f"showStatus('Error: {e}')")


@rt("/execute/python-pipeline")
async def get():
    """
    SSE endpoint for Python-based pipeline execution.

    This demonstrates:
    - FlowExecutor with typed nodes (InputNode, FilterNode, etc.)
    - Two-way callbacks (TimingCallback, SSECallback, custom StatusUpdateCallback)
    - Real-time SSE streaming to browser
    - Type-dispatched execution via execute()
    """
    async def event_generator():
        # Run the executor and yield SSE messages
        async for msg in python_executor.run():
            yield msg

    return EventStream(event_generator())


# =============================================================================
# Styles
# =============================================================================
APP_STYLES = """
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
"""


# =============================================================================
# Scripts
# =============================================================================
TAB_SCRIPT = """
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
            'flowchart': 'flowchart-flow',
            'python-exec': 'python-exec-flow'
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
"""


if __name__ == "__main__":
    serve()
