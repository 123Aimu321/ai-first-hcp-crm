from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.hcp import HCP
from app.models.interaction import Interaction
from app.schemas.interaction import InteractionCreate
from app.services.audit_service import create_audit_log


def create_interaction(
    db: Session,
    payload: InteractionCreate,
) -> Interaction:
    hcp = db.get(HCP, payload.hcp_id)

    if not hcp:
        raise HTTPException(
            status_code=404,
            detail="HCP not found",
        )

    interaction = Interaction(
        **payload.model_dump()
    )

    db.add(interaction)
    db.flush()

    create_audit_log(
        db=db,
        action="CREATE_INTERACTION",
        entity_type="interaction",
        entity_id=interaction.id,
        details={
            "hcp_id": interaction.hcp_id,
            "interaction_type": interaction.interaction_type,
        },
    )

    db.commit()
    db.refresh(interaction)

    return interaction