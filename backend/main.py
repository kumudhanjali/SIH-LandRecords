from fastapi import FastAPI, UploadFile, File
from pipeline.process_document import process_document
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "Land Record Backend is running"
    }


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    # -----------------------------
    # File type validation
    # -----------------------------

    allowed_types = {
        "image/jpeg",
        "image/png"
    }

    if file.content_type not in allowed_types:
        return {
            "error": "Unsupported file type"
        }

    # -----------------------------
    # Save uploaded file
    # -----------------------------

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # -----------------------------
    # Process document
    # -----------------------------

    result = process_document(
        file_path,
        PROCESSED_DIR
    )

    # -----------------------------
    # Return result
    # -----------------------------

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "File uploaded and processed successfully",
        "processing": result
    }