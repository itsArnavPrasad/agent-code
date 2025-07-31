# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langgraph_runner import get_graph
from agents.tools.search_internal import list_files, get_file_content
import os
from typing import Optional

app = FastAPI()

# CORS for frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schemas
class AgentRequest(BaseModel):
    current_code: str
    task: str
    current_file: Optional[str] = None
    codebase_dir: Optional[str] = None

class FolderRequest(BaseModel):
    directory: str

class FileRequest(BaseModel):
    file_path: str

class SaveFileRequest(BaseModel):
    file_path: str
    content: str

@app.post("/run-developer-agent")
async def run_developer_agent(req: AgentRequest):
    try:
        graph = get_graph()

        initial_state = {
            "planner_state": {
                "task": req.task,
                "steps": []
            },
            "developer_state": {
                "code": req.current_code,
                "logs": []
            },
            "current_file": req.current_file,
            "codebase_dir": req.codebase_dir or "."
        }

        print("Initial state:", initial_state)  # Debug log
        final_state = graph.invoke(initial_state)
        print("Final state:", final_state)  # Debug log
        
        # Ensure logs exist and are a list
        logs = final_state["developer_state"].get("logs", [])
        if not isinstance(logs, list):
            logs = [str(logs)] if logs else ["Task completed"]
        
        new_code = final_state["developer_state"].get("code", req.current_code)
        
        return {
            "new_code": new_code,
            "logs": logs
        }
    except Exception as e:
        print(f"Error in agent execution: {e}")  # Debug log
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-folder-structure")
async def get_folder_structure(req: FolderRequest):
    """Get the folder structure for the file explorer"""
    try:
        if not os.path.exists(req.directory):
            raise HTTPException(status_code=404, detail="Directory not found")
        
        structure = list_files(req.directory, max_depth=3)
        return {"structure": structure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-file-content")  
async def get_file_content_endpoint(req: FileRequest):
    """Get the content of a specific file"""
    try:
        if not os.path.exists(req.file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        content = get_file_content(req.file_path)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-file")
async def save_file(req: SaveFileRequest):
    """Save content to a specific file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(req.file_path), exist_ok=True)
        
        with open(req.file_path, 'w', encoding='utf-8') as f:
            f.write(req.content)
        
        return {"message": f"File saved successfully: {req.file_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))