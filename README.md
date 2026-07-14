AI-First HCP CRM

An AI-powered Healthcare Professional (HCP) CRM built using React, Redux Toolkit, FastAPI, LangGraph, Groq, SQLAlchemy, and SQLite.

The application allows users to describe HCP interactions using natural language. A LangGraph AI agent processes the request, selects the required CRM tools, performs database operations, and automatically populates the interaction form.

---

## Features

- Natural-language AI Assistant
- HCP search
- AI-generated interaction drafts
- CRM interaction logging
- Existing interaction updates
- AI-based follow-up recommendations
- LangGraph tool orchestration
- Redux Toolkit state management
- SQLite database persistence
- Audit logging

---

## LangGraph Tools

The AI agent has access to five CRM tools:

1. `search_hcps`
   - Searches HCPs by name, specialty, or organization.

2. `prepare_interaction_draft`
   - Converts natural-language interaction details into structured CRM form data.

3. `log_interaction`
   - Saves an HCP interaction to the CRM database.

4. `update_interaction`
   - Updates an existing interaction record.

5. `suggest_follow_up`
   - Provides context for AI-generated professional follow-up recommendations.

The LangGraph agent dynamically selects the required tools based on the user's natural-language request.

---

## Tech Stack

### Frontend

- React
- Vite
- Redux Toolkit
- React Redux
- Lucide React

### Backend

- Python
- FastAPI
- LangGraph
- LangChain
- Groq LLM
- SQLAlchemy
- SQLite
- Uvicorn

---

## Project Structure

```text
ai-first-hcp-crm/
│
├── backend/
│   └── app/
│       ├── agent/
│       │   ├── graph.py
│       │   ├── prompts.py
│       │   ├── state.py
│       │   └── tools.py
│       │
│       ├── api/
│       │   └── agent.py
│       │
│       ├── models/
│       ├── schemas/
│       ├── services/
│       ├── database.py
│       └── main.py
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── AIAssistant.jsx
│       │   └── InteractionForm.jsx
│       │
│       ├── store/
│       │   ├── store.js
│       │   └── interactionSlice.js
│       │
│       ├── services/
│       │   └── api.js
│       │
│       ├── App.jsx
│       └── main.jsx
│
└── README.md
````

---

# How to Run the Project

## 1. Clone the Repository

Open a terminal and run:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Move into the project directory:

```bash
cd ai-first-hcp-crm
```

---

# Backend Setup

## 2. Open the Backend Directory

```bash
cd backend
```

## 3. Create a Python Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

## 4. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Create a `.env` file inside the `backend` directory.

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Replace `your_groq_api_key` with your own Groq API key.

Do not upload the `.env` file or API keys to GitHub.

---

## 6. Start the FastAPI Backend

Run:

```bash
python -m uvicorn app.main:app --reload
```

The backend should start at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Keep this terminal running.

---

# Frontend Setup

## 7. Open a New Terminal

Return to the project root directory and open the frontend directory:

```bash
cd frontend
```

---

## 8. Install Frontend Dependencies

```bash
npm install
```

---

## 9. Start the React Frontend

```bash
npm run dev
```

Vite will display the frontend URL in the terminal.

Usually:

```text
http://localhost:5173
```

Open the displayed URL in your browser.

---

# How to Test the AI Agent

Open the AI Assistant section on the frontend.

Paste the following instruction:

```text
Find Dr. Ananya Rao, prepare and log today's meeting interaction about Product X efficacy with positive sentiment and brochures shared, update the notes to mention her request for clinical evidence, and recommend the best follow-up action.
```

The LangGraph agent should execute the following workflow:

```text
search_hcps
      ↓
prepare_interaction_draft
      ↓
log_interaction
      ↓
update_interaction
      ↓
suggest_follow_up
```

The frontend interaction form should automatically display:

* HCP Name
* Interaction Type
* Current Date and Time
* Topics Discussed
* Materials Shared
* Samples Distributed
* HCP Sentiment
* Outcomes
* Follow-up Actions

---

# Application Flow

```text
React Frontend
      ↓
Redux Toolkit
      ↓
FastAPI /agent/chat
      ↓
LangGraph AI Agent
      ↓
CRM Tools
      ↓
SQLAlchemy / SQLite
      ↓
Structured API Response
      ↓
Redux Store Update
      ↓
React UI Re-render
```

The React frontend sends a natural-language CRM instruction to the FastAPI backend.

FastAPI passes the instruction to the LangGraph agent.

The LangGraph agent reasons about the request and selects the required CRM tools.

Database operations are performed through controlled Python tools using SQLAlchemy.

The backend returns structured `form_update` data.

Redux Toolkit updates the centralized frontend state, and React automatically re-renders the interaction form.

---

# Example API Request

Endpoint:

```text
POST /agent/chat
```

Request body:

```json
{
  "message": "Find Dr. Ananya Rao and prepare today's meeting interaction about Product X efficacy."
}
```

Example response:

```json
{
  "response": "Interaction details captured successfully.",
  "form_update": {
    "hcp_name": "Dr. Ananya Rao",
    "interaction_type": "meeting",
    "topics_discussed": "Product X efficacy",
    "sentiment": "positive"
  }
}
```

---

# Important Notes

* The backend must be running before using the AI Assistant.
* A valid Groq API key is required.
* Never commit the `.env` file.
* LangGraph tool execution depends on the configured LLM.
* The default database is SQLite.
* API documentation is available through FastAPI Swagger UI.

---

# Author

Aiman

BE Artificial Intelligence and Machine Learning

---

# Task Summary

This project demonstrates an AI-first CRM workflow where LangGraph orchestrates multiple CRM tools based on natural-language instructions.

The project combines AI reasoning, tool calling, database persistence, FastAPI APIs, Redux state management, and a React user interface to create an intelligent HCP interaction management workflow.

````

### Before uploading to GitHub

Make sure your `.gitignore` contains:

```gitignore
# Environment variables
.env

# Python
.venv/
venv/
__pycache__/
*.pyc

# Node
node_modules/
dist/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
