"""
Utility to upload remarkable /usr/share/remarkable/templates directory to google cloud
storage and create upstream templates.json file.
"""

import json
import pathlib
import sys
import uuid

from google.cloud import storage


def parse_templates_json(templates_dir):
    with open(templates_dir, "r") as templates_file:
        return json.load(templates_file)


def upload_files(templates_dir):
    templates_json = parse_templates_json(templates_dir / "templates.json")
    client = storage.Client()
    bucket = client.get_bucket("remarkable-templates")

    for template in templates_json["templates"]:
        file_uuid = uuid.uuid4()
        blob = bucket.blob(f"templates/{file_uuid}.png")
        filename = (templates_dir / template["filename"]).with_suffix(".png")
        blob.upload_from_filename(filename=filename)

        json_info = {
            "author": "reMarkable",
            "name": template["name"],
            "url": blob.public_url,
            "landscape": template.get("landscape", False),
            "categories": template["categories"],
        }

        uploads_blob = bucket.blob(f"jsons/{file_uuid}.json")
        uploads_blob.upload_from_string(json.dumps(json_info))

        print(f"uploaded: {file_uuid}")



def main():
    upload_files(templates_dir=pathlib.Path(sys.argv[1]))


if __name__ == "__main__":
    main()
