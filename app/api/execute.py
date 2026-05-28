import asyncio
import json
import traceback

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from app.db.session import get_db
from app.engine.graph_factory import WorkflowState, build_workflow_graph
from langchain_core.messages import HumanMessage

router = APIRouter(prefix="/execute", tags=["execute"])
load_dotenv()


class WorkflowRunRequest(BaseModel):
    workflow_name: str
    user_input: str

@router.post("/")
def run_workflow(request: WorkflowRunRequest, db: Session = Depends(get_db)):
    """Endpoint to execute a defined workflow by name with user input."""
    try:
        builder, total_steps = build_workflow_graph(request.workflow_name, db)

        # Here we would implement the logic to execute the graph step by step, passing the user input and collecting outputs.
        initial_state = WorkflowState(
            messages=[HumanMessage(content=f"{request.user_input}")],
            workflow_name=request.workflow_name,
            current_step=1,
            total_steps=total_steps,
            logs=[f"Starting the workflow chain for '{request.workflow_name}'"]
        )

        final_output_state = builder.invoke(initial_state)
        return {
            "status": "success",
            "messages": final_output_state['messages'][-1].content,
            "logs": final_output_state['logs']
        }
    except Exception as e:
        print(traceback.format_exc(e))
        details = f"Graph execution failed for workflow '{request.workflow_name}': {str(e)}"
        raise HTTPException(status_code=500, detail=details)
    
@router.get("/stream")
async def stream_workflow_pipeline(
    workflow_name: str = Query(..., description="Name of the pipeline to run"),
    user_input: str = Query(..., description="The prompt input from the user"),
    db: Session = Depends(get_db)
):
    """Establishes an HTTP SSE connection to stream real-time execution states from LangGraph."""
    
    # 1. Fetch data configurations and compile the LangGraph runnable asset on the fly
    try:
        graph, total_steps = build_workflow_graph(workflow_name, db)
    except ValueError as val_err:
        async def error_generator():
            yield {"event": "error", "data": json.dumps({"detail": str(val_err)})}
        return EventSourceResponse(error_generator())

    # 2. Build the initial Pydantic state context mapping tracker
    initial_state = WorkflowState(
        messages=[HumanMessage(content=user_input)],
        workflow_name=workflow_name,
        current_step=1,
        total_steps=total_steps,
        logs=[f"Starting dynamic streaming engine for '{workflow_name}'."]
    )

    # 3. Create an asynchronous event generator loop
    async def log_event_generator():
        try:
            # LangGraph's astream_events captures internal state changes step-by-step
            # v2 configuration parameter is optimal for robust metadata capture
            async for event in graph.astream_events(initial_state, version="v2"):
                kind = event.get("event")
                node_name = event.get("name")
                
                # Capture when a specific custom agent node begins running
                if kind == "on_chain_start" and node_name == "LangGraph":
                    yield {
                        "event": "info",
                        "data": json.dumps({"msg": f"Pipeline initialization accepted. Running {total_steps} steps."})
                    }
                
                elif kind == "on_custom_event":
                    # Captures ad-hoc event messages dispatched manually if using custom nodes
                    pass
                    
                # Capture when a node completes processing duty
                elif kind == "on_chain_end" and node_name and not node_name.startswith("LangGraph"):
                    # Extract the update payload context details safely
                    output_data = event.get("data", {}).get("output", {})
                    
                    # Look for logs or outputs emitted by the node
                    if isinstance(output_data, dict) and "logs" in output_data:
                        last_log = output_data["logs"][-1] if output_data["logs"] else "Node complete."
                        yield {
                            "event": "log",
                            "data": json.dumps({
                                "node": node_name,
                                "message": last_log,
                                "next_step_index": output_data.get("current_step", 1)
                            })
                        }
                    
                    elif hasattr(output_data, "messages") and output_data.messages:
                        # Fallback parsing strategy for structured base object representations
                        yield {
                            "event": "log",
                            "data": json.dumps({
                                "node": node_name,
                                "message": f"Node [{node_name}] finished step processing successfully."
                            })
                        }

                # Capture streaming text chunks directly from the LLM tokens as they generate
                elif kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and chunk.content:
                        yield {
                            "event": "token",
                            "data": json.dumps({"content": chunk.content})
                        }
            
            # Send a terminal packet indicating the stream is successfully done
            yield {
                "event": "done",
                "data": json.dumps({"msg": "Execution complete. Closing link safely."})
            }
            
        except Exception as crash_err:
            yield {
                "event": "error",
                "data": json.dumps({"detail": f"Streaming disrupted: {str(crash_err)}"})
            }

    # 4. Hand the generator over to EventSourceResponse to manage connection life
    return EventSourceResponse(log_event_generator())
