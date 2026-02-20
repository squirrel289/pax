# Skill Wording Bakeoff (A/B)

- Run ID: `2026-02-20-skill-wording-ab`
- Scenario source: `/tmp/skill_option_empirical_scenarios.json`

## Variant Summary

| Variant | Completion Rate | Avg Top Score | Avg Top Coverage | Autonomy Blocked Scenarios |
|---|---:|---:|---:|---|
| pre_edit_head | 0.667 | 82.22 | 1.0 | S2_confirmation_missing |
| post_edit_worktree | 1.000 | 82.97 | 1.0 | - |

## Scenario Comparison

| Scenario | Result |
|---|---|
| S1_normal_confirmed | same_top=True same_action=True delta=0.0 |
| S2_confirmation_missing | pre=`failed` post=`ok` |
| S3_forced_tie | same_top=True same_action=True delta=0.0 |
