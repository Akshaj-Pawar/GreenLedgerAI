
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



# test parser script in its entirety
# test the LLM component + plumbing

# double check some stuff - emails, SLC response


# failure handling throughout
# convert to langchain or something + prompt engineering
# integrate tests 


# test archiving, implement retrieving from the 3 bucket archive, with restricted access
# add additional filters to task checkbox
# reviewer ux: ease of changing things, ease of viewing chunks

# explore adding async to handler and in general
