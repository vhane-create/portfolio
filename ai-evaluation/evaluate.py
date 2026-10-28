"""Transparent deterministic checks for synthetic AI golden examples.
Run: python ai-evaluation/evaluate.py
This checks reference fixture consistency, not LLM quality or human approval.
"""
import json
from pathlib import Path
P=Path(__file__).with_name("golden_dataset.json")
d=json.loads(P.read_text(encoding="utf-8"))
assert sum(d["rubric"].values())==100, "Rubric must total 100"
ids=set()
for task in d["tasks"]:
    assert task["id"] not in ids, "Duplicate task"
    ids.add(task["id"])
    assert task["prompt"] and task["golden"]
    for phrase in task["must_include"]:
        assert phrase.lower() in task["golden"].lower(), (task["id"],phrase)
    assert task["review_status"]=="reference_example_not_externally_reviewed"
print(f"PASS: {len(ids)} synthetic golden examples; rubric sums to 100")
