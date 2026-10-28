# AI Evaluation & Prompt Engineering Lab

**Portfolio project by Vannetta Haney** — finance-specific prompts, golden reference answers, failure-mode analysis, and rubric design. All examples are synthetic.

## Purpose
Show the skills used in AI-assisted finance workflows: specifying a task, defining a verifiable reference answer (often called a *golden*), identifying hallucinations or arithmetic failures, and establishing a human review process.

## Contents
- `golden_dataset.json` — four synthetic FP&A tasks with prompts, reference answers, required facts, and common failure modes.
- `evaluate.py` — dependency-free dataset consistency checks.
- `rubric.md` — weighted evaluation criteria and manual scoring procedure.

## Run
```bash
python ai-evaluation/evaluate.py
```

## Evaluation process
1. Freeze a test prompt and inputs.
2. Obtain candidate model output (not included; no model comparison has yet been performed).
3. Have a qualified reviewer verify calculations and grounding against supplied data.
4. Score each rubric category, record the evidence, and identify failures.
5. Revise prompts and rerun on a held-out test set.
6. Track false positives, false negatives, and reviewer agreement before making reliability claims.

**Important:** These are authored *reference examples*, not independently approved gold standards. The script verifies fixture integrity only; it does **not** grade a model, certify an answer, or prove production AI performance. No proprietary Mercor tasks, customer data, or confidential materials are included.
