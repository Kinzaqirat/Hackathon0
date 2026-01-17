# Skill: Ralph Wiggum Autonomy Loop
## Purpose
Enables continuous, multi-step task completion without repeated user interaction.

## Concept
This skill mimics the "Ralph Wiggum Stop" hook. When Claude finishes a sub-task, instead of stopping, it evaluates if the overall mission objective is met.

## Instructions
1. **Initialize Mission**: Set a clear objective (e.g., "Process all files in /Needs_Action until folder is empty").
2. **Execute Step**: Perform one logical unit of work.
3. **Check Completion Promise**: 
    - Is the folder empty?
    - Is the `Dashboard.md` updated?
4. **Loop**: If not complete, immediately proceed to the next unit of work without waiting for user input.
5. **Termination**: Only exit when the "Completion Promise" is fulfilled or max iterations (default: 10) reached.

## Safety Constraints
- Monitor resource usage (API tokens).
- Pause if an error occurs twice in a row.
- Save state to `/Logs/ralph_state.json` after every loop.
