"""
Two-way callback system for flow execution.

This module implements a fastai-style callback system where callbacks can
both READ and MODIFY execution state at any lifecycle point.

Key features:
- FlowState: Mutable state object passed to all callbacks (like fastai's Learner)
- FlowCallback: Base class with lifecycle hooks
- Control flow via exceptions (CancelFlow, SkipNode, RetryNode)
- Built-in callbacks: SSE, Logging, Timing, Retry, Progress

Example:
    ```python
    from fastflow.callbacks import FlowCallback, FlowState, SSECallback

    class MyCallback(FlowCallback):
        def before_node(self, state: FlowState):
            # Can read and modify state
            print(f"About to execute: {state.current_node.id}")
            state.context["my_data"] = "injected"

        def after_node(self, state: FlowState):
            # Can access results
            result = state.results.get(state.current_node.id)
            print(f"Result: {result}")

    executor = FlowExecutor(
        graph_id="flow",
        steps=[...],
        callbacks=[SSECallback(), MyCallback()]
    )
    ```
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Callable
from abc import ABC
import time
import logging

from .core import raw_node_status, raw_edge_status, raw_complete, raw_error

__all__ = [
    # State
    "FlowState",
    # Exceptions
    "CancelFlowException",
    "SkipNodeException",
    "RetryNodeException",
    # Base callback
    "FlowCallback",
    # Built-in callbacks
    "SSECallback",
    "LoggingCallback",
    "TimingCallback",
    "RetryCallback",
    "ProgressCallback",
    "ValidationCallback",
]


# =============================================================================
# Control Flow Exceptions
# =============================================================================

class CancelFlowException(Exception):
    """
    Raise to cancel the entire flow execution.

    Example:
        ```python
        class SafetyCallback(FlowCallback):
            def before_node(self, state):
                if state.current_node.id == "dangerous":
                    raise CancelFlowException("Safety check failed")
        ```
    """
    pass


class SkipNodeException(Exception):
    """
    Raise to skip the current node and continue with the next.

    Example:
        ```python
        class ConditionalCallback(FlowCallback):
            def before_node(self, state):
                if not state.context.get("should_run_" + state.current_node.id, True):
                    raise SkipNodeException("Condition not met")
        ```
    """
    pass


class RetryNodeException(Exception):
    """
    Raise to retry the current node.

    Attributes:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds

    Example:
        ```python
        class RetryOnErrorCallback(FlowCallback):
            def on_error(self, state, exc):
                if isinstance(exc, ConnectionError):
                    raise RetryNodeException(max_retries=3, delay=1.0)
        ```
    """
    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        self.max_retries = max_retries
        self.delay = delay
        super().__init__(f"Retry requested (max={max_retries}, delay={delay}s)")


# =============================================================================
# Flow State
# =============================================================================

@dataclass
class FlowState:
    """
    Mutable state passed to callbacks.

    This is similar to fastai's Learner - a central object that holds
    all execution state. Callbacks can READ and MODIFY any attribute.

    Attributes:
        graph_id: Identifier for the flow being executed
        nodes: List of all nodes in the flow
        edges: List of all edges as (source_id, target_id) tuples
        current_node: The node currently being executed (or about to be)
        current_edge: The edge currently being traversed
        context: Shared context dictionary (user-provided + accumulated)
        results: Dictionary mapping node_id to execution result
        errors: List of errors that occurred
        cancelled: Whether the flow was cancelled
        skip_current: Whether to skip the current node
        start_time: Flow start timestamp
        node_times: Dictionary mapping node_id to execution time
        iteration: Current iteration number (for loops/retries)
    """
    graph_id: str
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)
    current_node: Any = None
    current_edge: Optional[tuple[str, str]] = None
    context: dict = field(default_factory=dict)
    results: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    cancelled: bool = False
    skip_current: bool = False
    start_time: float = 0
    node_times: dict = field(default_factory=dict)
    iteration: int = 0

    def get_result(self, node_id: str) -> Any:
        """Get the result for a specific node."""
        return self.results.get(node_id)

    def set_result(self, node_id: str, result: Any) -> None:
        """Set the result for a specific node."""
        self.results[node_id] = result

    def add_error(self, error: Exception, node_id: Optional[str] = None) -> None:
        """Record an error."""
        self.errors.append({
            "error": error,
            "node_id": node_id or (self.current_node.id if self.current_node else None),
            "message": str(error),
        })

    @property
    def has_errors(self) -> bool:
        """Check if any errors occurred."""
        return len(self.errors) > 0

    @property
    def total_time(self) -> float:
        """Get total execution time so far."""
        if self.start_time == 0:
            return 0
        return time.time() - self.start_time


# =============================================================================
# Base Callback Class
# =============================================================================

class FlowCallback(ABC):
    """
    Base class for flow execution callbacks.

    Callbacks can READ and MODIFY the FlowState at any lifecycle point.
    This enables powerful patterns like:
    - Logging and monitoring
    - Dynamic flow modification
    - Error recovery and retry
    - Progress reporting
    - Data transformation between nodes

    Lifecycle hooks (called in order):
    1. `before_flow(state)` - Called once before execution starts
    2. `before_node(state)` - Called before each node executes
    3. `after_node(state)` - Called after each node (even on error)
    4. `before_edge(state)` - Called before traversing each edge
    5. `after_edge(state)` - Called after traversing each edge
    6. `after_flow(state)` - Called once after execution completes
    7. `on_error(state, exc)` - Called when an error occurs
    8. `on_cancel(state)` - Called when flow is cancelled

    Attributes:
        order: Lower values run first. Default is 0.

    Example:
        ```python
        class MyCallback(FlowCallback):
            order = 10  # Run after default callbacks

            def before_node(self, state):
                # Inject data before each node
                state.context["timestamp"] = time.time()

            def after_node(self, state):
                # Log results
                print(f"{state.current_node.id}: {state.results.get(state.current_node.id)}")

            def on_error(self, state, exc):
                # Handle errors
                state.context["last_error"] = str(exc)
        ```
    """
    order: int = 0  # Lower runs first

    def before_flow(self, state: FlowState) -> None:
        """Called once before flow execution starts."""
        pass

    def after_flow(self, state: FlowState) -> None:
        """Called once after flow execution completes (success or failure)."""
        pass

    def before_node(self, state: FlowState) -> None:
        """Called before each node executes."""
        pass

    def after_node(self, state: FlowState) -> None:
        """Called after each node executes (even on error)."""
        pass

    def before_edge(self, state: FlowState) -> None:
        """Called before traversing an edge to the next node."""
        pass

    def after_edge(self, state: FlowState) -> None:
        """Called after traversing an edge."""
        pass

    def on_error(self, state: FlowState, exc: Exception) -> None:
        """
        Called when an error occurs during node execution.

        Can raise control flow exceptions:
        - RetryNodeException: Retry the current node
        - SkipNodeException: Skip the node and continue
        - CancelFlowException: Cancel the entire flow
        """
        pass

    def on_cancel(self, state: FlowState) -> None:
        """Called when the flow is cancelled (via CancelFlowException)."""
        pass


# =============================================================================
# Built-in Callbacks
# =============================================================================

class SSECallback(FlowCallback):
    """
    Built-in callback that yields SSE messages for browser updates.

    This is the standard way to send real-time status updates to the browser.
    Messages are accumulated in a buffer and retrieved via `get_messages()`.

    Attributes:
        order: 100 (runs after most callbacks to capture final state)

    Example:
        ```python
        sse = SSECallback()
        executor = FlowExecutor(graph_id="flow", steps=[...], callbacks=[sse])

        async for msg in executor.run():
            yield msg  # SSE messages are yielded automatically
        ```
    """
    order = 100  # Run after other callbacks to capture final state

    def __init__(self):
        self.messages: list[str] = []

    def before_flow(self, state: FlowState) -> None:
        """Reset all nodes to pending."""
        for node in state.nodes:
            node_id = node.id if hasattr(node, "id") else str(node)
            self.messages.append(raw_node_status(node_id, "pending", graphId=state.graph_id))

    def before_node(self, state: FlowState) -> None:
        """Mark node as running."""
        if state.current_node:
            node_id = state.current_node.id if hasattr(state.current_node, "id") else str(state.current_node)
            self.messages.append(raw_node_status(node_id, "running", graphId=state.graph_id))

    def after_node(self, state: FlowState) -> None:
        """Mark node as success or error."""
        if state.current_node:
            node_id = state.current_node.id if hasattr(state.current_node, "id") else str(state.current_node)
            # Check if this node had an error
            has_error = any(
                e.get("node_id") == node_id
                for e in state.errors
            )
            status = "error" if has_error else "success"
            self.messages.append(raw_node_status(node_id, status, graphId=state.graph_id))

    def before_edge(self, state: FlowState) -> None:
        """Animate edge as running."""
        if state.current_edge:
            src, tgt = state.current_edge
            self.messages.append(raw_edge_status(src, tgt, "running", animated=True, graphId=state.graph_id))

    def after_edge(self, state: FlowState) -> None:
        """Mark edge as success."""
        if state.current_edge:
            src, tgt = state.current_edge
            self.messages.append(raw_edge_status(src, tgt, "success", graphId=state.graph_id))

    def after_flow(self, state: FlowState) -> None:
        """Signal completion."""
        if state.cancelled:
            self.messages.append(raw_error("Flow cancelled"))
        elif state.has_errors:
            last_error = state.errors[-1] if state.errors else {}
            self.messages.append(raw_error(
                last_error.get("message", "Execution failed"),
                nodeId=last_error.get("node_id")
            ))
        else:
            self.messages.append(raw_complete(
                message="Execution completed successfully",
                results=state.results
            ))

    def on_error(self, state: FlowState, exc: Exception) -> None:
        """Send error message."""
        node_id = None
        if state.current_node:
            node_id = state.current_node.id if hasattr(state.current_node, "id") else str(state.current_node)
        self.messages.append(raw_error(str(exc), nodeId=node_id))

    def get_messages(self) -> list[str]:
        """Get accumulated messages and clear buffer."""
        msgs = self.messages.copy()
        self.messages.clear()
        return msgs


class LoggingCallback(FlowCallback):
    """
    Callback for logging execution progress.

    Uses Python's logging module to record flow execution events.

    Attributes:
        order: 10 (runs early to capture initial state)
        logger: Python logger instance

    Example:
        ```python
        import logging
        logging.basicConfig(level=logging.DEBUG)

        executor = FlowExecutor(
            graph_id="flow",
            steps=[...],
            callbacks=[LoggingCallback()]
        )
        ```
    """
    order = 10

    def __init__(self, logger: Optional[logging.Logger] = None, level: int = logging.INFO):
        self.logger = logger or logging.getLogger("fastflow")
        self.level = level

    def before_flow(self, state: FlowState) -> None:
        self.logger.log(self.level, f"Starting flow execution: {state.graph_id}")

    def before_node(self, state: FlowState) -> None:
        if state.current_node:
            node_id = state.current_node.id if hasattr(state.current_node, "id") else str(state.current_node)
            self.logger.log(logging.DEBUG, f"Executing node: {node_id}")

    def after_node(self, state: FlowState) -> None:
        if state.current_node:
            node_id = state.current_node.id if hasattr(state.current_node, "id") else str(state.current_node)
            elapsed = state.node_times.get(node_id, 0)
            self.logger.log(logging.DEBUG, f"Completed node: {node_id} ({elapsed:.2f}s)")

    def on_error(self, state: FlowState, exc: Exception) -> None:
        node_id = None
        if state.current_node:
            node_id = state.current_node.id if hasattr(state.current_node, "id") else "unknown"
        self.logger.error(f"Error in node {node_id}: {exc}")

    def after_flow(self, state: FlowState) -> None:
        status = "cancelled" if state.cancelled else ("failed" if state.has_errors else "completed")
        self.logger.log(self.level, f"Flow {status}: {state.graph_id} ({state.total_time:.2f}s)")


class TimingCallback(FlowCallback):
    """
    Callback for timing node execution.

    Records execution time for each node and total flow time.

    Attributes:
        order: 5 (runs very early)

    Example:
        ```python
        timing = TimingCallback()
        executor = FlowExecutor(graph_id="flow", steps=[...], callbacks=[timing])
        await executor.run()

        # Access timing data from state
        print(state.node_times)  # {"step1": 0.5, "step2": 1.2, ...}
        print(state.context["total_execution_time"])
        ```
    """
    order = 5

    def __init__(self):
        self._node_start: float = 0

    def before_flow(self, state: FlowState) -> None:
        state.start_time = time.time()

    def before_node(self, state: FlowState) -> None:
        self._node_start = time.time()

    def after_node(self, state: FlowState) -> None:
        if state.current_node:
            node_id = state.current_node.id if hasattr(state.current_node, "id") else str(state.current_node)
            elapsed = time.time() - self._node_start
            state.node_times[node_id] = elapsed

    def after_flow(self, state: FlowState) -> None:
        total = time.time() - state.start_time
        state.context["total_execution_time"] = total


class RetryCallback(FlowCallback):
    """
    Callback for automatic retry on failure.

    Tracks retry counts per node and raises RetryNodeException if
    retries are available.

    Attributes:
        order: 50 (runs in the middle)
        max_retries: Maximum retry attempts per node
        delay: Delay between retries in seconds
        retry_on: Exception types to retry on (default: all)

    Example:
        ```python
        executor = FlowExecutor(
            graph_id="flow",
            steps=[...],
            callbacks=[RetryCallback(max_retries=3, delay=1.0)]
        )
        ```
    """
    order = 50

    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        retry_on: Optional[tuple[type[Exception], ...]] = None
    ):
        self.max_retries = max_retries
        self.delay = delay
        self.retry_on = retry_on  # None means retry on any exception
        self._retries: dict[str, int] = {}

    def before_flow(self, state: FlowState) -> None:
        self._retries.clear()

    def on_error(self, state: FlowState, exc: Exception) -> None:
        # Check if we should retry this exception type
        if self.retry_on is not None and not isinstance(exc, self.retry_on):
            return

        if not state.current_node:
            return

        node_id = state.current_node.id if hasattr(state.current_node, "id") else str(state.current_node)
        retries = self._retries.get(node_id, 0)

        if retries < self.max_retries:
            self._retries[node_id] = retries + 1
            remaining = self.max_retries - retries - 1
            raise RetryNodeException(max_retries=remaining, delay=self.delay)


class ProgressCallback(FlowCallback):
    """
    Callback for reporting progress percentage.

    Calls a user-provided function with progress updates.

    Attributes:
        order: 90 (runs late)
        on_progress: Callback function(percent: float, node_id: str)

    Example:
        ```python
        def my_progress(percent, node_id):
            print(f"{percent:.0f}% - {node_id}")

        executor = FlowExecutor(
            graph_id="flow",
            steps=[...],
            callbacks=[ProgressCallback(on_progress=my_progress)]
        )
        ```
    """
    order = 90

    def __init__(self, on_progress: Optional[Callable[[float, str], None]] = None):
        self.on_progress = on_progress
        self._total: int = 0
        self._completed: int = 0

    def before_flow(self, state: FlowState) -> None:
        self._total = len(state.nodes)
        self._completed = 0

    def after_node(self, state: FlowState) -> None:
        self._completed += 1
        pct = (self._completed / self._total) * 100 if self._total > 0 else 100

        node_id = ""
        if state.current_node:
            node_id = state.current_node.id if hasattr(state.current_node, "id") else str(state.current_node)

        if self.on_progress:
            self.on_progress(pct, node_id)

        # Also store in context
        state.context["progress_percent"] = pct


class ValidationCallback(FlowCallback):
    """
    Callback for validating nodes before execution.

    Uses the type-dispatched validate() function to check nodes.

    Attributes:
        order: 1 (runs very early, before execution)
        fail_fast: If True, cancel flow on first validation error

    Example:
        ```python
        executor = FlowExecutor(
            graph_id="flow",
            steps=[...],
            callbacks=[ValidationCallback(fail_fast=True)]
        )
        ```
    """
    order = 1

    def __init__(self, fail_fast: bool = True):
        self.fail_fast = fail_fast
        self.validation_errors: list[tuple[str, list[str]]] = []

    def before_flow(self, state: FlowState) -> None:
        self.validation_errors.clear()

        # Try to import validate from types
        try:
            from .types import validate
        except ImportError:
            return

        for node in state.nodes:
            if hasattr(node, "id"):
                errors = validate(node)
                if errors:
                    self.validation_errors.append((node.id, errors))
                    if self.fail_fast:
                        raise CancelFlowException(
                            f"Validation failed for {node.id}: {errors}"
                        )

        # Store all validation errors in context
        if self.validation_errors:
            state.context["validation_errors"] = self.validation_errors

    def before_node(self, state: FlowState) -> None:
        # Re-validate current node in case it was modified
        if not state.current_node or not hasattr(state.current_node, "id"):
            return

        try:
            from .types import validate
            errors = validate(state.current_node)
            if errors and self.fail_fast:
                raise CancelFlowException(
                    f"Validation failed for {state.current_node.id}: {errors}"
                )
        except ImportError:
            pass
