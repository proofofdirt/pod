# Workflow: Grant Application Pipeline

## Trigger
Grant Hunter Agent identifies open grant round with POD eligibility.

## Step-by-step

1. **Grant Hunter** researches requirements, eligibility, deadline
2. **Grant Hunter** drafts application using narrative from `pod-grants/grants/[funder]/`
3. **Content Agent** reviews and edits narrative for clarity + impact
4. **Analytics Agent** provides impact metrics (plots verified, capital deployed, producer income delta)
5. **MENA IR Agent** reviews if application is relevant to Gulf funders
6. **Legal Agent** reviews any IP or licensing disclosures required
7. **Orchestrator** routes to human for final approval
8. **Grant Hunter** submits and tracks in `pod-grants/tracker.md`
