from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.hcp import HCP
from app.schemas.hcp import HCPCreate, HCPResponse


router = APIRouter(prefix="/hcps", tags=["HCPs"])


@router.post("/", response_model=HCPResponse, status_code=201)
def create_hcp(
    payload: HCPCreate,
    db: Session = Depends(get_db),
):
    hcp = HCP(**payload.model_dump())

    db.add(hcp)
    db.commit()
    db.refresh(hcp)

    return hcp


@router.get("/", response_model=list[HCPResponse])
def get_hcps(
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    statement = select(HCP)

    if search:
        search_term = f"%{search}%"

        statement = statement.where(
            or_(
                HCP.name.ilike(search_term),
                HCP.specialty.ilike(search_term),
                HCP.organization.ilike(search_term),
            )
        )

    return db.scalars(statement).all()


@router.get("/{hcp_id}", response_model=HCPResponse)
def get_hcp(
    hcp_id: int,
    db: Session = Depends(get_db),
):
    hcp = db.get(HCP, hcp_id)

    if not hcp:
        raise HTTPException(
            status_code=404,
            detail="HCP not found",
        )

    return hcp