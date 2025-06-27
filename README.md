# AgentCode

AgentCode is a simple AI-driven code planning and development system.

This project is under active development. Feedback and ideas welcome!

It has two main agents:
- **Planner Agent**: Breaks down tasks into development steps.
- **Developer Agent**: Writes and edits code using AST-based tools.

### Features

- Search and analyze local Python codebases
- Plan tasks step-by-step using LLMs
- Modify source code in-place with safe AST transformations
- Simple web API using FastAPI + Uvicorn

### Getting Started

```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API server
uvicorn api:app --reload
```
