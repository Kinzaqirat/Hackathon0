# Skill: Generate Plan
## Purpose
Analyzes a task in `Needs_Action` and creates a detailed `Plan.md` for execution.

## Instructions
When invoked with a target task file:
1. **Analyze Requirements**: Read the content of the task file and its metadata.
2. **Break Down**: Divide the task into sub-steps.
3. **Draft Plan**: Create a file `Needs_Action/PLAN_[TaskName].md` with:
    - [ ] Step 1
    - [ ] Step 2
    - [ ] Final Verification
4. **Approval Request**: Notify the user that a new plan is ready for review.

## Output Format
```markdown
# Plan: [Task Name]
- **Objective**: ...
- **Steps**:
    1. ...
- **Estimated Effort**: ...
```
