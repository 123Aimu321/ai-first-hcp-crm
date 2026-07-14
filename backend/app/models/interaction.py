from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    hcp_id: Mapped[int] = mapped_column(
        ForeignKey("hcps.id"),
        index=True,
    )

    interaction_type: Mapped[str] = mapped_column(String(50))
    notes: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    hcp = relationship(
        "HCP",
        back_populates="interactions",
    )