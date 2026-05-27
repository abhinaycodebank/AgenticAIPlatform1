from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from app.models import AgentModel, WorkflowStepModel

router = APIRouter(prefix="/agents", tags=["Agents"])

# Pydantic Schemas for Input Validation
class AgentCreate(BaseModel):
    name: str
    system_prompt: str
    llm_model: str = "gpt-4o-mini"
    llm_provider: str = "openai"

class AgentResponse(AgentCreate):
    id: int
    class Config:
        from_attributes = True

class AgentFilter(BaseModel):
    name: Optional[str] = None
    llm_model: Optional[str] = None
    llm_provider: Optional[str] = None
    
@router.post("/", response_model=AgentResponse)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    db_agent = db.query(AgentModel).filter(AgentModel.name == agent.name).first()
    if db_agent:
        raise HTTPException(status_code=400, detail="Agent name already exists")
    
    new_agent = AgentModel(**agent.model_dump())
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent

@router.get("/", response_model=list[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    return db.query(AgentModel).all()

@router.delete("/{agent_id}", status_code=204)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if db.query(WorkflowStepModel).filter(WorkflowStepModel.agent_id == agent_id).first():
        raise HTTPException(status_code=400, detail="Cannot delete agent assigned to workflow steps")
    
    db.delete(agent)
    db.commit()

@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: int, agent_update: AgentCreate, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check for name uniqueness if the name is being updated
    if agent.name != agent_update.name:
        existing_agent = db.query(AgentModel).filter(AgentModel.name == agent_update.name).first()
        if existing_agent:
            raise HTTPException(status_code=400, detail="Agent name already exists")
    
    for key, value in agent_update.model_dump().items():
        setattr(agent, key, value)

    db.commit()
    db.refresh(agent)
    return agent

@router.post("/list", response_model=list[AgentResponse])
def list_agents(filters: Optional[AgentFilter] = None, db: Session = Depends(get_db)):
    query = db.query(AgentModel) if not filters else db.query(AgentModel).filter_by(**filters.model_dump(exclude_none=True))
    return query.all()