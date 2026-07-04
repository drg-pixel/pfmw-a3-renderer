#!/usr/bin/env python3
"""
PFMW A.3 coded renderer - Option 1
Fixed 3-page PDF renderer with locked Page 1 B1-B7 matrix.

Usage:
  python render_a3.py sample_case.json --out output/PFMW_A3_Output.pdf
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

PHASES = ["TODAY / RUN", "NEXT / WHEN STABLE", "FUTURE / BUILD CAPACITY"]
BLOCK_IDS = ["B1", "B2", "B3", "B4", "B5", "B6", "B7"]
BLOCKS = [
    "B1\nUnload / Calm",
    "B2\nSoft Tissue Doorway",
    "B3\nJoint / Mobility / Adj",
    "B4\nMotor Control Reset",
    "B5\nCapacity / Loading",
    "B6\nEducation / Exposure",
    "B7\nHEP / ChiroUp",
]
REQUIRED_CELL_KEYS = ["do", "dose", "test", "rule"]
MAX_CHARS = {
    "do": 55,
    "dose": 50,
    "test": 45,
    "rule": 55,
}


def _shorten(text: Any, limit: int) -> str:
    s = "" if text is None else str(text)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= limit:
        return s
    cut = s[: max(0, limit - 1)].rsplit(" ", 1)[0]
    return (cut or s[: limit - 1]).rstrip() + "..."


def _html_list(items: List[str]) -> str:
    if not items:
        return ""
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def validate_case(data: Dict[str, Any]) -> None:
    errors: List[str] = []
    matrix = data.get("matrix")
    if not isinstance(matrix, dict):
        errors.append("Missing matrix object")
    else:
        for p in PHASES:
            if p not in matrix:
                errors.append(f"Missing phase row: {p}")
                continue
            row = matrix[p]
            for b in BLOCK_IDS:
                if b not in row:
                    errors.append(f"Missing block {b} in phase {p}")
                    continue
                cell = row[b]
                for k in REQUIRED_CELL_KEYS:
                    if k not in cell:
                        errors.append(f"Missing {k} in {p} {b}")
    if errors:
        raise ValueError("Invalid PFMW A.3 case JSON:\n- " + "\n- ".join(errors))


def normalize_case(raw: Dict[str, Any]) -> Dict[str, Any]:
    data = copy.deepcopy(raw)
    validate_case(data)
    phases = []
    for p in PHASES:
        cells = {}
        for b in BLOCK_IDS:
            cell = data["matrix"][p][b]
            cells[b] = {k: _shorten(cell.get(k, ""), MAX_CHARS[k]) for k in REQUIRED_CELL_KEYS}
        phases.append({"label": p.replace(" / ", " /\n"), "cells": cells})

    # Build HTML sections from simple lists if not supplied as html.
    def box(title: str, obj: Any) -> Dict[str, str]:
        if isinstance(obj, dict) and "html" in obj:
            return {"title": title, "html": str(obj["html"])}
        if isinstance(obj, list):
            return {"title": title, "html": _html_list([_shorten(x, 150) for x in obj])}
        return {"title": title, "html": f"<p>{_shorten(obj, 350)}</p>"}

    page2 = data.get("page2", {})
    page3 = data.get("page3", {})

    return {
        "title": data.get("title", "PFMW A.3 Large-Font Matrix Cockpit"),
        "subtitle": data.get("subtitle", "Doctor-facing, marker-driven clinical cockpit"),
        "primary_region": data.get("primary_region", ""),
        "main_marker": data.get("main_marker", ""),
        "lead_card": data.get("lead_card", ""),
        "secondary": data.get("secondary", ""),
        "safety": data.get("safety", ""),
        "blocks": BLOCKS,
        "block_ids": BLOCK_IDS,
        "phases": phases,
        "page1_note": data.get("page1_note", "One lane leads. Re-test the same marker. HEP stays 1-3 items."),
        "page2_subtitle": page2.get("subtitle", "Exact in-room protocol"),
        "page2_top_boxes": [
            box("Safety Gate", page2.get("safety_gate", [])),
            box("Primary Marker", page2.get("primary_marker", "")),
            box("HEP - Start Simple", page2.get("hep", [])),
        ],
        "protocol_rows": page2.get("protocol_rows", []),
        "page2_bottom_boxes": [
            box("Avoid Today", page2.get("avoid_today", [])),
            box("Secondary Handling", page2.get("secondary_handling", [])),
        ],
        "page3_subtitle": page3.get("subtitle", "What this case teaches"),
        "page3_top_boxes": [
            box("Expert Read", page3.get("expert_read", [])),
            box("Re-Test Logic", page3.get("retest_logic", [])),
        ],
        "lesson_rows": page3.get("lesson_rows", []),
        "patient_script": page3.get("patient_script", ""),
        "doctor_close": page3.get("doctor_close", ""),
        "clinical_bottom_line": page3.get("clinical_bottom_line", ""),
    }


def render(case_json: Path, out_pdf: Path, keep_html: bool = False) -> Path:
    root = Path(__file__).resolve().parent
    templates = root / "templates"
    env = Environment(loader=FileSystemLoader(str(templates)), autoescape=select_autoescape())
    tmpl = env.get_template("template_a3.html")
    raw = json.loads(case_json.read_text(encoding="utf-8"))
    data = normalize_case(raw)
    html = tmpl.render(**data)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    html_path = out_pdf.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    # Copy CSS next to HTML so relative link resolves for portable inspection.
    css_dst = out_pdf.parent / "style_a3.css"
    if not css_dst.exists():
        shutil.copy2(templates / "style_a3.css", css_dst)
    HTML(filename=str(html_path), base_url=str(out_pdf.parent)).write_pdf(str(out_pdf))
    if not keep_html:
        try:
            html_path.unlink()
        except OSError:
            pass
    return out_pdf


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("case_json", type=Path)
    ap.add_argument("--out", type=Path, default=Path("output/PFMW_A3_Output.pdf"))
    ap.add_argument("--keep-html", action="store_true")
    args = ap.parse_args()
    pdf = render(args.case_json, args.out, args.keep_html)
    print(pdf)


if __name__ == "__main__":
    main()
