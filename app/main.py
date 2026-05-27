from fastapi import FastAPI
from app.db.session import engine, Base
from app.api import agents, workflows, execute

# Create local SQLite tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Agent Orchestration Platform Engine")

# Include Routers
app.include_router(agents.router)
app.include_router(workflows.router)
app.include_router(execute.router)


@app.get("/")
def root():
    return {"status": "Platform backend is live!"}
