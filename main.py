
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


# Week One

# fix the flattening problem
# retest

# send demo
# add a claude version
# users as primary key in initial cache


# table should show chunks when asked to
# back button and switch from automatic redirect to button revelation
# final archive phase and reset afterwards - send the user some sql files, clean the users cache (possibly)

# integrate tests - delegate
# test on different models and come to final test idea - delegate


# Week 2+3

# reviewer ux: view row, override row
# test archiving, implement retrieving from the 3 bucket archive, with restricted access
# seperate page for accessing archived documents

# find an even better form of chunking, don't send out the whole thing at once, may require intelligent merging
# add and test vectorisation layer
# human review chunking?

# new functionality to task:
# scope 1 / 2 / 3
# product intelligence + lifecycle intelligence
# IOT ingestion and processing


# Later / idc
# what if scenario modelling: supplier changes
# add evidence graph (whatever tf this is)


# continuous monitoring and real time ingestion (good idea?)

# explore adding async to handler and in general
# best practices for human in the loop
# apply any new skills you learn