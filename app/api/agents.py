import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, model_validator
from typing import Any, Dict, Optional, List
from app.db.session import get_db
from app.models import AgentModel, WorkflowStepModel

router = APIRouter(prefix="/agents", tags=["Agents"])

# Pydantic Schemas for Input Validation
class AgentCreate(BaseModel):
    name: str
    system_prompt: str
    llm_model: str = "gpt-4o-mini"
    llm_provider: str = "openai"
    personality: str = "Professional"
    # tools_config: List[str] = Field(default_factory=list)
    # schedule_config: str = "Manual"
    memory_enabled: bool = True
    execution_limits: Dict[str, Any] = Field(default_factory=lambda: {"max_tokens": 2000})


class AgentResponse(BaseModel):
    id: int
    name: str
    system_prompt: str
    llm_model: str
    llm_provider: str
    personality: str
    # tools_config: List[str]       # Expecting a clean Python List on output
    # schedule_config: str
    memory_enabled: bool          # Expecting a true Boolean flag on output
    execution_limits: Dict[str, Any] # Expecting a structural Python Dict on output
    
    class Config:
        from_attributes = True
    
    # --- AUTOMATIC JSON TRANSLATOR ---
    @model_validator(mode="before")
    @classmethod
    def parse_database_strings(cls, data: Any) -> Any:
        """Intercepts the database object attributes and safely decompresses string columns."""
        # Check if we are reading from an ORM database object model
        if hasattr(data, "__dict__") or not isinstance(data, dict):
            # Convert orm object attributes into a workable dictionary context copy
            attrs = {c.key: getattr(data, c.key) for c in data.__mapper__.local_table.columns}
        else:
            attrs = data

        # 1. Safely decompress tools_config text string into a Python list
        if isinstance(attrs.get("tools_config"), str):
            try:
                attrs["tools_config"] = json.loads(attrs["tools_config"])
            except Exception:
                attrs["tools_config"] = []

        # 2. Safely decompress execution_limits text string into a Python dictionary
        if isinstance(attrs.get("execution_limits"), str):
            try:
                attrs["execution_limits"] = json.loads(attrs["execution_limits"])
            except Exception:
                attrs["execution_limits"] = {"max_tokens": 2000, "max_loops": 5}

        # 3. Cast string value flags ('True' or 'False') back into pristine Python Booleans
        if isinstance(attrs.get("memory_enabled"), str):
            attrs["memory_enabled"] = attrs["memory_enabled"] == "True"

        return attrs


class AgentFilter(BaseModel):
    name: Optional[str] = None
    llm_model: Optional[str] = None
    llm_provider: Optional[str] = None


    
@router.post("/", response_model=AgentResponse)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    db_agent = db.query(AgentModel).filter(AgentModel.name == agent.name).first()
    if db_agent:
        raise HTTPException(status_code=400, detail="Agent name already exists")
    
    agent_data = agent.model_dump()
    
    # 2. CRITICAL STEP: Serialize the Python dict/list into flat JSON text strings for SQLite
    # agent_data["tools_config"] = json.dumps(agent_data.get("tools_config", []))
    agent_data["execution_limits"] = json.dumps(agent_data.get("execution_limits", {}))
    
    # 3. Handle data casting for the boolean flag cleanly
    agent_data["memory_enabled"] = str(agent_data.get("memory_enabled", True))
    
    # 4. Pass the string-safe dictionary into the database model
    new_agent = AgentModel(**agent_data)
    
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
    
    update_data = agent_update.model_dump()
    
    # Clean and serialize fields before execution mapping updates
    # update_data["tools_config"] = json.dumps(update_data.get("tools_config", []))
    update_data["execution_limits"] = json.dumps(update_data.get("execution_limits", {}))
    update_data["memory_enabled"] = str(update_data.get("memory_enabled", True))

    for key, value in update_data.items():
        setattr(agent, key, value)

    db.commit()
    db.refresh(agent)
    return agent

@router.post("/list", response_model=list[AgentResponse])
def list_agents(filters: Optional[AgentFilter] = None, db: Session = Depends(get_db)):
    query = db.query(AgentModel) if not filters else db.query(AgentModel).filter_by(**filters.model_dump(exclude_none=True))
    return query.all()