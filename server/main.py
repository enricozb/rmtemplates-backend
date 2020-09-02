from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://0.0.0.0:8000", "https://gittattoo.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

bucket = storage.Client().get_bucket("remarkable-templates")


@app.get("/files")
def files():
    for f in bucket.list_blobs(prefix="templates"):
        print('blob', f)

    return {}
