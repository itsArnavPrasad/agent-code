# agents/developerAgent.py
from dotenv import load_dotenv
import os
import google.generativeai as genai
from agents.tools.search_internal import search_internal, SearchMode, get_file_content, analyze_file_structure
from agents.tools.write_utils import add_code, replace_code, delete_code, WriteUtilsError

# Load model
load_dotenv()  
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def developerNode(state):
    print("\nDeveloper agent running...")
    print("Input state:", state)  # Debug log

    steps = state["planner_state"].get("steps", [])
    current_code = state["developer_state"].get("code", "")
    current_file = state.get("current_file", "")  # File being edited
    codebase_dir = state.get("codebase_dir", ".")
    
    # Ensure current_code is a string
    if isinstance(current_code, list):
        current_code = "\n".join(current_code)

    if not steps:
        print("Warning: No steps provided by planner")
        # Return state with basic logs
        state["developer_state"]["logs"] = ["No steps provided by planner"]
        return state

    # Initialize logs list
    logs = ["Starting development task..."]
    
    # If we have a specific file being worked on, get its full content
    file_context = ""
    if current_file and os.path.exists(current_file):
        file_context = f"\nCURRENT FILE CONTENT ({current_file}):\n"
        file_context += get_file_content(current_file)
        logs.append(f"Analyzing file: {current_file}")
    
    # Search for relevant code patterns based on the steps
    relevant_code = ""
    for step in steps:
        if any(keyword in step.lower() for keyword in ['function', 'method', 'def']):
            # Look for existing functions that might be relevant
            search_results = search_internal(codebase_dir, "def", SearchMode.CONTAINS, max_results=5, include_context=True)
            if "Found" in search_results:
                relevant_code += f"\nRelevant functions for step '{step[:50]}...':\n{search_results}\n"
    
    # Create prompt for Gemini
    prompt = f"""You are an AI code developer. 

Your job is to implement the development steps provided by analyzing the current code and making precise modifications.

### Current Code:
{current_code}

{file_context}

{relevant_code}

### Development Steps to Implement:
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(steps)])}

### Instructions:
1. If working with a specific file, make targeted changes to that file
2. Follow best practices for the programming language
3. Keep existing code structure and style
4. Add proper comments for new functionality

Please return ONLY the final, modified code that implements ALL the steps.
Do NOT include explanations, markdown formatting, or unit tests.
"""

    print("Sending prompt to Gemini...")
    response = model.generate_content(prompt)
    edited_code = response.text.strip()
    
    # Clean up code formatting
    if edited_code.startswith("```python"):
        edited_code = edited_code[len("```python"):].strip()
    if edited_code.startswith("```"):
        edited_code = edited_code[3:].strip()
    if edited_code.endswith("```"):
        edited_code = edited_code[:-3].strip()

    # If we have a specific file, try to write changes back to it
    if current_file and os.path.exists(current_file):
        try:
            # For now, replace the entire file content
            # In a more sophisticated version, we could detect specific changes
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(edited_code)
            logs.append(f"Updated file: {current_file}")
        except Exception as e:
            logs.append(f"Error writing to file {current_file}: {str(e)}")

    # Update developer state with guaranteed logs
    final_logs = logs + [f"Implemented: {step}" for step in steps]
    state["developer_state"]["code"] = edited_code
    state["developer_state"]["logs"] = final_logs

    print("Developer Agent - Final logs:", final_logs)  # Debug log
    print("Developer Agent - Edited Code:")
    print(edited_code[:500] + "..." if len(edited_code) > 500 else edited_code)

    return state