import os
import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Resolve paths relative to this script
SCRIPT_DIR = Path(__file__).parent.resolve()
VAULT_ROOT = SCRIPT_DIR.parent
LOG_DIR = VAULT_ROOT / "Logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "orchestrator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Orchestrator")

import re
from gmail_service import GmailService

class GlobalEventHandler(FileSystemEventHandler):
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.dashboard_path = vault_path / "Dashboard.md"
        
        # Initialize Gmail Service
        creds_path = SCRIPT_DIR / "gmail_credentials.json"
        token_path = SCRIPT_DIR / "gmail_token.json"
        self.gmail = GmailService(str(creds_path), str(token_path))

    def on_created(self, event):
        if event.is_directory:
            return
        
        path = Path(event.src_path).resolve()
        # Determine which folder it's in by comparing with vault subfolders
        folder = path.parent.name
        filename = path.name

        logger.info(f"Event in {folder}: {filename}")
        
        # Add a delay for file completion (Obsidian and other apps write in steps)
        time.sleep(2)

        if folder == 'Inbox':
            self.handle_inbox(path)
        elif folder == 'Approved':
            self.handle_approval(path)
        elif folder == 'Rejected':
            self.handle_rejection(path)
        elif folder == 'Done':
            self.handle_completion(path)

    def handle_inbox(self, path):
        abs_path = str(path.absolute())
        logger.info(f"Ingesting from Inbox. Full path: {abs_path}")
        
        # Robust content reading: Wait for content to appear (up to 5 attempts)
        content = ""
        for i in range(5):
            try:
                if not path.exists():
                    logger.warning(f"File {path.name} disappeared before processing.")
                    return
                
                # Check size first
                size = os.path.getsize(path)
                logger.info(f"File {path.name} current size: {size} bytes")
                
                if size > 0:
                    content = path.read_text(encoding='utf-8', errors='ignore').strip()
                    if content:
                        break
                
                logger.warning(f"File {path.name} is empty or unreadable. Attempt {i+1}/5, retrying in 1s...")
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Could not read {path.name} (locked?): {e}. Retrying...")
                time.sleep(1)

        if not content:
            logger.error(f"File {path.name} still empty after retries. Skipping command detection.")
        else:
            try:
                # Command pattern: write mail to (name/email): (message)
                match = re.search(r'write mail to\s+([\w\.-]+@[\w\.-]+\.\w+|[\w\s]+)[:\s]+(.*)', content, re.IGNORECASE | re.DOTALL)
                
                if match:
                    recipient = match.group(1).strip()
                    message_body = match.group(2).strip()
                    logger.info(f"Detected email command: to={recipient}, body={message_body[:50]}...")
                
                    # Check if it's an email address or a name (for now we require email or specific known addresses)
                    # If it's not an email, we could look it up in a contact list (future feature)
                    if '@' not in recipient:
                        logger.warning(f"Recipient '{recipient}' is not a valid email address. Skipping auto-send.")
                    else:
                        logger.info(f"Sending email to {recipient}...")
                        result = self.gmail.send_message(recipient, f"Message from AI Employee", message_body)
                        if result:
                            logger.info(f"Successfully sent email to {recipient}")
                            # Move to Done immediately for auto-executed commands
                            dest = self.vault_path / "Done" / path.name
                            shutil.move(str(path), str(dest))
                            self.update_dashboard_metric("Active Tasks", 0) # No change needed to active tasks if it goes straight to done
                            return

            except Exception as e:
                logger.error(f"Error processing inbox file for commands: {e}")

        dest = self.vault_path / "Needs_Action" / f"FILE_{path.name}"
        shutil.copy2(path, dest)
        
        # Create metadata
        meta_path = dest.with_suffix(".md")
        meta_path.write_text(f"---\ntype: ingestion\nstatus: pending\ntimestamp: {time.ctime()}\n---\n# New Task: {path.name}\nPlease process this file.", encoding='utf-8')
        self.update_dashboard_metric("Active Tasks", 1)

    def handle_approval(self, path):
        logger.info(f"Executing Approved Action: {path.name}")
        # Simulation: After approval, move to Done
        # In Gold tier, this is where you'd call an MCP server/script
        time.sleep(2) 
        dest = self.vault_path / "Done" / path.name
        try:
            shutil.move(str(path), str(dest))
            logger.info(f"Moved approved task {path.name} to Done.")
        except Exception as e:
            logger.error(f"Error moving approved task: {e}")

    def handle_rejection(self, path):
        logger.warning(f"Task Rejected: {path.name}")
        # Log to a central audit file
        log_file = self.vault_path / "Logs" / "rejections.log"
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(f"{time.ctime()} - REJECTED: {path.name}\n")
        
        # Move to a rejection archive if needed, or leave it
        archive = self.vault_path / "Logs" / "Archive" / "Rejected"
        archive.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(path), str(archive / path.name))
        except Exception as e:
            logger.error(f"Error moving rejected task: {e}")

    def handle_completion(self, path):
        logger.info(f"Task Verified Complete: {path.name}")
        self.update_dashboard_metric("Active Tasks", -1)

    def update_dashboard_metric(self, metric_name, delta):
        try:
            if not self.dashboard_path.exists():
                logger.error(f"Dashboard not found at {self.dashboard_path}")
                return
            content = self.dashboard_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            new_lines = []
            updated = False
            for line in lines:
                if f"**{metric_name}**" in line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        try:
                            value_str = parts[3].strip()
                            current_val = int(''.join(filter(str.isdigit, value_str)) or 0)
                            new_val = max(0, current_val + delta)
                            parts[3] = f" {new_val} in `/Needs_Action` "
                            line = "|".join(parts)
                            updated = True
                        except Exception as e:
                            logger.error(f"Failed to parse metric value: {e}")
                new_lines.append(line)
            if updated:
                self.dashboard_path.write_text("\n".join(new_lines), encoding='utf-8')
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")

if __name__ == "__main__":
    vault = VAULT_ROOT
    event_handler = GlobalEventHandler(vault)
    observer = Observer()

    # Folders to watch
    folders = ["Inbox", "Approved", "Rejected", "Done"]
    for f in folders:
        f_path = vault / f
        f_path.mkdir(parents=True, exist_ok=True)
        observer.schedule(event_handler, str(f_path), recursive=False)
        logger.info(f"Monitoring folder: {f_path}")

    observer.start()
    logger.info("Orchestrator started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
