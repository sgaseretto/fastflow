"""
Python-based flow execution with callback system and SSE support.

This module provides the FlowExecutor class that orchestrates node execution
with a two-way callback system inspired by fastai.

Key features:
- Topological ordering via Kahn's algorithm
- Two-way callbacks that can read/modify execution state
- Control flow via exceptions (Cancel, Skip, Retry)
- SSE-based real-time status updates
- Support for typed nodes from types.py

Example:
    ```python
    from fastflow.execution import FlowExecutor, ExecutionStep
    from fastflow.callbacks import SSECallback, LoggingCallback, TimingCallback

    executor = FlowExecutor(
        graph_id="my-pipeline",
        steps=[
            ExecutionStep("load", handler=load_data),
            ExecutionStep("process", depends_on=["load"], handler=process),
            ExecutionStep("save", depends_on=["process"], handler=save),
        ],
        callbacks=[SSECallback(), LoggingCallback(), TimingCallback()]
    )

    @rt("/execute")
    async def execute():
        return EventStream(executor.run(context={"db": db}))
    ```
"""

from dataclasses import dataclass, field
from typing import Optional, Callable, Any, AsyncIterator, Union
import asyncio

from .callbacks import (
    FlowCallback,
    FlowState,
    SSECallback,
    CancelFlowException,
    SkipNodeException,
    RetryNodeException,
)
from .core import raw_node_status, raw_edge_status, raw_complete, raw_error

__all__ = [
    "ExecutionStep",
    "FlowExecutor",
    # Re-export for convenience (backward compat)
    "node_status",
    "edge_status",
    "execution_complete",
    "execution_error",
    "run_sequential",
]

# Type alias for nodes - can be typed FlowNode or simple dict/object
NodeLike = Any


# =============================================================================
# Execution Step
# =============================================================================

@dataclass
class ExecutionStep:
    """
    Represents a single step in the execution pipeline.

    Attributes:
        node_id: Unique identifier for this step
        node: Optional typed FlowNode instance
        depends_on: List of node_ids that must complete before this step
        duration: Simulated duration in seconds (used if no handler)
        handler: Async function to execute for this step

    Handler signature:
        ```python
        async def handler(context: dict, inputs: dict) -> Any:
            # context: Shared state across all steps
            # inputs: Dict mapping dependency node_ids to their results
            return result
        ```

    Example:
        ```python
        async def load_data(context, inputs):
            return await context["db"].fetch_all()

        step = ExecutionStep(
            node_id="load",
            handler=load_data,
            depends_on=[]
        )
        ```
    """
    node_id: str
    node: Optional[NodeLike] = None
    depends_on: list[str] = field(default_factory=list)
    duration: float = 1.0
    handler: Optional[Callable[..., Any]] = None

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


# =============================================================================
# Flow Executor
# =============================================================================

@dataclass
class FlowExecutor:
    """
    Manages flow execution with topological ordering and callbacks.

    The executor handles:
    - Dependency resolution via topological sort
    - Callback lifecycle management
    - Error handling and retry logic
    - SSE message generation

    Attributes:
        graph_id: Identifier for this flow
        steps: List of ExecutionStep instances
        callbacks: List of FlowCallback instances (auto-sorted by order)

    Example:
        ```python
        executor = FlowExecutor(
            graph_id="ml-pipeline",
            steps=[
                ExecutionStep("load", handler=load_data),
                ExecutionStep("train", depends_on=["load"], handler=train, duration=5.0),
                ExecutionStep("eval", depends_on=["train"], handler=evaluate),
            ],
            callbacks=[
                SSECallback(),
                LoggingCallback(),
                TimingCallback(),
                RetryCallback(max_retries=2),
            ]
        )

        @rt("/execute/ml-pipeline")
        async def execute():
            return EventStream(executor.run(context={"model": model}))
        ```
    """
    graph_id: str
    steps: list[ExecutionStep] = field(default_factory=list)
    callbacks: list[FlowCallback] = field(default_factory=list)

    def __post_init__(self):
        # Sort callbacks by order
        self.callbacks = sorted(self.callbacks, key=lambda c: c.order)
        # Ensure SSECallback is present
        if not any(isinstance(c, SSECallback) for c in self.callbacks):
            self.callbacks.append(SSECallback())
            self.callbacks = sorted(self.callbacks, key=lambda c: c.order)

    def _get_sse_callback(self) -> Optional[SSECallback]:
        """Get the SSE callback instance."""
        for cb in self.callbacks:
            if isinstance(cb, SSECallback):
                return cb
        return None

    def _call_callbacks(
        self,
        method: str,
        state: FlowState,
        exc: Optional[Exception] = None
    ) -> None:
        """
        Call a method on all callbacks.

        Handles control flow exceptions (Cancel, Skip, Retry) by re-raising.
        Other callback exceptions are caught and logged but don't stop execution.
        """
        for cb in self.callbacks:
            try:
                fn = getattr(cb, method, None)
                if fn is None:
                    continue
                if exc is not None and method == "on_error":
                    fn(state, exc)
                else:
                    fn(state)
            except (CancelFlowException, SkipNodeException, RetryNodeException):
                raise
            except Exception as e:
                # Log but don't fail on callback errors
                import logging
                logging.getLogger("fastflow").warning(f"Callback {cb.__class__.__name__}.{method} error: {e}")

    def _topological_sort(self) -> list[ExecutionStep]:
        """
        Sort steps in topological order based on dependencies.

        Uses Kahn's algorithm.

        Returns:
            List of steps in execution order

        Raises:
            ValueError: If there's a cycle in dependencies
        """
        # Build dependency graph
        in_degree = {step.node_id: 0 for step in self.steps}
        dependents = {step.node_id: [] for step in self.steps}
        step_map = {step.node_id: step for step in self.steps}

        for step in self.steps:
            for dep in step.depends_on:
                if dep in dependents:
                    dependents[dep].append(step.node_id)
                    in_degree[step.node_id] += 1

        # Kahn's algorithm
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node_id = queue.pop(0)
            result.append(step_map[node_id])

            for dependent in dependents[node_id]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self.steps):
            raise ValueError("Cycle detected in step dependencies")

        return result

    def _get_incoming_edges(self, step: ExecutionStep) -> list[tuple[str, str]]:
        """Get edges leading into this step as (source, target) tuples."""
        return [(dep, step.node_id) for dep in step.depends_on]

    async def run(
        self,
        context: Optional[dict] = None,
        reset_first: bool = True,
        pre_delay: float = 0.3,
        post_delay: float = 0.2,
    ) -> AsyncIterator[str]:
        """
        Execute the flow and yield SSE status updates.

        This is the main entry point for flow execution. It:
        1. Creates a FlowState with all nodes and context
        2. Calls before_flow on all callbacks
        3. Executes each step in topological order
        4. Calls appropriate callbacks at each lifecycle point
        5. Handles errors, retries, and cancellation
        6. Yields SSE messages for browser updates

        Args:
            context: Initial context dictionary shared between steps
            reset_first: Whether to reset all nodes to pending first
            pre_delay: Delay before starting execution
            post_delay: Delay between steps

        Yields:
            SSE messages for node and edge status updates

        Example:
            ```python
            @rt("/execute")
            async def execute():
                return EventStream(executor.run(context={"api_key": key}))
            ```
        """
        # Create FlowState
        nodes = [step.node or _create_node_proxy(step.node_id) for step in self.steps]
        edges = [(dep, step.node_id) for step in self.steps for dep in step.depends_on]

        state = FlowState(
            graph_id=self.graph_id,
            nodes=nodes,
            edges=edges,
            context=context.copy() if context else {},
        )

        sse = self._get_sse_callback()
        sorted_steps = self._topological_sort()

        # === before_flow ===
        try:
            self._call_callbacks("before_flow", state)
        except CancelFlowException as e:
            state.cancelled = True
            state.add_error(e)
            self._call_callbacks("on_cancel", state)
            if sse:
                for msg in sse.get_messages():
                    yield msg
            return

        if sse:
            for msg in sse.get_messages():
                yield msg

        await asyncio.sleep(pre_delay)

        # === Execute each step ===
        try:
            for step in sorted_steps:
                if state.cancelled:
                    break

                # Set current node
                state.current_node = step.node or _create_node_proxy(step.node_id)
                state.skip_current = False

                # === before_edge for each dependency ===
                for source, target in self._get_incoming_edges(step):
                    state.current_edge = (source, target)
                    try:
                        self._call_callbacks("before_edge", state)
                    except SkipNodeException:
                        state.skip_current = True
                        break
                    except CancelFlowException:
                        state.cancelled = True
                        break

                    if sse:
                        for msg in sse.get_messages():
                            yield msg

                if state.cancelled:
                    break
                if state.skip_current:
                    continue

                # === before_node ===
                try:
                    self._call_callbacks("before_node", state)
                except SkipNodeException:
                    state.skip_current = True
                except CancelFlowException:
                    state.cancelled = True

                if sse:
                    for msg in sse.get_messages():
                        yield msg

                if state.cancelled:
                    break
                if state.skip_current:
                    continue

                # === Execute the node ===
                retry_count = 0
                max_retries = 3
                retry_delay = 1.0

                while True:
                    try:
                        result = await self._execute_step(step, state)
                        state.results[step.node_id] = result
                        break  # Success, exit retry loop

                    except SkipNodeException:
                        state.skip_current = True
                        break

                    except CancelFlowException as e:
                        state.cancelled = True
                        state.add_error(e, step.node_id)
                        break

                    except RetryNodeException as e:
                        if retry_count < e.max_retries:
                            retry_count += 1
                            await asyncio.sleep(e.delay)
                            continue
                        else:
                            # Max retries exceeded
                            state.add_error(Exception(f"Max retries exceeded for {step.node_id}"), step.node_id)
                            break

                    except Exception as exc:
                        state.add_error(exc, step.node_id)

                        # Let callbacks handle the error
                        try:
                            self._call_callbacks("on_error", state, exc)
                        except RetryNodeException as e:
                            if retry_count < e.max_retries:
                                retry_count += 1
                                max_retries = e.max_retries
                                retry_delay = e.delay
                                await asyncio.sleep(e.delay)
                                continue
                        except SkipNodeException:
                            state.skip_current = True
                        except CancelFlowException:
                            state.cancelled = True

                        if sse:
                            for msg in sse.get_messages():
                                yield msg
                        break

                if state.cancelled:
                    break

                # === after_node ===
                try:
                    self._call_callbacks("after_node", state)
                except CancelFlowException:
                    state.cancelled = True

                if sse:
                    for msg in sse.get_messages():
                        yield msg

                if state.cancelled:
                    break

                # === after_edge for each dependency ===
                for source, target in self._get_incoming_edges(step):
                    state.current_edge = (source, target)
                    try:
                        self._call_callbacks("after_edge", state)
                    except CancelFlowException:
                        state.cancelled = True
                        break

                    if sse:
                        for msg in sse.get_messages():
                            yield msg

                if state.cancelled:
                    break

                await asyncio.sleep(post_delay)

        except CancelFlowException:
            state.cancelled = True

        # === Cleanup ===
        if state.cancelled:
            self._call_callbacks("on_cancel", state)

        # === after_flow ===
        self._call_callbacks("after_flow", state)

        if sse:
            for msg in sse.get_messages():
                yield msg

    async def _execute_step(self, step: ExecutionStep, state: FlowState) -> Any:
        """Execute a single step."""
        if step.handler:
            # Call custom handler
            dep_results = {dep: state.results.get(dep) for dep in step.depends_on}
            return await step.handler(context=state.context, inputs=dep_results)

        elif step.node:
            # Try to use type-dispatched execute
            try:
                from .types import execute
                dep_results = {dep: state.results.get(dep) for dep in step.depends_on}
                return await execute(step.node, state.context, dep_results)
            except ImportError:
                pass

        # Default: simulate work
        await asyncio.sleep(step.duration)
        return {"status": "completed", "node_id": step.node_id}

    async def run_with_results(
        self,
        context: Optional[dict] = None,
    ) -> AsyncIterator[str]:
        """
        Execute the flow with handlers that pass results between steps.

        This is an alias for run() maintained for backward compatibility.
        """
        async for msg in self.run(context=context):
            yield msg


# =============================================================================
# Helper: Node Proxy
# =============================================================================

class _NodeProxy:
    """Simple proxy object when no typed node is provided."""
    def __init__(self, node_id: str):
        self.id = node_id

    def __repr__(self):
        return f"Node({self.id!r})"


def _create_node_proxy(node_id: str) -> _NodeProxy:
    return _NodeProxy(node_id)


# =============================================================================
# Backward Compatibility Functions
# =============================================================================

def node_status(
    node_id: str,
    status: str,
    graph_id: Optional[str] = None,
    message: Optional[str] = None,
) -> str:
    """
    Create an SSE message for node status update.

    This function is maintained for backward compatibility.
    New code should use callbacks or raw_node_status().

    Args:
        node_id: The ID of the node to update
        status: The new status ('pending', 'running', 'success', 'error', 'warning')
        graph_id: Optional graph ID
        message: Optional message to include

    Returns:
        SSE message string
    """
    kwargs = {}
    if graph_id:
        kwargs["graphId"] = graph_id
    if message:
        kwargs["message"] = message
    return raw_node_status(node_id, status, **kwargs)


def edge_status(
    source_id: str,
    target_id: str,
    status: str,
    animated: bool = False,
    graph_id: Optional[str] = None,
) -> str:
    """
    Create an SSE message for edge status update.

    This function is maintained for backward compatibility.

    Args:
        source_id: Source node ID
        target_id: Target node ID
        status: The new status
        animated: Whether to animate the edge
        graph_id: Optional graph ID

    Returns:
        SSE message string
    """
    kwargs = {"animated": animated}
    if graph_id:
        kwargs["graphId"] = graph_id
    return raw_edge_status(source_id, target_id, status, **kwargs)


def execution_complete(
    message: Optional[str] = None,
    results: Optional[dict] = None,
) -> str:
    """
    Create an SSE message signaling execution completion.

    This function is maintained for backward compatibility.

    Args:
        message: Optional completion message
        results: Optional results dictionary

    Returns:
        SSE message string
    """
    return raw_complete(message, results)


def execution_error(
    message: str,
    node_id: Optional[str] = None,
    details: Optional[dict] = None,
) -> str:
    """
    Create an SSE message for execution error.

    This function is maintained for backward compatibility.

    Args:
        message: Error message
        node_id: Optional node ID where error occurred
        details: Optional error details

    Returns:
        SSE message string
    """
    kwargs = {}
    if node_id:
        kwargs["nodeId"] = node_id
    if details:
        kwargs["details"] = details
    return raw_error(message, **kwargs)


# =============================================================================
# Convenience Function
# =============================================================================

async def run_sequential(
    node_ids: list[str],
    graph_id: Optional[str] = None,
    duration: float = 1.0,
) -> AsyncIterator[str]:
    """
    Run nodes sequentially with status updates.

    Simple helper for linear pipelines without complex dependencies.

    Args:
        node_ids: List of node IDs to execute in order
        graph_id: Optional graph ID
        duration: Duration for each step in seconds

    Yields:
        SSE messages for status updates

    Example:
        ```python
        @rt("/execute/simple")
        async def execute():
            return EventStream(run_sequential(
                ["step1", "step2", "step3"],
                graph_id="my-flow",
                duration=0.5
            ))
        ```
    """
    # Create steps with sequential dependencies
    steps = []
    for i, node_id in enumerate(node_ids):
        depends_on = [node_ids[i - 1]] if i > 0 else []
        steps.append(ExecutionStep(node_id=node_id, depends_on=depends_on, duration=duration))

    executor = FlowExecutor(graph_id=graph_id or "sequential", steps=steps)

    async for msg in executor.run():
        yield msg
