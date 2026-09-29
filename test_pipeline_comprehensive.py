"""Integration check for pipeline persistence and PII encryption using SQLite.

Run from the repository root with: python test_pipeline_comprehensive.py
This process intentionally overrides DATABASE_URL and supplies a temporary
users table, so it does not require the separately managed users schema or
the local PostgreSQL service.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from sqlalchemy import Column, Integer, Table, text


ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

# Set these before importing backend.db.database, which creates its engine at
# import time. The key is generated for this process only unless one was given.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("PII_ENCRYPTION_KEY", Fernet.generate_key().decode("ascii"))

from db.database import Base, SessionLocal, engine  # noqa: E402
from db.crud import create_document  # noqa: E402
from services.pipeline_integration import save_pipeline_output  # noqa: E402


class PipelinePersistenceIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Register the separately owned users table in the same metadata so
        # SQLAlchemy can resolve ExtractedField.verified_by's FK. Create it
        # first, then create the application tables.
        cls.users_table = Table(
            "users",
            Base.metadata,
            Column("id", Integer, primary_key=True),
            extend_existing=True,
        )
        cls.users_table.create(bind=engine, checkfirst=True)
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls) -> None:
        engine.dispose()

    def test_pipeline_saves_document_fields_and_encrypts_pii(self) -> None:
        test_aadhaar = "234567890123"
        with SessionLocal() as db:
            document = create_document(
                db,
                "integration-sample-rtc.pdf",
                original_storage_path="uploads/integration-sample-rtc.pdf",
                processed_storage_path="processed/integration-sample-rtc.pdf",
                document_type="rtc",
                language_detected="en",
            )
            document_id = document.id

        save_pipeline_output(
            document_id,
            {
                "document_type": "rtc",
                "fields": {
                    "owner_name": {"value": "Test Owner", "raw_match": "Test Owner"},
                    "owner_id_number": {
                        "value": test_aadhaar,
                        "raw_match": test_aadhaar,
                        "pii": True,
                    },
                    "survey_number": {"value": "142/1", "raw_match": "142/1"},
                },
            },
            {
                "overall_confidence": 0.97,
                "fields": {
                    "owner_name": 0.99,
                    "owner_id_number": 0.96,
                    "survey_number": 0.96,
                },
            },
            [],
        )

        with SessionLocal() as db:
            document_row = db.execute(
                text("SELECT id, filename, status, overall_confidence FROM documents WHERE id = :id"),
                {"id": document_id},
            ).mappings().one()
            fields = db.execute(
                text(
                    "SELECT field_name, value, raw_match, is_pii "
                    "FROM extracted_fields WHERE document_id = :id ORDER BY field_name"
                ),
                {"id": document_id},
            ).mappings().all()

        self.assertEqual(document_row["filename"], "integration-sample-rtc.pdf")
        self.assertEqual(document_row["status"], "auto_approved")
        self.assertAlmostEqual(document_row["overall_confidence"], 0.97)
        self.assertEqual(len(fields), 3)

        pii_row = next(row for row in fields if row["field_name"] == "owner_id_number")
        self.assertTrue(pii_row["is_pii"])
        self.assertTrue(pii_row["value"].startswith("gAAAAA"), repr(pii_row["value"]))
        self.assertTrue(pii_row["raw_match"].startswith("gAAAAA"), repr(pii_row["raw_match"]))
        self.assertNotEqual(pii_row["value"], test_aadhaar)
        self.assertNotEqual(pii_row["raw_match"], test_aadhaar)

        print("PASS: document and 3 extracted fields are present in SQLite.")
        print(f"PASS: document status={document_row['status']}, confidence={document_row['overall_confidence']:.2f}.")
        print(f"PASS: stored PII value ciphertext: {pii_row['value'][:24]}...")
        print(f"PASS: stored raw_match ciphertext: {pii_row['raw_match'][:24]}...")
        print("PASS: both PII columns start with 'gAAAAA' and are not plaintext.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
