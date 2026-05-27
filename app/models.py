from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    system_prompt = Column(String, nullable=False)
    llm_model = Column(String, default="gpt-4o-mini", nullable=False)
    llm_provider = Column(String, default="openai", nullable=False)

class WorkflowStepModel(Base):
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String, index=True, nullable=False)
    sequence_number = Column(Integer, nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)

    agent = relationship("AgentModel")
