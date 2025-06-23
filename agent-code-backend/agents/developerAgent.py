# developerAgent.py
from dotenv import load_dotenv
import os
import google.generativeai as genai

def developerNode(state):
    print("\n Developer agent running...")
    steps = state["planner_state"]["steps"]
    mock_code_edits = []

    for step in steps:
        mock_code_edits.append(f"# [AUTOEDIT] Implementing: {step}\n")

    # Combine them into a string and store in code
    state["developer_state"]["code"] = mock_code_edits
    print("State after Developer Agent:")
    print(state["developer_state"])
    return state