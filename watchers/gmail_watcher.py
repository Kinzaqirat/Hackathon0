import os
from datetime import datetime
from pathlib import Path
from base_watcher import BaseWatcher

# Note: In a real scenario, you'd use google-api-python-client
# For this hackathon deliverable, we provide the robust structure.

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str):
        super().__init__(vault_path, check_interval=60)
        from gmail_service import GmailService
        script_dir = Path(__file__).parent.resolve()
        creds_path = script_dir / "gmail_credentials.json"
        token_path = script_dir / "gmail_token.json"
        self.gmail = GmailService(str(creds_path), str(token_path))
        
    def check_for_updates(self) -> list:
        self.logger.info("Checking for new emails...")
        
        # Only fetch emails from today to avoid "old unread" clutter
        today = datetime.now().strftime('%Y/%m/%d')
        msg_ids = self.gmail.list_unread_messages(query=f'is:unread after:{today}')
        
        if not msg_ids:
            self.logger.info("No new unread emails from today found.")
            return []
            
        self.logger.info(f"Detected {len(msg_ids)} unread emails from today.")
        
        # Process up to 20 per cycle
        process_limit = 20
        messages = []
        for msg_id in msg_ids[:process_limit]:
            msg_content = self.gmail.get_message_content(msg_id)
            if msg_content:
                subject = msg_content.get('subject', 'No Subject')
                self.logger.info(f"Processing: {subject}")
                messages.append(msg_content)
                self.gmail.mark_as_read(msg_id)
        
        if messages:
            self.logger.info(f"Successfully ingested {len(messages)} new emails.")
        
        return messages
    
    def create_action_file(self, message) -> Path:
        # Implementation to convert Gmail message to .md in Needs_Action
        content = f'''---
type: email
from: {message.get('from', 'Unknown')}
subject: {message.get('subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Content
{message.get('snippet', 'No content')}

## Suggested Actions
- [ ] Reply to sender
- [ ] Archive after processing
'''
        filepath = self.needs_action / f"EMAIL_{message.get('id', 'unknown')}.md"
        filepath.write_text(content, encoding='utf-8')
        return filepath

if __name__ == "__main__":
    vault_path = Path(__file__).parent.parent.resolve()
    watcher = GmailWatcher(vault_path=str(vault_path))
    watcher.run()