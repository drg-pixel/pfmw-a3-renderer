# PFMW A.3 JSON Generation Prompt

Use this prompt before running the renderer when starting from raw subjective text.

```text
Convert the following case into PFMW A.3 renderer JSON only.
Do not write markdown.
Do not add commentary.
Return valid JSON matching sample_case.json exactly.

Rules:
- One primary complaint leads.
- One primary marker leads.
- One lead card/lane.
- Page 1 matrix must include exactly these phase keys:
  - TODAY / RUN
  - NEXT / WHEN STABLE
  - FUTURE / BUILD CAPACITY
- Each phase must include exactly B1 through B7.
- Each B-cell must include exactly: do, dose, test, rule.
- Keep every cell short. The renderer will trim long text.
- B7 must contain HEP / ChiroUp exercises for each phase.
- HEP 1-3 exercises max.
- No ChiroUp IDs unless specifically requested.
- Safety first.
- Progress calm -> motion/control -> capacity -> exposure -> independence.

CASE INPUT:
[paste case]
```

Then save the JSON as `case.json` and run:

```bash
python render_a3.py case.json --out output/PFMW_A3_Output.pdf
```
