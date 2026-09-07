from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from supabase import create_client

import os
from dotenv import load_dotenv

import LLM_call
import user_verifier
import data_handlers

load_dotenv()
user_recent_results_cache: dict[str, dict] = {} # more robust cache needed long term

# This script handles the direct interaction between the tasks.html frontend page and the backend
# Its priamry purpose is to run the LLM execute taks function using all tasks provided by the frontend, and compiling a dictionary with one entry per task
# Each entry is represented as a seperate table on the frontend
# It is responsible for adding a success or failure status to the backend's response, but it is not repsonsible for the format of the response dictionary, which should be flat
# The front end is designed to flexibly work with whatever this script gives it - so it's important that it returns a flat dictionary

router = APIRouter()

class TaskRequest(BaseModel):
    #document_name: str
    #file_path: str
    tasks: List[str]

@router.get("/tasks")
async def list_documents(user_id: str = Depends(user_verifier.get_current_user)):

    sb_url = os.getenv("SUPABASE_URL")
    sb_key = os.getenv("SUPABASE_ADMIN_KEY")

    db_connection = create_client(
        sb_url,
        sb_key
    )

    response = data_handlers.get_documents_for_user(db_connection, user_id)
    return response



def sql_quote(val):
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    # Escape single quotes by doubling them -- standard SQL string escaping
    escaped = str(val).replace("'", "''")
    return f"'{escaped}'"

def results_to_sql(results: dict) -> str:
    statements = []
    for task_name, task_result in results.items():
        if not task_result.get("success") or not task_result.get("rows"):
            continue
        table_name = task_name.replace(" ", "_")
        for row in task_result["rows"]:
            columns = ", ".join(row.keys())
            values = ", ".join(sql_quote(v) for v in row.values())
            statements.append(f"INSERT INTO {table_name} ({columns}) VALUES ({values});")
    return "\n".join(statements)

@router.get("/results/sql")
async def get_results_sql(user_id: str = Depends(user_verifier.get_current_user)):
    results = user_recent_results_cache.get(user_id)
    if results is None:
        results = {}

    sql_text = results_to_sql(results)
    return Response(
        content=sql_text,
        media_type="application/sql",
        headers={"Content-Disposition": "attachment; filename=results.sql"}
    )

@router.get("/results/recent")
async def get_recent_results(user_id: str = Depends(user_verifier.get_current_user)):
    results = user_recent_results_cache.get(user_id)
    if results is None:
        results = {}
    return {"status": "success", "results": results}



@router.post("/tasks")
async def run_tasks(payload: TaskRequest, user_id: str = Depends(user_verifier.get_current_user)):
    print(payload)
    # payload.document_name, payload.file_path, payload.tasks are now
    # validated and typed -- FastAPI parses the JSON body against
    # TaskRequest automatically, and rejects the request with a 422
    # if the shape doesn't match (e.g. tasks isn't a list of strings).

    results = user_recent_results_cache.get(user_id)
    if results is None:
        results = {}

    for task in payload.tasks:
        # placeholder -- this is where you'd dispatch to whatever
        # function actually performs each task against payload.file_path

        # test to see if frontend will work - comment out in deeper tests and production
        # results[task] = {"success": True, "rows": [{"col_A": 5, "col_B": 7, "col_C": 9}], "error": None}

        # production code - comment out when testing
        results[task] = LLM_call.execute_task(task, user_id, model_family="openai") # returns eg: {"success": True, "results": response, "error": None}
        user_recent_results_cache[user_id] = results

    return {"status": "success", "results": results}