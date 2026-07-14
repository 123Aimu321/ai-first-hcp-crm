from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    message: str


class InteractionFormUpdate(BaseModel):
    hcp_name: str | None = None
    interaction_type: str | None = None
    date: str | None = None
    time: str | None = None

    attendees: list[str] = Field(default_factory=list)

    topics_discussed: str | None = None

    materials_shared: list[str] = Field(
        default_factory=list
    )

    samples_distributed: list[str] = Field(
        default_factory=list
    )

    sentiment: str | None = None
    outcomes: str | None = None
    follow_up_actions: str | None = None


class AgentChatResponse(BaseModel):
    response: str
    form_update: InteractionFormUpdate | None = None