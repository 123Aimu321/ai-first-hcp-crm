import json
from datetime import datetime

from langchain_groq import ChatGroq

from app.config import settings


model = ChatGroq(
    api_key=settings.groq_api_key,
    model=settings.groq_model,
    temperature=0,
)


async def extract_interaction_data(message: str) -> dict | None:
    now = datetime.now()

    prompt = f"""
You are a structured data extraction AI for an HCP CRM.

Your ONLY job is to determine whether the user is describing an HCP
interaction or updating an interaction form.

CURRENT LOCAL DATE: {now.strftime("%Y-%m-%d")}
CURRENT LOCAL TIME: {now.strftime("%H:%M")}

USER MESSAGE:
{message}

IMPORTANT INTENT RULES:

Messages such as:
"hi"
"hello"
"Dr. Ananya Rao"
"find cardiologists"
"show doctors"
"who is Dr. Rao"

ARE NOT interaction form updates.

Messages such as:
"today I met with Dr. Ananya Rao"
"I called Dr. Rao"
"change sentiment to negative"
"add brochures to materials"
"update topic to Product X"

ARE interaction form updates.

EXTRACTION RULES:

1. "met", "met with", "meeting" => Meeting
2. "called", "phone call", "spoke by phone" => Call
3. "emailed", "sent an email" => Email
4. "conference" => Conference

5. If user says "today", date = {now.strftime("%Y-%m-%d")}
6. If interaction happened today and exact time is not supplied,
   time = {now.strftime("%H:%M")}

7. Extract the complete doctor's name.

8. Extract ONLY the discussion subject.
Example:
"discussed product x efficiency"
=> "Product X efficiency"

9. Sentiment must be exactly:
Positive
Neutral
Negative

10. Materials must ALWAYS be a JSON array.
Example:
"shared brochures"
=> ["Brochures"]

11. Samples must ALWAYS be a JSON array.

12. Do not invent outcomes or follow-up actions.

13. Return ONLY JSON. No markdown.

Return exactly:

{{
    "is_interaction_update": false,
    "hcp_name": null,
    "interaction_type": null,
    "date": null,
    "time": null,
    "attendees": null,
    "topics_discussed": null,
    "materials_shared": null,
    "samples_distributed": null,
    "sentiment": null,
    "outcomes": null,
    "follow_up_actions": null
}}
"""

    response = await model.ainvoke(prompt)
    content = response.content.strip()

    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    try:
        data = json.loads(content.strip())
    except json.JSONDecodeError:
        return None

    if not data.get("is_interaction_update"):
        return None

    data.pop("is_interaction_update", None)

    for field in ("materials_shared", "samples_distributed"):
        value = data.get(field)

        if isinstance(value, str):
            data[field] = [value]

        if value == "":
            data[field] = None

    return data