# agents/plannerAgent.py
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

def plannerNode(state):
    print("\n Planner agent running...")
    task = state["planner_state"]["task"]
    if not task:
        raise ValueError("Task is required in the state.")
    
    prompt = f"""You are a planning assistant.
    Break down the following software task into 2-3 clear, actionable development steps, which can be clearly understandable by a developer agent.:
    
    Current Code:
    {state["developer_state"].get("code", "")}
    
    Task: "{task}"

    Format:
    - Step 1: ...
    - Step 2: ...
    - Step 3: ...
    """

    response = model.generate_content(prompt)
    text = response.text.strip()
    steps = [line.strip("- ").strip() for line in text.split("\n") if "Step" in line]
    
    state["planner_state"]["steps"] = steps
    print("Planner State after Planning:")
    print(state["planner_state"])
    return state