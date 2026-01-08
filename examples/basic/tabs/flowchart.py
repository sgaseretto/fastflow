"""Traditional Flowchart tab."""

from fasthtml.common import *
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
from fastflow import (
    FlowEditor, Node, Edge, NodePalette, PaletteItem, PaletteGroup,
)


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
