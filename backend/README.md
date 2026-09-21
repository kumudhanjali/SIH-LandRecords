# SIH Land Record Digitization — Backend Handover

## What I Built

This backend currently implements the document upload, preprocessing, and basic classification stage of the Land Record Digitization project.

Current flow:

Image Upload
↓
File Type Validation
↓
Quality Check
↓
Denoising
↓
Deskewing
↓
Document Classification
↓
Language Detection
↓
HANDOFF TO OCR


## 1. Technology Used

- Python
- FastAPI
- Uvicorn
- OpenCV
- Python Multipart


## 2. What Has Been Implemented

### FastAPI Backend

File:

    main.py

Implemented endpoints:

    GET /
    POST /upload

The `/upload` endpoint accepts a document image and sends it through the current processing pipeline.


### Image Upload

Currently supported formats:

    JPEG
    PNG

Original uploaded files are stored in:

    uploads/

Example:

    uploads/
        document.jpg

The original uploaded image is kept unchanged.


### Quality Check

File:

    pipeline/preprocessing/quality_check.py

The quality-check module checks:

- Image resolution
- Blur
- Brightness

It returns:

- Quality status
- Width
- Height
- Blur score
- Brightness
- Detected issues


### Denoising

File:

    pipeline/preprocessing/denoise.py

OpenCV denoising is used to reduce noise from the document image.

Input:

    Original uploaded image

Output:

    processed/<filename>_denoised.jpg


### Deskewing

File:

    pipeline/preprocessing/deskew.py

The deskew module corrects document orientation and perspective before the document is passed to later stages such as OCR.

Output:

    processed/<filename>_deskewed.jpg

The deskewing implementation has been tested using actual document images.

IMPORTANT:

If `deskew.py` is modified, visually inspect the generated image.

A terminal test saying `PASS` only means that the function executed successfully. It does not automatically mean that the resulting image is visually correct.


### Document Classification

File:

    pipeline/classification/document_type.py

The current implementation is a basic keyword-based classifier.

Current categories:

    land_record
    sale_deed
    property_tax
    unknown

This is an MVP/rule-based implementation and can be improved later.


### Language Detection

File:

    pipeline/classification/language_detect.py

The current implementation detects the dominant writing script using Unicode ranges.

Currently handled:

    Telugu
    Kannada
    Hindi
    English

This is a basic script detector and not a complete semantic language-detection model.


## 3. Project Structure

    backend/
    │
    ├── main.py
    ├── README.md
    │
    ├── uploads/
    │
    ├── processed/
    │
    ├── pipeline/
    │   ├── __init__.py
    │   ├── process_document.py
    │   │
    │   ├── preprocessing/
    │   │   ├── __init__.py
    │   │   ├── denoise.py
    │   │   ├── deskew.py
    │   │   └── quality_check.py
    │   │
    │   └── classification/
    │       ├── __init__.py
    │       ├── document_type.py
    │       └── language_detect.py
    │
    ├── test_denoise.py
    ├── test_preprocessing.py
    └── test_pipeline.py


## 4. How to Clone the Repository

Open a terminal and run:

    git clone https://github.com/kumudhanjali/SIH-LandRecords.git

Then enter the repository:

    cd SIH-LandRecords

Then enter the backend:

    cd backend


## 5. Check Python

Run:

    python --version

Python 3.x should be installed.


## 6. Install Dependencies

Run:

    pip install fastapi uvicorn python-multipart opencv-python


## 7. Start the Backend Server

From the `backend` folder run:

    python -m uvicorn main:app --reload

The server should start at:

    http://127.0.0.1:8000

Keep this terminal running.


## 8. Open Swagger

Open this in the browser:

    http://127.0.0.1:8000/docs

This opens the FastAPI Swagger interface.


## 9. Test the Upload API

In Swagger:

    POST /upload
        ↓
    Try it out
        ↓
    Choose a JPG or PNG image
        ↓
    Execute

The image will go through the current backend pipeline.


## 10. What Happens During Upload

The current server performs:

    Uploaded Image
          ↓
    File Type Validation
          ↓
    Save Original Image
          ↓
    Quality Check
          ↓
    Denoising
          ↓
    Deskewing
          ↓
    Document Classification
          ↓
    Language Detection
          ↓
    Return JSON Response


## 11. Processed Output

After uploading a document, check:

    processed/

For example:

    processed/
        document_denoised.jpg
        document_deskewed.jpg

The most important output for the next developer is:

    processed/document_deskewed.jpg

This is the image that should be passed to OCR.


## 12. API Response

A successful upload returns a response similar to:

    {
        "filename": "document.jpg",
        "content_type": "image/jpeg",
        "message": "File uploaded and processed successfully",
        "processing": {
            "quality": {},
            "denoised_file": "processed\\document_denoised.jpg",
            "deskewed_file": "processed\\document_deskewed.jpg",
            "document_type": {},
            "language": {}
        }
    }

The exact values depend on the uploaded document.


## 13. Current Pipeline File

The complete pipeline is controlled by:

    pipeline/process_document.py

Current flow:

    Input Image
        ↓
    Quality Check
        ↓
    Denoising
        ↓
    Deskewing
        ↓
    Document Classification
        ↓
    Language Detection
        ↓
    Result


## 14. Important Limitation — OCR Is Not Implemented Yet

OCR has NOT been implemented yet.

Currently, `process_document.py` uses temporary sample text for testing classification and language detection.

The sample text is currently:

    Survey Number
    Land
    Owner
    Village

This sample text is passed to:

    document_type.py
    language_detect.py

Therefore, the current document classification and language-detection results are NOT actually extracted from the uploaded image.

This is temporary.

Once OCR is implemented, the sample text must be removed and replaced with actual OCR output.


## 15. Current Handoff Point

My work currently ends at the processed/deskewed document image:

    processed/<filename>_deskewed.jpg

Example:

    processed/document_deskewed.jpg

The next developer should use this image as the input for OCR.


## 16. NEXT — OCR

Create:

    pipeline/ocr/

Suggested structure:

    pipeline/
    └── ocr/
        ├── __init__.py
        ├── engine_router.py
        ├── tesseract_engine.py
        ├── nayana_engine.py
        └── qwen_engine.py

The OCR module should take:

    processed/<filename>_deskewed.jpg

and produce:

    Extracted Text

Then connect the OCR output to:

    pipeline/process_document.py


## 17. After OCR

The pipeline should become:

    Upload
      ↓
    Quality Check
      ↓
    Denoising
      ↓
    Deskewing
      ↓
    OCR
      ↓
    Extracted Text
      ↓
    Document Classification
      ↓
    Language Detection


The hardcoded sample text in `process_document.py` must be removed after OCR is connected.


## 18. NEXT — Field Extraction

After OCR, build structured field extraction.

Suggested location:

    pipeline/extraction/

Possible fields:

    Survey Number
    Owner Name
    Village
    Taluk
    District
    Land Area
    Document Number
    Date

The input will be OCR text.

The output should be structured data.

Example:

    {
        "survey_number": "...",
        "owner_name": "...",
        "village": "...",
        "district": "...",
        "land_area": "..."
    }


## 19. NEXT — Validation

After field extraction, implement validation.

Suggested location:

    pipeline/validation/

Possible modules:

    format_checks.py
    logical_checks.py
    cross_record_checks.py

Validation should eventually check:

- Field formats
- Required fields
- Logical consistency
- Cross-record consistency


## 20. NEXT — Confidence Scoring

After OCR, extraction, and validation, implement confidence scoring.

Suggested location:

    pipeline/scoring/

Possible file:

    confidence_scorer.py

The confidence system can eventually combine:

    OCR confidence
    +
    Extraction confidence
    +
    Validation results

The result can then determine whether a record needs human verification.


## 21. NEXT — Human Verification

The eventual flow should be:

    Document
       ↓
    OCR
       ↓
    Field Extraction
       ↓
    Validation
       ↓
    Confidence Score
       ↓
    High Confidence ─────→ Digital Record
       ↓
    Low Confidence
       ↓
    Human Verification
       ↓
    Corrected Digital Record


## 22. Current Tests

### Test Denoising

Run:

    python test_denoise.py


### Test Preprocessing and Classification

Run:

    python test_preprocessing.py

This tests:

- Denoising
- Deskewing
- Quality Check
- Document Classification
- Language Detection


### Test Complete Pipeline

Run:

    python test_pipeline.py

This tests the integrated:

    process_document()

pipeline.


## 23. Recommended Testing

For normal testing, use Swagger:

    http://127.0.0.1:8000/docs

Upload an actual document and inspect:

    API response
    processed/
    
For image-processing changes, always visually inspect the generated image.

Especially check:

    processed/<filename>_denoised.jpg
    processed/<filename>_deskewed.jpg


## 24. Important Development Rules

1. Do not modify the original files inside `uploads/`.

2. Create processed versions inside `processed/`.

3. Do not remove the existing preprocessing modules without discussing with the team.

4. Extend the current pipeline instead of rebuilding completed stages.

5. Do not treat the temporary sample text as OCR output.

6. Once OCR is implemented, replace the sample text with actual OCR output.

7. When modifying image-processing code, visually inspect the output.

8. Run the tests before pushing changes.

9. Keep the API and pipeline structure understandable for the rest of the team.


## 25. Git Workflow

Before starting work:

    git pull

Check the current state:

    git status

Create a feature branch:

    git checkout -b feature/ocr

After completing the work:

    git status

    git add .

    git commit -m "Add OCR processing"

    git push -u origin feature/ocr


## 26. Current Status

    FastAPI Server                 COMPLETED
    Image Upload                   COMPLETED
    File Validation                COMPLETED
    Quality Check                  COMPLETED
    Denoising                     COMPLETED
    Deskewing                     COMPLETED
    Processed File Handling        COMPLETED
    Document Classification        MVP
    Language Detection             MVP

    OCR                            NEXT
    Field Extraction               NEXT
    Validation                     NEXT
    Confidence Scoring             NEXT
    Human Verification             NEXT
    Database Integration           FUTURE


## 27. Final Handoff

The backend currently provides:

    Image
      ↓
    Upload
      ↓
    Quality Check
      ↓
    Denoising
      ↓
    Deskewing
      ↓
    Basic Classification
      ↓
    Basic Language Detection

The main handoff output is:

    processed/<filename>_deskewed.jpg

Continue from this output.

DO NOT rebuild the existing preprocessing.

NEXT:

    Deskewed Image
         ↓
        OCR
         ↓
    Field Extraction
         ↓
      Validation
         ↓
    Confidence Scoring
         ↓
    Human Verification
         ↓
    Digital Land Record