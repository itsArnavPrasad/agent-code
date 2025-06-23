from dotenv import load_dotenv
import os
import google.generativeai as genai

def developerNode(state):
    print("💻 Developer agent running...")

    steps = state.get("steps", [])
    mock_code_edits = []

    for step in steps:
        mock_code_edits.append(f"# [AUTOEDIT] Implementing: {step}\n")

    # Combine them into a string and store in code
    state["code"] = "\n".join(mock_code_edits)
    print("State after Developer Agent:")
    print(state)
    return state