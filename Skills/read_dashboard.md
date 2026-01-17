# Skill: Read Dashboard
## Purpose
Provides a real-time summary of the AI Employee's current state based on the Dashboard.md file.

## Instructions
When invoked, you should:
1. **Read Dashboard.md**: Get the core metrics and status indicators.
2. **Scan Folders**: 
    - Count files in /Inbox
    - Count files in /Needs_Action
    - Count files in /Done (last 24 hours)
3. **Verify Watchers**: Check /Logs/watcher.log for recent activity.
4. **Summary**: Provide a concise summary to the user including current task load and system health.

## Output Format
Respond with a callout summary:
```markdown
> [!TIP] Dashboard Summary
> - **Inbox:** X items pending ingestion.
> - **Needs Action:** Y tasks awaiting processing.
> - **Recent Completions:** Z tasks finished today.
> - **System Health:** [Online/Offline]
```
