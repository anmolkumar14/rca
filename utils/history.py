import csv
import json
import re
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_FILE = DATA_DIR / "incident_history.json"
INCIDENTS_FILE = DATA_DIR / "incidents.json"
EXPORT_FILE = DATA_DIR / "incidents_export.csv"


def ensure_history_file(path=HISTORY_FILE):
    DATA_DIR.mkdir(exist_ok=True)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")


def ensure_incidents_file(path=INCIDENTS_FILE):
    DATA_DIR.mkdir(exist_ok=True)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")


def _parse_mttr(timeline):
    pattern = r"(\d{1,2}:\d{2}(?::\d{2})?)"
    matches = re.findall(pattern, timeline)
    if len(matches) >= 2:
        try:
            start = datetime.strptime(matches[0], "%H:%M")
            end = datetime.strptime(matches[-1], "%H:%M")
            if end < start:
                end = end.replace(day=end.day + 1)
            return int((end - start).total_seconds() // 60)
        except ValueError:
            return None
    return None


def _normalize_incident(item):
    created_at = item.get("created_at") or datetime.utcnow().isoformat() + "Z"
    mttr_minutes = item.get("mttr_minutes")
    if mttr_minutes is None:
        mttr_minutes = _parse_mttr(item.get("timeline", ""))

    return {
        "id": item.get("id", f"inc-{len(str(created_at))}"),
        "title": item.get("title", "Untitled Incident"),
        "severity": item.get("severity", "P2"),
        "systems": item.get("systems", "Unknown"),
        "style": item.get("style", "Blameless"),
        "summary": item.get("summary", ""),
        "description": item.get("description", ""),
        "timeline": item.get("timeline", ""),
        "root_cause": item.get("root_cause", ""),
        "fix_applied": item.get("fix_applied", ""),
        "created_at": created_at,
        "mttr_minutes": mttr_minutes,
    }


def load_history(limit=10):
    return load_incidents(limit=limit)


def load_incidents(query=None, limit=None):
    ensure_incidents_file()
    with INCIDENTS_FILE.open("r", encoding="utf-8") as handle:
        items = json.load(handle)

    normalized = [_normalize_incident(item) for item in items]
    if query:
        query_lower = query.lower()
        normalized = [
            item for item in normalized
            if query_lower in " ".join([
                item.get("title", ""),
                item.get("severity", ""),
                item.get("systems", ""),
                item.get("style", ""),
                item.get("summary", ""),
                item.get("description", ""),
            ]).lower()
        ]

    normalized.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    if limit:
        normalized = normalized[:limit]
    return normalized


def save_history(entry):
    ensure_history_file()
    ensure_incidents_file()

    timestamp = datetime.utcnow().isoformat() + "Z"
    incident = {
        "id": entry.get("id") or f"inc-{int(datetime.utcnow().timestamp())}",
        "title": entry.get("title", "Untitled Incident"),
        "severity": entry.get("severity", "P2"),
        "systems": entry.get("systems", "Unknown"),
        "style": entry.get("style", "Blameless"),
        "summary": entry.get("summary", ""),
        "description": entry.get("description", ""),
        "timeline": entry.get("timeline", ""),
        "root_cause": entry.get("root_cause", ""),
        "fix_applied": entry.get("fix_applied", ""),
        "created_at": timestamp,
        "mttr_minutes": entry.get("mttr_minutes") or _parse_mttr(entry.get("timeline", "")),
    }

    with HISTORY_FILE.open("r", encoding="utf-8") as handle:
        history_items = json.load(handle)
    history_items.append(incident)
    with HISTORY_FILE.open("w", encoding="utf-8") as handle:
        json.dump(history_items, handle, indent=2)

    with INCIDENTS_FILE.open("r", encoding="utf-8") as handle:
        incidents = json.load(handle)
    incidents.append(incident)
    with INCIDENTS_FILE.open("w", encoding="utf-8") as handle:
        json.dump(incidents, handle, indent=2)

    return incident


def compute_history_stats(incidents=None):
    incidents = incidents or load_incidents()
    now = datetime.utcnow()
    this_month = sum(1 for item in incidents if _incident_month(item) == (now.year, now.month))

    mttr_values = [item.get("mttr_minutes") for item in incidents if item.get("mttr_minutes") is not None]
    avg_mttr = round(sum(mttr_values) / len(mttr_values), 1) if mttr_values else 0

    p1_count = sum(1 for item in incidents if str(item.get("severity", "")).upper() == "P1")
    p2_count = sum(1 for item in incidents if str(item.get("severity", "")).upper() == "P2")

    return {
        "total_incidents": len(incidents),
        "this_month": this_month,
        "average_mttr": avg_mttr,
        "p1_count": p1_count,
        "p2_count": p2_count,
    }


def _incident_month(item):
    stamp = item.get("created_at")
    if not stamp:
        return None
    try:
        dt = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone().replace(tzinfo=None)
        return dt.year, dt.month
    except ValueError:
        return None


def export_history_csv(output_path=None):
    ensure_incidents_file()
    incidents = load_incidents()
    export_path = Path(output_path) if output_path else EXPORT_FILE
    export_path.parent.mkdir(exist_ok=True)

    with export_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["ID", "Title", "Severity", "Systems", "Style", "MTTR (min)", "Created At", "Summary"])
        for item in incidents:
            writer.writerow([
                item.get("id", ""),
                item.get("title", ""),
                item.get("severity", ""),
                item.get("systems", ""),
                item.get("style", ""),
                item.get("mttr_minutes", ""),
                item.get("created_at", ""),
                item.get("summary", ""),
            ])

    return str(export_path)
