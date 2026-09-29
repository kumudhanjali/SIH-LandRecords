"""Integration tests for encrypted PII persistence in the pipeline layer."""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from pathlib import Path

from cryptography.fernet import Fernet
import pytest
from sqlalchemy import Column, Integer, Table, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# The backend creates its engine when db.database is imported. Set safe test
# values before importing it; the fixture below supplies a per-test engine.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["PII_ENCRYPTION_KEY"] = Fernet.generate_key().decode("ascii")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.security import decrypt_pii, encrypt_pii  # noqa: E402
from db.crud import create_document  # noqa: E402
from db.database import Base  # noqa: E402
from models.document import DocumentStatus  # noqa: E402
from services import pipeline_integration  # noqa: E402


@pytest.fixture
def test_session_factory(monkeypatch: pytest.MonkeyPatch) -> Iterator[sessionmaker[Session]]:
    """Create isolated SQLite tables, including the separately owned users table."""
    engine: Engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    # Register the mock users table in ORM metadata so the verified_by FK is
    # resolvable, then physically create it before the remaining app tables.
    users = Base.metadata.tables.get("users")
    if users is None:
        users = Table("users", Base.metadata, Column("id", Integer, primary_key=True))
    users.create(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)

    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    monkeypatch.setattr(pipeline_integration, "SessionLocal", factory)
    try:
        yield factory
    finally:
        engine.dispose()


def test_pii_fernet_encryption_decryption_roundtrip() -> None:
    sensitive_value = "234567890123"

    ciphertext = encrypt_pii(sensitive_value)

    assert ciphertext.startswith("gAAAAA")
    assert ciphertext != sensitive_value
    assert decrypt_pii(ciphertext) == sensitive_value


def test_pipeline_persists_document_fields_and_encrypts_pii_at_rest(
    test_session_factory: sessionmaker[Session],
) -> None:
    sensitive_value = "234567890123"
    with test_session_factory() as db:
        document = create_document(
            db,
            "sample-rtc.pdf",
            original_storage_path="uploads/sample-rtc.pdf",
            processed_storage_path="processed/sample-rtc.pdf",
            document_type="rtc",
            language_detected="en",
        )
        document_id = document.id

    pipeline_integration.save_pipeline_output(
        document_id,
        {
            "document_type": "rtc",
            "fields": {
                "owner_name": {"value": "Test Owner", "raw_match": "Test Owner"},
                "owner_id_number": {
                    "value": sensitive_value,
                    "raw_match": sensitive_value,
                    "pii": True,
                },
                "survey_number": {"value": "142/1", "raw_match": "142/1"},
            },
        },
        {
            "overall_confidence": 0.97,
            "fields": {"owner_name": 0.99, "owner_id_number": 0.96, "survey_number": 0.96},
        },
        [],
    )

    with test_session_factory() as db:
        document_row = db.execute(
            text("SELECT filename, status, overall_confidence FROM documents WHERE id = :id"),
            {"id": document_id},
        ).mappings().one()
        fields = db.execute(
            text(
                "SELECT field_name, value, raw_match, confidence, is_pii, verified "
                "FROM extracted_fields WHERE document_id = :id"
            ),
            {"id": document_id},
        ).mappings().all()

    assert document_row["filename"] == "sample-rtc.pdf"
    assert document_row["status"] == DocumentStatus.auto_approved.value
    assert document_row["overall_confidence"] == pytest.approx(0.97)
    assert len(fields) == 3

    pii_row = next(row for row in fields if row["field_name"] == "owner_id_number")
    assert bool(pii_row["is_pii"]) is True
    assert bool(pii_row["verified"]) is False
    assert pii_row["confidence"] == pytest.approx(0.96)
    assert pii_row["value"].startswith("gAAAAA")
    assert pii_row["raw_match"].startswith("gAAAAA")
    assert pii_row["value"] != sensitive_value
    assert pii_row["raw_match"] != sensitive_value
    assert decrypt_pii(pii_row["value"]) == sensitive_value
    assert decrypt_pii(pii_row["raw_match"]) == sensitive_value


@pytest.mark.parametrize(
    ("confidence", "validation_issues", "expected_status"),
    [
        (0.72, [], DocumentStatus.needs_review.value),
        (0.98, ["survey number mismatch"], DocumentStatus.needs_review.value),
    ],
)
def test_pipeline_routes_low_confidence_or_invalid_output_to_review(
    test_session_factory: sessionmaker[Session],
    confidence: float,
    validation_issues: list[str],
    expected_status: str,
) -> None:
    with test_session_factory() as db:
        document = create_document(db, "review-case.pdf", document_type="rtc")
        document_id = document.id

    pipeline_integration.save_pipeline_output(
        document_id,
        {"document_type": "rtc", "fields": {"survey_number": {"value": "142/1"}}},
        {"overall_confidence": confidence, "fields": {"survey_number": confidence}},
        validation_issues,
    )

    with test_session_factory() as db:
        row = db.execute(
            text("SELECT status FROM documents WHERE id = :id"), {"id": document_id}
        ).one()
    assert row.status == expected_status
