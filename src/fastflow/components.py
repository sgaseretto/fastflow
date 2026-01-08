"""
FastHTML components for Fastflow.

Provides FlowEditor, Node, Edge, NodePalette, and PaletteItem components
that integrate AntV X6 with FastHTML.
"""

from fasthtml.common import Div, Script, to_xml, Button, Span, H4, P, Ul, Li
from typing import Optional, Any, Literal
import json


# Type aliases for better documentation
PortPosition = Literal["top", "right", "bottom", "left"]
NodeShape = Literal["rect", "circle", "polygon", "diamond", "ellipse"]
NodeStatus = Literal["default", "success", "error", "running"]
ConnectorType = Literal["smooth", "rounded", "manhattan", "normal"]
RouterType = Literal["manhattan", "orth", "metro", "er", "normal"]


# Extended node style mappings including all example types
NODE_STYLES = {
    # LangGraph-style nodes
    'start': {'fill': '#1e293b', 'stroke': '#1e293b', 'textColor': '#fff', 'rx': 20, 'ry': 20},
    'end': {'fill': '#1e293b', 'stroke': '#1e293b', 'textColor': '#fff', 'rx': 20, 'ry': 20},
    'agent': {'fill': '#dbeafe', 'stroke': '#60a5fa', 'textColor': '#1e40af', 'rx': 8, 'ry': 8},
    'tool': {'fill': '#fce7f3', 'stroke': '#f472b6', 'textColor': '#9d174d', 'rx': 8, 'ry': 8},
    'llm': {'fill': '#f3e8ff', 'stroke': '#c084fc', 'textColor': '#6b21a8', 'rx': 8, 'ry': 8},
    'condition': {'fill': '#fef3c7', 'stroke': '#fbbf24', 'textColor': '#92400e', 'rx': 8, 'ry': 8},

    # Data processing DAG nodes
    'input': {'fill': '#dcfce7', 'stroke': '#4ade80', 'textColor': '#166534', 'rx': 8, 'ry': 8},
    'output': {'fill': '#fee2e2', 'stroke': '#f87171', 'textColor': '#991b1b', 'rx': 8, 'ry': 8},
    'filter': {'fill': '#e0f2fe', 'stroke': '#38bdf8', 'textColor': '#0369a1', 'rx': 8, 'ry': 8},
    'join': {'fill': '#fef3c7', 'stroke': '#fbbf24', 'textColor': '#92400e', 'rx': 8, 'ry': 8},
    'union': {'fill': '#f3e8ff', 'stroke': '#c084fc', 'textColor': '#6b21a8', 'rx': 8, 'ry': 8},
    'agg': {'fill': '#fce7f3', 'stroke': '#f472b6', 'textColor': '#9d174d', 'rx': 8, 'ry': 8},
    'transform': {'fill': '#e0f2fe', 'stroke': '#38bdf8', 'textColor': '#0369a1', 'rx': 8, 'ry': 8},

    # Agent flow nodes
    'code': {'fill': '#e6fffb', 'stroke': '#08979c', 'textColor': '#08979c', 'rx': 8, 'ry': 8},
    'branch': {'fill': '#fff7e6', 'stroke': '#fa8c16', 'textColor': '#fa8c16', 'rx': 8, 'ry': 8},
    'loop': {'fill': '#fff7e6', 'stroke': '#fa8c16', 'textColor': '#fa8c16', 'rx': 8, 'ry': 8},
    'kb': {'fill': '#f0f5ff', 'stroke': '#1d39c4', 'textColor': '#1d39c4', 'rx': 8, 'ry': 8},
    'mcp': {'fill': '#e6fffb', 'stroke': '#08979c', 'textColor': '#08979c', 'rx': 8, 'ry': 8},
    'db': {'fill': '#f0f5ff', 'stroke': '#1d39c4', 'textColor': '#1d39c4', 'rx': 8, 'ry': 8},

    # Flowchart shapes
    'process': {'fill': '#eff4ff', 'stroke': '#5f95ff', 'textColor': '#262626', 'rx': 0, 'ry': 0},
    'decision': {'fill': '#eff4ff', 'stroke': '#5f95ff', 'textColor': '#262626', 'rx': 0, 'ry': 0},
    'data': {'fill': '#eff4ff', 'stroke': '#5f95ff', 'textColor': '#262626', 'rx': 0, 'ry': 0},
    'connector': {'fill': '#eff4ff', 'stroke': '#5f95ff', 'textColor': '#262626', 'rx': 22, 'ry': 22},

    # ER Diagram nodes
    'table': {'fill': '#fff', 'stroke': '#1890ff', 'textColor': '#262626', 'rx': 8, 'ry': 8},

    # Default
    'default': {'fill': '#f1f5f9', 'stroke': '#94a3b8', 'textColor': '#334155', 'rx': 8, 'ry': 8},
}


def FlowEditor(
    *children,
    id: str = "flowgraph",
    width: str = "100%",
    height: str = "600px",
    grid: bool = True,
    grid_size: int = 10,
    panning: bool = True,
    mousewheel: bool = True,
    connecting: bool = True,
    selecting: bool = True,
    readonly: bool = False,
    auto_fit: bool = True,
    on_change: Optional[str] = None,
    on_node_select: Optional[str] = None,
    on_node_added: Optional[str] = None,
    on_node_removed: Optional[str] = None,
    on_edge_connected: Optional[str] = None,
    on_edge_removed: Optional[str] = None,
    initial_data: Optional[str] = None,
    cls: str = "",
    **kwargs
):
    """
    Create an X6 graph editor container.

    Args:
        *children: Node and Edge components to initialize the flow
        id: Container ID
        width: Canvas width
        height: Canvas height
        grid: Show background grid
        grid_size: Grid cell size in pixels
        panning: Enable canvas panning
        mousewheel: Enable zoom with mousewheel
        connecting: Enable edge creation by dragging
        selecting: Enable node/edge selection
        readonly: Make the graph read-only
        auto_fit: Auto-fit content to viewport after initialization (default True)
        on_change: HTMX endpoint for any flow change
        on_node_select: HTMX endpoint for node selection
        on_node_added: HTMX endpoint for node creation
        on_node_removed: HTMX endpoint for node removal
        on_edge_connected: HTMX endpoint for edge creation
        on_edge_removed: HTMX endpoint for edge removal
        initial_data: JSON string of initial flow data
        cls: Additional CSS classes
        **kwargs: Additional attributes

    Example:
        ```python
        FlowEditor(
            Node("start", x=100, y=100, label="__start__", node_type="start"),
            Node("agent", x=300, y=200, label="Node 1", node_type="agent"),
            Edge(source="start", target="agent", label="conditional_edge_1"),
            on_change="/flow/changed",
        )
        ```
    """
    # Parse children to extract nodes and edges
    nodes = []
    edges = []
    other_children = []

    for child in children:
        if isinstance(child, dict):
            if child.get("_type") == "node":
                nodes.append(child)
            elif child.get("_type") == "edge":
                edges.append(child)
            else:
                other_children.append(child)
        else:
            other_children.append(child)

    # Build configuration object
    config = {
        "width": width,
        "height": height,
        "grid": grid,
        "gridSize": grid_size,
        "panning": panning,
        "mousewheel": mousewheel,
        "connecting": connecting,
        "selecting": selecting,
        "readonly": readonly,
        "autoFit": auto_fit,
        "endpoints": {},
        "nodes": nodes,
        "edges": edges,
    }

    # Add event endpoints
    if on_change:
        config["endpoints"]["change"] = on_change
    if on_node_select:
        config["endpoints"]["nodeSelected"] = on_node_select
    if on_node_added:
        config["endpoints"]["nodeAdded"] = on_node_added
    if on_node_removed:
        config["endpoints"]["nodeRemoved"] = on_node_removed
    if on_edge_connected:
        config["endpoints"]["edgeConnected"] = on_edge_connected
    if on_edge_removed:
        config["endpoints"]["edgeRemoved"] = on_edge_removed

    # Handle initial data
    if initial_data:
        config["initialData"] = initial_data

    config_json = json.dumps(config)

    # Build container classes
    container_cls = f"fastflow-container {cls}".strip()

    return Div(
        # The X6 graph container
        Div(id=f"{id}-graph", cls="fastflow-graph"),
        # Other children (like controls)
        *other_children,
        # Initialization script
        Script(f"""
(function() {{
    function initGraph() {{
        // Wait for X6 to be available
        if (typeof X6 === 'undefined') {{
            setTimeout(initGraph, 50);
            return;
        }}

        const container = document.getElementById('{id}-graph');
        if (!container) {{
            setTimeout(initGraph, 50);
            return;
        }}

        const config = {config_json};

        // Create X6 Graph instance
        const graph = new X6.Graph({{
            container: container,
            width: container.clientWidth || 800,
            height: container.clientHeight || 600,
            background: {{
                color: '#fafafa',
            }},
            grid: config.grid ? {{
                visible: true,
                type: 'dot',
                size: config.gridSize,
                args: {{
                    color: '#d4d4d4',
                    thickness: 1,
                }}
            }} : false,
            // Enable keyboard for delete shortcuts
            keyboard: {{
                enabled: true,
                global: false,
            }},
            panning: {{
                enabled: config.panning,
                eventTypes: ['leftMouseDown', 'mouseWheel'],
            }},
            mousewheel: {{
                enabled: config.mousewheel,
                zoomAtMousePosition: true,
                modifiers: 'ctrl',
                minScale: 0.5,
                maxScale: 3,
            }},
            connecting: config.connecting ? {{
                router: 'manhattan',
                connector: {{
                    name: 'rounded',
                    args: {{
                        radius: 8,
                    }},
                }},
                anchor: 'center',
                connectionPoint: 'anchor',
                allowBlank: false,
                snap: {{
                    radius: 20,
                }},
                createEdge() {{
                    return graph.createEdge({{
                        attrs: {{
                            line: {{
                                stroke: '#94a3b8',
                                strokeWidth: 2,
                                targetMarker: {{
                                    name: 'block',
                                    width: 12,
                                    height: 8,
                                }},
                            }},
                        }},
                        zIndex: 0,
                    }});
                }},
                validateConnection({{ targetMagnet }}) {{
                    return !!targetMagnet;
                }},
            }} : false,
            highlighting: {{
                magnetAdsorbed: {{
                    name: 'stroke',
                    args: {{
                        attrs: {{
                            fill: '#5F95FF',
                            stroke: '#5F95FF',
                        }},
                    }},
                }},
            }},
            selecting: config.selecting ? {{
                enabled: true,
                rubberband: true,
                showNodeSelectionBox: true,
            }} : false,
            interacting: !config.readonly,
        }});

        // Store reference globally
        window.fastflow = window.fastflow || {{}};
        window.fastflow['{id}'] = graph;

        // ==========================================
        // REGISTER CUSTOM SHAPES
        // ==========================================

        // Register Polygon shape for flowchart diamond
        if (!X6.Graph.registerNode.registered?.['flowchart-diamond']) {{
            X6.Graph.registerNode('flowchart-diamond', {{
                inherit: 'polygon',
                width: 100,
                height: 60,
                attrs: {{
                    body: {{
                        strokeWidth: 2,
                        stroke: '#5F95FF',
                        fill: '#EFF4FF',
                        refPoints: '0.5,0 1,0.5 0.5,1 0,0.5',
                    }},
                    label: {{
                        fontSize: 13,
                        fill: '#262626',
                        textAnchor: 'middle',
                        textVerticalAnchor: 'middle',
                        refX: '50%',
                        refY: '50%',
                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    }},
                }},
            }}, true);
        }}

        // Register Ellipse shape for flowchart start/end
        if (!X6.Graph.registerNode.registered?.['flowchart-ellipse']) {{
            X6.Graph.registerNode('flowchart-ellipse', {{
                inherit: 'ellipse',
                width: 100,
                height: 50,
                attrs: {{
                    body: {{
                        strokeWidth: 2,
                        stroke: '#5F95FF',
                        fill: '#EFF4FF',
                    }},
                    label: {{
                        fontSize: 13,
                        fill: '#262626',
                        textAnchor: 'middle',
                        textVerticalAnchor: 'middle',
                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    }},
                }},
            }}, true);
        }}

        // Register Parallelogram shape for flowchart data
        if (!X6.Graph.registerNode.registered?.['flowchart-parallelogram']) {{
            X6.Graph.registerNode('flowchart-parallelogram', {{
                inherit: 'polygon',
                width: 100,
                height: 50,
                attrs: {{
                    body: {{
                        strokeWidth: 2,
                        stroke: '#5F95FF',
                        fill: '#EFF4FF',
                        refPoints: '0.1,0 1,0 0.9,1 0,1',
                    }},
                    label: {{
                        fontSize: 13,
                        fill: '#262626',
                        textAnchor: 'middle',
                        textVerticalAnchor: 'middle',
                        refX: '50%',
                        refY: '50%',
                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    }},
                }},
            }}, true);
        }}

        // Register Circle connector for flowchart
        if (!X6.Graph.registerNode.registered?.['flowchart-circle']) {{
            X6.Graph.registerNode('flowchart-circle', {{
                inherit: 'circle',
                width: 50,
                height: 50,
                attrs: {{
                    body: {{
                        strokeWidth: 2,
                        stroke: '#5F95FF',
                        fill: '#EFF4FF',
                    }},
                    label: {{
                        fontSize: 13,
                        fill: '#262626',
                        textAnchor: 'middle',
                        textVerticalAnchor: 'middle',
                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    }},
                }},
            }}, true);
        }}

        // ==========================================
        // END CUSTOM SHAPES
        // ==========================================

        // Register custom port layout
        const portAttrs = {{
            circle: {{
                r: 5,
                magnet: true,
                stroke: '#5F95FF',
                strokeWidth: 1,
                fill: '#fff',
                style: {{
                    visibility: 'hidden',
                }},
            }},
        }};

        // Port visibility on hover
        graph.on('node:mouseenter', ({{ node }}) => {{
            const ports = node.getPorts();
            ports.forEach((port) => {{
                node.setPortProp(port.id, 'attrs/circle/style/visibility', 'visible');
            }});
        }});

        graph.on('node:mouseleave', ({{ node }}) => {{
            const ports = node.getPorts();
            ports.forEach((port) => {{
                node.setPortProp(port.id, 'attrs/circle/style/visibility', 'hidden');
            }});
        }});

        // Node style mappings - extended with all types
        const nodeStyles = {{
            // LangGraph-style nodes
            'start': {{ fill: '#1e293b', stroke: '#1e293b', textColor: '#fff', rx: 20, ry: 20 }},
            'end': {{ fill: '#1e293b', stroke: '#1e293b', textColor: '#fff', rx: 20, ry: 20 }},
            'agent': {{ fill: '#dbeafe', stroke: '#60a5fa', textColor: '#1e40af', rx: 8, ry: 8 }},
            'tool': {{ fill: '#fce7f3', stroke: '#f472b6', textColor: '#9d174d', rx: 8, ry: 8 }},
            'llm': {{ fill: '#f3e8ff', stroke: '#c084fc', textColor: '#6b21a8', rx: 8, ry: 8 }},
            'condition': {{ fill: '#fef3c7', stroke: '#fbbf24', textColor: '#92400e', rx: 8, ry: 8 }},
            // Data processing DAG nodes
            'input': {{ fill: '#dcfce7', stroke: '#4ade80', textColor: '#166534', rx: 8, ry: 8 }},
            'output': {{ fill: '#fee2e2', stroke: '#f87171', textColor: '#991b1b', rx: 8, ry: 8 }},
            'filter': {{ fill: '#e0f2fe', stroke: '#38bdf8', textColor: '#0369a1', rx: 8, ry: 8 }},
            'join': {{ fill: '#fef3c7', stroke: '#fbbf24', textColor: '#92400e', rx: 8, ry: 8 }},
            'union': {{ fill: '#f3e8ff', stroke: '#c084fc', textColor: '#6b21a8', rx: 8, ry: 8 }},
            'agg': {{ fill: '#fce7f3', stroke: '#f472b6', textColor: '#9d174d', rx: 8, ry: 8 }},
            'transform': {{ fill: '#e0f2fe', stroke: '#38bdf8', textColor: '#0369a1', rx: 8, ry: 8 }},
            // Agent flow nodes
            'code': {{ fill: '#e6fffb', stroke: '#08979c', textColor: '#08979c', rx: 8, ry: 8 }},
            'branch': {{ fill: '#fff7e6', stroke: '#fa8c16', textColor: '#fa8c16', rx: 8, ry: 8 }},
            'loop': {{ fill: '#fff7e6', stroke: '#fa8c16', textColor: '#fa8c16', rx: 8, ry: 8 }},
            'kb': {{ fill: '#f0f5ff', stroke: '#1d39c4', textColor: '#1d39c4', rx: 8, ry: 8 }},
            'mcp': {{ fill: '#e6fffb', stroke: '#08979c', textColor: '#08979c', rx: 8, ry: 8 }},
            'db': {{ fill: '#f0f5ff', stroke: '#1d39c4', textColor: '#1d39c4', rx: 8, ry: 8 }},
            // Flowchart shapes
            'process': {{ fill: '#eff4ff', stroke: '#5f95ff', textColor: '#262626', rx: 0, ry: 0 }},
            'decision': {{ fill: '#eff4ff', stroke: '#5f95ff', textColor: '#262626', rx: 0, ry: 0 }},
            'data': {{ fill: '#eff4ff', stroke: '#5f95ff', textColor: '#262626', rx: 0, ry: 0 }},
            'connector': {{ fill: '#eff4ff', stroke: '#5f95ff', textColor: '#262626', rx: 22, ry: 22 }},
            // ER Diagram
            'table': {{ fill: '#fff', stroke: '#1890ff', textColor: '#262626', rx: 8, ry: 8 }},
            // Default
            'default': {{ fill: '#f1f5f9', stroke: '#94a3b8', textColor: '#334155', rx: 8, ry: 8 }},
        }};

        // Status colors for node status indicators
        const statusColors = {{
            'success': '#52c41a',
            'error': '#ff4d4f',
            'running': '#1890ff',
            'pending': '#d9d9d9',
        }};

        // Helper function to create ER table node (SVG-based)
        function createERTableNode(nodeConfig, style) {{
            const columns = nodeConfig.data?.columns || [];
            const headerHeight = 36;
            const rowHeight = 24;
            const nodeWidth = nodeConfig.width || 220;
            const nodeHeight = headerHeight + (columns.length * rowHeight) + 12;
            const headerFill = nodeConfig.data?.headerFill || '#1890ff';
            const headerColor = nodeConfig.data?.headerColor || '#fff';

            // Build markup for table using foreignObject for HTML content
            const markup = [
                {{ tagName: 'rect', selector: 'body' }},
                {{
                    tagName: 'foreignObject',
                    selector: 'fo',
                    children: [
                        {{
                            ns: 'http://www.w3.org/1999/xhtml',
                            tagName: 'div',
                            selector: 'foBody',
                        }},
                    ],
                }},
            ];

            // Build HTML content for the table - matching X6 ER example styling
            let htmlContent = `<div class="er-table" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 100%; height: 100%; display: flex; flex-direction: column; background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border-radius: 6px; overflow: hidden;">`;
            // Header with gradient
            htmlContent += `<div style="background: linear-gradient(135deg, ${{headerFill}} 0%, #096dd9 100%); color: ${{headerColor}}; padding: 8px 12px; font-size: 13px; font-weight: 600; text-align: center; border-radius: 6px 6px 0 0;">${{nodeConfig.label || nodeConfig.name}}</div>`;
            // Fields container
            htmlContent += `<div style="flex: 1; overflow: hidden; border-radius: 0 0 6px 6px;">`;

            columns.forEach((col, idx) => {{
                // Different background colors for different key types
                let bgColor;
                if (col.pk) {{
                    bgColor = '#e6f7ff';  // Light blue for primary keys
                }} else if (col.fk) {{
                    bgColor = '#fff7e6';  // Light orange for foreign keys
                }} else {{
                    bgColor = idx % 2 === 0 ? '#fafafa' : '#fff';
                }}

                let keyIcon = '';
                if (col.pk) keyIcon = '<span style="margin-right: 4px; font-size: 10px;">🔑</span>';
                else if (col.fk) keyIcon = '<span style="margin-right: 4px; font-size: 10px;">🔗</span>';

                const isLast = idx === columns.length - 1;
                const borderBottom = isLast ? '' : 'border-bottom: 1px solid #e8e8e8;';
                const borderRadius = isLast ? 'border-radius: 0 0 6px 6px;' : '';

                htmlContent += `<div style="display: flex; align-items: center; padding: 4px 8px; background: ${{bgColor}}; font-size: 11px; ${{borderBottom}} ${{borderRadius}} transition: background-color 0.2s;">`;
                htmlContent += `<span style="flex: 1; font-weight: 500; color: #262626;">${{keyIcon}}${{col.name}}</span>`;
                htmlContent += `<span style="color: #666; font-family: Monaco, Menlo, monospace; font-size: 10px;">${{col.type}}</span>`;
                htmlContent += `</div>`;
            }});

            htmlContent += `</div></div>`;

            const attrs = {{
                body: {{
                    width: nodeWidth,
                    height: nodeHeight,
                    fill: 'transparent',
                    stroke: headerFill,
                    strokeWidth: 2,
                    rx: 8,
                    ry: 8,
                    filter: 'drop-shadow(0 4px 12px rgba(0, 0, 0, 0.1))',
                }},
                fo: {{
                    width: nodeWidth,
                    height: nodeHeight,
                    x: 0,
                    y: 0,
                }},
                foBody: {{
                    style: {{
                        width: '100%',
                        height: '100%',
                    }},
                    html: htmlContent,
                }},
            }};

            // Port style - hidden by default, shown on hover via CSS
            const portAttrs = {{
                circle: {{
                    r: 4,
                    magnet: true,
                    stroke: '#1890ff',
                    strokeWidth: 2,
                    fill: '#fff',
                    style: {{ visibility: 'hidden' }},
                }},
            }};

            return graph.addNode({{
                id: nodeConfig.id || nodeConfig.name,
                shape: 'rect',
                x: nodeConfig.x || 0,
                y: nodeConfig.y || 0,
                width: nodeWidth,
                height: nodeHeight,
                markup: markup,
                attrs: attrs,
                ports: {{
                    groups: {{
                        top: {{ position: 'top', attrs: portAttrs }},
                        bottom: {{ position: 'bottom', attrs: portAttrs }},
                        left: {{ position: 'left', attrs: portAttrs }},
                        right: {{ position: 'right', attrs: portAttrs }},
                    }},
                    items: [
                        {{ id: 'port_top', group: 'top' }},
                        {{ id: 'port_bottom', group: 'bottom' }},
                        {{ id: 'port_left', group: 'left' }},
                        {{ id: 'port_right', group: 'right' }},
                    ],
                }},
                data: {{
                    name: nodeConfig.name,
                    label: nodeConfig.label,
                    nodeType: 'table',
                    ...nodeConfig.data
                }},
            }});
        }}

        // Helper function to create DAG node with left status bar using foreignObject
        function createDAGNode(nodeConfig, style, statusBorderColor) {{
            const nodeWidth = nodeConfig.width || 180;
            const nodeHeight = nodeConfig.height || 44;
            const icon = nodeConfig.icon || '⚙️';
            const labelText = nodeConfig.label || nodeConfig.name;
            const status = nodeConfig.status;

            const statusColor = status ? statusColors[status] : '#d9d9d9';
            const statusSymbol = status === 'success' ? '✓' : status === 'error' ? '✕' : status === 'running' ? '↻' : '';
            const statusBgColor = status === 'error' ? '#fef2f2' : status === 'success' ? '#f0fdf4' : status === 'running' ? '#eff6ff' : '#f9fafb';

            // Build markup using foreignObject for HTML content
            const markup = [
                {{ tagName: 'rect', selector: 'body' }},
                {{
                    tagName: 'foreignObject',
                    selector: 'fo',
                    children: [
                        {{
                            ns: 'http://www.w3.org/1999/xhtml',
                            tagName: 'div',
                            selector: 'foBody',
                        }},
                    ],
                }},
            ];

            // Build HTML content for the DAG node
            let htmlContent = `<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 100%; height: 100%; display: flex; align-items: center; position: relative;">`;
            // Status bar on the left
            htmlContent += `<div style="position: absolute; left: 0; top: 0; width: 4px; height: 100%; background: ${{statusColor}}; border-radius: 2px 0 0 2px;"></div>`;
            // Icon
            htmlContent += `<div style="margin-left: 16px; font-size: 16px;">${{icon}}</div>`;
            // Label
            htmlContent += `<div style="flex: 1; margin-left: 8px; font-size: 13px; color: #374151; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${{labelText}}</div>`;
            // Status circle with symbol
            if (status) {{
                htmlContent += `<div style="width: 20px; height: 20px; border-radius: 50%; background: ${{statusBgColor}}; border: 1.5px solid ${{statusColor}}; display: flex; align-items: center; justify-content: center; margin-right: 8px;">`;
                htmlContent += `<span style="font-size: 11px; font-weight: bold; color: ${{statusColor}};">${{statusSymbol}}</span>`;
                htmlContent += `</div>`;
            }}
            htmlContent += `</div>`;

            const attrs = {{
                body: {{
                    width: nodeWidth,
                    height: nodeHeight,
                    fill: '#fff',
                    stroke: '#e5e7eb',
                    strokeWidth: 1,
                    rx: 6,
                    ry: 6,
                }},
                fo: {{
                    width: nodeWidth,
                    height: nodeHeight,
                    x: 0,
                    y: 0,
                }},
                foBody: {{
                    style: {{
                        width: '100%',
                        height: '100%',
                    }},
                    html: htmlContent,
                }},
            }};

            return graph.addNode({{
                id: nodeConfig.id || nodeConfig.name,
                shape: 'rect',
                x: nodeConfig.x || 0,
                y: nodeConfig.y || 0,
                width: nodeWidth,
                height: nodeHeight,
                markup: markup,
                attrs: attrs,
                ports: {{
                    groups: {{
                        left: {{ position: 'left', attrs: {{ circle: {{ r: 5, magnet: true, stroke: '#52c41a', strokeWidth: 2, fill: '#fff', style: {{ visibility: 'hidden' }} }} }} }},
                        right: {{ position: 'right', attrs: {{ circle: {{ r: 5, magnet: true, stroke: '#52c41a', strokeWidth: 2, fill: '#fff', style: {{ visibility: 'hidden' }} }} }} }},
                    }},
                    items: [
                        {{ id: 'in_0', group: 'left' }},
                        {{ id: 'out_0', group: 'right' }},
                    ],
                }},
                data: {{
                    name: nodeConfig.name,
                    label: labelText,
                    nodeType: nodeConfig.node_type,
                    status: status,
                    ...nodeConfig.data
                }},
            }});
        }}

        // Add initial nodes
        const nodeMap = {{}};
        if (config.nodes && config.nodes.length > 0) {{
            config.nodes.forEach(function(nodeConfig) {{
                const nodeType = nodeConfig.node_type || 'default';
                const customShape = nodeConfig.shape || 'rect';
                let style = nodeStyles[nodeType] || nodeStyles['default'];
                const isStartEnd = nodeType === 'start' || nodeType === 'end';

                // Allow custom colors to override defaults
                if (nodeConfig.fill) style = {{ ...style, fill: nodeConfig.fill }};
                if (nodeConfig.stroke) style = {{ ...style, stroke: nodeConfig.stroke }};
                if (nodeConfig.text_color) style = {{ ...style, textColor: nodeConfig.text_color }};

                // Status-based border color
                const statusBorderColor = nodeConfig.status ? statusColors[nodeConfig.status] : null;

                // Handle special node types
                if (nodeType === 'table' || customShape === 'table') {{
                    // ER Table node
                    const node = createERTableNode(nodeConfig, style);
                    nodeMap[nodeConfig.name] = node.id;
                    return;
                }}

                // DAG nodes with status bars (data processing types)
                const dagTypes = ['input', 'output', 'filter', 'join', 'union', 'agg', 'transform'];
                if (dagTypes.includes(nodeType) && nodeConfig.status !== undefined) {{
                    const node = createDAGNode(nodeConfig, style, statusBorderColor);
                    nodeMap[nodeConfig.name] = node.id;
                    return;
                }}

                // Determine shape to use
                let shapeToUse = 'rect';
                if (nodeType === 'decision' || customShape === 'diamond' || customShape === 'polygon') {{
                    shapeToUse = 'flowchart-diamond';
                }} else if (customShape === 'ellipse' || (isStartEnd && customShape !== 'rect')) {{
                    shapeToUse = 'flowchart-ellipse';
                }} else if (customShape === 'parallelogram' || nodeType === 'data') {{
                    shapeToUse = 'flowchart-parallelogram';
                }} else if (nodeType === 'connector' || customShape === 'circle') {{
                    shapeToUse = 'flowchart-circle';
                }}

                const ports = [];

                // Determine port positions (can be customized via port_positions)
                const portPositions = nodeConfig.port_positions || {{}};
                const inputGroup = portPositions.inputs || 'top';
                const outputGroup = portPositions.outputs || 'bottom';

                // Add input ports
                for (let i = 0; i < (nodeConfig.inputs || 0); i++) {{
                    ports.push({{
                        id: 'in_' + i,
                        group: inputGroup,
                        attrs: {{
                            circle: {{
                                r: 5,
                                magnet: true,
                                stroke: '#5F95FF',
                                strokeWidth: 1,
                                fill: '#fff',
                                style: {{ visibility: 'hidden' }},
                            }},
                        }},
                    }});
                }}

                // Add output ports
                for (let i = 0; i < (nodeConfig.outputs || 0); i++) {{
                    ports.push({{
                        id: 'out_' + i,
                        group: outputGroup,
                        attrs: {{
                            circle: {{
                                r: 5,
                                magnet: true,
                                stroke: '#5F95FF',
                                strokeWidth: 1,
                                fill: '#fff',
                                style: {{ visibility: 'hidden' }},
                            }},
                        }},
                    }});
                }}

                const nodeWidth = isStartEnd ? 120 : (nodeConfig.width || 160);
                const nodeHeight = isStartEnd ? 40 : (nodeConfig.height || 50);

                // Build label text (include icon if provided)
                let labelText = nodeConfig.label || nodeConfig.name;
                if (nodeConfig.icon) {{
                    labelText = nodeConfig.icon + ' ' + labelText;
                }}

                // Build node attrs based on shape
                let nodeAttrs;
                if (shapeToUse === 'rect') {{
                    nodeAttrs = {{
                        body: {{
                            fill: style.fill,
                            stroke: statusBorderColor || style.stroke,
                            strokeWidth: statusBorderColor ? 3 : 2,
                            rx: style.rx,
                            ry: style.ry,
                        }},
                        label: {{
                            text: labelText,
                            fill: style.textColor,
                            fontSize: 14,
                            fontWeight: isStartEnd ? 600 : 500,
                            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                        }},
                    }};
                }} else {{
                    // Custom shapes (diamond, ellipse, parallelogram, circle)
                    nodeAttrs = {{
                        body: {{
                            fill: style.fill,
                            stroke: statusBorderColor || style.stroke,
                            strokeWidth: 2,
                        }},
                        label: {{
                            text: labelText,
                            fill: style.textColor,
                            fontSize: 13,
                            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                        }},
                    }};
                }}

                const node = graph.addNode({{
                    id: nodeConfig.id || nodeConfig.name,
                    shape: shapeToUse,
                    x: nodeConfig.x || 0,
                    y: nodeConfig.y || 0,
                    width: nodeWidth,
                    height: nodeHeight,
                    attrs: nodeAttrs,
                    ports: {{
                        groups: {{
                            top: {{
                                position: 'top',
                                attrs: {{
                                    circle: {{
                                        r: 5,
                                        magnet: true,
                                        stroke: '#5F95FF',
                                        strokeWidth: 1,
                                        fill: '#fff',
                                        style: {{ visibility: 'hidden' }},
                                    }},
                                }},
                            }},
                            bottom: {{
                                position: 'bottom',
                                attrs: {{
                                    circle: {{
                                        r: 5,
                                        magnet: true,
                                        stroke: '#5F95FF',
                                        strokeWidth: 1,
                                        fill: '#fff',
                                        style: {{ visibility: 'hidden' }},
                                    }},
                                }},
                            }},
                            left: {{
                                position: 'left',
                                attrs: {{
                                    circle: {{
                                        r: 5,
                                        magnet: true,
                                        stroke: '#5F95FF',
                                        strokeWidth: 1,
                                        fill: '#fff',
                                        style: {{ visibility: 'hidden' }},
                                    }},
                                }},
                            }},
                            right: {{
                                position: 'right',
                                attrs: {{
                                    circle: {{
                                        r: 5,
                                        magnet: true,
                                        stroke: '#5F95FF',
                                        strokeWidth: 1,
                                        fill: '#fff',
                                        style: {{ visibility: 'hidden' }},
                                    }},
                                }},
                            }},
                        }},
                        items: ports,
                    }},
                    data: {{
                        name: nodeConfig.name,
                        label: nodeConfig.label,
                        nodeType: nodeConfig.node_type,
                        ...nodeConfig.data
                    }},
                }});

                nodeMap[nodeConfig.name] = node.id;
            }});
        }}

        // Add initial edges
        if (config.edges && config.edges.length > 0) {{
            config.edges.forEach(function(edgeConfig) {{
                const sourceId = nodeMap[edgeConfig.source] || edgeConfig.source;
                const targetId = nodeMap[edgeConfig.target] || edgeConfig.target;

                // Get marker type
                const markerMap = {{
                    'block': {{ name: 'block', width: 12, height: 8 }},
                    'classic': {{ name: 'classic', size: 10 }},
                    'diamond': {{ name: 'diamond', size: 10 }},
                    'circle': {{ name: 'circle', size: 8 }},
                    'arrow': {{ name: 'classic', size: 12 }},
                }};
                const marker = markerMap[edgeConfig.marker] || markerMap['block'];

                const edgeAttrs = {{
                    line: {{
                        stroke: edgeConfig.color || '#94a3b8',
                        strokeWidth: 2,
                        targetMarker: marker,
                    }},
                }};

                // Dashed line for conditional edges
                if (edgeConfig.dashed) {{
                    edgeAttrs.line.strokeDasharray = '5 5';
                }}

                // Animated edge (for running status)
                if (edgeConfig.animated) {{
                    edgeAttrs.line.strokeDasharray = '5 5';
                    edgeAttrs.line.style = {{
                        animation: 'ant-line 30s infinite linear',
                    }};
                }}

                // Get router configuration
                const routerName = edgeConfig.router || 'manhattan';
                const routerConfig = routerName === 'er'
                    ? {{ name: 'er', args: {{ offset: 'center' }} }}
                    : {{ name: routerName, args: {{ padding: 20 }} }};

                // Get connector configuration
                const connectorName = edgeConfig.connector || 'rounded';
                const connectorConfig = connectorName === 'smooth'
                    ? {{ name: 'smooth' }}
                    : {{ name: connectorName, args: {{ radius: 8 }} }};

                const edge = graph.addEdge({{
                    source: {{ cell: sourceId, port: 'out_' + (edgeConfig.source_port || 0) }},
                    target: {{ cell: targetId, port: 'in_' + (edgeConfig.target_port || 0) }},
                    attrs: edgeAttrs,
                    router: routerConfig,
                    connector: connectorConfig,
                }});

                // Add label if provided (either regular label or relationship)
                const labelText = edgeConfig.label || edgeConfig.relationship;
                if (labelText) {{
                    edge.appendLabel({{
                        attrs: {{
                            text: {{
                                text: labelText,
                                fill: '#64748b',
                                fontSize: 11,
                                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                            }},
                            rect: {{
                                fill: '#fff',
                                stroke: '#e2e8f0',
                                strokeWidth: 1,
                                rx: 10,
                                ry: 10,
                                refWidth: 10,
                                refHeight: 6,
                                refX: -5,
                                refY: -3,
                            }},
                        }},
                        position: {{
                            distance: 0.5,
                        }},
                    }});
                }}
            }});
        }}

        // Auto-fit content after initialization (with a small delay to ensure rendering is complete)
        setTimeout(function() {{
            if (config.autoFit !== false) {{
                graph.zoomToFit({{ padding: 40, maxScale: 1 }});
            }}
        }}, 100);

        // Set up event handlers for HTMX
        function sendToServer(eventName, eventData) {{
            const endpoint = config.endpoints[eventName] || config.endpoints.change;
            if (!endpoint) return;

            const flowData = JSON.stringify(exportFlow());

            if (typeof htmx !== 'undefined') {{
                htmx.ajax('POST', endpoint, {{
                    values: {{
                        event: eventName,
                        data: JSON.stringify(eventData),
                        flow: flowData
                    }},
                    target: '#{id}-status',
                    swap: 'innerHTML'
                }});
            }}
        }}

        // Export flow data
        function exportFlow() {{
            const nodes = graph.getNodes().map(node => ({{
                id: node.id,
                x: node.position().x,
                y: node.position().y,
                width: node.size().width,
                height: node.size().height,
                data: node.getData(),
            }}));

            const edges = graph.getEdges().map(edge => ({{
                id: edge.id,
                source: edge.getSourceCellId(),
                target: edge.getTargetCellId(),
                sourcePort: edge.getSourcePortId(),
                targetPort: edge.getTargetPortId(),
                labels: edge.getLabels(),
            }}));

            return {{ nodes, edges }};
        }}

        // Make export function available
        window.fastflow['{id}'].exportFlow = exportFlow;

        // Event listeners
        graph.on('node:added', ({{ node }}) => {{
            sendToServer('nodeAdded', {{ id: node.id, data: node.getData() }});
        }});

        graph.on('node:removed', ({{ node }}) => {{
            sendToServer('nodeRemoved', {{ id: node.id }});
        }});

        graph.on('node:change:position', ({{ node }}) => {{
            sendToServer('change', {{ type: 'nodeMoved', id: node.id, position: node.position() }});
        }});

        graph.on('node:selected', ({{ node }}) => {{
            sendToServer('nodeSelected', {{ id: node.id, data: node.getData() }});
        }});

        graph.on('edge:connected', ({{ edge }}) => {{
            sendToServer('edgeConnected', {{
                id: edge.id,
                source: edge.getSourceCellId(),
                target: edge.getTargetCellId(),
            }});
        }});

        graph.on('edge:removed', ({{ edge }}) => {{
            sendToServer('edgeRemoved', {{ id: edge.id }});
        }});

        // Keyboard shortcuts for delete
        graph.bindKey(['delete', 'backspace'], () => {{
            const cells = graph.getSelectedCells();
            if (cells.length) {{
                graph.removeCells(cells);
            }}
            return false;
        }});

        // Double-click on node to edit label
        graph.on('node:dblclick', ({{ node, e }}) => {{
            const data = node.getData() || {{}};
            const currentLabel = data.label || node.id;

            // Create inline edit input
            const input = document.createElement('input');
            input.type = 'text';
            input.value = currentLabel;
            input.className = 'fastflow-inline-edit';
            input.style.cssText = `
                position: absolute;
                left: ${{e.clientX - 50}}px;
                top: ${{e.clientY - 15}}px;
                width: 100px;
                padding: 4px 8px;
                border: 2px solid #3b82f6;
                border-radius: 4px;
                font-size: 14px;
                z-index: 1000;
                background: white;
                color: #333;
            `;

            document.body.appendChild(input);
            input.focus();
            input.select();

            const finishEdit = () => {{
                const newLabel = input.value.trim();
                if (newLabel && newLabel !== currentLabel) {{
                    // Update node label
                    node.setData({{ ...data, label: newLabel }});
                    node.attr('label/text', newLabel);
                    sendToServer('change', {{ type: 'nodeRenamed', id: node.id, label: newLabel }});
                }}
                input.remove();
            }};

            input.addEventListener('blur', finishEdit);
            input.addEventListener('keydown', (evt) => {{
                if (evt.key === 'Enter') {{
                    finishEdit();
                }} else if (evt.key === 'Escape') {{
                    input.remove();
                }}
            }});
        }});

        // Double-click on edge to edit label
        graph.on('edge:dblclick', ({{ edge, e }}) => {{
            const labels = edge.getLabels();
            const currentLabel = labels.length > 0 ?
                (labels[0].attrs?.text?.text || '') : '';

            // Create inline edit input
            const input = document.createElement('input');
            input.type = 'text';
            input.value = currentLabel;
            input.placeholder = 'Enter label...';
            input.className = 'fastflow-inline-edit';
            input.style.cssText = `
                position: absolute;
                left: ${{e.clientX - 50}}px;
                top: ${{e.clientY - 15}}px;
                width: 100px;
                padding: 4px 8px;
                border: 2px solid #3b82f6;
                border-radius: 4px;
                font-size: 12px;
                z-index: 1000;
                background: white;
                color: #333;
            `;

            document.body.appendChild(input);
            input.focus();
            input.select();

            const finishEdit = () => {{
                const newLabel = input.value.trim();

                // Remove existing labels
                edge.setLabels([]);

                // Add new label if provided
                if (newLabel) {{
                    edge.appendLabel({{
                        attrs: {{
                            text: {{
                                text: newLabel,
                                fill: '#64748b',
                                fontSize: 11,
                                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                            }},
                            rect: {{
                                fill: '#fff',
                                stroke: '#e2e8f0',
                                strokeWidth: 1,
                                rx: 10,
                                ry: 10,
                                refWidth: 10,
                                refHeight: 6,
                                refX: -5,
                                refY: -3,
                            }},
                        }},
                        position: {{ distance: 0.5 }},
                    }});
                }}

                sendToServer('change', {{
                    type: 'edgeLabelChanged',
                    id: edge.id,
                    label: newLabel,
                    source: edge.getSourceCellId(),
                    target: edge.getTargetCellId(),
                }});
                input.remove();
            }};

            input.addEventListener('blur', finishEdit);
            input.addEventListener('keydown', (evt) => {{
                if (evt.key === 'Enter') {{
                    finishEdit();
                }} else if (evt.key === 'Escape') {{
                    input.remove();
                }}
            }});
        }});

        // Right-click context menu
        graph.on('cell:contextmenu', ({{ cell, e }}) => {{
            e.preventDefault();

            // Remove any existing context menu
            const existingMenu = document.getElementById('fastflow-context-menu');
            if (existingMenu) existingMenu.remove();

            const menu = document.createElement('div');
            menu.id = 'fastflow-context-menu';
            menu.style.cssText = `
                position: fixed;
                left: ${{e.clientX}}px;
                top: ${{e.clientY}}px;
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                padding: 4px 0;
                z-index: 1000;
                min-width: 120px;
            `;

            const isNode = cell.isNode();
            const nodeData = isNode ? (cell.getData() || {{}}) : {{}};
            const isTableNode = isNode && nodeData.nodeType === 'table';

            let items;
            if (isTableNode) {{
                items = [
                    {{ label: '✏️ Rename Table', action: 'rename' }},
                    {{ label: '➕ Add Column', action: 'addColumn' }},
                    {{ label: '📝 Edit Column', action: 'editColumn' }},
                    {{ label: '➖ Remove Column', action: 'removeColumn' }},
                    {{ label: '🗑️ Delete Table', action: 'delete' }},
                ];
            }} else if (isNode) {{
                items = [
                    {{ label: '✏️ Rename', action: 'rename' }},
                    {{ label: '🗑️ Delete', action: 'delete' }},
                ];
            }} else {{
                items = [
                    {{ label: '✏️ Edit Label', action: 'editLabel' }},
                    {{ label: '➖ Make Solid', action: 'solid' }},
                    {{ label: '- - Make Dashed', action: 'dashed' }},
                    {{ label: '🗑️ Delete', action: 'delete' }},
                ];
            }}

            items.forEach(item => {{
                const menuItem = document.createElement('div');
                menuItem.textContent = item.label;
                menuItem.style.cssText = `
                    padding: 8px 16px;
                    cursor: pointer;
                    font-size: 13px;
                    color: #334155;
                `;
                menuItem.onmouseenter = () => menuItem.style.background = '#f1f5f9';
                menuItem.onmouseleave = () => menuItem.style.background = 'transparent';
                menuItem.onclick = () => {{
                    menu.remove();

                    if (item.action === 'delete') {{
                        graph.removeCell(cell);
                    }} else if (item.action === 'rename' && isNode) {{
                        // Trigger double-click behavior
                        graph.trigger('node:dblclick', {{ node: cell, e }});
                    }} else if (item.action === 'editLabel' && !isNode) {{
                        graph.trigger('edge:dblclick', {{ edge: cell, e }});
                    }} else if (item.action === 'solid' && !isNode) {{
                        cell.attr('line/strokeDasharray', null);
                        sendToServer('change', {{ type: 'edgeStyleChanged', id: cell.id, dashed: false }});
                    }} else if (item.action === 'dashed' && !isNode) {{
                        cell.attr('line/strokeDasharray', '5 5');
                        sendToServer('change', {{ type: 'edgeStyleChanged', id: cell.id, dashed: true }});
                    }} else if (item.action === 'addColumn' && isTableNode) {{
                        showAddColumnDialog(cell);
                    }} else if (item.action === 'editColumn' && isTableNode) {{
                        showEditColumnDialog(cell);
                    }} else if (item.action === 'removeColumn' && isTableNode) {{
                        showRemoveColumnDialog(cell);
                    }}
                }};
                menu.appendChild(menuItem);
            }});

            document.body.appendChild(menu);

            // Close menu when clicking elsewhere
            const closeMenu = (evt) => {{
                if (!menu.contains(evt.target)) {{
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                }}
            }};
            setTimeout(() => document.addEventListener('click', closeMenu), 0);
        }});

        // Function to rebuild table node with updated columns
        function rebuildTableNode(node, newColumns) {{
            const data = node.getData() || {{}};
            const headerFill = data.headerFill || '#1890ff';
            const headerColor = data.headerColor || '#fff';
            const nodeWidth = node.size().width;
            const headerHeight = 36;
            const rowHeight = 24;
            const newHeight = headerHeight + (newColumns.length * rowHeight) + 12;

            // Build new HTML content - matching X6 ER example styling
            let htmlContent = `<div class="er-table" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 100%; height: 100%; display: flex; flex-direction: column; background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border-radius: 6px; overflow: hidden;">`;
            // Header with gradient
            htmlContent += `<div style="background: linear-gradient(135deg, ${{headerFill}} 0%, #096dd9 100%); color: ${{headerColor}}; padding: 8px 12px; font-size: 13px; font-weight: 600; text-align: center; border-radius: 6px 6px 0 0;">${{data.label || node.id}}</div>`;
            // Fields container
            htmlContent += `<div style="flex: 1; overflow: hidden; border-radius: 0 0 6px 6px;">`;

            newColumns.forEach((col, idx) => {{
                // Different background colors for different key types
                let bgColor;
                if (col.pk) {{
                    bgColor = '#e6f7ff';  // Light blue for primary keys
                }} else if (col.fk) {{
                    bgColor = '#fff7e6';  // Light orange for foreign keys
                }} else {{
                    bgColor = idx % 2 === 0 ? '#fafafa' : '#fff';
                }}

                let keyIcon = '';
                if (col.pk) keyIcon = '<span style="margin-right: 4px; font-size: 10px;">🔑</span>';
                else if (col.fk) keyIcon = '<span style="margin-right: 4px; font-size: 10px;">🔗</span>';

                const isLast = idx === newColumns.length - 1;
                const borderBottom = isLast ? '' : 'border-bottom: 1px solid #e8e8e8;';
                const borderRadius = isLast ? 'border-radius: 0 0 6px 6px;' : '';

                htmlContent += `<div style="display: flex; align-items: center; padding: 4px 8px; background: ${{bgColor}}; font-size: 11px; ${{borderBottom}} ${{borderRadius}} transition: background-color 0.2s;">`;
                htmlContent += `<span style="flex: 1; font-weight: 500; color: #262626;">${{keyIcon}}${{col.name}}</span>`;
                htmlContent += `<span style="color: #666; font-family: Monaco, Menlo, monospace; font-size: 10px;">${{col.type}}</span>`;
                htmlContent += `</div>`;
            }});

            htmlContent += `</div></div>`;

            // Update node size and content
            node.resize(nodeWidth, newHeight);
            node.attr('body/height', newHeight);
            node.attr('fo/height', newHeight);
            node.attr('foBody/html', htmlContent);
            node.setData({{ ...data, columns: newColumns }});

            sendToServer('change', {{ type: 'tableColumnsChanged', id: node.id, columns: newColumns }});
        }}

        // Dialog for adding a column to a table node
        function showAddColumnDialog(node) {{
            const overlay = document.createElement('div');
            overlay.id = 'fastflow-column-dialog-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.4);
                z-index: 1000;
                display: flex;
                align-items: center;
                justify-content: center;
            `;

            const dialog = document.createElement('div');
            dialog.style.cssText = `
                background: white;
                border-radius: 12px;
                padding: 24px;
                min-width: 320px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `;

            dialog.innerHTML = `
                <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #1e293b;">Add Column</h3>
                <div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: 12px; font-weight: 500; color: #64748b; margin-bottom: 4px;">Column Name</label>
                    <input type="text" id="col-name" placeholder="e.g. user_id" style="width: 100%; padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
                </div>
                <div style="margin-bottom: 12px;">
                    <label style="display: block; font-size: 12px; font-weight: 500; color: #64748b; margin-bottom: 4px;">Data Type</label>
                    <select id="col-type" style="width: 100%; padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
                        <option value="int">int</option>
                        <option value="bigint">bigint</option>
                        <option value="varchar(255)">varchar(255)</option>
                        <option value="text">text</option>
                        <option value="boolean">boolean</option>
                        <option value="timestamp">timestamp</option>
                        <option value="date">date</option>
                        <option value="decimal(10,2)">decimal(10,2)</option>
                        <option value="float">float</option>
                        <option value="json">json</option>
                        <option value="uuid">uuid</option>
                    </select>
                </div>
                <div style="margin-bottom: 16px; display: flex; gap: 16px;">
                    <label style="display: flex; align-items: center; gap: 6px; font-size: 13px; color: #334155; cursor: pointer;">
                        <input type="checkbox" id="col-pk" style="width: 16px; height: 16px;"> Primary Key
                    </label>
                    <label style="display: flex; align-items: center; gap: 6px; font-size: 13px; color: #334155; cursor: pointer;">
                        <input type="checkbox" id="col-fk" style="width: 16px; height: 16px;"> Foreign Key
                    </label>
                </div>
                <div style="display: flex; gap: 8px; justify-content: flex-end;">
                    <button id="col-cancel" style="padding: 8px 16px; border: 1px solid #e2e8f0; background: white; border-radius: 6px; cursor: pointer; font-size: 14px;">Cancel</button>
                    <button id="col-add" style="padding: 8px 16px; border: none; background: #3b82f6; color: white; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;">Add Column</button>
                </div>
            `;

            overlay.appendChild(dialog);
            document.body.appendChild(overlay);

            const nameInput = dialog.querySelector('#col-name');
            nameInput.focus();

            dialog.querySelector('#col-cancel').onclick = () => overlay.remove();
            overlay.onclick = (e) => {{ if (e.target === overlay) overlay.remove(); }};

            dialog.querySelector('#col-add').onclick = () => {{
                const name = dialog.querySelector('#col-name').value.trim();
                if (!name) {{
                    alert('Please enter a column name');
                    return;
                }}
                const type = dialog.querySelector('#col-type').value;
                const pk = dialog.querySelector('#col-pk').checked;
                const fk = dialog.querySelector('#col-fk').checked;

                const data = node.getData() || {{}};
                const columns = [...(data.columns || [])];
                const newCol = {{ name, type }};
                if (pk) newCol.pk = true;
                if (fk) newCol.fk = true;
                columns.push(newCol);

                rebuildTableNode(node, columns);
                overlay.remove();
            }};

            // Allow Enter key to submit
            nameInput.onkeydown = (e) => {{
                if (e.key === 'Enter') dialog.querySelector('#col-add').click();
                if (e.key === 'Escape') overlay.remove();
            }};
        }}

        // Dialog for removing a column from a table node
        function showRemoveColumnDialog(node) {{
            const data = node.getData() || {{}};
            const columns = data.columns || [];

            if (columns.length === 0) {{
                alert('This table has no columns to remove.');
                return;
            }}

            const overlay = document.createElement('div');
            overlay.id = 'fastflow-column-dialog-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.4);
                z-index: 1000;
                display: flex;
                align-items: center;
                justify-content: center;
            `;

            const dialog = document.createElement('div');
            dialog.style.cssText = `
                background: white;
                border-radius: 12px;
                padding: 24px;
                min-width: 320px;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `;

            let columnListHtml = columns.map((col, idx) => {{
                let keyIcons = '';
                if (col.pk) keyIcons += '🔑 ';
                if (col.fk) keyIcons += '🔗 ';
                return `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: ${{idx % 2 === 0 ? '#f8fafc' : '#fff'}}; border-radius: 4px; margin-bottom: 4px;">
                        <span style="font-size: 13px; color: #334155;">${{keyIcons}}${{col.name}} <span style="color: #94a3b8; font-size: 11px;">(${{col.type}})</span></span>
                        <button class="remove-col-btn" data-idx="${{idx}}" style="padding: 4px 10px; border: none; background: #fee2e2; color: #dc2626; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 500;">Remove</button>
                    </div>
                `;
            }}).join('');

            dialog.innerHTML = `
                <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #1e293b;">Remove Column</h3>
                <p style="font-size: 13px; color: #64748b; margin: 0 0 12px 0;">Click "Remove" next to a column to delete it.</p>
                <div style="margin-bottom: 16px;">
                    ${{columnListHtml}}
                </div>
                <div style="display: flex; justify-content: flex-end;">
                    <button id="col-close" style="padding: 8px 16px; border: 1px solid #e2e8f0; background: white; border-radius: 6px; cursor: pointer; font-size: 14px;">Close</button>
                </div>
            `;

            overlay.appendChild(dialog);
            document.body.appendChild(overlay);

            dialog.querySelector('#col-close').onclick = () => overlay.remove();
            overlay.onclick = (e) => {{ if (e.target === overlay) overlay.remove(); }};

            dialog.querySelectorAll('.remove-col-btn').forEach(btn => {{
                btn.onclick = () => {{
                    const idx = parseInt(btn.getAttribute('data-idx'));
                    const newColumns = columns.filter((_, i) => i !== idx);
                    rebuildTableNode(node, newColumns);
                    overlay.remove();
                }};
            }});
        }}

        // Dialog for editing a column in a table node
        function showEditColumnDialog(node) {{
            const data = node.getData() || {{}};
            const columns = data.columns || [];

            if (columns.length === 0) {{
                alert('This table has no columns to edit. Add a column first.');
                return;
            }}

            const overlay = document.createElement('div');
            overlay.id = 'fastflow-column-dialog-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.4);
                z-index: 1000;
                display: flex;
                align-items: center;
                justify-content: center;
            `;

            const dialog = document.createElement('div');
            dialog.style.cssText = `
                background: white;
                border-radius: 12px;
                padding: 24px;
                min-width: 360px;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `;

            // Build column selection list
            let columnListHtml = columns.map((col, idx) => {{
                let keyIcons = '';
                if (col.pk) keyIcons += '🔑 ';
                if (col.fk) keyIcons += '🔗 ';
                return `
                    <div class="edit-col-item" data-idx="${{idx}}" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: ${{idx % 2 === 0 ? '#f8fafc' : '#fff'}}; border-radius: 4px; margin-bottom: 4px; cursor: pointer; transition: background 0.2s;">
                        <span style="font-size: 13px; color: #334155;">${{keyIcons}}${{col.name}} <span style="color: #94a3b8; font-size: 11px;">(${{col.type}})</span></span>
                        <span style="color: #3b82f6; font-size: 12px;">Edit →</span>
                    </div>
                `;
            }}).join('');

            dialog.innerHTML = `
                <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #1e293b;">Edit Column</h3>
                <p style="font-size: 13px; color: #64748b; margin: 0 0 12px 0;">Select a column to edit:</p>
                <div id="column-list" style="margin-bottom: 16px;">
                    ${{columnListHtml}}
                </div>
                <div id="edit-form" style="display: none;">
                    <div style="margin-bottom: 12px;">
                        <label style="display: block; font-size: 12px; font-weight: 500; color: #64748b; margin-bottom: 4px;">Column Name</label>
                        <input type="text" id="edit-col-name" style="width: 100%; padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; box-sizing: border-box;">
                    </div>
                    <div style="margin-bottom: 12px;">
                        <label style="display: block; font-size: 12px; font-weight: 500; color: #64748b; margin-bottom: 4px;">Data Type</label>
                        <select id="edit-col-type" style="width: 100%; padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; box-sizing: border-box; background: white;">
                            <option value="int">int</option>
                            <option value="bigint">bigint</option>
                            <option value="varchar(255)">varchar(255)</option>
                            <option value="text">text</option>
                            <option value="boolean">boolean</option>
                            <option value="timestamp">timestamp</option>
                            <option value="date">date</option>
                            <option value="decimal">decimal</option>
                            <option value="float">float</option>
                            <option value="json">json</option>
                            <option value="uuid">uuid</option>
                        </select>
                    </div>
                    <div style="display: flex; gap: 16px; margin-bottom: 16px;">
                        <label style="display: flex; align-items: center; gap: 6px; font-size: 13px; color: #334155; cursor: pointer;">
                            <input type="checkbox" id="edit-col-pk" style="width: 16px; height: 16px;">
                            🔑 Primary Key
                        </label>
                        <label style="display: flex; align-items: center; gap: 6px; font-size: 13px; color: #334155; cursor: pointer;">
                            <input type="checkbox" id="edit-col-fk" style="width: 16px; height: 16px;">
                            🔗 Foreign Key
                        </label>
                    </div>
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 8px;">
                    <button id="col-back" style="display: none; padding: 8px 16px; border: 1px solid #e2e8f0; background: white; border-radius: 6px; cursor: pointer; font-size: 14px;">← Back</button>
                    <button id="col-save" style="display: none; padding: 8px 16px; border: none; background: #3b82f6; color: white; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;">Save</button>
                    <button id="col-close" style="padding: 8px 16px; border: 1px solid #e2e8f0; background: white; border-radius: 6px; cursor: pointer; font-size: 14px;">Close</button>
                </div>
            `;

            overlay.appendChild(dialog);
            document.body.appendChild(overlay);

            let selectedIdx = -1;
            const columnList = dialog.querySelector('#column-list');
            const editForm = dialog.querySelector('#edit-form');
            const backBtn = dialog.querySelector('#col-back');
            const saveBtn = dialog.querySelector('#col-save');
            const closeBtn = dialog.querySelector('#col-close');

            // Show edit form for selected column
            function showEditForm(idx) {{
                selectedIdx = idx;
                const col = columns[idx];
                dialog.querySelector('#edit-col-name').value = col.name || '';
                dialog.querySelector('#edit-col-type').value = col.type || 'varchar(255)';
                dialog.querySelector('#edit-col-pk').checked = !!col.pk;
                dialog.querySelector('#edit-col-fk').checked = !!col.fk;

                columnList.style.display = 'none';
                editForm.style.display = 'block';
                backBtn.style.display = 'inline-block';
                saveBtn.style.display = 'inline-block';
                dialog.querySelector('p').textContent = `Editing: ${{col.name}}`;
            }}

            // Go back to column list
            function showColumnList() {{
                selectedIdx = -1;
                columnList.style.display = 'block';
                editForm.style.display = 'none';
                backBtn.style.display = 'none';
                saveBtn.style.display = 'none';
                dialog.querySelector('p').textContent = 'Select a column to edit:';
            }}

            dialog.querySelectorAll('.edit-col-item').forEach(item => {{
                item.onmouseenter = () => item.style.background = '#e0f2fe';
                item.onmouseleave = () => {{
                    const idx = parseInt(item.getAttribute('data-idx'));
                    item.style.background = idx % 2 === 0 ? '#f8fafc' : '#fff';
                }};
                item.onclick = () => {{
                    const idx = parseInt(item.getAttribute('data-idx'));
                    showEditForm(idx);
                }};
            }});

            backBtn.onclick = showColumnList;
            closeBtn.onclick = () => overlay.remove();
            overlay.onclick = (e) => {{ if (e.target === overlay) overlay.remove(); }};

            saveBtn.onclick = () => {{
                if (selectedIdx < 0) return;

                const newName = dialog.querySelector('#edit-col-name').value.trim();
                const newType = dialog.querySelector('#edit-col-type').value;
                const isPk = dialog.querySelector('#edit-col-pk').checked;
                const isFk = dialog.querySelector('#edit-col-fk').checked;

                if (!newName) {{
                    alert('Column name cannot be empty.');
                    return;
                }}

                const newColumns = [...columns];
                newColumns[selectedIdx] = {{
                    name: newName,
                    type: newType,
                    pk: isPk || undefined,
                    fk: isFk || undefined,
                }};

                rebuildTableNode(node, newColumns);
                overlay.remove();
            }};

            document.onkeydown = (e) => {{
                if (e.key === 'Escape') overlay.remove();
            }};
        }}

        // Helper functions exposed to window.fastflow
        window.fastflow['{id}'].deleteSelected = function() {{
            const cells = graph.getSelectedCells();
            if (cells.length) {{
                graph.removeCells(cells);
            }}
        }};

        window.fastflow['{id}'].renameNode = function(nodeId, newLabel) {{
            const node = graph.getCellById(nodeId);
            if (node && node.isNode()) {{
                const data = node.getData() || {{}};
                node.setData({{ ...data, label: newLabel }});
                node.attr('label/text', newLabel);
            }}
        }};

        window.fastflow['{id}'].setEdgeLabel = function(edgeId, label) {{
            const edge = graph.getCellById(edgeId);
            if (edge && edge.isEdge()) {{
                edge.setLabels([]);
                if (label) {{
                    edge.appendLabel({{
                        attrs: {{
                            text: {{ text: label, fill: '#64748b', fontSize: 11 }},
                            rect: {{ fill: '#fff', stroke: '#e2e8f0', strokeWidth: 1, rx: 10, ry: 10 }},
                        }},
                        position: {{ distance: 0.5 }},
                    }});
                }}
            }}
        }};

        window.fastflow['{id}'].setEdgeDashed = function(edgeId, dashed) {{
            const edge = graph.getCellById(edgeId);
            if (edge && edge.isEdge()) {{
                edge.attr('line/strokeDasharray', dashed ? '5 5' : null);
            }}
        }};

        // Table node column management functions
        window.fastflow['{id}'].addTableColumn = function(nodeId, column) {{
            const node = graph.getCellById(nodeId);
            if (node && node.isNode()) {{
                const data = node.getData() || {{}};
                if (data.nodeType === 'table') {{
                    const columns = [...(data.columns || [])];
                    columns.push(column);
                    rebuildTableNode(node, columns);
                    return true;
                }}
            }}
            return false;
        }};

        window.fastflow['{id}'].removeTableColumn = function(nodeId, columnIndex) {{
            const node = graph.getCellById(nodeId);
            if (node && node.isNode()) {{
                const data = node.getData() || {{}};
                if (data.nodeType === 'table') {{
                    const columns = (data.columns || []).filter((_, i) => i !== columnIndex);
                    rebuildTableNode(node, columns);
                    return true;
                }}
            }}
            return false;
        }};

        window.fastflow['{id}'].getTableColumns = function(nodeId) {{
            const node = graph.getCellById(nodeId);
            if (node && node.isNode()) {{
                const data = node.getData() || {{}};
                if (data.nodeType === 'table') {{
                    return data.columns || [];
                }}
            }}
            return null;
        }};

        window.fastflow['{id}'].setTableColumns = function(nodeId, columns) {{
            const node = graph.getCellById(nodeId);
            if (node && node.isNode()) {{
                const data = node.getData() || {{}};
                if (data.nodeType === 'table') {{
                    rebuildTableNode(node, columns);
                    return true;
                }}
            }}
            return false;
        }};

        console.log('Fastflow X6 graph initialized:', '{id}');
    }}

    // Start initialization
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initGraph);
    }} else {{
        initGraph();
    }}
}})();
"""),
        # Hidden status div for HTMX responses
        Div(id=f"{id}-status", style="display:none"),
        id=id,
        cls=container_cls,
        style=f"width: {width}; height: {height};",
        data_fastflow="true",
        **kwargs
    )


def Node(
    name: str,
    x: int = 0,
    y: int = 0,
    label: Optional[str] = None,
    node_type: str = "default",
    inputs: int = 1,
    outputs: int = 1,
    width: int = 160,
    height: int = 60,
    data: Optional[dict] = None,
    html: Optional[str] = None,
    # Enhanced features
    shape: str = "rect",
    icon: Optional[str] = None,
    status: Optional[str] = None,
    port_positions: Optional[dict] = None,
    fill: Optional[str] = None,
    stroke: Optional[str] = None,
    text_color: Optional[str] = None,
    **kwargs
) -> dict:
    """
    Define a node for the X6 flow editor.

    Args:
        name: Node identifier (must be unique)
        x: X position in the canvas
        y: Y position in the canvas
        label: Display label (defaults to name)
        node_type: Node type for styling ('start', 'end', 'agent', 'tool', 'llm', etc.)
        inputs: Number of input ports
        outputs: Number of output ports
        width: Node width in pixels
        height: Node height in pixels
        data: Custom data to attach to the node
        html: Custom HTML content
        shape: Node shape ('rect', 'circle', 'polygon', 'diamond', 'ellipse')
        icon: Icon emoji or URL to display
        status: Node status ('default', 'success', 'error', 'running')
        port_positions: Custom port positions {'inputs': 'top'|'left', 'outputs': 'bottom'|'right'}
        fill: Override fill color
        stroke: Override stroke color
        text_color: Override text color
        **kwargs: Additional data

    Example:
        ```python
        # Basic node
        Node("start", x=100, y=100, label="__start__", node_type="start", inputs=0, outputs=1)

        # Node with status
        Node("process", x=200, y=200, label="Process", node_type="agent", status="running")

        # Custom styled node
        Node("custom", x=300, y=300, fill="#ff0000", stroke="#880000")

        # Node with ports on sides
        Node("join", x=400, y=300, port_positions={'inputs': 'left', 'outputs': 'right'})
        ```
    """
    display_label = label or name

    # Generate default HTML based on node_type
    if not html:
        html = f'<div class="node-container {node_type}-node"><div class="node-title">{display_label}</div></div>'

    node_config = {
        "_type": "node",
        "id": name,
        "name": name,
        "x": x,
        "y": y,
        "label": display_label,
        "node_type": node_type,
        "inputs": inputs,
        "outputs": outputs,
        "width": width,
        "height": height,
        "data": data or {},
        "html": html,
        "shape": shape,
    }

    # Add optional enhanced features
    if icon:
        node_config["icon"] = icon
    if status:
        node_config["status"] = status
    if port_positions:
        node_config["port_positions"] = port_positions
    if fill:
        node_config["fill"] = fill
    if stroke:
        node_config["stroke"] = stroke
    if text_color:
        node_config["text_color"] = text_color

    node_config.update(kwargs)
    return node_config


def Edge(
    source: str,
    target: str,
    label: Optional[str] = None,
    source_port: int = 0,
    target_port: int = 0,
    dashed: bool = False,
    # Enhanced features
    connector: str = "rounded",
    router: str = "manhattan",
    color: Optional[str] = None,
    animated: bool = False,
    marker: str = "block",
    relationship: Optional[str] = None,
    **kwargs
) -> dict:
    """
    Define an edge/connection between nodes.

    Args:
        source: Source node ID
        target: Target node ID
        label: Edge label (displayed as pill badge)
        source_port: Source output port index
        target_port: Target input port index
        dashed: Whether to use dashed line style
        connector: Connector type ('smooth', 'rounded', 'manhattan', 'normal')
        router: Router type ('manhattan', 'orth', 'metro', 'er', 'normal')
        color: Override line color
        animated: Whether to animate the edge (for running state)
        marker: Arrow marker type ('block', 'classic', 'diamond', 'circle', 'arrow')
        relationship: ER relationship label ('1:1', '1:N', 'N:1', 'N:N')
        **kwargs: Additional data

    Example:
        ```python
        # Basic edge
        Edge(source="start", target="agent", label="next")

        # Dashed conditional edge
        Edge(source="agent", target="end", dashed=True)

        # ER relationship
        Edge(source="users", target="orders", relationship="1:N", router="er")

        # Animated running edge
        Edge(source="input", target="process", animated=True, color="#52c41a")
        ```
    """
    edge_config = {
        "_type": "edge",
        "source": source,
        "target": target,
        "label": label,
        "source_port": source_port,
        "target_port": target_port,
        "dashed": dashed,
        "connector": connector,
        "router": router,
        "marker": marker,
    }

    # Add optional enhanced features
    if color:
        edge_config["color"] = color
    if animated:
        edge_config["animated"] = animated
    if relationship:
        edge_config["relationship"] = relationship
        # ER relationships typically use different router
        if router == "manhattan":
            edge_config["router"] = "er"

    edge_config.update(kwargs)
    return edge_config


def NodePalette(
    *items,
    id: str = "node-palette",
    title: str = "Nodes",
    target_editor: str = "flowgraph",
    cls: str = "",
    **kwargs
):
    """
    Create a palette of draggable node types.

    Args:
        *items: PaletteItem components
        id: Palette container ID
        title: Palette title
        target_editor: ID of the FlowEditor to add nodes to
        cls: Additional CSS classes
        **kwargs: Additional attributes
    """
    palette_cls = f"node-palette {cls}".strip()

    return Div(
        Div(title, cls="palette-title") if title else None,
        *items,
        Script(f"""
(function() {{
    function setupPalette() {{
        const palette = document.getElementById('{id}');
        const graph = window.fastflow && window.fastflow['{target_editor}'];

        if (!palette || !graph) {{
            setTimeout(setupPalette, 100);
            return;
        }}

        const items = palette.querySelectorAll('[data-node-type]');
        const container = document.getElementById('{target_editor}-graph');

        items.forEach(function(item) {{
            item.draggable = true;

            item.addEventListener('dragstart', function(e) {{
                e.dataTransfer.setData('node-type', item.dataset.nodeType);
                e.dataTransfer.setData('node-label', item.dataset.nodeLabel || item.dataset.nodeType);
                e.dataTransfer.setData('node-inputs', item.dataset.nodeInputs || '1');
                e.dataTransfer.setData('node-outputs', item.dataset.nodeOutputs || '1');
            }});
        }});

        container.addEventListener('dragover', function(e) {{
            e.preventDefault();
        }});

        container.addEventListener('drop', function(e) {{
            e.preventDefault();

            const nodeType = e.dataTransfer.getData('node-type');
            const nodeLabel = e.dataTransfer.getData('node-label');
            const inputs = parseInt(e.dataTransfer.getData('node-inputs')) || 1;
            const outputs = parseInt(e.dataTransfer.getData('node-outputs')) || 1;

            // Calculate position relative to graph
            // clientToLocal expects raw client (viewport) coordinates
            const point = graph.clientToLocal(e.clientX, e.clientY);

            // Generate unique ID
            const nodeId = nodeType + '_' + Date.now();

            // Node style mappings - extended with all types
            const nodeStyles = {{
                // LangGraph-style nodes
                'start': {{ fill: '#1e293b', stroke: '#1e293b', textColor: '#fff', rx: 20, ry: 20 }},
                'end': {{ fill: '#1e293b', stroke: '#1e293b', textColor: '#fff', rx: 20, ry: 20 }},
                'agent': {{ fill: '#dbeafe', stroke: '#60a5fa', textColor: '#1e40af', rx: 8, ry: 8 }},
                'tool': {{ fill: '#fce7f3', stroke: '#f472b6', textColor: '#9d174d', rx: 8, ry: 8 }},
                'llm': {{ fill: '#f3e8ff', stroke: '#c084fc', textColor: '#6b21a8', rx: 8, ry: 8 }},
                'condition': {{ fill: '#fef3c7', stroke: '#fbbf24', textColor: '#92400e', rx: 8, ry: 8 }},
                // Data processing DAG nodes
                'input': {{ fill: '#dcfce7', stroke: '#4ade80', textColor: '#166534', rx: 8, ry: 8 }},
                'output': {{ fill: '#fee2e2', stroke: '#f87171', textColor: '#991b1b', rx: 8, ry: 8 }},
                'filter': {{ fill: '#e0f2fe', stroke: '#38bdf8', textColor: '#0369a1', rx: 8, ry: 8 }},
                'join': {{ fill: '#fef3c7', stroke: '#fbbf24', textColor: '#92400e', rx: 8, ry: 8 }},
                'union': {{ fill: '#f3e8ff', stroke: '#c084fc', textColor: '#6b21a8', rx: 8, ry: 8 }},
                'agg': {{ fill: '#fce7f3', stroke: '#f472b6', textColor: '#9d174d', rx: 8, ry: 8 }},
                'transform': {{ fill: '#e0f2fe', stroke: '#38bdf8', textColor: '#0369a1', rx: 8, ry: 8 }},
                // Agent flow nodes
                'code': {{ fill: '#e6fffb', stroke: '#08979c', textColor: '#08979c', rx: 8, ry: 8 }},
                'branch': {{ fill: '#fff7e6', stroke: '#fa8c16', textColor: '#fa8c16', rx: 8, ry: 8 }},
                'loop': {{ fill: '#fff7e6', stroke: '#fa8c16', textColor: '#fa8c16', rx: 8, ry: 8 }},
                'kb': {{ fill: '#f0f5ff', stroke: '#1d39c4', textColor: '#1d39c4', rx: 8, ry: 8 }},
                'mcp': {{ fill: '#e6fffb', stroke: '#08979c', textColor: '#08979c', rx: 8, ry: 8 }},
                'db': {{ fill: '#f0f5ff', stroke: '#1d39c4', textColor: '#1d39c4', rx: 8, ry: 8 }},
                // Flowchart shapes
                'process': {{ fill: '#eff4ff', stroke: '#5f95ff', textColor: '#262626', rx: 0, ry: 0 }},
                'decision': {{ fill: '#eff4ff', stroke: '#5f95ff', textColor: '#262626', rx: 0, ry: 0 }},
                'data': {{ fill: '#eff4ff', stroke: '#5f95ff', textColor: '#262626', rx: 0, ry: 0 }},
                'connector': {{ fill: '#eff4ff', stroke: '#5f95ff', textColor: '#262626', rx: 22, ry: 22 }},
                // ER Diagram
                'table': {{ fill: '#fff', stroke: '#1890ff', textColor: '#262626', rx: 8, ry: 8 }},
                // Default
                'default': {{ fill: '#f1f5f9', stroke: '#94a3b8', textColor: '#334155', rx: 8, ry: 8 }},
            }};

            const style = nodeStyles[nodeType] || nodeStyles['default'];
            const isStartEnd = nodeType === 'start' || nodeType === 'end';

            // Build ports
            const ports = [];
            for (let i = 0; i < inputs; i++) {{
                ports.push({{
                    id: 'in_' + i,
                    group: 'top',
                }});
            }}
            for (let i = 0; i < outputs; i++) {{
                ports.push({{
                    id: 'out_' + i,
                    group: 'bottom',
                }});
            }}

            // Handle table nodes specially - use createERTableNode
            if (nodeType === 'table') {{
                const tableLabel = 'New Table';
                createERTableNode({{
                    id: nodeId,
                    name: nodeId,
                    label: tableLabel,
                    x: point.x - 110,
                    y: point.y - 30,
                    width: 220,
                    data: {{
                        columns: [],
                        headerFill: '#1890ff',
                        headerColor: '#fff',
                    }},
                }}, style);
            }} else {{
                // Add regular node
                graph.addNode({{
                    id: nodeId,
                    shape: 'rect',
                    x: point.x - 80,
                    y: point.y - 25,
                    width: isStartEnd ? 120 : 160,
                    height: isStartEnd ? 40 : 50,
                    attrs: {{
                        body: {{
                            fill: style.fill,
                            stroke: style.stroke,
                            strokeWidth: 2,
                            rx: style.rx,
                            ry: style.ry,
                        }},
                        label: {{
                            text: nodeLabel,
                            fill: style.textColor,
                            fontSize: 14,
                            fontWeight: isStartEnd ? 600 : 500,
                            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                        }},
                    }},
                    ports: {{
                        groups: {{
                            top: {{
                                position: 'top',
                                attrs: {{
                                    circle: {{
                                        r: 5,
                                        magnet: true,
                                        stroke: '#5F95FF',
                                        strokeWidth: 1,
                                        fill: '#fff',
                                        style: {{ visibility: 'hidden' }},
                                    }},
                                }},
                            }},
                            bottom: {{
                                position: 'bottom',
                                attrs: {{
                                    circle: {{
                                        r: 5,
                                        magnet: true,
                                        stroke: '#5F95FF',
                                        strokeWidth: 1,
                                        fill: '#fff',
                                        style: {{ visibility: 'hidden' }},
                                    }},
                                }},
                            }},
                        }},
                        items: ports,
                    }},
                    data: {{
                        name: nodeId,
                        label: nodeLabel,
                        nodeType: nodeType,
                    }},
                }});
            }}
        }});
    }}

    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', setupPalette);
    }} else {{
        setupPalette();
    }}
}})();
"""),
        id=id,
        cls=palette_cls,
        **kwargs
    )


def PaletteItem(
    node_type: str,
    label: str,
    icon: Optional[str] = None,
    inputs: int = 1,
    outputs: int = 1,
    cls: str = "",
    **kwargs
):
    """
    Create a draggable item for the node palette.

    Args:
        node_type: The node type to create when dropped
        label: Display label
        icon: Optional icon (emoji or icon class)
        inputs: Default number of input ports
        outputs: Default number of output ports
        cls: Additional CSS classes
        **kwargs: Additional attributes
    """
    item_cls = f"palette-item {cls}".strip()

    return Div(
        Div(icon, cls="icon") if icon else None,
        Div(label, cls="label"),
        cls=item_cls,
        data_node_type=node_type,
        data_node_label=label,
        data_node_inputs=str(inputs),
        data_node_outputs=str(outputs),
        draggable="true",
        **kwargs
    )


def FlowControls(
    editor_id: str = "flowgraph",
    show_zoom: bool = True,
    show_fit: bool = True,
    show_clear: bool = False,
    cls: str = "",
    **kwargs
):
    """
    Create zoom and control buttons for the flow editor.

    Args:
        editor_id: ID of the FlowEditor to control
        show_zoom: Show zoom in/out buttons
        show_fit: Show fit view button
        show_clear: Show clear all button
        cls: Additional CSS classes
        **kwargs: Additional attributes
    """
    controls_cls = f"flow-controls {cls}".strip()

    buttons = []
    if show_zoom:
        buttons.extend([
            Button("+", onclick=f"window.fastflow['{editor_id}'].zoom(0.1)", title="Zoom In"),
            Button("-", onclick=f"window.fastflow['{editor_id}'].zoom(-0.1)", title="Zoom Out"),
        ])
    if show_fit:
        buttons.append(
            Button("⊡", onclick=f"window.fastflow['{editor_id}'].zoomToFit()", title="Fit View")
        )
    if show_clear:
        buttons.append(
            Button("🗑", onclick=f"if(confirm('Clear all?')) window.fastflow['{editor_id}'].clearCells()", title="Clear All")
        )

    return Div(*buttons, cls=controls_cls, **kwargs)


def TableNode(
    name: str,
    x: int = 0,
    y: int = 0,
    label: Optional[str] = None,
    columns: Optional[list] = None,
    width: int = 220,
    fill: str = "#fff",
    stroke: str = "#1890ff",
    header_fill: str = "#1890ff",
    header_color: str = "#fff",
    **kwargs
) -> dict:
    """
    Create a table/entity node for ER diagrams.

    Args:
        name: Node identifier
        x: X position
        y: Y position
        label: Table name (defaults to name)
        columns: List of column definitions [{"name": "id", "type": "int", "pk": True}, ...]
        width: Node width (default 220)
        fill: Body fill color
        stroke: Border color
        header_fill: Header background color
        header_color: Header text color
        **kwargs: Additional attributes

    Example:
        ```python
        TableNode("users", x=100, y=100, label="Users", columns=[
            {"name": "id", "type": "int", "pk": True},
            {"name": "name", "type": "varchar(255)"},
            {"name": "email", "type": "varchar(255)"},
        ])
        ```
    """
    display_label = label or name
    cols = columns or []

    # Calculate height based on columns (matching JS function)
    header_height = 36
    row_height = 24
    height = header_height + (len(cols) * row_height) + 12

    return {
        "_type": "node",
        "id": name,
        "name": name,
        "x": x,
        "y": y,
        "label": display_label,
        "node_type": "table",
        "inputs": 1,
        "outputs": 1,
        "width": width,
        "height": height,
        "shape": "table",
        "data": {
            "columns": cols,
            "headerFill": header_fill,
            "headerColor": header_color,
        },
        "fill": fill,
        "stroke": stroke,
        "port_positions": {"inputs": "left", "outputs": "right"},
        **kwargs
    }


def PaletteGroup(
    *items,
    title: str,
    collapsed: bool = False,
    cls: str = "",
    **kwargs
):
    """
    Create a collapsible group within a node palette.

    Args:
        *items: PaletteItem components in this group
        title: Group title
        collapsed: Whether to start collapsed
        cls: Additional CSS classes
        **kwargs: Additional attributes

    Example:
        ```python
        NodePalette(
            PaletteGroup(
                PaletteItem("input", "Input"),
                PaletteItem("output", "Output"),
                title="Basic Nodes"
            ),
            PaletteGroup(
                PaletteItem("llm", "LLM"),
                PaletteItem("agent", "Agent"),
                title="AI Nodes"
            ),
            target_editor="main-flow"
        )
        ```
    """
    group_cls = f"palette-group {cls}".strip()
    group_id = f"group-{title.lower().replace(' ', '-')}"

    return Div(
        Div(
            Span("▼" if not collapsed else "▶", cls="group-arrow"),
            Span(title, cls="group-title-text"),
            cls="palette-group-header",
            onclick=f"togglePaletteGroup('{group_id}')",
        ),
        Div(
            *items,
            id=group_id,
            cls="palette-group-content",
            style="display: none;" if collapsed else ""
        ),
        Script(f"""
        function togglePaletteGroup(id) {{
            const content = document.getElementById(id);
            const arrow = content.previousElementSibling.querySelector('.group-arrow');
            if (content.style.display === 'none') {{
                content.style.display = 'block';
                arrow.textContent = '▼';
            }} else {{
                content.style.display = 'none';
                arrow.textContent = '▶';
            }}
        }}
        """) if "togglePaletteGroup" not in str(kwargs.get("_defined_funcs", [])) else None,
        cls=group_cls,
        **kwargs
    )


def StatusBadge(
    status: str,
    cls: str = "",
    **kwargs
):
    """
    Create a status badge indicator.

    Args:
        status: Status type ('success', 'error', 'running', 'pending')
        cls: Additional CSS classes
        **kwargs: Additional attributes

    Example:
        ```python
        Node("process", x=100, y=100, data={"status": StatusBadge("running")})
        ```
    """
    status_colors = {
        "success": "#52c41a",
        "error": "#ff4d4f",
        "running": "#1890ff",
        "pending": "#d9d9d9",
    }

    color = status_colors.get(status, status_colors["pending"])
    badge_cls = f"status-badge status-{status} {cls}".strip()

    return Span(
        cls=badge_cls,
        style=f"background-color: {color};",
        data_status=status,
        **kwargs
    )


def DAGNode(
    name: str,
    x: int = 0,
    y: int = 0,
    label: Optional[str] = None,
    node_type: str = "default",
    status: Optional[str] = None,
    icon: Optional[str] = None,
    inputs: int = 1,
    outputs: int = 1,
    **kwargs
) -> dict:
    """
    Create a DAG (Directed Acyclic Graph) node for data processing pipelines.

    Args:
        name: Node identifier
        x: X position
        y: Y position
        label: Display label
        node_type: Node type ('input', 'output', 'filter', 'join', 'union', 'agg', 'transform')
        status: Status indicator ('success', 'error', 'running')
        icon: Icon emoji
        inputs: Number of input ports
        outputs: Number of output ports
        **kwargs: Additional attributes

    Example:
        ```python
        DAGNode("input1", x=100, y=100, label="INPUT", node_type="input", status="success")
        DAGNode("filter1", x=250, y=100, label="FILTER", node_type="filter", status="running")
        ```
    """
    # Default icons for DAG node types
    default_icons = {
        "input": "📥",
        "output": "📤",
        "filter": "🔍",
        "join": "🔗",
        "union": "⊕",
        "agg": "∑",
        "transform": "🔄",
    }

    return Node(
        name=name,
        x=x,
        y=y,
        label=label,
        node_type=node_type,
        status=status,
        icon=icon or default_icons.get(node_type),
        inputs=inputs,
        outputs=outputs,
        width=100,
        height=50,
        **kwargs
    )


def AgentNode(
    name: str,
    x: int = 0,
    y: int = 0,
    label: Optional[str] = None,
    node_type: str = "llm",
    icon: Optional[str] = None,
    inputs: int = 1,
    outputs: int = 1,
    **kwargs
) -> dict:
    """
    Create an agent workflow node.

    Args:
        name: Node identifier
        x: X position
        y: Y position
        label: Display label
        node_type: Agent node type ('llm', 'code', 'branch', 'loop', 'kb', 'mcp', 'db', 'tool')
        icon: Icon emoji
        inputs: Number of input ports
        outputs: Number of output ports
        **kwargs: Additional attributes

    Example:
        ```python
        AgentNode("llm1", x=200, y=100, label="LLM", node_type="llm")
        AgentNode("code1", x=200, y=200, label="Code", node_type="code")
        ```
    """
    # Default icons for agent node types
    default_icons = {
        "llm": "🧠",
        "code": "💻",
        "branch": "🔀",
        "loop": "🔄",
        "kb": "📚",
        "mcp": "🔌",
        "db": "🗄️",
        "tool": "🛠️",
    }

    return Node(
        name=name,
        x=x,
        y=y,
        label=label,
        node_type=node_type,
        icon=icon or default_icons.get(node_type),
        inputs=inputs,
        outputs=outputs,
        **kwargs
    )


def FlowchartNode(
    name: str,
    x: int = 0,
    y: int = 0,
    label: Optional[str] = None,
    node_type: str = "process",
    **kwargs
) -> dict:
    """
    Create a flowchart node with standard shapes.

    Args:
        name: Node identifier
        x: X position
        y: Y position
        label: Display label
        node_type: Flowchart shape type:
            - 'process': Rectangle for processes
            - 'decision': Diamond for decisions/conditions
            - 'data': Parallelogram for data
            - 'connector': Circle for connectors
            - 'start'/'end': Rounded pill for start/end
        **kwargs: Additional attributes

    Example:
        ```python
        FlowchartNode("start", x=100, y=50, label="Start", node_type="start")
        FlowchartNode("decision", x=100, y=150, label="Check?", node_type="decision")
        ```
    """
    # Shape mappings for flowchart nodes
    shapes = {
        "process": "rect",
        "decision": "polygon",
        "data": "polygon",
        "connector": "circle",
        "start": "rect",
        "end": "rect",
    }

    # Default sizes for different shapes
    sizes = {
        "process": (100, 50),
        "decision": (100, 60),
        "data": (100, 50),
        "connector": (50, 50),
        "start": (80, 40),
        "end": (80, 40),
    }

    # Port configurations for flowchart nodes
    ports_config = {
        "decision": {"inputs": 1, "outputs": 2},  # Yes/No branches
    }

    width, height = sizes.get(node_type, (100, 50))
    port_cfg = ports_config.get(node_type, {"inputs": 1, "outputs": 1})

    return Node(
        name=name,
        x=x,
        y=y,
        label=label,
        node_type=node_type,
        shape=shapes.get(node_type, "rect"),
        width=width,
        height=height,
        inputs=port_cfg.get("inputs", 1),
        outputs=port_cfg.get("outputs", 1),
        **kwargs
    )


# =============================================================================
# Type Dispatch Integration
# =============================================================================
# These functions bridge Layer 2 typed nodes (types.py) with UI components

def node_from_typed(typed_node) -> dict:
    """
    Convert a typed FlowNode (from types.py) to a UI Node component.

    This provides seamless integration between Layer 2 typed nodes
    and the UI layer. The typed node's class determines the node_type,
    and its attributes are mapped to UI Node parameters.

    Args:
        typed_node: A FlowNode subclass instance from fastflow.types
            (e.g., AgentNode, ToolNode, InputNode, etc.)

    Returns:
        dict: A Node component dict ready for use in FlowEditor

    Example:
        ```python
        from fastflow.types import AgentNode, InputNode, FilterNode
        from fastflow.components import node_from_typed, FlowEditor, Edge

        # Create typed nodes
        agent = AgentNode(id="agent1", x=200, y=100, label="My Agent", model="gpt-4")
        input_node = InputNode(id="input1", x=50, y=100, label="Load Data")

        # Convert to UI nodes
        FlowEditor(
            node_from_typed(agent),
            node_from_typed(input_node),
            Edge(source="input1", target="agent1"),
            id="my-flow"
        )
        ```
    """
    # Try to get node style from types module
    try:
        from .types import get_node_style, NODE_STYLES as TYPE_STYLES
        style = get_node_style(typed_node)
    except ImportError:
        style = NODE_STYLES.get(typed_node.node_type, NODE_STYLES.get("default", {}))

    # Extract common attributes
    node_id = typed_node.id
    x = getattr(typed_node, "x", 0)
    y = getattr(typed_node, "y", 0)
    width = getattr(typed_node, "width", 160)
    height = getattr(typed_node, "height", 60)
    label = getattr(typed_node, "label", "") or node_id
    inputs = getattr(typed_node, "inputs", 1)
    outputs = getattr(typed_node, "outputs", 1)

    # Get node type from class (e.g., AgentNode -> "agent")
    node_type = typed_node.node_type

    # Build data dict from extra attributes
    data = getattr(typed_node, "data", {}).copy() if hasattr(typed_node, "data") else {}

    # Add type-specific attributes to data
    base_attrs = {"id", "x", "y", "width", "height", "label", "data", "inputs", "outputs"}
    for attr, value in typed_node.__dict__.items():
        if attr not in base_attrs and not attr.startswith("_"):
            data[attr] = value

    # Create the Node dict
    return Node(
        name=node_id,
        x=x,
        y=y,
        label=label,
        node_type=node_type,
        width=width,
        height=height,
        inputs=inputs,
        outputs=outputs,
        fill=style.get("fill"),
        stroke=style.get("stroke"),
        text_color=style.get("textColor"),
        data=data
    )


def nodes_from_typed(typed_nodes: list) -> list[dict]:
    """
    Convert a list of typed FlowNodes to UI Node components.

    Convenience function for converting multiple typed nodes at once.

    Args:
        typed_nodes: List of FlowNode subclass instances

    Returns:
        list: List of Node component dicts

    Example:
        ```python
        from fastflow.types import StartNode, AgentNode, EndNode
        from fastflow.components import nodes_from_typed, FlowEditor

        nodes = [
            StartNode(id="start", x=100, y=50),
            AgentNode(id="agent", x=100, y=150, model="gpt-4"),
            EndNode(id="end", x=100, y=250),
        ]

        ui_nodes = nodes_from_typed(nodes)
        FlowEditor(*ui_nodes, id="my-flow")
        ```
    """
    return [node_from_typed(n) for n in typed_nodes]


def validate_typed_node(typed_node) -> list[str]:
    """
    Validate a typed FlowNode before creating a UI component.

    Uses the type-dispatched validate() function from types.py.

    Args:
        typed_node: A FlowNode subclass instance

    Returns:
        list: List of validation error messages (empty if valid)

    Example:
        ```python
        from fastflow.types import AgentNode
        from fastflow.components import validate_typed_node

        agent = AgentNode(id="agent1", model="", temperature=5.0)  # Invalid!
        errors = validate_typed_node(agent)
        # errors = ["AgentNode must specify a model", "Temperature must be between 0 and 2"]
        ```
    """
    try:
        from .types import validate
        return validate(typed_node)
    except ImportError:
        # types.py not available, skip validation
        return []
