from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import json
import re

app = FastAPI()

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VAULT_ROOT = Path(__file__).parent.parent.resolve()

@app.get("/api/ping")
async def ping():
    return {"status": "pong", "version": "1.1"}

@app.get("/api/stats")
async def get_stats():
    """Returns core metrics from the vault."""
    dashboard_path = VAULT_ROOT / "Dashboard.md"
    needs_action_path = VAULT_ROOT / "Needs_Action"
    done_path = VAULT_ROOT / "Done"
    logs_path = VAULT_ROOT / "Logs"
    
    # Count active tasks
    active_tasks = len(list(needs_action_path.glob("*.md"))) if needs_action_path.exists() else 0
    done_tasks = len(list(done_path.glob("*"))) if done_path.exists() else 0
    
    # Parse revenue from Dashboard.md (simple regex)
    revenue = "$0.00"
    if dashboard_path.exists():
        content = dashboard_path.read_text(encoding="utf-8")
        revenue_match = re.search(r"\*\*Weekly Revenue\*\*\s*\|\s*🟢 Healthy\s*\|\s*(\$[0-9,.]+)", content)
        if revenue_match:
            revenue = revenue_match.group(1)
            
    return {
        "active_tasks": active_tasks,
        "completed_tasks": done_tasks,
        "revenue": revenue,
        "system_health": "Online",
        "last_updated": os.path.getmtime(dashboard_path) if dashboard_path.exists() else 0
    }

@app.get("/api/tasks")
async def get_tasks():
    """Returns the list of pending tasks with snippets."""
    needs_action_path = VAULT_ROOT / "Needs_Action"
    if not needs_action_path.exists():
        return []
    
    tasks = []
    for file in needs_action_path.glob("*.md"):
        try:
            content = file.read_text(encoding="utf-8")
            # Extract title or snippet
            lines = content.splitlines()
            title = file.name
            snippet = ""
            sender = ""
            for line in lines:
                if line.startswith("# "):
                    title = line[2:].strip()
                elif line.startswith("from:"):
                    sender = line[5:].strip()
                elif not line.startswith("---") and line.strip() and not snippet:
                    snippet = line.strip()[:100]
            
            tasks.append({
                "id": file.name,
                "title": title,
                "snippet": snippet,
                "sender": sender,
                "time": os.path.getmtime(file),
                "type": "email" if "EMAIL" in file.name else "file"
            })
        except Exception:
            continue
    
    return sorted(tasks, key=lambda x: x["time"], reverse=True)

@app.post("/api/task/complete")
async def complete_task(data: dict):
    """Moves a task and all its related files from Needs_Action to Done."""
    task_id = data.get("id")
    if not task_id:
        raise HTTPException(status_code=400, detail="Missing task ID")
    
    needs_action_path = VAULT_ROOT / "Needs_Action"
    done_path = VAULT_ROOT / "Done"
    done_path.mkdir(parents=True, exist_ok=True)
    
    src_main = needs_action_path / task_id
    if not src_main.exists():
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    import shutil
    try:
        base_name = src_main.stem
        related_files = list(needs_action_path.glob(f"{base_name}.*"))
        
        for file_path in related_files:
            dest = done_path / file_path.name
            if dest.exists():
                if dest.is_dir(): shutil.rmtree(dest)
                else: dest.unlink()
            shutil.move(str(file_path), str(dest))
            
        return {"status": "success"}
    except Exception as e:
        import logging
        logging.error(f"Failed to complete task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task/{task_id}")
async def get_task_detail(task_id: str):
    """Returns the parsed content of a specific task."""
    task_path = VAULT_ROOT / "Needs_Action" / task_id
    if not task_path.exists():
        raise HTTPException(status_code=404, detail="Task not found")
    
    content = task_path.read_text(encoding="utf-8")
    
    # Parse markdown headers if it's an email
    result = {"content": content, "from": "Unknown", "subject": "No Subject", "body": content}
    
    if task_id.startswith("EMAIL_") or content.startswith("---"):
        lines = content.splitlines()
        body_start = 0
        in_header = False
        for i, line in enumerate(lines):
            if line.startswith("---"):
                if not in_header: in_header = True
                else: 
                    body_start = i + 1
                    break
            elif in_header:
                if line.startswith("from:"): 
                    raw_from = line[5:].strip()
                    # Try to extract email from "Name <email@..."
                    email_match = re.search(r'<(.+?)>', raw_from)
                    result["from"] = email_match.group(1) if email_match else raw_from
                elif line.startswith("subject:"): result["subject"] = line[8:].strip()
        
        # Strip ## Email Content etc
        result["body"] = "\n".join(lines[body_start:]).replace("## Email Content", "").replace("## Suggested Actions", "").strip()
    
    return result

@app.get("/api/logs")
async def get_logs():
    """Returns recent orchestrator logs."""
    log_file = VAULT_ROOT / "Logs" / "orchestrator.log"
    if not log_file.exists():
        return []
    
    lines = log_file.read_text(encoding="utf-8").splitlines()
    return lines[-10:] # Last 10 lines

from pydantic import BaseModel
from datetime import datetime

class ChatMessage(BaseModel):
    message: str

@app.post("/api/chat")
async def post_chat(chat: ChatMessage):
    """Writes a chat message to the Inbox for the orchestrator to process."""
    inbox_path = VAULT_ROOT / "Inbox"
    inbox_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = inbox_path / f"CHAT_{timestamp}.txt"
    
    try:
        file_path.write_text(chat.message, encoding="utf-8")
        return {"status": "success", "message": "Command recognized by system."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files for the dashboard
app.mount("/", StaticFiles(directory=str(Path(__file__).parent), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
