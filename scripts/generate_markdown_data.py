#!/usr/bin/env python3
"""Convert ABSP.xlsx antibiogram workbook into Markdown tables with metadata."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Dict, List, Optional

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "ABSP.xlsx"
OUTPUT_DIR = ROOT / "data" / "2024"
INDEX_FILE = ROOT / "data" / "index.json"

SITE_META: Dict[str, Dict[str, str]] = {
    "NMH": {
        "site_id": "nmh",
        "site": "NMH",
        "region": "Northwestern Memorial Hospital",
        "display": "Northwestern Memorial Hospital (NMH)",
    },
    "LFH": {
        "site_id": "lfh",
        "site": "LFH",
        "region": "Lake Forest Hospital",
        "display": "Lake Forest Hospital (LFH)",
    },
    "Marianjoy": {
        "site_id": "marianjoy",
        "site": "Marianjoy",
        "region": "Marianjoy Rehabilitation Hospital",
        "display": "Marianjoy Rehabilitation Hospital",
    },
    "Northwest Region": {
        "site_id": "northwest-region",
        "site": "Huntley/McHenry/Woodstock Hospitals",
        "region": "Northwest Region",
        "display": "Northwest Region (Huntley/McHenry/Woodstock Hospitals)",
    },
    "Palos": {
        "site_id": "palos",
        "site": "Palos Hospital",
        "region": "Palos Hospital",
        "display": "Palos Hospital",
    },
    "CDH": {
        "site_id": "cdh",
        "site": "Central DuPage Hospital (CDH)",
        "region": "West Region",
        "display": "West Region (Central DuPage Hospital)",
    },
    "DCH": {
        "site_id": "dch",
        "site": "Delnor Hospital (DCH)",
        "region": "West Region",
        "display": "West Region (Delnor Hospital)",
    },
    "KH/VW": {
        "site_id": "khvw",
        "site": "Kishwaukee/Valley West Hospitals (KH/VW)",
        "region": "West Region",
        "display": "West Region (Kishwaukee/Valley West Hospitals)",
    },
}

CONTEXT_MAP = {
    "Facility-Wide": "Facility-Wide",
    "Blood-specific": "Blood",
    "Blood": "Blood",
    "Emergency Dept": "ED",
    "ED": "ED",
    "Urine": "Urine",
    "Urinary": "Urine",
    "Respiratory": "Respiratory",
    "Medical ICU": "MICU",
    "Other ICU": "Other ICU",
    "Immunocompromised Host": "Immunocompromised Host",
}

CONTEXT_LABELS = {
    "Facility-Wide": "Facility-Wide",
    "Blood": "Blood",
    "ED": "Emergency Department",
    "Urine": "Urine",
    "Respiratory": "Respiratory",
    "MICU": "Medical ICU",
    "Other ICU": "Other ICU",
    "Immunocompromised Host": "Immunocompromised Host",
}


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def extract_site_key(header: str) -> str:
    normalized = header.replace("*", "").strip()
    for key in SITE_META:
        if normalized.startswith(key):
            return key
    raise ValueError(f"Unrecognised site header: {header!r}")


def extract_year(header: str) -> Optional[int]:
    match = re.search(r"(20\d{2})", header)
    return int(match.group(1)) if match else None


def clean_header_cell(cell: Optional[str]) -> str:
    if cell is None:
        return ""
    return str(cell).replace("\n", " ").strip()


def combine_notes(lines: List[str]) -> List[str]:
    notes: List[str] = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        if notes and not text.startswith("*"):
            notes[-1] = f"{notes[-1]} {text}".strip()
        else:
            notes.append(text)
    return notes


def iter_contexts(sheet):
    current = None
    for row in sheet.iter_rows(values_only=True):
        first = row[0]
        if first and "Antibiogram" in str(first):
            if current:
                yield current
            header_text = str(first)
            site_key = extract_site_key(header_text)
            year = extract_year(header_text)
            lines = [part.strip() for part in header_text.split("\n") if part and part.strip()]
            context_line = next((ln for ln in lines[1:] if "Antibiogram" in ln), None)
            if not context_line:
                raise ValueError(f"Missing context line in header: {header_text!r}")
            base_context = context_line.replace("Antibiogram", "").replace("*", "").strip()
            canonical_context = CONTEXT_MAP.get(base_context)
            if not canonical_context:
                raise ValueError(f"Unknown context label: {base_context!r}")
            display_context = CONTEXT_LABELS.get(canonical_context, canonical_context)
            note_lines = [ln for ln in lines[1:] if ln != context_line]
            notes = combine_notes(note_lines)
            header_cells = list(row)
            last_idx = len(header_cells) - 1
            while last_idx > 0 and (header_cells[last_idx] is None or str(header_cells[last_idx]).strip() == ""):
                last_idx -= 1
            columns = ["Organism"] + [clean_header_cell(cell) for cell in header_cells[1:last_idx + 1]]
            current = {
                "site_key": site_key,
                "year": year,
                "context": canonical_context,
                "context_label": display_context,
                "notes": notes,
                "columns": columns,
                "rows": [],
            }
        elif current is not None:
            row_values = list(row[: len(current["columns"])])
            if len(row_values) < len(current["columns"]):
                row_values.extend([None] * (len(current["columns"]) - len(row_values)))
            current["rows"].append(row_values)
    if current:
        yield current


def format_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isclose(value, round(value)):
            return f"{value:.1f}".rstrip("0").rstrip(".")
        return str(int(round(value)))
    text = str(value).strip()
    return text


def render_markdown(meta: Dict[str, object], columns: List[str], rows: List[List[object]]) -> str:
    header_line = "| " + " | ".join(columns) + " |"
    separator_line = "| " + " | ".join(["---"] * len(columns)) + " |"
    body_lines = [
        "| " + " | ".join(format_cell(cell) for cell in row) + " |"
        for row in rows
    ]
    front_matter = json.dumps(meta, indent=2, ensure_ascii=False)
    parts = ["---", front_matter, "---", "", header_line, separator_line]
    parts.extend(body_lines)
    parts.append("")
    return "\n".join(parts)


def main() -> None:
    if not WORKBOOK.exists():
        raise SystemExit(f"Workbook not found: {WORKBOOK}")
    wb = load_workbook(WORKBOOK, data_only=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    index_entries: List[Dict[str, object]] = []
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        for ctx in iter_contexts(sheet):
            site_info = SITE_META.get(ctx["site_key"])
            if not site_info:
                raise ValueError(f"Missing site metadata for key {ctx['site_key']!r}")
            data_rows: List[List[object]] = []
            for row in ctx["rows"]:
                first = row[0]
                if first is None or str(first).strip() == "":
                    continue
                remaining = row[1:]
                if all((cell is None or str(cell).strip() == "") for cell in remaining):
                    continue
                formatted = [format_cell(cell) for cell in row[: len(ctx["columns"])] ]
                # Ensure row length matches columns
                if len(formatted) < len(ctx["columns"]):
                    formatted.extend([""] * (len(ctx["columns"]) - len(formatted)))
                data_rows.append(formatted)
            if not data_rows:
                continue
            meta = {
                "site_id": site_info["site_id"],
                "site": site_info["site"],
                "region": site_info["region"],
                "display": site_info["display"],
                "year": ctx["year"],
                "context": ctx["context"],
                "context_label": ctx["context_label"],
                "notes": ctx["notes"],
                "flags": [],
            }
            site_dir = OUTPUT_DIR / site_info["site_id"]
            site_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{slugify(ctx['context'])}.md"
            output_path = site_dir / filename
            markdown = render_markdown(meta, ctx["columns"], data_rows)
            output_path.write_text(markdown, encoding="utf-8")
            rel_path = output_path.relative_to(ROOT).as_posix()
            index_entries.append(
                {
                    "path": rel_path,
                    "site_id": site_info["site_id"],
                    "context": ctx["context"],
                    "year": ctx["year"],
                }
            )
    index_entries.sort(key=lambda entry: (entry["site_id"], entry["context"]))
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(index_entries, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
