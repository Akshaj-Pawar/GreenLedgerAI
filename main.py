
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



# add display board - display as table - handle none's - surely this is easy

# ask AI for testing

# test supabase retrieval functions
# test 3 bucket archiving component
# test the LLM component

# double check some stuff - emails, SLC response, look over computer systems

# test all scripts individually in their entirety


# replace the type in text with a dropdown select
# add additional filters to task checkbox

# parsing documents from the 3 bucket archive and restricting access
# reviewer ux: ease of changing things, ease of viewing chunks

# failure handling throughout
# convert to langchain or something + prompt engineering
# explore adding async to handler and in general
