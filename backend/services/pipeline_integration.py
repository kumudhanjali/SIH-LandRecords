from db import crud
from db.database import SessionLocal
from models.document import DocumentStatus
from pipeline.extraction.schemas import get_schema_for_type

AUTO_APPROVE_THRESHOLD = 0.90
REVIEW_THRESHOLD = 0.60

def _field_payload(value, confidence, is_pii):
    if isinstance(value, dict):
        result = dict(value)
        result.setdefault("confidence", confidence)
        result.setdefault("is_pii", is_pii)
        return result
    return {"value": value, "confidence": confidence, "is_pii": is_pii}

def save_pipeline_output(document_id: int, extracted_fields: dict, scores: dict, validation_issues: list) -> None:
    """Persist extracted values, scores and status; owns its transaction/session."""
    fields = extracted_fields.get("fields", extracted_fields)
    if not isinstance(fields, dict):
        raise TypeError("extracted_fields must be a mapping or contain a 'fields' mapping")
    score_values = scores.get("fields", scores) if isinstance(scores, dict) else {}
    details = {name: _field_payload(value, score_values.get(name) if isinstance(score_values, dict) else None,
                                    bool((get_schema_for_type(extracted_fields.get("document_type", "")) or {}).get(name, {}).get("pii")))
               for name, value in fields.items() if name != "document_type"}
    numeric = [float(v.get("confidence")) for v in details.values() if isinstance(v, dict) and v.get("confidence") is not None]
    if isinstance(scores, dict) and scores.get("overall_confidence") is not None:
        confidence = float(scores["overall_confidence"])
    else:
        confidence = sum(numeric) / len(numeric) if numeric else None
    issues = validation_issues or []
    if confidence is None:
        status = DocumentStatus.pending
    elif confidence >= AUTO_APPROVE_THRESHOLD and not issues:
        status = DocumentStatus.auto_approved
    else:
        status = DocumentStatus.needs_review
    with SessionLocal() as db:
        try:
            document = crud.get_document(db, document_id)
            if document is None:
                raise ValueError(f"Document {document_id} does not exist")
            document.overall_confidence = confidence
            document.status = status
            if extracted_fields.get("document_type"):
                document.document_type = extracted_fields["document_type"]
            crud.create_extracted_fields(db, document_id, details)
        except Exception:
            db.rollback()
            raise
