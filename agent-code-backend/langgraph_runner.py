from langgraph.graph import StateGraph
from agents.developerAgent import developerNode
from agents.plannerAgent import plannerNode

# this is the state class that will be used in the graph
class AppState(dict):
    task: str
    steps: list = []
    code: list = []
    pass

# Building the graph
workflow = StateGraph(AppState)

workflow.add_node("planner", plannerNode)
workflow.add_node("developer", developerNode)
workflow.set_entry_point("planner")
workflow.add_edge("planner", "developer")
workflow.set_finish_point("developer")

graph = workflow.compile()

# Runing a test
if __name__ == "__main__":
    initial_state = {"task": "Write a sort function"}
    final_state = graph.invoke(initial_state)
    print("Final state:", final_state)
