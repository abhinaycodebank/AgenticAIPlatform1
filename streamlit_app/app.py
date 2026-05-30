import streamlit as str_ui
import requests
import json
import sseclient

# Target address where your FastAPI application layer is hosted
BACKEND_URL = "http://127.0.0.1:8000"

str_ui.set_page_config(page_title="AI Agent Orchestrator", page_icon="🤖", layout="wide")
str_ui.title("🤖 AI Agent Orchestration Dashboard")
str_ui.caption("Manage agent properties, assemble sequential pipelines, and trace execution analytics.")

# Create the top navigation tab bar layout
tab1, tab2, tab3 = str_ui.tabs(["🧑‍💻 Agent Admin Registry", "⛓️ Sequential Workflow Builder", "📺 Live Log Console Monitor"])

# =====================================================================
# TAB 1: AGENT ADMIN REGISTRY
# =====================================================================
with tab1:
    str_ui.header("Configure & Register Advanced AI Agents")
    
    col1, col2 = str_ui.columns([1, 1])
    with col1:
        str_ui.subheader("Agent Configuration Panel")
        with str_ui.form("agent_creation_form", clear_on_submit=True):
            # Basic Identity
            agent_name = str_ui.text_input("Agent Name", placeholder="e.g., Financial Audit Bot")
            llm_model = str_ui.selectbox("LLM Brain Model", ["gpt-4o", "gpt-4o-mini"])
            system_prompt = str_ui.text_area("System Base Instructions")
            
            str_ui.markdown("---")
            str_ui.markdown("### ⚙️ Extended Behavior Specs")
            
            # Personality & Schedule
            personality = str_ui.text_input("Behavior Personality Traits", value="Analytical, direct, and factual")
            
            # Memory Toggle
            memory_enabled = str_ui.checkbox("Enable Memory (Track conversation history context)", value=True)
            
            # Multi-Select Tools
            tools_config = str_ui.multiselect("Equip Functional Tools", ["web_search"])
            
            # Numeric Execution Limits
            max_tokens = str_ui.number_input("Max Generation Tokens Limit", min_value=100, max_value=4000, value=2000, step=100)
            max_loops = str_ui.number_input("Max Workflow Loop Safety Circuit", min_value=1, max_value=20, value=5, step=1)
            
            submit_btn = str_ui.form_submit_button("Deploy Agent Blueprint")
            if submit_btn:
                # Structure the extended operational payload dictionary matching Pydantic Create schema
                payload = {
                    "name": agent_name.strip(),
                    "system_prompt": system_prompt.strip(),
                    "llm_model": llm_model,
                    "personality": personality,
                    "tools_config": tools_config,
                    "memory_enabled": memory_enabled,   
                    "execution_limits": {"max_tokens": int(max_tokens), "max_loops": int(max_loops)}
                }
                
                # Make the POST connection request to your updated FastAPI layer
                res = requests.post(f"{BACKEND_URL}/agents/", json=payload)
                if res.status_code == 200:
                    str_ui.success(f"Fully configured agent '{agent_name}' deployed to platform database successfully!")
                else:
                    str_ui.error(f"Deployment Refused: {res.json().get('detail')}")

# =====================================================================
# TAB 2: SEQUENTIAL WORKFLOW BUILDER
# =====================================================================
with tab2:
    str_ui.header("Pipeline Linear Assembler Chain")
    str_ui.write("Chain multiple agents together sequentially without a complex canvas layer.")
    
    col_w1, col_w2 = str_ui.columns([1, 1])
    
    with col_w1:
        str_ui.subheader("Map Step to Pipeline ID")
        try:
            # Pull active agents to feed dropdown selection lists
            agent_res = requests.post(f"{BACKEND_URL}/agents/list", json={})
            if agent_res.status_code == 200:
                available_agents = agent_res.json()
                agent_mapping = {a['name']: a['id'] for a in available_agents}
                
                with str_ui.form("workflow_step_form", clear_on_submit=True):
                    wf_name = str_ui.text_input("Workflow Targeting Name Identifier", placeholder="e.g., content_pipeline")
                    seq_num = str_ui.number_input("Sequence Step Positioning Order Index", min_value=1, value=1, step=1)
                    target_agent = str_ui.selectbox("Assign Worker Agent to Step", list(agent_mapping.keys()) if agent_mapping else ["Register an agent first"])
                    
                    save_step_btn = str_ui.form_submit_button("Link Step to Workflow Mapping")
                    if save_step_btn and agent_mapping:
                        step_payload = {
                            "workflow_name": wf_name.strip(),
                            "sequence_number": int(seq_num),
                            "agent_id": agent_mapping[target_agent]
                        }
                        res = requests.post(f"{BACKEND_URL}/workflows/steps", json=step_payload)
                        if res.status_code == 200:
                            str_ui.success("Step mapping written safely to junction state table!")
                        else:
                            str_ui.error("Failed to append pipeline step parameters.")
            else:
                str_ui.error("Could not fetch database agent profiles.")
        except Exception as e:
            str_ui.error(f"Backend data stream offline: {str(e)}")
            
    with col_w2:
        str_ui.subheader("Query Configuration State Maps")
        search_wf_name = str_ui.text_input("Enter Pipeline Name to inspect", value="content_pipeline")
        
        if search_wf_name:
            try:
                wf_res = requests.get(f"{BACKEND_URL}/workflows/{search_wf_name}")
                if wf_res.status_code == 200:
                    steps_list = wf_res.json()
                    if not steps_list:
                        str_ui.info(f"No configured steps mapped under pipeline sequence key '{search_wf_name}'.")
                    else:
                        str_ui.write("### Current Pipeline Execution Pathway Map")
                        for step in steps_list:
                            str_ui.info(f"➡️ **Step {step['sequence_number']}** assigned to Database Agent Reference ID: `[{step['agent_id']}]`")
                else:
                    str_ui.error("Query parameters returned structural error code.")
            except Exception as e:
                str_ui.error(f"Mapping engine query error: {str(e)}")

# =====================================================================
# TAB 3: LIVE LOG CONSOLE MONITOR (SSE STREAMING)
# =====================================================================
with tab3:
    str_ui.header("Real-Time Telemetry Live Log Console")
    str_ui.write("Triggers your compiled LangGraph pipeline and prints live token streams and node jumps via SSE.")
    
    exec_wf_name = str_ui.text_input("Pipeline Profile Target to Run", value="content_pipeline", key="run_wf")
    user_prompt_input = str_ui.text_area("Initial Inbound Trigger Prompt", value="Write a notice saying the system server crashed.")
    
    if str_ui.button("🚀 Fire Pipeline & Stream Output Link"):
        if not exec_wf_name or not user_prompt_input:
            str_ui.warning("Missing workflow identifier parameters or target entry instructions.")
        else:
            # 1. Establish visual anchor elements to drop text outputs into asynchronously
            status_box = str_ui.empty()
            console_box = str_ui.empty()
            token_stream_box = str_ui.empty()
            
            status_box.warning("Opening Server-Sent Events channel link. Listening...")
            
            console_accumulator = "--- START TELEMETRY LOGS ---\n"
            token_accumulator = "--- LLM TOKEN GENERATION CHUNKS ---\n"
            
            # 2. Open an HTTP link targeting the FastAPI SSE router endpoint built on Day 2
            target_stream_url = f"{BACKEND_URL}/execute/stream?workflow_name={exec_wf_name}&user_input={user_prompt_input}"
            
            try:
                # stream=True holds the network socket chunk pipeline open
                response = requests.get(target_stream_url, stream=True)
                client = sseclient.SSEClient(response)
                
                # 3. Read incoming W3C specified text event frames live as they leave your laptop memory
                for event in client.events():
                    # Parse out custom structured JSON blobs packed inside the SSE payload data attributes
                    payload_data = json.loads(event.data)
                    
                    if event.event == "info":
                        status_box.info(f"ℹ️ {payload_data.get('msg')}")
                        
                    elif event.event == "log":
                        new_log = f"[{payload_data.get('node')}] -> {payload_data.get('message')}\n"
                        console_accumulator += new_log
                        console_box.code(console_accumulator, language="text")
                        
                    elif event.event == "token":
                        # Prints the individual characters/tokens as the LLM thinks in real-time
                        token_accumulator += payload_data.get("content", "")
                        token_stream_box.markdown(token_accumulator)
                        
                    elif event.event == "done":
                        status_box.success("🎯 Pipeline execution completed successfully! Stream closed safely.")
                        break
                        
                    elif event.event == "error":
                        status_box.error(f"❌ Execution Fault: {payload_data.get('detail')}")
                        break
                        
            except Exception as conn_err:
                status_box.error(f"SSE Streaming channel disconnect encountered: {str(conn_err)}")
