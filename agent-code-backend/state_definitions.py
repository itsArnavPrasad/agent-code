# state_definitions.py
from typing import TypedDict, List, Dict, Any, Optional
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    DEVELOPING = "developing"
    SEARCHING = "searching"
    COMPLETED = "completed"
    ERROR = "error"

class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class PlanStep(TypedDict):
    step_id: int
    description: str
    status: StepStatus
    details: Optional[str]
    search_required: bool
    search_results: Optional[Dict[str, Any]]

class PlannerState(TypedDict):
    task: str
    total_steps: int
    current_step_index: int
    steps: List[PlanStep]
    status: AgentStatus


class DeveloperState(TypedDict):
    code: str  # latest code after agent changes
    logs: List[str]  # logs for what was changed
    current_step_index: int # step from PlannerState
    status: AgentStatus
    files_modified: List[str]


class OverallState(TypedDict):
    planner_state: PlannerState
    developer_state: DeveloperState
    current_agent: str  # "planner" or "developer"