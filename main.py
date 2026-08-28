
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import parser
import display_backend

import os
from dotenv import load_dotenv
load_dotenv()


# This script is primarily the backend manager for the website as a whole
# It sets up server logic and coordinates async functions that can accept post requests


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
    # redirects user on root to upload form
    return RedirectResponse(url="/static/upload_form.html")