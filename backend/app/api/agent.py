# backend/app/api/agent.py

import json

from fastapi import APIRouter, HTTPException
from groq import RateLimitError
from langchain_core.messages import AIMessage, ToolMessage

from app.agent.graph import agent_graph
from app.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
)


router = APIRouter(
    prefix="/agent",
    tags=["AI Agent"],
)


# ---------------------------------------------------------
# MODEL ERROR DETECTION
# ---------------------------------------------------------

MODEL_ERROR_MESSAGES = (
    "rate limit",
    "temporarily busy",
    "retry shortly",
    "model error",
    "ai service",
    "groq",
    "try again",
)


def is_model_error_response(
    response: str,
) -> bool:
    if not response:
        return False

    response_lower = response.lower()

    return any(
        text in response_lower
        for text in MODEL_ERROR_MESSAGES
    )


# ---------------------------------------------------------
# FALLBACK FOLLOW-UP
# ---------------------------------------------------------

def build_fallback_follow_up(
    form_update: dict,
) -> str:
    hcp_name = form_update.get(
        "hcp_name",
        "the HCP",
    )

    outcomes = form_update.get(
        "outcomes",
        "",
    ).lower()

    topics = form_update.get(
        "topics_discussed",
        "",
    )

    if "clinical evidence" in outcomes:
        return (
            f"Send the requested clinical evidence to "
            f"{hcp_name} and schedule a follow-up "
            f"discussion regarding {topics or 'the product'}."
        )

    return (
        f"Follow up with {hcp_name} regarding "
        f"{topics or 'the interaction'} and confirm "
        "the appropriate next action."
    )


# ---------------------------------------------------------
# CHAT ENDPOINT
# ---------------------------------------------------------

@router.post(
    "/chat",
    response_model=AgentChatResponse,
)
async def chat_with_agent(
    request: AgentChatRequest,
):
    # -----------------------------------------------------
    # RUN LANGGRAPH
    # -----------------------------------------------------

    try:
        result = await agent_graph.ainvoke(
            {
                "messages": [
                    (
                        "user",
                        request.message,
                    )
                ]
            },
            config={
                "recursion_limit": 20,
            },
        )

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail=(
                "The AI model rate limit was reached. "
                "Please wait a few seconds and retry "
                "the CRM workflow."
            ),
        )

    except Exception as error:
        print(
            "[AGENT API] LangGraph error:",
            repr(error),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "The AI agent encountered an error "
                "while processing the CRM workflow."
            ),
        )

    messages = result.get(
        "messages",
        [],
    )

    # -----------------------------------------------------
    # WORKFLOW STATE
    # -----------------------------------------------------

    form_update = None

    interaction_logged = False
    interaction_updated = False
    follow_up_requested = False

    final_response = ""

    logged_interaction_id = None

    # -----------------------------------------------------
    # PROCESS LANGGRAPH MESSAGE HISTORY
    # -----------------------------------------------------

    for message in messages:

        # -------------------------------------------------
        # TOOL RESULTS
        # -------------------------------------------------

        if isinstance(
            message,
            ToolMessage,
        ):
            try:
                tool_result = json.loads(
                    message.content
                )

            except (
                json.JSONDecodeError,
                TypeError,
            ):
                print(
                    "[AGENT API] Invalid tool result:",
                    message.content,
                )

                continue

            # ---------------------------------------------
            # SEARCH RESULTS
            # ---------------------------------------------

            if isinstance(
                tool_result,
                list,
            ):
                continue

            if not isinstance(
                tool_result,
                dict,
            ):
                continue

            action = tool_result.get(
                "action"
            )

            status = tool_result.get(
                "status"
            )

            # ---------------------------------------------
            # INTERACTION DRAFT
            # ---------------------------------------------

            if (
                action
                == "populate_interaction_form"
            ):
                form_data = tool_result.get(
                    "form_data",
                    {},
                )

                if isinstance(
                    form_data,
                    dict,
                ):
                    form_update = {
                        **form_data,
                        "attendees": form_data.get(
                            "attendees",
                            [],
                        ),
                        "materials_shared": (
                            form_data.get(
                                "materials_shared",
                                [],
                            )
                        ),
                        "samples_distributed": (
                            form_data.get(
                                "samples_distributed",
                                [],
                            )
                        ),
                    }

            # ---------------------------------------------
            # FOLLOW-UP REQUEST
            # ---------------------------------------------

            elif (
                action
                == "generate_follow_up"
            ):
                follow_up_requested = True

            # ---------------------------------------------
            # DATABASE SUCCESS RESULTS
            # ---------------------------------------------

            if status == "success":

                interaction_id = tool_result.get(
                    "interaction_id"
                )

                if interaction_id is not None:
                    logged_interaction_id = (
                        interaction_id
                    )

                # -----------------------------------------
                # UPDATE INTERACTION
                # -----------------------------------------

                if (
                    "updated_field"
                    in tool_result
                ):
                    interaction_updated = True

                    updated_field = tool_result.get(
                        "updated_field"
                    )

                    new_value = tool_result.get(
                        "new_value",
                        "",
                    )

                    if (
                        form_update
                        and updated_field == "notes"
                        and new_value
                    ):
                        form_update[
                            "outcomes"
                        ] = new_value

                # -----------------------------------------
                # LOG INTERACTION
                # -----------------------------------------

                elif interaction_id is not None:
                    interaction_logged = True

        # -------------------------------------------------
        # AI RESPONSE
        # -------------------------------------------------

        elif isinstance(
            message,
            AIMessage,
        ):
            content = message.content

            tool_calls = getattr(
                message,
                "tool_calls",
                None,
            )

            if (
                isinstance(content, str)
                and content.strip()
                and not tool_calls
            ):
                final_response = content.strip()

    # -----------------------------------------------------
    # DETECT MODEL FAILURE RESPONSE
    # -----------------------------------------------------

    model_error = is_model_error_response(
        final_response
    )

    # -----------------------------------------------------
    # FOLLOW-UP VALUE
    # -----------------------------------------------------

    follow_up_response = ""

    if (
        follow_up_requested
        and form_update
    ):
        if (
            final_response
            and not model_error
        ):
            follow_up_response = final_response

        else:
            print(
                "[AGENT API] Using deterministic "
                "follow-up fallback."
            )

            follow_up_response = (
                build_fallback_follow_up(
                    form_update
                )
            )

        form_update[
            "follow_up_actions"
        ] = follow_up_response

    # -----------------------------------------------------
    # STRUCTURED CRM RESPONSE
    # -----------------------------------------------------

    if form_update:
        operations = []

        if interaction_logged:
            operations.append(
                "saved to the CRM"
            )

        if interaction_updated:
            operations.append(
                "updated successfully"
            )

        if follow_up_requested:
            operations.append(
                "reviewed for follow-up"
            )

        operation_text = ", ".join(
            operations
        )

        response_text = (
            "✅ Interaction details captured "
            "successfully! "
        )

        if operation_text:
            response_text += (
                "The LangGraph AI agent processed "
                f"the workflow, {operation_text}, "
                "and automatically populated the "
                "interaction form."
            )

        else:
            response_text += (
                "The interaction form was "
                "automatically populated."
            )

        # ---------------------------------------------
        # SAFE FOLLOW-UP RESPONSE
        # ---------------------------------------------

        if (
            follow_up_requested
            and follow_up_response
        ):
            response_text += (
                "\n\nRecommended follow-up: "
                f"{follow_up_response}"
            )

        # ---------------------------------------------
        # DEBUG WORKFLOW RESULT
        # ---------------------------------------------

        print(
            "[AGENT API] Workflow result:",
            {
                "interaction_id": (
                    logged_interaction_id
                ),
                "logged": interaction_logged,
                "updated": interaction_updated,
                "follow_up": follow_up_requested,
                "model_error": model_error,
            },
        )

        return AgentChatResponse(
            response=response_text,
            form_update=form_update,
        )

    # -----------------------------------------------------
    # NORMAL AI CHAT RESPONSE
    # -----------------------------------------------------

    if (
        final_response
        and not model_error
    ):
        return AgentChatResponse(
            response=final_response,
            form_update=None,
        )

    # -----------------------------------------------------
    # MODEL RATE LIMIT WITHOUT FORM
    # -----------------------------------------------------

    if model_error:
        raise HTTPException(
            status_code=429,
            detail=(
                "The AI model is temporarily busy. "
                "Please retry the request shortly."
            ),
        )

    # -----------------------------------------------------
    # ACTUAL INCOMPLETE WORKFLOW
    # -----------------------------------------------------

    raise HTTPException(
        status_code=500,
        detail=(
            "The LangGraph workflow ended without "
            "producing a final response or interaction "
            "draft."
        ),
    )