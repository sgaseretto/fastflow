"""Tests for type dispatch system."""

import pytest
from fastflow.types import (
    FlowNode,
    StartNode,
    EndNode,
    AgentNode,
    ToolNode,
    render,
    execute,
    validate,
    can_connect,
    node_to_x6,
    node_from_x6,
    NODE_TYPE_MAP,
    register_node_type,
)


class TestTypedNodes:
    """Test typed node classes."""

    def test_start_node_creation(self):
        node = StartNode(id="start1", x=100, y=200)
        assert node.id == "start1"
        assert node.x == 100
        assert node.y == 200
        assert node.node_type == "start"
        assert node.inputs == 0
        assert node.outputs == 1

    def test_end_node_creation(self):
        node = EndNode(id="end1")
        assert node.node_type == "end"
        assert node.inputs == 1
        assert node.outputs == 0

    def test_agent_node_creation(self):
        node = AgentNode(id="agent1", model="gpt-4", temperature=0.5)
        assert node.id == "agent1"
        assert node.model == "gpt-4"
        assert node.temperature == 0.5
        assert node.node_type == "agent"

    def test_tool_node_creation(self):
        node = ToolNode(id="tool1", tool_name="search")
        assert node.tool_name == "search"
        assert node.node_type == "tool"


class TestTypeDispatch:
    """Test type-dispatched operations."""

    def test_render_start_node(self):
        node = StartNode(id="start")
        html = render(node)
        assert "node-start" in html

    def test_render_agent_node(self):
        node = AgentNode(id="agent", model="gpt-4")
        html = render(node)
        assert "gpt-4" in html

    def test_validate_valid_agent(self):
        node = AgentNode(id="agent", model="gpt-4", temperature=0.5)
        errors = validate(node)
        assert len(errors) == 0

    def test_validate_invalid_agent_no_model(self):
        node = AgentNode(id="agent", model="", temperature=0.5)
        errors = validate(node)
        assert any("model" in e.lower() for e in errors)

    def test_validate_invalid_agent_temperature(self):
        node = AgentNode(id="agent", model="gpt-4", temperature=3.0)
        errors = validate(node)
        assert any("temperature" in e.lower() for e in errors)

    def test_validate_tool_node_no_name(self):
        node = ToolNode(id="tool", tool_name="")
        errors = validate(node)
        assert any("tool_name" in e.lower() for e in errors)


class TestConnectionValidation:
    """Test two-parameter type dispatch for connection validation."""

    def test_can_connect_start_to_agent(self):
        start = StartNode(id="start")
        agent = AgentNode(id="agent")
        allowed, reason = can_connect(start, agent)
        assert allowed == True

    def test_cannot_connect_start_to_end(self):
        start = StartNode(id="start")
        end = EndNode(id="end")
        allowed, reason = can_connect(start, end)
        assert allowed == False
        assert "start directly to end" in reason.lower()

    def test_cannot_connect_from_end(self):
        end = EndNode(id="end")
        agent = AgentNode(id="agent")
        allowed, reason = can_connect(end, agent)
        assert allowed == False
        assert "outgoing" in reason.lower()

    def test_cannot_connect_to_start(self):
        agent = AgentNode(id="agent")
        start = StartNode(id="start")
        allowed, reason = can_connect(agent, start)
        assert allowed == False
        assert "incoming" in reason.lower()


class TestSerialization:
    """Test node serialization."""

    def test_node_to_x6(self):
        node = AgentNode(id="agent1", x=100, y=200, model="gpt-4")
        x6_data = node_to_x6(node)
        assert x6_data["id"] == "agent1"
        assert x6_data["x"] == 100
        assert x6_data["y"] == 200
        assert x6_data["data"]["nodeType"] == "agent"
        assert x6_data["data"]["model"] == "gpt-4"

    def test_node_from_x6(self):
        x6_data = {
            "id": "agent1",
            "x": 100,
            "y": 200,
            "data": {
                "label": "My Agent",
                "nodeType": "agent",
                "model": "gpt-4",
            }
        }
        node = node_from_x6(x6_data)
        assert node.id == "agent1"
        assert isinstance(node, AgentNode)


class TestNodeRegistry:
    """Test node type registry."""

    def test_builtin_types_registered(self):
        assert "agent" in NODE_TYPE_MAP
        assert "tool" in NODE_TYPE_MAP
        assert "start" in NODE_TYPE_MAP
        assert "end" in NODE_TYPE_MAP

    def test_register_custom_type(self):
        from dataclasses import dataclass, field

        @dataclass
        class CustomNode(FlowNode):
            custom_field: str = "default"

        register_node_type("custom", CustomNode)
        assert "custom" in NODE_TYPE_MAP
        assert NODE_TYPE_MAP["custom"] == CustomNode


@pytest.mark.asyncio
class TestExecuteDispatch:
    """Test async execute dispatch."""

    async def test_execute_start_node(self):
        node = StartNode(id="start")
        result = await execute(node, {"initial_data": {"foo": "bar"}}, {})
        assert result == {"foo": "bar"}

    async def test_execute_end_node(self):
        node = EndNode(id="end")
        inputs = {"step1": "result1", "step2": "result2"}
        result = await execute(node, {}, inputs)
        assert "final_results" in result
        assert result["final_results"] == inputs

    async def test_execute_agent_node_no_llm(self):
        node = AgentNode(id="agent", model="gpt-4")
        result = await execute(node, {}, {})
        assert result["status"] == "no_llm_configured"
