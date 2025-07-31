# agents/plannerAgent.py
from dotenv import load_dotenv
import os
import google.generativeai as genai
from agents.tools.search_internal import search_internal, SearchMode, list_files, analyze_file_structure
from agents.tools.search_external import search_external

# Load .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

def plannerNode(state):
    print("\n Planner agent running...")
    task = state["planner_state"]["task"]
    codebase_dir = state.get("codebase_dir", ".")  # Get codebase directory from state
    
    if not task:
        raise ValueError("Task is required in the state.")
    
    # First, analyze the codebase structure if directory is provided
    codebase_analysis = ""
    if codebase_dir and codebase_dir != ".":
        print(f"Analyzing codebase in: {codebase_dir}")
        
        # Get file listing
        file_list = list_files(codebase_dir, max_depth=3)
        
        # Search for relevant patterns based on the task
        search_results = ""
        if any(keyword in task.lower() for keyword in ['function', 'method', 'def']):
            search_results += "\nRelevant functions found:\n"
            search_results += search_internal(codebase_dir, "def", SearchMode.CONTAINS, max_results=10)
        
        if any(keyword in task.lower() for keyword in ['class', 'object']):
            search_results += "\nRelevant classes found:\n" 
            search_results += search_internal(codebase_dir, "class", SearchMode.CONTAINS, max_results=10)
        
        codebase_analysis = f"""
CODEBASE ANALYSIS:
{file_list}

{search_results if search_results else ""}
"""
    
    # Check if external search might be helpful
    external_info = ""
    if any(keyword in task.lower() for keyword in ['how to', 'implement', 'create', 'build']):
        print("Searching for external information...")
        search_query = task[:50]  # Limit search query length
        external_info = f"\nEXTERNAL RESOURCES:\n{search_external(search_query, max_results=3)}"
    
    prompt = f"""You are a planning assistant for software development.
    Break down the following software task into 2-4 clear, actionable development steps.
    
    Current Code:
    {state["developer_state"].get("code", "")}
    
    {codebase_analysis}
    
    {external_info}
    
    Task: "{task}"
    
    Based on the codebase analysis and task, provide steps that are:
    1. Specific and actionable
    2. Consider existing code structure
    3. Reference specific files when needed
    
    IMPORTANT: Format your response EXACTLY like this:
    Step 1: [specific action]
    Step 2: [specific action]  
    Step 3: [specific action]
    
    Do not include any other text or explanations, just the steps.
    """

    response = model.generate_content(prompt)
    text = response.text.strip()
    steps = [line.strip("- ").strip() for line in text.split("\n") if line.strip().startswith("Step")]
    
    state["planner_state"]["steps"] = steps
    print("Planner State after Planning:")
    print(state["planner_state"])
    return state