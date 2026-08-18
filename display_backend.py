from pydantic import BaseModel
from typing import List


class TaskRequest(BaseModel):
    document_name: str
    file_path: str
    tasks: List[str]

@app.post("/tasks")
async def run_tasks(payload: TaskRequest):
    print(payload)
    # payload.document_name, payload.file_path, payload.tasks are now
    # validated and typed -- FastAPI parses the JSON body against
    # TaskRequest automatically, and rejects the request with a 422
    # if the shape doesn't match (e.g. tasks isn't a list of strings).

    results = {}
    for task in payload.tasks:
        # placeholder -- this is where you'd dispatch to whatever
        # function actually performs each task against payload.file_path
        results[task] = f"pretend result for {task}"

    return {"status": "success", "results": results}

# need to replace pretend result with actual result by calling LLM