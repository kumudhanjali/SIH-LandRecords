import uuid
from datetime import datetime
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import Base

class Owner(Base):
    __tablename__ = "owners"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id_number_encrypted: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    owner_id_number_lookup_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    contact_info: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    properties: Mapped[list["OwnerProperty"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
