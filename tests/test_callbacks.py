"""Tests for callback system."""

import pytest
from fastflow.callbacks import (
    FlowCallback,
    FlowState,
    SSECallback,
    LoggingCallback,
    TimingCallback,
    RetryCallback,
    ProgressCallback,
    CancelFlowException,
    SkipNodeException,
    RetryNodeException,
)


class TestFlowState:
    """Test FlowState dataclass."""

    def test_flow_state_creation(self):
        state = FlowState(
            graph_id="test-flow",
            nodes=[{"id": "n1"}, {"id": "n2"}],
            edges=[("n1", "n2")],
        )
        assert state.graph_id == "test-flow"
        assert len(state.nodes) == 2
        assert len(state.edges) == 1
        assert state.cancelled == False
        assert state.has_errors == False

    def test_get_set_result(self):
        state = FlowState(graph_id="test")
        state.set_result("node1", {"data": "value"})
        assert state.get_result("node1") == {"data": "value"}
        assert state.get_result("nonexistent") is None

    def test_add_error(self):
        state = FlowState(graph_id="test")
        state.add_error(Exception("Test error"), "node1")
        assert state.has_errors == True
        assert len(state.errors) == 1
        assert state.errors[0]["node_id"] == "node1"
        assert "Test error" in state.errors[0]["message"]


class TestControlFlowExceptions:
    """Test control flow exceptions."""

    def test_cancel_flow_exception(self):
        exc = CancelFlowException("Cancelled for testing")
        assert str(exc) == "Cancelled for testing"

    def test_skip_node_exception(self):
        exc = SkipNodeException("Skip this node")
        assert str(exc) == "Skip this node"

    def test_retry_node_exception(self):
        exc = RetryNodeException(max_retries=5, delay=2.0)
        assert exc.max_retries == 5
        assert exc.delay == 2.0


class TestSSECallback:
    """Test SSECallback."""

    def test_sse_callback_before_flow(self):
        """Test that before_flow resets nodes to pending."""

        class MockNode:
            def __init__(self, id):
                self.id = id

        sse = SSECallback()
        state = FlowState(
            graph_id="test",
            nodes=[MockNode("n1"), MockNode("n2")],
        )
        sse.before_flow(state)
        messages = sse.get_messages()

        assert len(messages) == 2
        assert "pending" in messages[0]
        assert "n1" in messages[0]

    def test_sse_callback_before_node(self):
        """Test that before_node marks node as running."""

        class MockNode:
            def __init__(self, id):
                self.id = id

        sse = SSECallback()
        state = FlowState(graph_id="test")
        state.current_node = MockNode("test-node")

        sse.before_node(state)
        messages = sse.get_messages()

        assert len(messages) == 1
        assert "running" in messages[0]
        assert "test-node" in messages[0]

    def test_sse_callback_after_flow_success(self):
        """Test completion message on success."""
        sse = SSECallback()
        state = FlowState(graph_id="test", results={"n1": "result1"})

        sse.after_flow(state)
        messages = sse.get_messages()

        assert len(messages) == 1
        assert "complete" in messages[0].lower() or "completed" in messages[0].lower()


class TestLoggingCallback:
    """Test LoggingCallback."""

    def test_logging_callback_creates_logger(self):
        cb = LoggingCallback()
        assert cb.logger is not None
        assert cb.logger.name == "fastflow"

    def test_logging_callback_custom_logger(self):
        import logging
        custom_logger = logging.getLogger("custom")
        cb = LoggingCallback(logger=custom_logger)
        assert cb.logger.name == "custom"


class TestTimingCallback:
    """Test TimingCallback."""

    def test_timing_callback_records_start_time(self):
        cb = TimingCallback()
        state = FlowState(graph_id="test")

        cb.before_flow(state)
        assert state.start_time > 0

    def test_timing_callback_records_total_time(self):
        import time
        cb = TimingCallback()
        state = FlowState(graph_id="test")

        cb.before_flow(state)
        time.sleep(0.01)  # Small delay
        cb.after_flow(state)

        assert "total_execution_time" in state.context
        assert state.context["total_execution_time"] > 0


class TestRetryCallback:
    """Test RetryCallback."""

    def test_retry_callback_triggers_retry(self):
        cb = RetryCallback(max_retries=3, delay=0.1)

        class MockNode:
            id = "test-node"

        state = FlowState(graph_id="test")
        state.current_node = MockNode()

        # First error should trigger retry
        with pytest.raises(RetryNodeException) as exc_info:
            cb.on_error(state, Exception("Test error"))

        assert exc_info.value.max_retries == 2  # 3 - 1 = 2 remaining

    def test_retry_callback_respects_max_retries(self):
        cb = RetryCallback(max_retries=2, delay=0.1)

        class MockNode:
            id = "test-node"

        state = FlowState(graph_id="test")
        state.current_node = MockNode()

        # Exhaust retries
        cb.before_flow(state)
        with pytest.raises(RetryNodeException):
            cb.on_error(state, Exception("Error 1"))
        with pytest.raises(RetryNodeException):
            cb.on_error(state, Exception("Error 2"))

        # Third error should not raise (no more retries)
        cb.on_error(state, Exception("Error 3"))  # Should not raise


class TestProgressCallback:
    """Test ProgressCallback."""

    def test_progress_callback_tracks_progress(self):
        progress_values = []

        def on_progress(pct, node_id):
            progress_values.append((pct, node_id))

        cb = ProgressCallback(on_progress=on_progress)

        class MockNode:
            def __init__(self, id):
                self.id = id

        state = FlowState(
            graph_id="test",
            nodes=[MockNode("n1"), MockNode("n2"), MockNode("n3")],
        )

        cb.before_flow(state)

        state.current_node = MockNode("n1")
        cb.after_node(state)
        assert len(progress_values) == 1
        assert progress_values[0][0] == pytest.approx(33.33, rel=0.01)

        state.current_node = MockNode("n2")
        cb.after_node(state)
        assert progress_values[1][0] == pytest.approx(66.67, rel=0.01)

        state.current_node = MockNode("n3")
        cb.after_node(state)
        assert progress_values[2][0] == 100.0


class TestCustomCallback:
    """Test creating custom callbacks."""

    def test_custom_callback_lifecycle(self):
        """Test that custom callbacks can implement all lifecycle hooks."""
        calls = []

        class TestCallback(FlowCallback):
            order = 50

            def before_flow(self, state):
                calls.append("before_flow")

            def before_node(self, state):
                calls.append("before_node")

            def after_node(self, state):
                calls.append("after_node")

            def after_flow(self, state):
                calls.append("after_flow")

        cb = TestCallback()
        state = FlowState(graph_id="test")

        cb.before_flow(state)
        cb.before_node(state)
        cb.after_node(state)
        cb.after_flow(state)

        assert calls == ["before_flow", "before_node", "after_node", "after_flow"]

    def test_callback_order(self):
        """Test that callbacks are sortable by order."""

        class HighPriority(FlowCallback):
            order = 1

        class LowPriority(FlowCallback):
            order = 100

        callbacks = [LowPriority(), HighPriority()]
        sorted_callbacks = sorted(callbacks, key=lambda c: c.order)

        assert isinstance(sorted_callbacks[0], HighPriority)
        assert isinstance(sorted_callbacks[1], LowPriority)
