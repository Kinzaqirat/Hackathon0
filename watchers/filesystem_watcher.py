import time
import shutil
from pathlib import Path
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Ensure base_watcher is importable if needed, 
# although watchdog uses an event-driven approach rather than the poll-loop of base_watcher.
# I will adapt the structure slightly to fit the watchdog requirement.

class InboxHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logger = logging.getLogger("InboxHandler")
        
        # Ensure directories exist
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.needs_action.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        if source.parent != self.inbox:
            return

        self.logger.info(f"New file detected: {source.name}")
        
        # Wait a moment for file to be fully written
        time.sleep(1)
        
        dest_file = self.needs_action / f"FILE_{source.name}"
        shutil.copy2(source, dest_file)
        
        # Create metadata file
        meta_path = self.needs_action / f"FILE_{source.name}.md"
        meta_path.write_text(f"""---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
timestamp: {time.strftime('%Y-%m-%dT%H:%M:%S')}
status: pending
---

# New File Dropped
The file `{source.name}` was detected in the Inbox and is ready for processing.

## Suggested Actions
- [ ] Review file content
- [ ] Categorize data
- [ ] Move to archive or delete original
""")
        self.logger.info(f"Created action file for {source.name}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    vault = Path("..").resolve()
    handler = InboxHandler(vault)
    observer = Observer()
    observer.schedule(handler, str(vault / 'Inbox'), recursive=False)
    
    print(f"Monitoring {vault / 'Inbox'}...")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
