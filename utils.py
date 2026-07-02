"""Pomocné funkce pro CSV, čísla a datumy."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable

DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y.%m.%d %H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%m/%d/%Y %I:%M %p",
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
    "%d.%m.%Y",
)


def parse_float(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip().replace(" ", "")
    if not text:
        return default
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    else:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return default


def parse_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def read_semicolon_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle, delimiter=";"))
    except PermissionError as exc:
        raise PermissionError("Soubor je pravděpodobně otevřený v Excelu") from exc


def write_semicolon_csv(path: Path, fieldnames: Iterable[str], rows: Iterable[dict[str, object]]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(fieldnames), delimiter=";", extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
    except PermissionError as exc:
        raise PermissionError("Soubor je pravděpodobně otevřený v Excelu") from exc


def fmt_pct(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:+.2f} %"
