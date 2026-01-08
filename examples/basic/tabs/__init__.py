"""
Tab modules for the Fastflow examples app.

Each tab is implemented as a separate module for better organization.
"""

from .langgraph import langgraph_tab
from .er_diagram import er_diagram_tab
from .data_dag import data_dag_tab
from .ai_model_dag import ai_model_dag_tab
from .agent_flow import agent_flow_tab
from .flowchart import flowchart_tab
from .python_exec import python_exec_tab, python_executor

__all__ = [
    "langgraph_tab",
    "er_diagram_tab",
    "data_dag_tab",
    "ai_model_dag_tab",
    "agent_flow_tab",
    "flowchart_tab",
    "python_exec_tab",
    "python_executor",
]
