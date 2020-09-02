import json
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
from google.oauth2 import service_account

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://0.0.0.0:8000", "https://gittattoo.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


credentials = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))

credentials["private_key"] = credentials["private_key"].replace("\\n", "\n")

bucket = storage.Client(
    project="Remarkable Templates",
    credentials=service_account.Credentials.from_service_account_info(credentials),
).get_bucket("remarkable-templates")


@app.get("/files")
def files():
    for blob in bucket.list_blobs(prefix="jsons"):
        print("blob", f)

    return {}
