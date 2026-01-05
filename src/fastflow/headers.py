"""
Headers for loading AntV X6 JavaScript library from CDN.
"""

from fasthtml.common import Script, Link, Style
from pathlib import Path

# X6 version - using version 1.x which has proper UMD build with global X6 variable
# X6 v2 uses ESM which doesn't expose global variables via script tags
X6_VERSION = "1"

# CDN URLs - using unpkg for X6 (has proper x6.js UMD build)
X6_JS_CDN = f"https://unpkg.com/@antv/x6@{X6_VERSION}/dist/x6.js"
X6_CSS_CDN = f"https://unpkg.com/@antv/x6@{X6_VERSION}/dist/x6.css"

# Get path to local JS file
_here = Path(__file__).parent
_fastflow_js_path = _here / "js" / "fastflow.js"
_fastflow_css_path = _here / "css" / "fastflow.css"


def _read_local_file(path: Path) -> str:
    """Read local file content."""
    if path.exists():
        return path.read_text()
    return ""


def fastflow_headers(
    x6_js: str = X6_JS_CDN,
    x6_css: str = X6_CSS_CDN,
    include_default_styles: bool = True,
) -> tuple:
    """
    Return headers needed to use Fastflow components with X6.

    Args:
        x6_js: URL to X6 JavaScript (defaults to CDN)
        x6_css: URL to X6 CSS (defaults to CDN)
        include_default_styles: Whether to include default Fastflow styles

    Returns:
        Tuple of Script/Link/Style elements for use in fast_app(hdrs=...)

    Example:
        ```python
        from fasthtml.common import *
        from fastflow import fastflow_headers

        app, rt = fast_app(hdrs=fastflow_headers())
        ```
    """
    hdrs = [
        # X6 core library CSS
        Link(rel="stylesheet", href=x6_css),
        # X6 core library JS
        Script(src=x6_js),
    ]

    # Fastflow custom JS bridge
    fastflow_js = _read_local_file(_fastflow_js_path)
    if fastflow_js:
        hdrs.append(Script(fastflow_js))

    # Default styles
    if include_default_styles:
        fastflow_css = _read_local_file(_fastflow_css_path)
        if fastflow_css:
            hdrs.append(Style(fastflow_css))
        else:
            # Inline default styles if file doesn't exist yet
            hdrs.append(Style(_default_styles()))

    return tuple(hdrs)


def _default_styles() -> str:
    """Return default Fastflow styles for X6."""
    return """
/* Fastflow default styles for X6 */
.fastflow-container {
    width: 100%;
    height: 600px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    overflow: hidden;
    background: #fafafa;
    position: relative;
}

.fastflow-graph {
    width: 100%;
    height: 100%;
}

/* Node container base style */
.node-container {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    min-width: 120px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.node-container.selected {
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}

.node-title {
    background: #3b82f6;
    color: white;
    padding: 8px 12px;
    font-weight: 600;
    border-radius: 6px 6px 0 0;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.node-body {
    padding: 10px 12px;
    font-size: 13px;
}

/* Start/End nodes - pill shaped like LangGraph Builder */
.node-container.start-node,
.node-container.end-node {
    border-radius: 20px;
    background: #f8fafc;
    border-color: #cbd5e1;
}

.node-container.start-node .node-title,
.node-container.end-node .node-title {
    background: #1e293b;
    border-radius: 18px;
    text-align: center;
    justify-content: center;
    padding: 10px 20px;
}

/* Agent/Process nodes - blue like LangGraph */
.node-container.agent-node,
.node-container.langgraph-blue {
    background: #e0f2fe;
    border-color: #7dd3fc;
}

.node-container.agent-node .node-title,
.node-container.langgraph-blue .node-title {
    background: transparent;
    color: #0c4a6e;
    font-weight: 500;
    border-radius: 6px 6px 0 0;
}

/* Tool nodes - pink like LangGraph */
.node-container.tool-node,
.node-container.langgraph-pink {
    background: #fce7f3;
    border-color: #f9a8d4;
}

.node-container.tool-node .node-title,
.node-container.langgraph-pink .node-title {
    background: transparent;
    color: #831843;
    font-weight: 500;
}

/* LLM nodes - purple */
.node-container.llm-node {
    background: #f3e8ff;
    border-color: #c4b5fd;
}

.node-container.llm-node .node-title {
    background: transparent;
    color: #581c87;
    font-weight: 500;
}

/* Condition nodes - orange */
.node-container.condition-node {
    background: #fef3c7;
    border-color: #fcd34d;
}

.node-container.condition-node .node-title {
    background: transparent;
    color: #92400e;
    font-weight: 500;
}

/* Edge label styles - pill badges like LangGraph */
.edge-label {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 11px;
    color: #64748b;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Node palette */
.node-palette {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 16px;
    background: white;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.node-palette .palette-title {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.palette-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    cursor: grab;
    user-select: none;
    transition: all 0.2s;
}

.palette-item:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
    transform: translateY(-1px);
}

.palette-item:active {
    cursor: grabbing;
    transform: translateY(0);
}

.palette-item .icon {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #3b82f6;
    color: white;
    border-radius: 6px;
    font-size: 14px;
}

.palette-item .label {
    font-size: 13px;
    font-weight: 500;
    color: #334155;
}

/* Controls */
.flow-controls {
    position: absolute;
    bottom: 16px;
    right: 16px;
    display: flex;
    gap: 4px;
    background: white;
    padding: 4px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #e2e8f0;
    z-index: 10;
}

.flow-controls button {
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    cursor: pointer;
    border-radius: 6px;
    font-size: 16px;
    color: #64748b;
    transition: all 0.2s;
}

.flow-controls button:hover {
    background: #f1f5f9;
    color: #334155;
}

/* Edge animation for running state */
@keyframes ant-line {
    to {
        stroke-dashoffset: -1000;
    }
}

/* Palette group styles */
.palette-group {
    margin-bottom: 8px;
}

.palette-group-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: #f8fafc;
    border-radius: 6px;
    cursor: pointer;
    user-select: none;
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
}

.palette-group-header:hover {
    background: #f1f5f9;
}

.group-arrow {
    font-size: 10px;
    color: #94a3b8;
}

.group-title-text {
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.palette-group-content {
    padding: 8px 0 0 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

/* Status badge */
.status-badge {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.status-badge.status-running {
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* ER Table styles */
.er-table-node {
    background: white;
    border-radius: 6px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.er-table-header {
    background: #5F95FF;
    color: white;
    padding: 8px 12px;
    font-weight: bold;
    font-size: 13px;
}

.er-table-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 12px;
    border-bottom: 1px solid #f1f5f9;
    font-size: 12px;
}

.er-table-row:nth-child(even) {
    background: #f8fafc;
}

.er-column-name {
    display: flex;
    align-items: center;
    gap: 4px;
}

.er-column-type {
    color: #94a3b8;
}

/* DAG node styles */
.dag-node {
    display: flex;
    align-items: center;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 8px 12px;
    gap: 8px;
}

.dag-node-status-bar {
    width: 4px;
    height: 100%;
    border-radius: 2px;
}

.dag-node-icon {
    font-size: 16px;
}

.dag-node-label {
    flex: 1;
    font-size: 13px;
    color: #374151;
}

.dag-node-status {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
}

/* Port visibility - hidden by default, shown on hover */
.x6-port-body {
    opacity: 0;
    transition: opacity 0.2s ease;
}

.x6-node:hover .x6-port-body {
    opacity: 1;
}

/* Port circle styling */
.x6-port-body circle {
    fill: #fff;
    stroke: #1890ff;
    stroke-width: 2;
    cursor: crosshair;
    r: 6;
    transition: all 0.2s ease;
}

.x6-port:hover .x6-port-body circle {
    fill: #e6f7ff;
    stroke: #40a9ff;
    stroke-width: 3;
    r: 8;
}

/* Port available state during connection */
.x6-port-available .x6-port-body {
    opacity: 1;
}

.x6-port-available .x6-port-body circle {
    fill: #f6ffed;
    stroke: #52c41a;
    stroke-width: 3;
    r: 8;
}

/* Edge hover effect */
.x6-edge:hover path:nth-child(2) {
    stroke: #1890ff;
}
"""
