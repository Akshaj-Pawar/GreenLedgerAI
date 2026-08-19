from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

import LLM_call

router = APIRouter()

class TaskRequest(BaseModel):
    document_name: str
    file_path: str
    tasks: List[str]

@router.post("/tasks")
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

        # test to see if frontend will work - comment out in deeper tests and production
        results[task] = {"success": True, "results": [{"col_A": 5, "col_B": 7, "col_C": 9}], "error": None}

        # production code - comment out when testing
        results[task] = LLM_call.execute_task(task) # returns eg: {"success": True, "results": response, "error": None}

    return {"status": "success", "results": results}