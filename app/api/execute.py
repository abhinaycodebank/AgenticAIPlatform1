
import traceback

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.engine.graph_factory import WorkflowState, build_workflow_graph
from app.models import WorkflowStepModel
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