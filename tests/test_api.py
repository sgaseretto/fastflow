"""Tests for Layer 3 convenience API."""

import pytest
from fastflow.api import (
    quick_flow,
    run_pipeline,
    from_dict,
    to_dict,
    flow_from_steps,
)
from fastflow.state import Flow, NodeData, EdgeData
from fastflow.execution import FlowExecutor, ExecutionStep


class TestQuickFlow:
    """Test quick_flow convenience function."""

    def test_quick_flow_basic(self):
        executor = quick_flow([
            {"id": "step1"},
            {"id": "step2", "depends_on": ["step1"]},
            {"id": "step3", "depends_on": ["step2"]},
        ])

        assert isinstance(executor, FlowExecutor)
        assert executor.graph_id == "quick-flow"
        assert len(executor.steps) == 3

    def test_quick_flow_with_handlers(self):
        async def handler1(context, inputs):
            return "result1"

        async def handler2(context, inputs):
            return "result2"

        executor = quick_flow([
            {"id": "step1", "handler": handler1},
            {"id": "step2", "depends_on": ["step1"], "handler": handler2},
        ])

        assert executor.steps[0].handler == handler1
        assert executor.steps[1].handler == handler2

    def test_quick_flow_custom_graph_id(self):
        executor = quick_flow(
            [{"id": "step1"}],
            graph_id="my-custom-flow"
        )
        assert executor.graph_id == "my-custom-flow"

    def test_quick_flow_with_duration(self):
        executor = quick_flow([
            {"id": "step1", "duration": 2.5},
        ])
        assert executor.steps[0].duration == 2.5


class TestRunPipeline:
    """Test run_pipeline convenience function."""

    def test_run_pipeline_basic(self):
        async def step1(context, inputs):
            return "step1"

        async def step2(context, inputs):
            return "step2"

        async def step3(context, inputs):
            return "step3"

        executor = run_pipeline([step1, step2, step3])

        assert isinstance(executor, FlowExecutor)
        assert len(executor.steps) == 3

        # Check sequential dependencies
        assert executor.steps[0].depends_on == []
        assert executor.steps[1].depends_on == ["step1"]
        assert executor.steps[2].depends_on == ["step2"]

    def test_run_pipeline_uses_function_names(self):
        async def load_data(context, inputs):
            pass

        async def process(context, inputs):
            pass

        executor = run_pipeline([load_data, process])

        assert executor.steps[0].node_id == "load_data"
        assert executor.steps[1].node_id == "process"


class TestFlowSerialization:
    """Test from_dict and to_dict functions."""

    def test_from_dict(self):
        data = {
            "nodes": [
                {"id": "n1", "x": 100, "y": 200, "data": {"label": "Node 1"}},
                {"id": "n2", "x": 300, "y": 200, "data": {"label": "Node 2"}},
            ],
            "edges": [
                {"source": "n1", "target": "n2"},
            ],
        }

        flow = from_dict(data, flow_id="test-flow", name="Test Flow")

        assert isinstance(flow, Flow)
        assert flow.id == "test-flow"
        assert flow.name == "Test Flow"
        assert len(flow.nodes) == 2
        assert len(flow.edges) == 1

    def test_to_dict(self):
        flow = Flow(
            id="test",
            name="Test",
            nodes=[
                NodeData(id="n1", x=100, y=100, label="Node 1"),
                NodeData(id="n2", x=200, y=100, label="Node 2"),
            ],
            edges=[
                EdgeData(source="n1", target="n2"),
            ],
        )

        data = to_dict(flow)

        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1
        assert data["nodes"][0]["id"] == "n1"

    def test_roundtrip(self):
        """Test that to_dict and from_dict are inverses."""
        original = Flow(
            id="test",
            name="Test Flow",
            nodes=[
                NodeData(id="n1", x=100, y=200, label="Start", node_type="start"),
                NodeData(id="n2", x=300, y=200, label="End", node_type="end"),
            ],
            edges=[
                EdgeData(source="n1", target="n2", label="next"),
            ],
        )

        data = to_dict(original)
        restored = from_dict(data, flow_id="test", name="Test Flow")

        assert len(restored.nodes) == len(original.nodes)
        assert len(restored.edges) == len(original.edges)
        assert restored.nodes[0].id == original.nodes[0].id


class TestFlowFromSteps:
    """Test flow_from_steps helper."""

    def test_flow_from_steps_vertical(self):
        flow = flow_from_steps([
            {"id": "start", "node_type": "start"},
            {"id": "process", "depends_on": ["start"]},
            {"id": "end", "node_type": "end", "depends_on": ["process"]},
        ], layout="vertical")

        assert len(flow.nodes) == 3
        assert len(flow.edges) == 2

        # Check vertical layout (y increases)
        assert flow.nodes[0].y < flow.nodes[1].y < flow.nodes[2].y

    def test_flow_from_steps_horizontal(self):
        flow = flow_from_steps([
            {"id": "start", "node_type": "start"},
            {"id": "process", "depends_on": ["start"]},
        ], layout="horizontal")

        # Check horizontal layout (x increases)
        assert flow.nodes[0].x < flow.nodes[1].x

    def test_flow_from_steps_with_labels(self):
        flow = flow_from_steps([
            {"id": "n1", "label": "Custom Label 1"},
            {"id": "n2", "label": "Custom Label 2", "depends_on": ["n1"]},
        ])

        assert flow.nodes[0].label == "Custom Label 1"
        assert flow.nodes[1].label == "Custom Label 2"

    def test_flow_from_steps_sets_ports(self):
        flow = flow_from_steps([
            {"id": "start", "node_type": "start"},
            {"id": "end", "node_type": "end", "depends_on": ["start"]},
        ])

        # Start should have no inputs, 1 output
        start_node = flow.get_node("start")
        assert start_node.inputs == 0
        assert start_node.outputs == 1

        # End should have 1 input, no outputs
        end_node = flow.get_node("end")
        assert end_node.inputs == 1
        assert end_node.outputs == 0
