import json

from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_core.tools import tool

from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction
from app.services.audit_service import create_audit_log


INDIA_TIMEZONE = ZoneInfo(
    "Asia/Kolkata"
)
@tool
def search_hcps(
    name: str = "",
    specialty: str = "",
    organization: str = "",
) -> str:
    """
    Search healthcare professionals by independently inferred
    name, specialty, or organization.

    The LLM must semantically separate the user's request into
    the appropriate tool arguments.
    """

    db = SessionLocal()

    try:
        query = db.query(HCP)

        if name:
            query = query.filter(
                HCP.name.ilike(f"%{name}%")
            )

        if specialty:
            query = query.filter(
                HCP.specialty.ilike(f"%{specialty}%")
            )

        if organization:
            query = query.filter(
                HCP.organization.ilike(
                    f"%{organization}%"
                )
            )

        hcps = query.all()

        create_audit_log(
            db=db,
            action="SEARCH_HCPS",
            entity_type="HCP",
            entity_id=0,
            details={
                "name": name,
                "specialty": specialty,
                "organization": organization,
                "results_found": len(hcps),
            },
        )

        db.commit()

        if not hcps:
            return json.dumps(
                {
                    "status": "not_found",
                    "message": "No matching HCP found.",
                }
            )

        return json.dumps(
            [
                {
                    "id": hcp.id,
                    "name": hcp.name,
                    "specialty": hcp.specialty,
                    "organization": hcp.organization,
                }
                for hcp in hcps
            ]
        )

    except Exception as error:
        db.rollback()

        return json.dumps(
            {
                "status": "error",
                "message": str(error),
            }
        )

    finally:
        db.close()


@tool
def log_interaction(
    hcp_id: int,
    interaction_type: str,
    notes: str,
) -> str:
    """
    Persist a confirmed HCP interaction into the CRM.
    """

    db = SessionLocal()

    try:
        hcp = db.get(HCP, hcp_id)

        if not hcp:
            return f"HCP with ID {hcp_id} was not found."

        interaction = Interaction(
            hcp_id=hcp_id,
            interaction_type=interaction_type,
            notes=notes,
        )

        db.add(interaction)
        db.flush()

        create_audit_log(
            db=db,
            action="LOG_INTERACTION",
            entity_type="Interaction",
            entity_id=interaction.id,
            details={
                "hcp_id": hcp.id,
                "hcp_name": hcp.name,
                "interaction_type": interaction_type,
            },
        )

        db.commit()
        db.refresh(interaction)

        return json.dumps(
            {
                "status": "success",
                "interaction_id": interaction.id,
                "hcp_name": hcp.name,
            }
        )

    except Exception as error:
        db.rollback()
        return json.dumps(
            {
                "status": "error",
                "message": str(error),
            }
        )

    finally:
        db.close()


@tool
def prepare_interaction_draft(
    hcp_name: str,
    interaction_type: str,
    topics_discussed: str,
    sentiment: str,
    materials_shared: list[str],
    attendees: list[str],
    outcomes: str,
    follow_up_actions: str,
) -> str:
    """
    Prepare structured interaction form data from the user's
    natural-language interaction description.

    The LLM must infer all arguments semantically.

    attendees must contain only additional participants explicitly
    mentioned by the user. The HCP represented by hcp_name must not
    be included in attendees.

    If the user says today or describes a current interaction,
    use the current Asia/Kolkata date and time.
    """

    now = datetime.now(
    INDIA_TIMEZONE
)

    cleaned_attendees = [
        attendee
        for attendee in attendees
        if attendee.strip().lower()
        != hcp_name.strip().lower()
    ]

    return json.dumps(
        {
            "action": "populate_interaction_form",
            "form_data": {
                "hcp_name": hcp_name,
                "interaction_type": interaction_type,
                "date": now.date().isoformat(),
                "time": now.strftime("%H:%M"),
                "attendees": cleaned_attendees,
                "topics_discussed": topics_discussed,
                "materials_shared": materials_shared,
                "sentiment": sentiment,
                "outcomes": outcomes,
                "follow_up_actions": follow_up_actions,
            },
        }
    )


@tool
def update_interaction(
    interaction_id: int,
    field_name: str,
    new_value: str,
) -> str:
    """
    Update an existing CRM interaction based on a natural-language
    user instruction. The LLM determines the field and new value.
    """

    db = SessionLocal()

    try:
        interaction = db.get(Interaction, interaction_id)

        if not interaction:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Interaction not found.",
                }
            )

        editable_fields = {
            "interaction_type",
            "notes",
        }

        if field_name not in editable_fields:
            return json.dumps(
                {
                    "status": "error",
                    "message": f"Field {field_name} cannot be updated.",
                }
            )

        old_value = getattr(interaction, field_name)

        setattr(interaction, field_name, new_value)

        create_audit_log(
            db=db,
            action="UPDATE_INTERACTION",
            entity_type="Interaction",
            entity_id=interaction.id,
            details={
                "field": field_name,
                "old_value": old_value,
                "new_value": new_value,
            },
        )

        db.commit()

        return json.dumps(
            {
                "status": "success",
                "interaction_id": interaction.id,
                "updated_field": field_name,
                "new_value": new_value,
            }
        )

    except Exception as error:
        db.rollback()

        return json.dumps(
            {
                "status": "error",
                "message": str(error),
            }
        )

    finally:
        db.close()


@tool
def suggest_follow_up(
    hcp_name: str,
    interaction_summary: str,
    sentiment: str,
) -> str:
    """
    Request a professional CRM follow-up recommendation.

    The LLM must review the interaction context and return
    one concise, specific next action.
    """

    return json.dumps(
        {
            "action": "generate_follow_up",
            "hcp_name": hcp_name,
            "interaction_summary": (
                interaction_summary
            ),
            "sentiment": sentiment,
            "instruction": (
                "Return exactly one concise professional "
                "follow-up recommendation. Do not describe "
                "the LangGraph workflow or tool execution."
            ),
        }
    )


TOOLS = [
    search_hcps,
    log_interaction,
    prepare_interaction_draft,
    update_interaction,
    suggest_follow_up,
]