from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models import WorkflowStepModel

router = APIRouter(prefix="/workflows", tags=["Workflows"])

class StepCreate(BaseModel):
    workflow_name: str
    sequence_number: int
    agent_id: int

class StepResponse(StepCreate):
    id: int
    class Config:
        from_attributes = True

@router.post("/steps", response_model=StepResponse)
def add_workflow_step(step: StepCreate, db: Session = Depends(get_db)):
    new_step = WorkflowStepModel(**step.model_dump())
    db.add(new_step)
    db.commit()
    db.refresh(new_step)
    return new_step

@router.get("/{name}", response_model=list[StepResponse])
def get_workflow(name: str, db: Session = Depends(get_db)):
    return db.query(WorkflowStepModel).filter(WorkflowStepModel.workflow_name == name).order_by(WorkflowStepModel.sequence_number).all()


