"""Apply migrations, then verify a dummy pipeline write and encrypted PII at rest.

Run from backend after setting DATABASE_URL and PII_ENCRYPTION_KEY:
    alembic upgrade head
    python scripts/check_pipeline_persistence.py
The separately owned users table must exist before the initial migration because
extracted_fields.verified_by has an FK to users.id.
"""
from sqlalchemy import text
from db.database import SessionLocal
from db.crud import create_document
from core.security import decrypt_pii
from services.pipeline_integration import save_pipeline_output

TEST_AADHAAR = "234567890123"

with SessionLocal() as db:
    doc = create_document(db, "dummy-rtc.pdf", document_type="rtc")
    document_id = doc.id

save_pipeline_output(document_id,
    {"document_type": "rtc", "fields": {
        "owner_name": {"value": "Example Owner", "raw_match": "Example Owner"},
        "owner_id_number": {"value": TEST_AADHAAR, "raw_match": TEST_AADHAAR, "pii": True},
        "survey_number": {"value": "142/1", "raw_match": "142/1"},
    }},
    {"overall_confidence": 0.97, "fields": {"owner_name": 0.99, "owner_id_number": 0.96, "survey_number": 0.96}},
    [])

with SessionLocal() as db:
    rows = db.execute(text("SELECT field_name, value, raw_match FROM extracted_fields WHERE document_id = :id"), {"id": document_id}).mappings().all()
    pii = next(row for row in rows if row["field_name"] == "owner_id_number")
    assert pii["value"] != TEST_AADHAAR and decrypt_pii(pii["value"]) == TEST_AADHAAR
    assert pii["raw_match"] != TEST_AADHAAR and decrypt_pii(pii["raw_match"]) == TEST_AADHAAR
    assert len(rows) == 3
    print(f"Verified document {document_id}: {len(rows)} extracted fields; PII encrypted at rest.")
