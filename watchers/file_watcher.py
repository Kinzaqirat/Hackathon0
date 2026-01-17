"""
Intelligent File System Watcher for Bronze Tier
Monitors /Inbox folder, moves files, AND analyzes content
"""

import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class IntelligentInboxWatcher(FileSystemEventHandler):
    """Watches Inbox folder and analyzes file content"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs = self.vault_path / 'Logs'
        
        # Create folders if they don't exist
        self.inbox.mkdir(exist_ok=True)
        self.needs_action.mkdir(exist_ok=True)
        self.logs.mkdir(exist_ok=True)
        
        print(f"📁 Watching: {self.inbox}")
        print(f"📋 Target: {self.needs_action}")
        print(f"🧠 Mode: INTELLIGENT (with content analysis)")
    
    def on_created(self, event):
        """Called when a new file is created in Inbox"""
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        
        # Ignore temporary Obsidian files
        if source.name.startswith('.') or source.suffix in ['.tmp', '.swp']:
            return
            
        print(f"\n{'='*60}")
        print(f"🆕 NEW FILE DETECTED: {source.name}")
        print(f"{'='*60}")
        
        # Wait for file to be fully written
        time.sleep(2)
        
        # Try multiple times if file is locked
        max_retries = 5
        for attempt in range(max_retries):
            dest = self.needs_action / source.name
            try:
                if not source.exists():
                    print(f"⚠️  File no longer exists: {source.name}")
                    return
                
                # STEP 1: Read file content
                print(f"\n📖 Reading file content...")
                file_content = self.read_file_content(source)
                
                # STEP 2: Analyze content
                print(f"🧠 Analyzing content...")
                analysis = self.analyze_content(file_content, source.name)
                
                # STEP 3: Move file
                print(f"📦 Moving file to Needs_Action...")
                shutil.move(str(source), str(dest))
                print(f"✅ Moved to: {dest}")
                
                # STEP 4: Create intelligent metadata
                print(f"📝 Creating intelligent task report...")
                self.create_intelligent_metadata(source.name, file_content, analysis)
                
                # STEP 5: Log the action
                self.log_action(source.name, analysis)
                
                print(f"\n{'='*60}")
                print(f"✅ PROCESSING COMPLETE!")
                print(f"{'='*60}\n")
                
                # Success - break the retry loop
                break
                
            except PermissionError:
                if attempt < max_retries - 1:
                    print(f"⏳ File locked, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
                else:
                    print(f"❌ File still locked after {max_retries} attempts")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
    
    def read_file_content(self, filepath: Path) -> str:
        """Read and return file content"""
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    content = filepath.read_text(encoding=encoding)
                    print(f"   ✓ File size: {len(content)} characters")
                    return content
                except UnicodeDecodeError:
                    continue
            return "[Binary or unreadable content]"
        except Exception as e:
            print(f"   ✗ Error reading file: {e}")
            return "[Error reading file]"
    
    def analyze_content(self, content: str, filename: str) -> dict:
        """Analyze file content and determine task type"""
        analysis = {
            'task_type': 'unknown',
            'priority': 'normal',
            'keywords': [],
            'estimated_time': 'unknown',
            'suggested_actions': []
        }
        
        content_lower = content.lower()
        
        # Detect task type
        if any(word in content_lower for word in ['invoice', 'payment', 'bill', 'receipt']):
            analysis['task_type'] = '💰 Financial Task'
            analysis['suggested_actions'] = [
                'Review payment details',
                'Verify amount and recipient',
                'Process payment or forward to accounting'
            ]
        elif any(word in content_lower for word in ['meeting', 'schedule', 'appointment', 'calendar']):
            analysis['task_type'] = '📅 Scheduling Task'
            analysis['suggested_actions'] = [
                'Check calendar availability',
                'Send meeting invite',
                'Prepare agenda'
            ]
        elif any(word in content_lower for word in ['email', 'reply', 'message', 'contact']):
            analysis['task_type'] = '✉️ Communication Task'
            analysis['suggested_actions'] = [
                'Draft response',
                'Review and send',
                'Follow up if needed'
            ]
        elif any(word in content_lower for word in ['report', 'analysis', 'summary', 'review']):
            analysis['task_type'] = '📊 Report/Analysis Task'
            analysis['suggested_actions'] = [
                'Gather required data',
                'Create analysis or summary',
                'Review and finalize'
            ]
        elif any(word in content_lower for word in ['buy', 'purchase', 'shopping', 'groceries']):
            analysis['task_type'] = '🛒 Shopping/Purchase Task'
            analysis['suggested_actions'] = [
                'Create shopping list',
                'Compare prices',
                'Make purchase'
            ]
        else:
            analysis['task_type'] = '📋 General Task'
            analysis['suggested_actions'] = [
                'Review task details',
                'Determine next steps',
                'Execute or delegate'
            ]
        
        # Detect priority
        if any(word in content_lower for word in ['urgent', 'asap', 'emergency', 'immediately']):
            analysis['priority'] = '🔴 HIGH'
            analysis['estimated_time'] = 'Today'
        elif any(word in content_lower for word in ['important', 'priority', 'soon']):
            analysis['priority'] = '🟡 MEDIUM'
            analysis['estimated_time'] = 'This week'
        else:
            analysis['priority'] = '🟢 NORMAL'
            analysis['estimated_time'] = 'When possible'
        
        # Extract keywords (first 5 meaningful words)
        words = [w for w in content.split() if len(w) > 3]
        analysis['keywords'] = words[:5]
        
        print(f"   ✓ Task Type: {analysis['task_type']}")
        print(f"   ✓ Priority: {analysis['priority']}")
        print(f"   ✓ Keywords: {', '.join(analysis['keywords'][:3])}")
        
        return analysis
    
    def create_intelligent_metadata(self, filename: str, content: str, analysis: dict):
        """Create an intelligent metadata file with analysis"""
        meta_file = self.needs_action / f"TASK_{filename}.md"
        
        # Preview content (first 200 chars)
        content_preview = content[:200].replace('\n', ' ')
        if len(content) > 200:
            content_preview += "..."
        
        metadata_content = f"""---
type: intelligent_task
filename: {filename}
created: {datetime.now().isoformat()}
task_type: {analysis['task_type']}
priority: {analysis['priority']}
estimated_time: {analysis['estimated_time']}
status: pending_review
---

# 🤖 AI Task Analysis Report

## 📄 File Information
- **Filename**: {filename}
- **Detected**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Content Length**: {len(content)} characters

## 🎯 Task Classification
- **Type**: {analysis['task_type']}
- **Priority**: {analysis['priority']}
- **Estimated Time**: {analysis['estimated_time']}

## 📝 Content Preview
```
{content_preview}
```

## 🔍 Detected Keywords
{', '.join(analysis['keywords'])}

## ✅ Suggested Actions
{chr(10).join(f"{i+1}. {action}" for i, action in enumerate(analysis['suggested_actions']))}

## 📋 Next Steps
- [ ] Review the original file: `{filename}`
- [ ] Verify AI analysis is correct
- [ ] Execute suggested actions
- [ ] Move to `/Done` when complete

## 💡 Notes
Add your observations here...

---
*Generated by Intelligent AI Employee Watcher v1.0*
*Analyzed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        meta_file.write_text(metadata_content, encoding='utf-8')
        print(f"   ✓ Intelligent report created: {meta_file.name}")
    
    def log_action(self, filename: str, analysis: dict):
        """Log the watcher action with analysis"""
        log_file = self.logs / f"watcher_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        log_entry = f"""
[{datetime.now().isoformat()}] FILE PROCESSED
  - Filename: {filename}
  - Task Type: {analysis['task_type']}
  - Priority: {analysis['priority']}
  - Status: Moved to Needs_Action
{'='*60}
"""
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)


def main():
    """Main function to run the intelligent watcher"""
    vault_path = Path(__file__).parent.parent
    
    print("🤖 INTELLIGENT AI EMPLOYEE FILE WATCHER")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print("\n🧠 Features:")
    print("  • Detects new files")
    print("  • Reads file content")
    print("  • Analyzes task type and priority")
    print("  • Suggests actionable next steps")
    print("  • Creates intelligent task reports")
    print("\n💡 Drop files into /Inbox folder to see magic!")
    print("🛑 Press Ctrl+C to stop\n")
    print("=" * 60)
    
    # Create event handler and observer
    event_handler = IntelligentInboxWatcher(str(vault_path))
    observer = Observer()
    observer.schedule(event_handler, str(event_handler.inbox), recursive=False)
    
    # Start watching
    observer.start()
    print("\n✅ Intelligent Watcher is now ACTIVE and ANALYZING!\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping intelligent watcher...")
        observer.stop()
    
    observer.join()
    print("✅ Watcher stopped successfully")


if __name__ == "__main__":
    main()