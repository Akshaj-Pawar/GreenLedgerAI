
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



# test the LLM component + plumbing


# 1: Model quality improvement
# convert to langchain or something + prompt engineering
# integrate tests 
# test on different models and come to final test idea


# 2: Usability
# failure handling throughout
# reviewer ux: view row, override row
# test archiving, implement retrieving from the 3 bucket archive, with restricted access
# add evidence graph


# 3: add and test chunking and vectorisation layer
# human review chunking?


# 4: new functionality to task:
# scope 1 / 2 / 3
# product intelligence + lifecycle intelligence
# IOT ingestion and processing


# new tasks:
# what if scenario modelling: supplier changes
# continuous monitoring and real time ingestion (good idea?)

# explore adding async to handler and in general
# best practices for human in the loop
# apply any new skills you learn