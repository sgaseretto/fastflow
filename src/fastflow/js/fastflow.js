/**
 * Fastflow JavaScript Bridge for X6
 *
 * Provides helper functions for X6-HTMX integration.
 * The main initialization happens inline in FlowEditor components,
 * but this file provides additional utilities.
 */

window.fastflow = window.fastflow || {};

/**
 * Get a Fastflow graph instance by ID
 * @param {string} id - The editor ID
 * @returns {X6.Graph|null} The X6 Graph instance or null
 */
window.fastflow.getGraph = function(id) {
    return window.fastflow[id] || null;
};

/**
 * Export flow data from a graph
 * @param {string} id - The graph ID
 * @returns {object|null} The exported flow data or null
 */
window.fastflow.exportFlow = function(id) {
    const graph = window.fastflow.getGraph(id);
    if (!graph) return null;

    // Use the attached exportFlow function if available
    if (graph.exportFlow) {
        return graph.exportFlow();
    }

    // Fallback export
    const nodes = graph.getNodes().map(node => ({
        id: node.id,
        x: node.position().x,
        y: node.position().y,
        width: node.size().width,
        height: node.size().height,
        data: node.getData(),
    }));

    const edges = graph.getEdges().map(edge => ({
        id: edge.id,
        source: edge.getSourceCellId(),
        target: edge.getTargetCellId(),
        sourcePort: edge.getSourcePortId(),
        targetPort: edge.getTargetPortId(),
        labels: edge.getLabels(),
    }));

    return { nodes, edges };
};

/**
 * Import flow data into a graph
 * @param {string} id - The graph ID
 * @param {object|string} data - The flow data (object or JSON string)
 */
window.fastflow.importFlow = function(id, data) {
    const graph = window.fastflow.getGraph(id);
    if (!graph) return;

    if (typeof data === 'string') {
        data = JSON.parse(data);
    }

    // Clear existing cells
    graph.clearCells();

    // Import nodes
    if (data.nodes) {
        data.nodes.forEach(nodeConfig => {
            const ports = [];
            const nodeData = nodeConfig.data || {};

            // Recreate ports from data
            const inputs = nodeData.inputs || 1;
            const outputs = nodeData.outputs || 1;

            for (let i = 0; i < inputs; i++) {
                ports.push({ id: 'in_' + i, group: 'top' });
            }
            for (let i = 0; i < outputs; i++) {
                ports.push({ id: 'out_' + i, group: 'bottom' });
            }

            // Get node style based on type
            const nodeStyles = {
                'start': { fill: '#1e293b', stroke: '#1e293b', textColor: '#fff', rx: 20, ry: 20 },
                'end': { fill: '#1e293b', stroke: '#1e293b', textColor: '#fff', rx: 20, ry: 20 },
                'agent': { fill: '#dbeafe', stroke: '#60a5fa', textColor: '#1e40af', rx: 8, ry: 8 },
                'tool': { fill: '#fce7f3', stroke: '#f472b6', textColor: '#9d174d', rx: 8, ry: 8 },
                'llm': { fill: '#f3e8ff', stroke: '#c084fc', textColor: '#6b21a8', rx: 8, ry: 8 },
                'condition': { fill: '#fef3c7', stroke: '#fbbf24', textColor: '#92400e', rx: 8, ry: 8 },
                'default': { fill: '#f1f5f9', stroke: '#94a3b8', textColor: '#334155', rx: 8, ry: 8 },
            };
            const nodeType = nodeData.nodeType || 'default';
            const style = nodeStyles[nodeType] || nodeStyles['default'];

            graph.addNode({
                id: nodeConfig.id,
                shape: 'rect',
                x: nodeConfig.x,
                y: nodeConfig.y,
                width: nodeConfig.width || 160,
                height: nodeConfig.height || 60,
                attrs: {
                    body: {
                        fill: style.fill,
                        stroke: style.stroke,
                        strokeWidth: 2,
                        rx: style.rx,
                        ry: style.ry,
                    },
                    label: {
                        text: nodeData.label || nodeConfig.id,
                        fill: style.textColor,
                        fontSize: 14,
                        fontWeight: 500,
                    },
                },
                ports: {
                    groups: {
                        top: {
                            position: 'top',
                            attrs: {
                                circle: { r: 5, magnet: true, stroke: '#5F95FF', strokeWidth: 1, fill: '#fff' },
                            },
                        },
                        bottom: {
                            position: 'bottom',
                            attrs: {
                                circle: { r: 5, magnet: true, stroke: '#5F95FF', strokeWidth: 1, fill: '#fff' },
                            },
                        },
                    },
                    items: ports,
                },
                data: nodeData,
            });
        });
    }

    // Import edges
    if (data.edges) {
        data.edges.forEach(edgeConfig => {
            const edge = graph.addEdge({
                source: { cell: edgeConfig.source, port: edgeConfig.sourcePort || 'out_0' },
                target: { cell: edgeConfig.target, port: edgeConfig.targetPort || 'in_0' },
                attrs: {
                    line: {
                        stroke: '#94a3b8',
                        strokeWidth: 2,
                        strokeDasharray: edgeConfig.dashed ? '5 5' : null,
                        targetMarker: {
                            name: 'classic',
                            size: 8,
                        },
                    },
                },
                connector: {
                    name: 'smooth',
                    args: { direction: 'V' },
                },
            });

            // Restore labels
            if (edgeConfig.labels && edgeConfig.labels.length > 0) {
                edgeConfig.labels.forEach(label => {
                    edge.appendLabel(label);
                });
            }
        });
    }
};

/**
 * Clear all cells from a graph
 * @param {string} id - The graph ID
 */
window.fastflow.clearFlow = function(id) {
    const graph = window.fastflow.getGraph(id);
    if (!graph) return;
    graph.clearCells();
};

/**
 * Add a node programmatically
 * @param {string} id - The graph ID
 * @param {object} nodeConfig - Node configuration
 */
window.fastflow.addNode = function(id, nodeConfig) {
    const graph = window.fastflow.getGraph(id);
    if (!graph) return null;

    const ports = [];
    const inputs = nodeConfig.inputs || 1;
    const outputs = nodeConfig.outputs || 1;

    for (let i = 0; i < inputs; i++) {
        ports.push({ id: 'in_' + i, group: 'top' });
    }
    for (let i = 0; i < outputs; i++) {
        ports.push({ id: 'out_' + i, group: 'bottom' });
    }

    // Get node style based on type
    const nodeStyles = {
        'start': { fill: '#1e293b', stroke: '#1e293b', textColor: '#fff', rx: 20, ry: 20 },
        'end': { fill: '#1e293b', stroke: '#1e293b', textColor: '#fff', rx: 20, ry: 20 },
        'agent': { fill: '#dbeafe', stroke: '#60a5fa', textColor: '#1e40af', rx: 8, ry: 8 },
        'tool': { fill: '#fce7f3', stroke: '#f472b6', textColor: '#9d174d', rx: 8, ry: 8 },
        'llm': { fill: '#f3e8ff', stroke: '#c084fc', textColor: '#6b21a8', rx: 8, ry: 8 },
        'condition': { fill: '#fef3c7', stroke: '#fbbf24', textColor: '#92400e', rx: 8, ry: 8 },
        'input': { fill: '#dcfce7', stroke: '#4ade80', textColor: '#166534', rx: 8, ry: 8 },
        'output': { fill: '#fee2e2', stroke: '#f87171', textColor: '#991b1b', rx: 8, ry: 8 },
        'transform': { fill: '#e0f2fe', stroke: '#38bdf8', textColor: '#0369a1', rx: 8, ry: 8 },
        'default': { fill: '#f1f5f9', stroke: '#94a3b8', textColor: '#334155', rx: 8, ry: 8 },
    };
    const nodeType = nodeConfig.nodeType || 'default';
    const style = nodeStyles[nodeType] || nodeStyles['default'];
    const isStartEnd = nodeType === 'start' || nodeType === 'end';

    return graph.addNode({
        id: nodeConfig.name || nodeConfig.id,
        shape: 'rect',
        x: nodeConfig.x || 100,
        y: nodeConfig.y || 100,
        width: isStartEnd ? 120 : (nodeConfig.width || 160),
        height: isStartEnd ? 40 : (nodeConfig.height || 50),
        attrs: {
            body: {
                fill: style.fill,
                stroke: style.stroke,
                strokeWidth: 2,
                rx: style.rx,
                ry: style.ry,
            },
            label: {
                text: nodeConfig.label || nodeConfig.name,
                fill: style.textColor,
                fontSize: 14,
                fontWeight: isStartEnd ? 600 : 500,
            },
        },
        ports: {
            groups: {
                top: {
                    position: 'top',
                    attrs: {
                        circle: { r: 5, magnet: true, stroke: '#5F95FF', strokeWidth: 1, fill: '#fff' },
                    },
                },
                bottom: {
                    position: 'bottom',
                    attrs: {
                        circle: { r: 5, magnet: true, stroke: '#5F95FF', strokeWidth: 1, fill: '#fff' },
                    },
                },
            },
            items: ports,
        },
        data: {
            name: nodeConfig.name,
            label: nodeConfig.label,
            nodeType: nodeConfig.nodeType,
            inputs: inputs,
            outputs: outputs,
            ...(nodeConfig.data || {})
        },
    });
};

/**
 * Remove a node by ID
 * @param {string} graphId - The graph ID
 * @param {string} nodeId - The node ID to remove
 */
window.fastflow.removeNode = function(graphId, nodeId) {
    const graph = window.fastflow.getGraph(graphId);
    if (!graph) return;

    const node = graph.getCellById(nodeId);
    if (node) {
        graph.removeCell(node);
    }
};

/**
 * Add an edge between nodes
 * @param {string} id - The graph ID
 * @param {object} edgeConfig - Edge configuration
 */
window.fastflow.addEdge = function(id, edgeConfig) {
    const graph = window.fastflow.getGraph(id);
    if (!graph) return null;

    const edge = graph.addEdge({
        source: { cell: edgeConfig.source, port: 'out_' + (edgeConfig.sourcePort || 0) },
        target: { cell: edgeConfig.target, port: 'in_' + (edgeConfig.targetPort || 0) },
        attrs: {
            line: {
                stroke: '#94a3b8',
                strokeWidth: 2,
                strokeDasharray: edgeConfig.dashed ? '5 5' : null,
                targetMarker: {
                    name: 'classic',
                    size: 8,
                },
            },
        },
        connector: {
            name: 'smooth',
            args: { direction: 'V' },
        },
    });

    // Add label if provided
    if (edgeConfig.label) {
        edge.appendLabel({
            attrs: {
                text: {
                    text: edgeConfig.label,
                    fill: '#64748b',
                    fontSize: 11,
                },
                rect: {
                    fill: '#fff',
                    stroke: '#e2e8f0',
                    strokeWidth: 1,
                    rx: 12,
                    ry: 12,
                },
            },
            position: {
                distance: 0.5,
            },
        });
    }

    return edge;
};

/**
 * Update node data
 * @param {string} graphId - The graph ID
 * @param {string} nodeId - The node ID
 * @param {object} data - New data to merge
 */
window.fastflow.updateNodeData = function(graphId, nodeId, data) {
    const graph = window.fastflow.getGraph(graphId);
    if (!graph) return;

    const node = graph.getCellById(nodeId);
    if (!node) return;

    const currentData = node.getData() || {};
    node.setData({ ...currentData, ...data });
};

/**
 * Get selected cells
 * @param {string} id - The graph ID
 * @returns {Array} Array of selected cell IDs
 */
window.fastflow.getSelected = function(id) {
    const graph = window.fastflow.getGraph(id);
    if (!graph) return [];

    const cells = graph.getSelectedCells();
    return cells.map(cell => cell.id);
};

/**
 * Zoom controls
 */
window.fastflow.zoomIn = function(id) {
    const graph = window.fastflow.getGraph(id);
    if (graph) graph.zoom(0.1);
};

window.fastflow.zoomOut = function(id) {
    const graph = window.fastflow.getGraph(id);
    if (graph) graph.zoom(-0.1);
};

window.fastflow.zoomToFit = function(id) {
    const graph = window.fastflow.getGraph(id);
    if (graph) graph.zoomToFit({ padding: 50 });
};

window.fastflow.centerContent = function(id) {
    const graph = window.fastflow.getGraph(id);
    if (graph) graph.centerContent();
};

/**
 * Delete selected cells (nodes and edges)
 * @param {string} id - The graph ID
 */
window.fastflow.deleteSelected = function(id) {
    const graph = window.fastflow.getGraph(id);
    if (!graph) return;
    const cells = graph.getSelectedCells();
    if (cells.length) {
        graph.removeCells(cells);
    }
};

/**
 * Delete a specific cell by ID
 * @param {string} graphId - The graph ID
 * @param {string} cellId - The cell ID to delete
 */
window.fastflow.deleteCell = function(graphId, cellId) {
    const graph = window.fastflow.getGraph(graphId);
    if (!graph) return;
    const cell = graph.getCellById(cellId);
    if (cell) {
        graph.removeCell(cell);
    }
};

/**
 * Rename a node
 * @param {string} graphId - The graph ID
 * @param {string} nodeId - The node ID
 * @param {string} newLabel - The new label
 */
window.fastflow.renameNode = function(graphId, nodeId, newLabel) {
    const graph = window.fastflow.getGraph(graphId);
    if (!graph) return;
    const node = graph.getCellById(nodeId);
    if (node && node.isNode()) {
        const data = node.getData() || {};
        node.setData({ ...data, label: newLabel });
        node.attr('label/text', newLabel);
    }
};

/**
 * Set edge label
 * @param {string} graphId - The graph ID
 * @param {string} edgeId - The edge ID
 * @param {string} label - The new label (empty string to remove)
 */
window.fastflow.setEdgeLabel = function(graphId, edgeId, label) {
    const graph = window.fastflow.getGraph(graphId);
    if (!graph) return;
    const edge = graph.getCellById(edgeId);
    if (edge && edge.isEdge()) {
        edge.setLabels([]);
        if (label) {
            edge.appendLabel({
                attrs: {
                    text: {
                        text: label,
                        fill: '#64748b',
                        fontSize: 11,
                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    },
                    rect: {
                        fill: '#fff',
                        stroke: '#e2e8f0',
                        strokeWidth: 1,
                        rx: 10,
                        ry: 10,
                        refWidth: 10,
                        refHeight: 6,
                        refX: -5,
                        refY: -3,
                    },
                },
                position: { distance: 0.5 },
            });
        }
    }
};

/**
 * Set edge dashed style
 * @param {string} graphId - The graph ID
 * @param {string} edgeId - The edge ID
 * @param {boolean} dashed - Whether to make edge dashed
 */
window.fastflow.setEdgeDashed = function(graphId, edgeId, dashed) {
    const graph = window.fastflow.getGraph(graphId);
    if (!graph) return;
    const edge = graph.getCellById(edgeId);
    if (edge && edge.isEdge()) {
        edge.attr('line/strokeDasharray', dashed ? '5 5' : null);
    }
};

/**
 * Get all nodes
 * @param {string} id - The graph ID
 * @returns {Array} Array of node data
 */
window.fastflow.getNodes = function(id) {
    const graph = window.fastflow.getGraph(id);
    if (!graph) return [];
    return graph.getNodes().map(node => ({
        id: node.id,
        x: node.position().x,
        y: node.position().y,
        data: node.getData(),
    }));
};

/**
 * Get all edges
 * @param {string} id - The graph ID
 * @returns {Array} Array of edge data
 */
window.fastflow.getEdges = function(id) {
    const graph = window.fastflow.getGraph(id);
    if (!graph) return [];
    return graph.getEdges().map(edge => ({
        id: edge.id,
        source: edge.getSourceCellId(),
        target: edge.getTargetCellId(),
        labels: edge.getLabels(),
    }));
};

/**
 * Set readonly mode
 * @param {string} id - The graph ID
 * @param {boolean} readonly - Whether to make readonly
 */
window.fastflow.setReadonly = function(id, readonly) {
    const graph = window.fastflow.getGraph(id);
    if (!graph) return;

    graph.disableSelection();
    graph.disablePanning();
    // Note: Full readonly requires graph recreation with interacting: false
};

/**
 * Helper to send flow data to server via HTMX
 * @param {string} graphId - The graph ID
 * @param {string} endpoint - The server endpoint
 * @param {object} extraData - Additional data to send
 */
window.fastflow.sendToServer = function(graphId, endpoint, extraData) {
    const flowData = JSON.stringify(window.fastflow.exportFlow(graphId));

    if (typeof htmx !== 'undefined') {
        htmx.ajax('POST', endpoint, {
            values: {
                flow: flowData,
                ...extraData
            }
        });
    }
};

/**
 * Get JSON representation of the flow
 * @param {string} id - The graph ID
 * @returns {string} JSON string of the flow
 */
window.fastflow.toJSON = function(id) {
    return JSON.stringify(window.fastflow.exportFlow(id), null, 2);
};

// ============================================================================
// SSE-based Execution Support
// These functions enable Python-driven execution visualization via Server-Sent Events
// ============================================================================

/**
 * Status colors for node states
 */
window.fastflow.statusColors = {
    'pending': '#d9d9d9',
    'running': '#1890ff',
    'success': '#52c41a',
    'error': '#ff4d4f',
    'warning': '#faad14',
};

/**
 * Set the execution status of a node
 * Updates the visual appearance (border color, stroke width)
 *
 * @param {string} graphId - The graph ID
 * @param {string} nodeId - The node ID
 * @param {string} status - Status: 'pending', 'running', 'success', 'error', 'warning'
 */
window.fastflow.setNodeStatus = function(graphId, nodeId, status) {
    const graph = window.fastflow.getGraph(graphId);
    if (!graph) return;

    const node = graph.getCellById(nodeId);
    if (!node || !node.isNode()) return;

    const color = window.fastflow.statusColors[status] || window.fastflow.statusColors['pending'];
    const data = node.getData() || {};

    // Store status in node data
    node.setData({ ...data, status: status });

    // Update visual appearance
    if (status === 'pending') {
        // Reset to original style
        const nodeType = data.nodeType || 'default';
        const originalStroke = window.fastflow._getOriginalStroke(nodeType);
        node.attr('body/stroke', originalStroke);
        node.attr('body/strokeWidth', 2);
    } else {
        node.attr('body/stroke', color);
        node.attr('body/strokeWidth', status === 'running' ? 3 : 2);
    }
};

/**
 * Get original stroke color for a node type
 * @private
 */
window.fastflow._getOriginalStroke = function(nodeType) {
    const strokes = {
        'start': '#1e293b', 'end': '#1e293b',
        'agent': '#60a5fa', 'tool': '#f472b6', 'llm': '#c084fc',
        'condition': '#fbbf24', 'input': '#4ade80', 'output': '#f87171',
        'filter': '#38bdf8', 'join': '#fbbf24', 'transform': '#38bdf8',
        'code': '#08979c', 'kb': '#1d39c4', 'mcp': '#08979c', 'db': '#1d39c4',
        'default': '#94a3b8',
    };
    return strokes[nodeType] || strokes['default'];
};

/**
 * Set the execution status of an edge
 * Updates the visual appearance (color, animation)
 *
 * @param {string} graphId - The graph ID
 * @param {string} sourceId - Source node ID
 * @param {string} targetId - Target node ID
 * @param {string} status - Status: 'pending', 'running', 'success', 'error'
 * @param {boolean} animated - Whether to animate the edge (for 'running' status)
 */
window.fastflow.setEdgeStatus = function(graphId, sourceId, targetId, status, animated = false) {
    const graph = window.fastflow.getGraph(graphId);
    if (!graph) return;

    const edges = graph.getEdges();
    for (const edge of edges) {
        if (edge.getSourceCellId() === sourceId && edge.getTargetCellId() === targetId) {
            const color = window.fastflow.statusColors[status] || '#94a3b8';

            edge.attr('line/stroke', color);

            if (animated && status === 'running') {
                edge.attr('line/strokeDasharray', '5 5');
                edge.attr('line/style/animation', 'fastflow-dash 0.5s linear infinite');
            } else {
                const data = edge.getData() || {};
                edge.attr('line/strokeDasharray', data.dashed ? '5 5' : null);
                edge.attr('line/style/animation', null);
            }
            break;
        }
    }
};

/**
 * Set edge status by edge ID
 * @param {string} graphId - The graph ID
 * @param {string} edgeId - The edge ID
 * @param {string} status - Status: 'pending', 'running', 'success', 'error'
 * @param {boolean} animated - Whether to animate
 */
window.fastflow.setEdgeStatusById = function(graphId, edgeId, status, animated = false) {
    const graph = window.fastflow.getGraph(graphId);
    if (!graph) return;

    const edge = graph.getCellById(edgeId);
    if (!edge || !edge.isEdge()) return;

    const color = window.fastflow.statusColors[status] || '#94a3b8';
    edge.attr('line/stroke', color);

    if (animated && status === 'running') {
        edge.attr('line/strokeDasharray', '5 5');
        edge.attr('line/style/animation', 'fastflow-dash 0.5s linear infinite');
    } else {
        const data = edge.getData() || {};
        edge.attr('line/strokeDasharray', data.dashed ? '5 5' : null);
        edge.attr('line/style/animation', null);
    }
};

/**
 * Reset all nodes and edges to pending/default status
 * @param {string} graphId - The graph ID
 */
window.fastflow.resetAllStatus = function(graphId) {
    const graph = window.fastflow.getGraph(graphId);
    if (!graph) return;

    // Reset all nodes
    graph.getNodes().forEach(node => {
        const data = node.getData() || {};
        const nodeType = data.nodeType || 'default';
        const originalStroke = window.fastflow._getOriginalStroke(nodeType);

        node.setData({ ...data, status: 'pending' });
        node.attr('body/stroke', originalStroke);
        node.attr('body/strokeWidth', 2);
    });

    // Reset all edges
    graph.getEdges().forEach(edge => {
        const data = edge.getData() || {};
        edge.attr('line/stroke', '#94a3b8');
        edge.attr('line/strokeDasharray', data.dashed ? '5 5' : null);
        edge.attr('line/style/animation', null);
    });
};

/**
 * Active SSE connections for cleanup
 * @private
 */
window.fastflow._sseConnections = {};

/**
 * Connect to an SSE endpoint for execution updates
 * The server sends events with JSON data containing:
 * - event: 'nodeStatus' | 'edgeStatus' | 'complete' | 'error'
 * - data: { graphId, nodeId?, sourceId?, targetId?, status, message? }
 *
 * @param {string} graphId - The graph ID
 * @param {string} endpoint - The SSE endpoint URL
 * @param {object} options - Options: { onComplete, onError, onProgress }
 * @returns {EventSource} The EventSource connection
 */
window.fastflow.connectExecution = function(graphId, endpoint, options = {}) {
    // Close existing connection if any
    if (window.fastflow._sseConnections[graphId]) {
        window.fastflow._sseConnections[graphId].close();
    }

    const eventSource = new EventSource(endpoint);
    window.fastflow._sseConnections[graphId] = eventSource;

    // Handle node status updates
    eventSource.addEventListener('nodeStatus', (event) => {
        try {
            const data = JSON.parse(event.data);
            window.fastflow.setNodeStatus(
                data.graphId || graphId,
                data.nodeId,
                data.status
            );
            if (options.onProgress) {
                options.onProgress('node', data);
            }
        } catch (e) {
            console.error('Error parsing nodeStatus event:', e);
        }
    });

    // Handle edge status updates
    eventSource.addEventListener('edgeStatus', (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.edgeId) {
                window.fastflow.setEdgeStatusById(
                    data.graphId || graphId,
                    data.edgeId,
                    data.status,
                    data.animated
                );
            } else {
                window.fastflow.setEdgeStatus(
                    data.graphId || graphId,
                    data.sourceId,
                    data.targetId,
                    data.status,
                    data.animated
                );
            }
            if (options.onProgress) {
                options.onProgress('edge', data);
            }
        } catch (e) {
            console.error('Error parsing edgeStatus event:', e);
        }
    });

    // Handle execution complete
    eventSource.addEventListener('complete', (event) => {
        eventSource.close();
        delete window.fastflow._sseConnections[graphId];
        if (options.onComplete) {
            try {
                const data = JSON.parse(event.data);
                options.onComplete(data);
            } catch (e) {
                options.onComplete({});
            }
        }
    });

    // Handle errors
    eventSource.addEventListener('error', (event) => {
        try {
            const data = JSON.parse(event.data);
            if (options.onError) {
                options.onError(data);
            }
        } catch (e) {
            // Connection error, not a message
            if (eventSource.readyState === EventSource.CLOSED) {
                delete window.fastflow._sseConnections[graphId];
                if (options.onError) {
                    options.onError({ message: 'Connection closed' });
                }
            }
        }
    });

    // Handle generic messages (default event)
    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            // Route based on type field
            if (data.type === 'nodeStatus') {
                window.fastflow.setNodeStatus(data.graphId || graphId, data.nodeId, data.status);
            } else if (data.type === 'edgeStatus') {
                if (data.edgeId) {
                    window.fastflow.setEdgeStatusById(data.graphId || graphId, data.edgeId, data.status, data.animated);
                } else {
                    window.fastflow.setEdgeStatus(data.graphId || graphId, data.sourceId, data.targetId, data.status, data.animated);
                }
            }
        } catch (e) {
            // Non-JSON message, ignore
        }
    };

    return eventSource;
};

/**
 * Disconnect an active SSE execution connection
 * @param {string} graphId - The graph ID
 */
window.fastflow.disconnectExecution = function(graphId) {
    if (window.fastflow._sseConnections[graphId]) {
        window.fastflow._sseConnections[graphId].close();
        delete window.fastflow._sseConnections[graphId];
    }
};

/**
 * Check if execution is currently connected
 * @param {string} graphId - The graph ID
 * @returns {boolean}
 */
window.fastflow.isExecutionConnected = function(graphId) {
    const conn = window.fastflow._sseConnections[graphId];
    return conn && conn.readyState === EventSource.OPEN;
};

console.log('Fastflow X6 bridge loaded (with SSE execution support)');
