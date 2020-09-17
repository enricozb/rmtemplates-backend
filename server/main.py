import json
import os
import uuid

from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.cloud import storage
from google.oauth2 import service_account
from PIL import Image
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://0.0.0.0:8000", "https://ezb.io/remarkable-templates/"],
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
async def files():
    return [blob.public_url for blob in bucket.list_blobs(prefix="jsons/")]


def parse_file(img_file):
    chunks = []
    while chunk := img_file.read():
        chunks.append(chunk)

    img_file.seek(0)
    pil_image = Image.open(img_file)

    if pil_image.format != "PNG":
        raise ValueError("Image format must be PNG")
    elif pil_image.size != (1404, 1872):
        raise ValueError(
            "Image dimensions must be 1404x1872. " "Landscape images are not rotated"
        )

    return b"".join(chunks)


@app.post("/upload")
async def upload(
    filedata: UploadFile = Form(...),
    author: str = Form(...),
    name: str = Form(...),
    categories: str = Form(...),
    landscape: bool = Form(...),
):
    try:
        file_data = parse_file(filedata.file)

        file_uuid = uuid.uuid4()
        blob = bucket.blob(f"templates/{file_uuid}.png")
        blob.upload_from_string(file_data)

        json_info = {
            "author": author,
            "name": name,
            "url": blob.public_url,
            "categories": categories,
            "landscape": landscape,
        }

        json_blob = bucket.blob(f"jsons/{file_uuid}.json")
        json_blob.upload_from_string(json.dumps(json_info))

    except Exception as e:
        return JSONResponse(status_code=422, content={"error": str(e)})

    return {}
