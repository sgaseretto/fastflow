"""LangGraph-style agent workflow tab."""

from fasthtml.common import *
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
from fastflow import (
    FlowEditor, Node, Edge, NodePalette, PaletteItem,
)


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
