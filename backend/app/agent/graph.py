import asyncio
from typing import Literal

from groq import RateLimitError
from langchain_core.messages import (
    AIMessage,
    SystemMessage,
)
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.state import AgentState
from app.agent.tools import TOOLS
from app.config import settings


# ---------------------------------------------------------
# LLM CONFIGURATION
# ---------------------------------------------------------

model = ChatGroq(
    api_key=settings.groq_api_key,
    model=settings.groq_model,
    temperature=0,
    max_tokens=800,
    max_retries=0,
)

model_with_tools = model.bind_tools(TOOLS)


# ---------------------------------------------------------
# TOOL NODE
# ---------------------------------------------------------

tool_node = ToolNode(TOOLS)


# ---------------------------------------------------------
# PERFORMANCE CONFIGURATION
# ---------------------------------------------------------

MAX_RATE_LIMIT_RETRIES = 2
RATE_LIMIT_RETRY_DELAY = 2


# ---------------------------------------------------------
# ASSISTANT NODE
# ---------------------------------------------------------

async def assistant_node(state: AgentState):
    """
    Main LangGraph reasoning node.

    IMPORTANT:
    Complete message history is preserved because tool-call
    and ToolMessage pairs must remain valid.
    """

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    for attempt in range(MAX_RATE_LIMIT_RETRIES):
        try:
            response = await model_with_tools.ainvoke(
                messages
            )

            tool_calls = getattr(
                response,
                "tool_calls",
                None,
            )

            content = response.content

            print(
                "[AI AGENT] Response:",
                {
                    "has_content": bool(content),
                    "tool_calls": [
                        call.get("name")
                        for call in (tool_calls or [])
                    ],
                    "response_metadata": (
                        response.response_metadata
                    ),
                },
            )

            # -------------------------------------------------
            # EMPTY MODEL RESPONSE PROTECTION
            # -------------------------------------------------

            if not content and not tool_calls:
                print(
                    "[AI AGENT] Empty model response detected."
                )

                return {
                    "messages": [
                        AIMessage(
                            content=(
                                "The AI model ended its reasoning "
                                "before completing the CRM workflow. "
                                "Please retry the request."
                            )
                        )
                    ],
                }

            return {
                "messages": [response],
            }

        except RateLimitError:
            print(
                "[AI AGENT] Groq rate limit "
                f"attempt {attempt + 1}/"
                f"{MAX_RATE_LIMIT_RETRIES}"
            )

            if attempt == MAX_RATE_LIMIT_RETRIES - 1:
                return {
                    "messages": [
                        AIMessage(
                            content=(
                                "The AI service is temporarily busy "
                                "because the Groq rate limit was "
                                "reached. Please retry shortly."
                            )
                        )
                    ],
                }

            print(
                "[AI AGENT] Retrying in "
                f"{RATE_LIMIT_RETRY_DELAY} seconds..."
            )

            await asyncio.sleep(
                RATE_LIMIT_RETRY_DELAY
            )

        except Exception as error:
            print(
                "[AI AGENT] Model error:",
                repr(error),
            )

            return {
                "messages": [
                    AIMessage(
                        content=(
                            "The AI assistant encountered a model "
                            "error while processing the CRM workflow."
                        )
                    )
                ],
            }


# ---------------------------------------------------------
# ROUTING
# ---------------------------------------------------------

def route_tools(
    state: AgentState,
) -> Literal["tools", "__end__"]:

    last_message = state["messages"][-1]

    tool_calls = getattr(
        last_message,
        "tool_calls",
        None,
    )

    if tool_calls:
        tool_names = [
            call.get("name")
            for call in tool_calls
        ]

        print(
            "[LANGGRAPH] Tool calls:",
            tool_names,
        )

        return "tools"

    print(
        "[LANGGRAPH] Workflow completed."
    )

    return END


# ---------------------------------------------------------
# WORKFLOW
# ---------------------------------------------------------

workflow = StateGraph(AgentState)

workflow.add_node(
    "assistant",
    assistant_node,
)

workflow.add_node(
    "tools",
    tool_node,
)

workflow.set_entry_point(
    "assistant"
)

workflow.add_conditional_edges(
    "assistant",
    route_tools,
)

workflow.add_edge(
    "tools",
    "assistant",
)


# ---------------------------------------------------------
# COMPILE
# ---------------------------------------------------------

agent_graph = workflow.compile()