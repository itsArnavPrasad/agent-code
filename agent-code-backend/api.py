# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langgraph_runner import get_graph

app = FastAPI()

# CORS for frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schema for request
class AgentRequest(BaseModel):
    current_code: str
    task: str

# TypedDict-based state
class OverallState(dict):
    def __init__(self, planner_state=None, developer_state=None):
        super().__init__()
        self["planner_state"] = planner_state or {}
        self["developer_state"] = developer_state or {}

@app.post("/run-developer-agent")
async def run_developer_agent(req: AgentRequest):
    graph = get_graph()

    initial_state = {
        "planner_state": {
            "task": req.task,
            "steps": []
        },
        "developer_state": {
            "code": [req.current_code],
            "logs": []
        }
    }

    final_state = graph.invoke(initial_state)

    return {
        "new_code": final_state["developer_state"]["code"],
        "logs": final_state["developer_state"]["logs"]
    }