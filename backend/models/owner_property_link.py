import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import Base

class OwnerProperty(Base):
    __tablename__ = "owner_property"
    owner_id: Mapped["uuid.UUID"] = mapped_column(ForeignKey("owners.id", ondelete="CASCADE"), primary_key=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    owner: Mapped["Owner"] = relationship(back_populates="properties")
    property: Mapped["Property"] = relationship(back_populates="owners")
