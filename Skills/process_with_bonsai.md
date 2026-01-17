# Process Tasks with Bonsai Skill

## Purpose

Process all pending tasks in /Needs_Action folder using Bonsai Claude integration

## Instructions for Claude (via Bonsai)

When invoked, you should:

1. **Scan Needs_Action Folder**
    
    - List all files (both original and TASK_*.md files)
    - Group them by task type
2. **Read Task Reports**
    
    - Open each TASK_*.md file
    - Extract: task type, priority, suggested actions
    - Read original file content if needed
3. **Create Priority Summary**
    
    - Sort tasks by priority (HIGH → MEDIUM → NORMAL)
    - List urgent tasks first
    - Estimate total time needed
4. **Generate Action Plan**
    
    - Create a numbered list of tasks to complete
    - Include: task name, type, priority, next action
    - Suggest an order of execution
5. **Update Dashboard**
    
    - Count total pending tasks
    - Update "Pending Tasks" number
    - Add today's activity summary

## Output Format

```markdown
# Task Processing Report - [Current Date]

## 🔴 High Priority Tasks (Urgent)
1. [Task name] - Type: [type] - Action: [next step]
2. ...

## 🟡 Medium Priority Tasks
1. [Task name] - Type: [type] - Action: [next step]

## 🟢 Normal Priority Tasks
1. [Task name] - Type: [type] - Action: [next step]

## 📊 Summary
- Total pending: X tasks
- Urgent: Y tasks
- Recommended: Start with task #1
```

## Usage with Bonsai

From vault directory:

```bash
bonsai start claude "Use the process_with_bonsai skill to analyze my tasks"
```

Or in interactive mode:

```
Read the process_with_bonsai skill file and execute it
```

## Safety Rules

- Never delete original files
- Never modify files without permission
- Always ask before moving files to /Done
- Log all actions in /Logs folder