
import json
from typing import List

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from app.models import AgentModel, WorkflowStepModel
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults

class WorkflowState(BaseModel):
    messages: List[AnyMessage] = Field(default_factory=list,
                                       description="List of messages exchanged in the workflow",
                                       metadata={"reducer": add_messages})
    workflow_name: str = Field(..., description="Name of the workflow, e.g., 'content_pipeline'")
    current_step: int = Field(default=1, description="Current step number in the workflow sequence")
    total_steps: int = Field(default=0, description="Total number of steps in the workflow")
    agent_id: int = Field(default=0, description="ID of the agent assigned to the current step")
    logs: list[str] = Field(default_factory=list, description="Logs of the workflow execution")

def create_agent_node(agent: AgentModel):
    """Dynamically generates a functional node execution block for a specific database agent."""
    
    # Initialize the specific model assigned to this agent

    print(f"DEBUG: The model provider being sent is: '{agent.llm_provider}'")
    print(f"DEBUG: The model ID being sent is: '{agent.llm_model}'")
    print(f"DEBUG: Type of variable: {type(agent.llm_model)}")
    print("******")

    limits = json.loads(agent.execution_limits)

    if agent.llm_provider == "groq":
        llm = ChatGroq(name=agent.name, model=agent.llm_model, temperature=0.5, max_tokens=limits.get("max_tokens", 2000))
    elif agent.llm_provider == "openai":
        llm = ChatOpenAI(name=agent.name, model=agent.llm_model, temperature=0.5, max_tokens=limits.get("max_tokens", 2000))
    else:
        raise ValueError(f"Unsupported LLM provider: {agent.llm_provider}")
            
    def agent_node(state: WorkflowState) -> dict:
        # Pull everything except system messages to keep history clean

        if state.current_step > limits.get("max_loops", 5):
            return {"logs": state.logs + [f"⚠️ Execution halted: Loop limit hit."]}

        if agent.memory_enabled == "True":
            conversation_history = [msg for msg in state.messages if not isinstance(msg, SystemMessage)]
        else:
            # Memory Disabled: Only pass the very first user message, erasing mid-pipeline history
            conversation_history = [state.messages[0]] if state.messages else []
        
        # Inject this agent's unique database prompt at the very beginning of the context
        composed_prompt = (
            f"{agent.system_prompt}\n\n"
            f"YOUR PERSONALITY: {agent.personality}"
        )
        system_message = SystemMessage(content=composed_prompt)        
        human_message = HumanMessage(content=conversation_history[-1].content if conversation_history else "No user input provided.")
        full_context = [system_message] + [human_message]
        
        # Invoke the LLM
        response = llm.invoke(full_context)
        
        # Log transition details for real-time monitoring
        log_entry = f"Agent [{agent.name}] executed step successfully."
        
        return {
            "messages": [response],
            "current_step": state.current_step + 1,
            "agent_id": agent.id,
            "logs": state.logs + [log_entry]
        }
        
    return agent_node

def build_workflow_graph(wf_name, db):
    """Fetches the workflow definition from the database and constructs a dynamic graph based on assigned agents."""

    steps = db.query(WorkflowStepModel).filter(WorkflowStepModel.workflow_name == wf_name).order_by(WorkflowStepModel.sequence_number).all()
    if not steps:
        raise ValueError(f"No workflow steps found with name: {wf_name}")

    # Build the graph with nodes corresponding to each workflow step's assigned agent
    builder = StateGraph(WorkflowState)
    node_names = []
    # llm_tools = []

    # Add nodes for each step based on the assigned agent
    for step in steps:
        agent = step.agent
        if not agent:
            raise ValueError(f"No agent found with ID: {step.agent_id} for workflow step {step.sequence_number}")
        
        agent_node = create_agent_node(agent)
        # tools = json.loads(agent.tools_config)
        # if "web_search" in tools:
        #     web_search_tool = TavilySearchResults(max_results=3)
        #     llm_tools = [web_search_tool]
        
        node_name = f"step_{step.sequence_number}_{agent.name.replace(' ', '_')}"
        builder.add_node(node_name, agent_node)
        node_names.append(node_name)

    # if llm_tools:
    #     builder.add_node("tools", ToolNode(llm_tools))


    # Connect the nodes sequentially
    builder.add_edge(START, node_names[0])
    for i in range(len(node_names) - 1):
        builder.add_edge(node_names[i], node_names[i + 1])
    builder.add_edge(node_names[-1], END)

    graph = builder.compile()
    return graph, len(node_names)


    
