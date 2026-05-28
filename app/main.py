from fastapi import FastAPI
from app.db.session import engine, Base
from app.api import agents, workflows, execute, telegram

import os
import httpx
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.session import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    # Read your running Ngrok base URL from an environment variable or set it directly
    NGROK_URL = "https://treat-retool-handwash.ngrok-free.dev"
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if BOT_TOKEN and "ngrok" in NGROK_URL:
        registration_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={NGROK_URL}/telegram/webhook"
        async with httpx.AsyncClient() as client:
            response = await client.get(registration_url)
            print("--- TELEGRAM WEBHOOK REGISTRATION STATUS ---")
            print(response.json())
            
    yield
    # --- SHUTDOWN LOGIC ---
    if BOT_TOKEN and "ngrok" in NGROK_URL:
        registration_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        async with httpx.AsyncClient() as client:
            response = await client.get(registration_url)
            print("--- TELEGRAM WEBHOOK DELETION STATUS ---")
            print(response.json())


# Update your application initialization to include this lifecycle lifespan context manager
app = FastAPI(title="AI Agent Orchestration Platform Engine", lifespan=lifespan)

# Create local SQLite tables automatically on startup
Base.metadata.create_all(bind=engine)

# Include Routers
app.include_router(agents.router)
app.include_router(workflows.router)
app.include_router(execute.router)
app.include_router(telegram.router)


@app.get("/")
def root():
    return {"status": "Platform backend is live!"}
