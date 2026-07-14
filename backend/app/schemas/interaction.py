from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InteractionBase(BaseModel):
    hcp_id: int
    interaction_type: str
    notes: str


class InteractionCreate(InteractionBase):
    pass


class InteractionResponse(InteractionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)