"""
Python-based flow execution with SSE (Server-Sent Events) support.

This module enables visual execution simulation driven entirely from Python,
using FastHTML's SSE capabilities to push real-time status updates to the browser.

Example usage:
    ```python
    from fasthtml.common import *
    from fastflow import FlowEditor, Node, Edge, fastflow_headers
    from fastflow.execution import FlowExecutor, node_status, edge_status, execution_complete

    app, rt = fast_app(hdrs=fastflow_headers())

    # Define your pipeline
    pipeline = [
        {"id": "load_data", "depends_on": []},
        {"id": "process", "depends_on": ["load_data"]},
        {"id": "save", "depends_on": ["process"]},
    ]

    @rt("/execute/{flow_id}")
    async def execute(flow_id: str):
        async def run():
            for step in pipeline:
                yield node_status(step["id"], "running")
                await asyncio.sleep(1)  # Simulate work
                yield node_status(step["id"], "success")
            yield execution_complete()
        return EventStream(run())
    ```
"""

from fasthtml.common import sse_message
from dataclasses import dataclass, field
from typing import Optional, Callable, Any, AsyncIterator, Literal
import json
import asyncio

# Status types
NodeStatus = Literal["pending", "running", "success", "error", "warning"]
EdgeStatus = Literal["pending", "running", "success", "error"]


def node_status(
    node_id: str,
    status: NodeStatus,
    graph_id: Optional[str] = None,
    message: Optional[str] = None,
) -> str:
    """
    Create an SSE message for node status update.

    Args:
        node_id: The ID of the node to update
        status: The new status ('pending', 'running', 'success', 'error', 'warning')
        graph_id: Optional graph ID (uses default if not specified)
        message: Optional message to include

    Returns:
        SSE message string to yield from an async generator

    Example:
        ```python
        async def run_pipeline():
            yield node_status("load_data", "running")
            await asyncio.sleep(1)
            yield node_status("load_data", "success")
        ```
    """
    data = {
        "nodeId": node_id,
        "status": status,
    }
    if graph_id:
        data["graphId"] = graph_id
    if message:
        data["message"] = message

    return sse_message(json.dumps(data), event="nodeStatus")


def edge_status(
    source_id: str,
    target_id: str,
    status: EdgeStatus,
    animated: bool = False,
    graph_id: Optional[str] = None,
) -> str:
    """
    Create an SSE message for edge status update.

    Args:
        source_id: Source node ID
        target_id: Target node ID
        status: The new status ('pending', 'running', 'success', 'error')
        animated: Whether to animate the edge (typically for 'running')
        graph_id: Optional graph ID

    Returns:
        SSE message string to yield from an async generator

    Example:
        ```python
        async def run_pipeline():
            yield edge_status("load_data", "process", "running", animated=True)
            await asyncio.sleep(0.5)
            yield edge_status("load_data", "process", "success")
        ```
    """
    data = {
        "sourceId": source_id,
        "targetId": target_id,
        "status": status,
        "animated": animated,
    }
    if graph_id:
        data["graphId"] = graph_id

    return sse_message(json.dumps(data), event="edgeStatus")


def execution_complete(
    message: Optional[str] = None,
    results: Optional[dict] = None,
) -> str:
    """
    Create an SSE message signaling execution completion.

    Args:
        message: Optional completion message
        results: Optional results dictionary

    Returns:
        SSE message string to yield from an async generator

    Example:
        ```python
        async def run_pipeline():
            # ... execute nodes ...
            yield execution_complete(message="Pipeline completed successfully!")
        ```
    """
    data = {"completed": True}
    if message:
        data["message"] = message
    if results:
        data["results"] = results

    return sse_message(json.dumps(data), event="complete")


def execution_error(
    message: str,
    node_id: Optional[str] = None,
    details: Optional[dict] = None,
) -> str:
    """
    Create an SSE message for execution error.

    Args:
        message: Error message
        node_id: Optional node ID where error occurred
        details: Optional error details

    Returns:
        SSE message string to yield from an async generator
    """
    data = {"error": True, "message": message}
    if node_id:
        data["nodeId"] = node_id
    if details:
        data["details"] = details

    return sse_message(json.dumps(data), event="error")


@dataclass
class ExecutionStep:
    """Represents a single step in the execution pipeline."""
    node_id: str
    depends_on: list[str] = field(default_factory=list)
    duration: float = 1.0  # Simulated duration in seconds
    handler: Optional[Callable[..., Any]] = None  # Optional async handler

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class FlowExecutor:
    """
    Manages flow execution with topological ordering and SSE updates.

    Example:
        ```python
        from fastflow.execution import FlowExecutor, ExecutionStep

        executor = FlowExecutor(
            graph_id="ml-pipeline",
            steps=[
                ExecutionStep("load_data"),
                ExecutionStep("preprocess", depends_on=["load_data"]),
                ExecutionStep("train", depends_on=["preprocess"], duration=2.0),
                ExecutionStep("evaluate", depends_on=["train"]),
            ]
        )

        @rt("/execute/ml-pipeline")
        async def execute():
            return EventStream(executor.run())
        ```
    """
    graph_id: str
    steps: list[ExecutionStep] = field(default_factory=list)

    def _topological_sort(self) -> list[ExecutionStep]:
        """Sort steps in topological order based on dependencies."""
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
        """Get edges leading into this step."""
        return [(dep, step.node_id) for dep in step.depends_on]

    async def run(
        self,
        reset_first: bool = True,
        pre_delay: float = 0.3,
        post_delay: float = 0.2,
    ) -> AsyncIterator[str]:
        """
        Execute the flow and yield SSE status updates.

        Args:
            reset_first: Whether to reset all nodes to pending first
            pre_delay: Delay before starting execution
            post_delay: Delay between steps

        Yields:
            SSE messages for node and edge status updates
        """
        sorted_steps = self._topological_sort()

        # Reset all nodes to pending
        if reset_first:
            for step in self.steps:
                yield node_status(step.node_id, "pending", self.graph_id)
            await asyncio.sleep(pre_delay)

        # Execute each step
        for step in sorted_steps:
            # Mark incoming edges as running
            for source, target in self._get_incoming_edges(step):
                yield edge_status(source, target, "running", animated=True, graph_id=self.graph_id)

            # Mark node as running
            yield node_status(step.node_id, "running", self.graph_id)

            # Execute handler or simulate work
            try:
                if step.handler:
                    await step.handler()
                else:
                    await asyncio.sleep(step.duration)

                # Mark node as success
                yield node_status(step.node_id, "success", self.graph_id)

                # Mark incoming edges as success
                for source, target in self._get_incoming_edges(step):
                    yield edge_status(source, target, "success", graph_id=self.graph_id)

            except Exception as e:
                # Mark node as error
                yield node_status(step.node_id, "error", self.graph_id, message=str(e))
                yield execution_error(str(e), step.node_id)
                return

            await asyncio.sleep(post_delay)

        # Signal completion
        yield execution_complete(message="Execution completed successfully")

    async def run_with_results(
        self,
        context: Optional[dict] = None,
    ) -> AsyncIterator[str]:
        """
        Execute the flow with handlers that can pass results between steps.

        Args:
            context: Initial context dictionary shared between steps

        Yields:
            SSE messages for status updates
        """
        if context is None:
            context = {}

        sorted_steps = self._topological_sort()
        results = {}

        for step in self.steps:
            yield node_status(step.node_id, "pending", self.graph_id)

        await asyncio.sleep(0.3)

        for step in sorted_steps:
            for source, target in self._get_incoming_edges(step):
                yield edge_status(source, target, "running", animated=True, graph_id=self.graph_id)

            yield node_status(step.node_id, "running", self.graph_id)

            try:
                if step.handler:
                    # Pass context and results from dependencies
                    dep_results = {dep: results.get(dep) for dep in step.depends_on}
                    result = await step.handler(context=context, inputs=dep_results)
                    results[step.node_id] = result
                else:
                    await asyncio.sleep(step.duration)
                    results[step.node_id] = {"status": "completed"}

                yield node_status(step.node_id, "success", self.graph_id)

                for source, target in self._get_incoming_edges(step):
                    yield edge_status(source, target, "success", graph_id=self.graph_id)

            except Exception as e:
                yield node_status(step.node_id, "error", self.graph_id, message=str(e))
                yield execution_error(str(e), step.node_id, details={"step": step.node_id})
                return

            await asyncio.sleep(0.2)

        yield execution_complete(
            message="Execution completed successfully",
            results=results,
        )


# Convenience function for simple sequential execution
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
    # Reset all
    for node_id in node_ids:
        yield node_status(node_id, "pending", graph_id)

    await asyncio.sleep(0.3)

    prev_node = None
    for node_id in node_ids:
        # Animate edge from previous node
        if prev_node:
            yield edge_status(prev_node, node_id, "running", animated=True, graph_id=graph_id)

        yield node_status(node_id, "running", graph_id)
        await asyncio.sleep(duration)
        yield node_status(node_id, "success", graph_id)

        if prev_node:
            yield edge_status(prev_node, node_id, "success", graph_id=graph_id)

        prev_node = node_id
        await asyncio.sleep(0.2)

    yield execution_complete()
