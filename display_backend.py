from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

import LLM_call


# This script handles the direct interaction between the tasks.html frontend page and the backend
# Its priamry purpose is to run the LLM execute taks function using all tasks provided by the frontend, and compiling a dictionary with one entry per task
# Each entry is represented as a seperate table on the frontend
# It is responsible for adding a success or failure status to the backend's response, but it is not repsonsible for the format of the response dictionary, which should be flat
# The front end is designed to flexibly work with whatever this script gives it - so it's important that it returns a flat dictionary


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
        # results[task] = {"success": True, "rows": [{"col_A": 5, "col_B": 7, "col_C": 9}], "error": None}

        # production code - comment out when testing
        results[task] = LLM_call.execute_task(task) # returns eg: {"success": True, "results": response, "error": None}

    return {"status": "success", "results": results}