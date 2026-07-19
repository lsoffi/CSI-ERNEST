from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from pdf_builder import build_student_pdf, build_teacher_pdf
from templates import normalize_case


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output"
DEFAULT_LOGO = ROOT / "assets" / "ERNEST-logo.svg"


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "case"


def load_cases(input_path: Path) -> list[dict[str, str]]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() == ".json":
        with input_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            data = data.get("cases", [])
        if not isinstance(data, list):
            raise ValueError("JSON input must be a list of case objects or an object with a 'cases' list.")
        return [normalize_case(item) for item in data]
    if input_path.suffix.lower() == ".csv":
        with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [normalize_case(row) for row in csv.DictReader(handle)]
    raise ValueError("Input must be a .csv or .json file.")


def combine_pdfs(paths: list[Path], output_path: Path) -> None:
    try:
        from pypdf import PdfWriter
    except Exception as exc:
        raise RuntimeError("Install pypdf to use --combined: pip install pypdf") from exc
    writer = PdfWriter()
    for path in paths:
        writer.append(str(path))
    with output_path.open("wb") as handle:
        writer.write(handle)


def generate(input_path: Path, output_dir: Path, combined: bool, logo_path: Path | None) -> None:
    cases = load_cases(input_path)
    if not cases:
        raise ValueError(f"No cases found in {input_path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    student_paths: list[Path] = []
    teacher_paths: list[Path] = []
    for case in cases:
        stem = f"{slugify(case['case_id'])}-{slugify(case['title'])}"
        student_path = output_dir / f"{stem}-student.pdf"
        teacher_path = output_dir / f"{stem}-teacher-guide.pdf"
        build_student_pdf(case, student_path, logo_path)
        build_teacher_pdf(case, teacher_path, logo_path)
        student_paths.append(student_path)
        teacher_paths.append(teacher_path)
        print(f"Generated {student_path}")
        print(f"Generated {teacher_path}")
    if combined:
        combine_pdfs(student_paths, output_dir / "combined-student-case-files.pdf")
        combine_pdfs(teacher_paths, output_dir / "combined-teacher-guides.pdf")
        print(f"Generated {output_dir / 'combined-student-case-files.pdf'}")
        print(f"Generated {output_dir / 'combined-teacher-guides.pdf'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera fascicoli ERNEST-CSI in PDF.")
    parser.add_argument("--input", "-i", default=str(ROOT / "data" / "cases.csv"), help="CSV or JSON case database.")
    parser.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT), help="Output folder.")
    parser.add_argument("--combined", action="store_true", help="Also create combined student and teacher PDFs.")
    parser.add_argument("--logo", default=str(DEFAULT_LOGO), help="Percorso del logo ERNEST. Usa una stringa vuota per disabilitarlo.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logo_path = Path(args.logo).resolve() if args.logo else None
    if logo_path and not logo_path.exists():
        logo_path = None
    generate(Path(args.input).resolve(), Path(args.output).resolve(), args.combined, logo_path)


if __name__ == "__main__":
    main()
