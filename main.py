
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import parser
import display_backend

import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    #allow_origins=os.getenv("CORS_ALLOWED_ORIGIN"),
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(parser.router)
app.include_router(display_backend.router)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/upload_form.html")



# add display board - display as table
# link execute_task to display_backend
# let frontend trigger the correct function via a string to function dictionary
# Test

# registration for next year


# ask AI for testing

# test supabase retrieval functions
# test 3 bucket archiving component

# test the LLM component
# convert to langchain or response API

# test all scripts individually in their entirety



# failure handling throughout
# convert to langchain or something
# parsing documents form the 3 bucket archive