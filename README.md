# 🤖 Advanced AI Agent Orchestration Platform

An enterprise-grade, asynchronous AI agent orchestration platform built from scratch. This system allows users to programmatically register autonomous AI agents with customized granular configurations (personalities, models, memory behavior, and execution limitations) and assemble them sequentially into collaborative multi-agent workflow pipelines.

The platform provides dual consumer access points: a high-utility management dashboard for visual analytics and an external messaging channel interface via a Telegram Bot.

---

## 🏗️ System Architecture & Data Flow

The platform implements a clean, decoupled, multi-tier architecture separating the Presentation layer, Business Logic layer, and Data Storage layer to ensure vertical scalability and non-blocking runtime properties.

```text
  [ User Interfaces ]           [ Backend Core Engine ]           [ Storage Layer ]
 ┌───────────────────┐         ┌───────────────────────┐         ┌─────────────────┐
 │ Streamlit Admin   │◄───────►│ FastAPI Router Engines│◄───────►│ SQLAlchemy ORM  │
 │  Dashboard        │   SSE   │ (Async Request Pool)  │         │  Data Mapping   │
 └───────────────────┘         └───────────┬───────────┘         └────────┬────────┘
                                           │                              │
 ┌───────────────────┐                     ▼                              ▼
 │ Telegram Channel  │◄────────────────────┴─────────────────────────────►│ SQLite Database │
 │  Bot Interface    │ Webhook                                           │ (platform.db)   │
 └───────────────────┘                                                   └─────────────────┘
                                           │
                                           ▼
                               ┌───────────────────────┐
                               │  LangGraph Orchestrator│
                               │ (Dynamic StateGraph)  │
                               └───────────┬───────────┘
                                           │
                                           ▼
                               ┌───────────────────────┐
                               │ OpenAI GPT-4o Engine │
                               └───────────────────────┘
```

### 🔁 End-to-End Operational Lifecycle
1. **Configuration**: Admin profiles and linear step pipelines are defined via the Streamlit interface and securely stored as stringified state maps inside SQLite.
2. **Ingress Call**: An execution trigger arrives via an HTTP stream call or a Telegram Bot webhook.
3. **Graph Assembly**: The FastAPI engine intercepts the call, fetches the assigned configuration sequence from the database, and feeds it into a **Dynamic LangGraph Graph Factory**.
4. **Stateful Execution**: LangGraph provisions a stateful thread model wrapper that compiles nodes programmatically. Each node references a distinct database agent prompt.
5. **Real-Time Streaming**: As the agents process their tasks sequentially, telemetry events and word chunks are pulled out using LangGraph's `astream_events` protocol and pushed to the UI via a persistent **Server-Sent Events (SSE)** channel.

---

## 🛠️ Technical Stack Specifications


| Architectural Layer | Selected Technology |
| :--- | :--- |
| **Backend API Engine** | FastAPI (Python 3.11) |
| **Orchestration Runtime** | LangGraph (LangChain Ecosystem) |
| **User Interface Portal** | Streamlit |
| **Database Core** | SQLite + SQLAlchemy ORM |
| **External Channel Wrapper** | Telegram Bot API Wrapper |
| **Real-Time Log Streamer** | Server-Sent Events (sse-starlette) |
| **Deployment Standard** | Docker & Docker Compose |

---

## 💡 Architectural Trade-off Analysis (Why This Stack Beats Alternatives)

### 1. LangGraph vs. CrewAI / AutoGen
* **The Choice**: **LangGraph** was selected as the AI execution engine.
* **The Reason**: Frameworks like CrewAI rely heavily on black-box, unpredictable agent behaviors. LangGraph models multi-agent interactions explicitly as state machines (graphs, nodes, and edges). This provides deterministic control over execution ordering, predictable memory management via persistent state schemas, and native asynchronous streaming support (`astream_events`), which is required for enterprise logs.

### 2. Streamlit + Static Diagrams vs. Next.js + React Flow
* **The Choice**: **Streamlit** was prioritized for the management portal interface.
* **The Reason**: While React Flow provides interactive canvas features, it introduces heavy frontend dependencies, state synchronization boilerplate across WebSockets, and slow development cycles. Streamlit allows for building a data-dense configuration dashboard using pure Python. This allowed development time to be reallocated toward refining the core AI orchestrator, ensuring memory isolation, and implementing execution limits.

### 3. FastAPI Server-Sent Events (SSE) vs. WebSockets
* **The Choice**: HTTP **Server-Sent Events (SSE)** via `sse-starlette`.
* **The Reason**: WebSockets require complex bidirectional handshake management, state tracking, and are prone to disconnecting through corporate firewalls. Because agent telemetry logs and token streams are strictly unidirectional (Backend \(\rightarrow\) Frontend), SSE is the most efficient choice. It operates over standard HTTP, includes automatic reconnection out of the box, and keeps resource consumption minimal.

### 4. SQLite vs. PostgreSQL (For Prototyping)
* **The Choice**: Local **SQLite** running in Write-Ahead Logging (WAL) mode.
* **The Reason**: SQLite eliminates the need to run an external database container during early testing, keeping deployment fast and single-command simple. By using SQLAlchemy ORM, the database access code remains completely independent of the underlying engine. If needed, the entire data layer can be migrated to production PostgreSQL by modifying a single line in the configuration string (`DATABASE_URL`).

---

## 🚀 Environment Setup & Local Execution

The platform is fully containerized to run smoothly on any machine with zero local dependency management.

### Prerequisites
* Ensure [Docker Desktop](https://docker.com) is installed and running on your laptop.

### 1. Configure the Environment Values
Create a file named `.env` in the **root directory** of the project and paste your credentials:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
TELEGRAM_BOT_TOKEN=your_official_telegram_bot_token_here
```

### 2. Launch the Single-Command Multi-Container Stack
Open your Windows PowerShell or local terminal inside the project root and run:

```powershell
docker compose up --build
```

Docker will automatically create an isolated network bridge, build the backend engine and frontend dashboard images, map your database persistence paths, and spin up both layers simultaneously.

### 🎯 Exposure Reference Ports
* **FastAPI Backend (Swagger Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Streamlit Admin Management Dashboard**: [http://localhost:8501](http://localhost:8501)

---

## 📖 Operational User Manual (Step-by-Step Workflow Execution)

### Step 1: Register Your Independent Agents
1. Open the Admin Dashboard at `http://localhost:8501` and navigate to the **🧑‍💻 Agent Admin Registry** tab.
2. Fill out the configuration fields:
   * **Agent Name**: `Triage Analyst`
   * **System Base Instructions**: `Extract the core technical problem from this message. Output as a short summary.`
   * **Personality**: `Highly professional, cold, and factual.`
   * **Memory**: Check the box to enable memory.
   * **Max Generation Tokens Limit**: `1500`
3. Click **Deploy Agent Blueprint**.
4. Repeat this step to register a second agent named `Resolution Expert` (System Instructions: `Take the technical summary and draft an email solution assuming the server will reboot in 20 minutes.`).

### Step 2: Assemble Your Sequential Workflow Pipeline
1. Navigate to the **⛓️ Sequential Workflow Builder** tab.
2. In the form field, type a unique matching pipeline name identifier: `server_escalation`.
3. Map the order of operations:
   * Set **Sequence Step Index** to `1` and select `Triage Analyst` from the dropdown. Click **Link Step**.
   * Set **Sequence Step Index** to `2` and select `Resolution Expert` from the dropdown. Click **Link Step**.
4. View your updated execution path in the right-hand panel to confirm the pipeline is wired correctly (`Step 1 ──► Step 2`).

### Step 3: Run and Monitor Real-Time Pipeline Executions

#### Method A: Via the Web Log Console Dashboard
1. Move over to the **📺 Live Log Console Monitor** tab.
2. Enter the target pipeline profile name to run: `server_escalation`.
3. Provide an inbound trigger prompt: *"Our core API production cluster crashed at 3 AM due to a database out-of-memory lock error!"*
4. Click **Fire Pipeline & Stream Output Link**.
5. Watch the real-time logs stream in: The dashboard will display info alerts as the pipeline wakes up, print execution events as the runtime transitions between nodes, and render text responses token-by-token.

#### Method B: Via the External Telegram Channel Interface
1. Open your Telegram application and start a conversation with your registered bot.
2. Type the platform runtime command syntax to trigger your pipeline remotely:
   ```text
   /run server_escalation The database is locked and everything is slow!
   ```
3. Your bot will send an immediate response confirming the task has started, pass processing duties across your database agents in the background, and message you the final response directly inside the chat window.

## Demo
Link: https://drive.google.com/file/d/1Mo7J7j1Lcfd7Rkge06SySz1BuaoK5AKb/view?usp=drive_link