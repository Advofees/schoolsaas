from dotenv import load_dotenv

load_dotenv()

import os
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(docs_url="/")

origins = [os.environ["FRONTEND_URL"]]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Authentication-Type"],
)


@app.get("/health")
def health():

    return {"version": os.environ.get("GIT_COMMIT_SHA")}
