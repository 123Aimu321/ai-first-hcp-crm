from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HCP(Base):
    __tablename__ = "hcps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    specialty: Mapped[str] = mapped_column(String(100), index=True)
    organization: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    interactions = relationship(
        "Interaction",
        back_populates="hcp",
        cascade="all, delete-orphan",
    )