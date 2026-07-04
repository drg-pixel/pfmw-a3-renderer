# PFMW A.3 Coded Renderer - Option 1

This is the locked practical renderer for the PFMW A.3 Large-Font Matrix Cockpit.

## What is locked

Page 1 is hard-coded as a true 3 x 7 matrix:

Rows:
1. TODAY / RUN
2. NEXT / WHEN STABLE
3. FUTURE / BUILD CAPACITY

Columns:
- B1 Unload / Calm
- B2 Soft Tissue Doorway
- B3 Joint / Mobility / Adjustment
- B4 Motor Control Reset
- B5 Capacity / Loading
- B6 Education / Exposure
- B7 HEP / ChiroUp

The renderer validates that every phase and every B1-B7 cell exists before creating the PDF. If a row, column, or cell field is missing, it fails instead of making a different layout.

## Usage

```bash
pip install -r requirements.txt
python render_a3.py sample_case.json --out output/PFMW_A3_Output.pdf
```

Optional:

```bash
python render_a3.py sample_case.json --out output/PFMW_A3_Output.pdf --keep-html
```

## Input contract

The input is a JSON file with:

- case header fields
- `matrix` object with exactly the 3 phase rows and 7 B-columns
- every cell contains:
  - `do`
  - `dose`
  - `test`
  - `rule`
- page 2 protocol sections
- page 3 clinician upgrade sections

## Current limitation

This renderer locks the PDF layout. It does not automatically read raw subjective text by itself. The AI still needs to convert the case into `sample_case.json`-style structured content, then this renderer produces the locked PDF.

## Practical workflow inside ChatGPT

1. Paste case.
2. ChatGPT creates structured A.3 JSON.
3. Run this renderer.
4. Return PDF + page previews.

## Validation built into renderer

The renderer checks that the matrix has all required rows, all B1-B7 columns, and every DO/DOSE/TEST/RULE field. This prevents the common failure where Page 1 turns into a summary table instead of the locked matrix.
