"""Synthetic reference CLI, NOT a device adapter or validated application."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def make_synthetic_event() -> dict:
    """Return one deterministic record for testing the export contract."""
    return {
        "schema_version": 1,
        "event_id": "synthetic-cli-001",
        "session_id": "synthetic-session",
        "timestamp_utc": "1970-01-01T00:00:00Z",
        "source": "reference_cli",
        "event_type": "synthetic_event",
        "quality": "synthetic",
        "equipment_id": None,
        "payload": {"value": 0, "units": "arbitrary"},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(make_synthetic_event(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"SYNTHETIC_EVENT_WRITTEN: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
