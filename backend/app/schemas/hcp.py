from pydantic import BaseModel, ConfigDict


class HCPBase(BaseModel):
    name: str
    specialty: str
    organization: str | None = None


class HCPCreate(HCPBase):
    pass


class HCPResponse(HCPBase):
    id: int

    model_config = ConfigDict(from_attributes=True)