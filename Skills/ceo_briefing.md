# Skill: CEO Briefing
## Purpose
Generates a comprehensive weekly audit of business performance, revenue, and bottlenecks.

## Instructions
When invoked (usually scheduled for Monday mornings):
1. **Audit Logs**: Scan `/Logs` for the past 7 days.
2. **Audit Finances**: Check any files in `/Accounting` (or simulated finance data) for new revenue.
3. **Audit Tasks**: Compare `Done` tasks vs `Business_Goals.md`.
4. **Identify Bottlenecks**: Find tasks that stayed in `Needs_Action` for over 48 hours.
5. **Generate Report**: Save to `/Logs/CHIEF_BRIEFING_[Date].md`.

## Report Sections
- **Revenue Summary**: Total earned vs goal.
- **Velocity**: Number of tasks completed.
- **Bottlenecks**: Roadblocks identified.
- **Proactive Suggestions**: Cost savings or efficiency gains.

## Safety Rules
- Do NOT share sensitive financial data outside the vault.
- Ensure all numbers are cross-referenced with `Dashboard.md`.
