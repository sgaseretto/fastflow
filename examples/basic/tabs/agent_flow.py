"""Agent Orchestration Flow tab."""

from fasthtml.common import *
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
from fastflow import (
    FlowEditor, Node, Edge, NodePalette, PaletteItem, PaletteGroup,
    AgentNode as UIAgentNode,
)


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
                    UIAgentNode("llm_router", x=400, y=120, label="LLM Router", node_type="llm"),
                    # Branch
                    Node("branch1", x=400, y=220, label="Route", node_type="branch",
                         inputs=1, outputs=3),
                    # Code execution path
                    UIAgentNode("code1", x=150, y=330, label="Code Exec", node_type="code"),
                    # Knowledge base path
                    UIAgentNode("kb1", x=400, y=330, label="Query KB", node_type="kb"),
                    # MCP/Tool path
                    UIAgentNode("mcp1", x=650, y=330, label="MCP Tools", node_type="mcp"),
                    # Database
                    UIAgentNode("db1", x=400, y=430, label="Save to DB", node_type="db"),
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
