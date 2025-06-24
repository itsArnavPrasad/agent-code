# langgraph_runner.py
from langgraph.graph import StateGraph
from agents.developerAgent import developerNode
from agents.plannerAgent import plannerNode
from typing import TypedDict, List, Dict, Any

# Defining states for agents
class PlannerState(TypedDict):
    task: str
    steps: List[str]

class DeveloperState(TypedDict):
    code: str            # latest code after agent changes
    logs: List[str]      # optional logs for what was changed

class OverallState(TypedDict):
    planner_state: PlannerState
    developer_state: DeveloperState

# Building the graph
def get_graph():
    workflow = StateGraph(OverallState)
    workflow.add_node("planner", plannerNode)
    workflow.add_node("developer", developerNode)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "developer")
    workflow.set_finish_point("developer")
    return workflow.compile()