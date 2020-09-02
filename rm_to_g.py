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

    uploads = []

    for template in templates_json["templates"]:
        blob = bucket.blob(f"templates/{uuid.uuid4()}.png")
        filename = (templates_dir / template["filename"]).with_suffix(".png")
        blob.upload_from_filename(filename=filename)
        print(blob.public_url)
        print("uploaded:", filename)

        uploads.append(
            {
                "name": template["name"],
                "url": blob.public_url,
                "landscape": template.get("landscape", False),
                "categories": template["categories"],
            }
        )

    uploads_json = templates_dir / "templates-gapi.json"
    with open(uploads_json, "w") as out:
        json.dump(uploads, out)

    uploads_blob = bucket.blob("templates.json")
    uploads_blob.upload_from_filename(filename=uploads_json)

    print(uploads_blob.public_url)


def main():
    upload_files(templates_dir=pathlib.Path(sys.argv[1]))


if __name__ == "__main__":
    main()
