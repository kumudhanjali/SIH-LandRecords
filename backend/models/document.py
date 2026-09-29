import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class DocumentStatus(str, enum.Enum):
    pending = "pending"
    auto_approved = "auto_approved"
    needs_review = "needs_review"
    verified = "verified"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    original_storage_path: Mapped[str | None] = mapped_column(String(2048))
    processed_storage_path: Mapped[str | None] = mapped_column(String(2048))
    document_type: Mapped[str | None] = mapped_column(String(100))
    language_detected: Mapped[str | None] = mapped_column(String(50))
    upload_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus, name="document_status"), default=DocumentStatus.pending, nullable=False)
    overall_confidence: Mapped[float | None] = mapped_column(Float)
    fields: Mapped[list["ExtractedField"]] = relationship(back_populates="document", cascade="all, delete-orphan")
