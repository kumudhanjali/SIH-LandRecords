from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.document import Document, DocumentStatus
from models.field import ExtractedField
from models.owner import Owner
from models.property import Property
from models.owner_property_link import OwnerProperty
from core.security import encrypt_pii, pii_lookup_hash

def create_document(db: Session, filename: str, **data) -> Document:
    document = Document(filename=filename, **data)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

def get_document(db: Session, document_id: int) -> Document | None:
    return db.get(Document, document_id)

def create_extracted_fields(db: Session, document_id: int, fields: dict) -> list[ExtractedField]:
    created = []
    for name, payload in fields.items():
        payload = payload if isinstance(payload, dict) else {"value": payload}
        pii = bool(payload.get("is_pii", payload.get("pii", False)))
        value = payload.get("value")
        if pii and value is not None:
            value = encrypt_pii(str(value))
        raw = payload.get("raw_match", payload.get("raw_value"))
        if pii and raw is not None:
            raw = encrypt_pii(str(raw))
        original_value = payload.get("original_value")
        if pii and original_value is not None:
            original_value = encrypt_pii(str(original_value))
        row = ExtractedField(document_id=document_id, field_name=name, value=None if value is None else str(value),
            raw_match=None if raw is None else str(raw), confidence=payload.get("confidence"), is_pii=pii,
            verified=bool(payload.get("verified", False)), original_value=original_value)
        db.add(row)
        created.append(row)
    db.commit()
    return created

def create_or_link_owner(db: Session, owner_data: dict, property_id: int | None = None, relationship_type: str = "current_owner") -> Owner:
    data = dict(owner_data)
    aadhaar = data.pop("owner_id_number", data.pop("aadhaar", None))
    encrypted = data.pop("owner_id_number_encrypted", None)
    encrypted = encrypted or (encrypt_pii(str(aadhaar)) if aadhaar is not None else None)
    lookup_hash = pii_lookup_hash(str(aadhaar)) if aadhaar is not None else None
    owner = db.scalar(select(Owner).where(Owner.owner_id_number_lookup_hash == lookup_hash)) if lookup_hash else None
    if owner is None:
        if not encrypted:
            raise ValueError("owner_data must include owner_id_number or owner_id_number_encrypted")
        owner = Owner(owner_id_number_encrypted=encrypted, owner_id_number_lookup_hash=lookup_hash or pii_lookup_hash(encrypted), **data)
        db.add(owner)
        db.flush()
    if property_id is not None and db.get(OwnerProperty, (owner.id, property_id)) is None:
        db.add(OwnerProperty(owner_id=owner.id, property_id=property_id, relationship_type=relationship_type))
    db.commit()
    db.refresh(owner)
    return owner

def create_or_link_property(db: Session, property_data: dict, owner_id: UUID | None = None, relationship_type: str = "current_owner") -> Property:
    data = dict(property_data)
    prop = data.pop("id", None)
    property_row = db.get(Property, prop) if prop is not None else None
    if property_row is None and all(data.get(key) is not None for key in ("survey_number", "village", "district")):
        statement = select(Property).where(Property.survey_number == data["survey_number"],
            Property.village == data["village"], Property.district == data["district"])
        if data.get("taluk") is not None:
            statement = statement.where(Property.taluk == data["taluk"])
        property_row = db.scalar(statement)
    if property_row is None:
        property_row = Property(**data)
        db.add(property_row)
        db.flush()
    if owner_id is not None and db.get(OwnerProperty, (owner_id, property_row.id)) is None:
        db.add(OwnerProperty(owner_id=owner_id, property_id=property_row.id, relationship_type=relationship_type))
    db.commit()
    db.refresh(property_row)
    return property_row

def update_document_status(db: Session, document_id: int, status: DocumentStatus | str) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise ValueError(f"Document {document_id} does not exist")
    document.status = DocumentStatus(status)
    db.commit()
    db.refresh(document)
    return document
