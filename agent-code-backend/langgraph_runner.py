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
    code: List[str]

class OverallState(TypedDict):
    planner_state: PlannerState
    developer_state: DeveloperState

# Building the graph
workflow = StateGraph(OverallState)

workflow.add_node("planner", plannerNode)
workflow.add_node("developer", developerNode)
workflow.set_entry_point("planner")
workflow.add_edge("planner", "developer")
workflow.set_finish_point("developer")

graph = workflow.compile()

# Runing a test
if __name__ == "__main__":
    initial_state = {
        "planner_state": {"task": "make a bubble sort function to sort a array", "steps": []},
        "developer_state": {"code": []}
    }
    final_state = graph.invoke(initial_state)
    print("Final state:", final_state)
