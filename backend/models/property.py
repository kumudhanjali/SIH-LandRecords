from datetime import datetime
from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.database import Base

class Property(Base):
    __tablename__ = "properties"
    id: Mapped[int] = mapped_column(primary_key=True)
    survey_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    village: Mapped[str] = mapped_column(String(200), nullable=False)
    taluk: Mapped[str | None] = mapped_column(String(200))
    district: Mapped[str] = mapped_column(String(200), nullable=False)
    land_area: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    owners: Mapped[list["OwnerProperty"]] = relationship(back_populates="property", cascade="all, delete-orphan")
