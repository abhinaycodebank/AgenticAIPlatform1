import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app.db.session import get_db
from app.engine.graph_factory import WorkflowState, build_workflow_graph
from langchain_core.messages import HumanMessage

load_dotenv()

router = APIRouter(prefix="/telegram", tags=["Telegram Channel"])

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def send_telegram_message(chat_id: int, text: str):
    """Helper function to send raw text responses back to the Telegram client."""
    async with httpx.AsyncClient() as client:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        await client.post(url, json=payload)

@router.post("/webhook")
async def telegram_webhook_receiver(request: Request, db: Session = Depends(get_db)):
    """Asynchronous endpoint that receives real-time messages forwarded by Telegram."""
    try:
        payload = await request.json()
        
        # Guard clause: Ignore non-message updates (like edits or channel posts)
        if "message" not in payload or "text" not in payload["message"]:
            return {"status": "ignored"}
            
        chat_id = payload["message"]["chat"]["id"]
        user_text = payload["message"]["text"]
        
        # --- COMMAND ROUTING PARSER ---
        # Syntax check: Expected input format is "/run workflow_name your prompt goes here"
        if user_text.startswith("/run"):
            parts = user_text.split(" ", 2)
            if len(parts) < 3:
                await send_telegram_message(chat_id, "⚠️ Invalid format! Use: /run [workflow_name] [your prompt]")
                return {"status": "bad_syntax"}
                
            workflow_name = parts[1]
            extracted_user_input = " ".join(parts[2:])
            
            await send_telegram_message(chat_id, f"🚀 Executing workflow pipeline: '{workflow_name}'...")
            
            try:
                # Build and compile your dynamic LangGraph from Day 1
                graph, total_steps = build_workflow_graph(workflow_name, db)
                
                initial_state = WorkflowState(
                    messages=[HumanMessage(content=extracted_user_input)],
                    workflow_name=workflow_name,
                    current_step=1,
                    total_steps=total_steps,
                    logs=[]
                )
                
                # Execute the multi-agent graph chain synchronously
                final_output_state = graph.invoke(initial_state)
                
                # Extract message state safely
                final_messages = final_output_state.get("messages") if isinstance(final_output_state, dict) else final_output_state.messages
                ai_final_answer = final_messages[-1].content
                
                # Ship the processed agent response back to the user
                await send_telegram_message(chat_id, ai_final_answer)
                
            except ValueError as val_err:
                await send_telegram_message(chat_id, f"❌ Configuration Error: {str(val_err)}")
            except Exception as graph_err:
                await send_telegram_message(chat_id, f"💥 Graph Execution Interrupted: {str(graph_err)}")
                
        else:
            # Fallback help menu response
            help_msg = (
                "👋 Welcome to the AI Agent Orchestration Platform!\n\n"
                "To trigger an agent pipeline chain, send:\n"
                "`/run [workflow_name] [your input query]`"
            )
            await send_telegram_message(chat_id, help_msg)
            
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook Callback Crash: {str(e)}")
