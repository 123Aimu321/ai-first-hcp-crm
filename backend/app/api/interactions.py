from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.interaction import Interaction
from app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
)
from app.services.interaction_service import (
    create_interaction as create_interaction_service,
)


router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"],
)


@router.post(
    "/",
    response_model=InteractionResponse,
    status_code=201,
)
def create_interaction(
    payload: InteractionCreate,
    db: Session = Depends(get_db),
):
    return create_interaction_service(
        db=db,
        payload=payload,
    )


@router.get(
    "/",
    response_model=list[InteractionResponse],
)
def get_interactions(
    db: Session = Depends(get_db),
):
    statement = select(Interaction).order_by(
        Interaction.created_at.desc()
    )

    return db.scalars(statement).all()


@router.get(
    "/{interaction_id}",
    response_model=InteractionResponse,
)
def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
):
    interaction = db.get(
        Interaction,
        interaction_id,
    )

    if not interaction:
        raise HTTPException(
            status_code=404,
            detail="Interaction not found",
        )

    return interaction