# developerAgent.py
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load model
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def developerNode(state):
    print("\nDeveloper agent running...")

    steps = state["planner_state"].get("steps", [])
    current_code = state["developer_state"].get("code", "")

    if not steps or not current_code:
        raise ValueError("Developer node requires both code and planner steps.")

    # Create prompt for Gemini
    prompt = f"""You are an AI code editor.

Your job is to modify the following Python code based on the development instructions provided.

### Original Code:
{current_code}

### Instructions:
{"; ".join(steps)}

Please return ONLY the final, modified Python code, without extra explanation or formatting.
"""

    print("Sending prompt to Gemini...")
    response = model.generate_content(prompt)
    edited_code = response.text.strip()
    if edited_code.startswith("```python"):
        edited_code = edited_code[len("```python"):].strip()
    if edited_code.endswith("```"):
        edited_code = edited_code[:-3].strip()

    # Update developer state
    state["developer_state"]["code"] = edited_code
    state["developer_state"]["logs"] = steps

    print("Developer Agent - Edited Code:")
    print(edited_code)

    return state
