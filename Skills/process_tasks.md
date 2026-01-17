# Skill: Process Tasks
## Purpose
Analyzes and initiates next steps for all items in the /Needs_Action folder.

## Instructions
When invoked, you should:
1. **List all files** in `/Needs_Action`.
2. **Prioritize**: Sort by file type (EMAIL > FILE) and any priority flags in the metadata.
3. **Plan**: For each item, generate a proposed plan in a new file called `PLAN_[Original_Name].md` if a plan doesn't exist.
4. **Execute**: If the plan is straightforward (e.g., sorting a file), perform the action. If sensitive, ask for approval.
5. **Update Dashboard**: Once processed or planned, update the `Active Tasks` metric in `Dashboard.md`.

## Safety Rules
- Do NOT move files to /Done without user confirmation.
- Do NOT delete files.
- Log every action to `/Logs/actions.log`.
