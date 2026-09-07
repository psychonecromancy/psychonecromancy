"""Per-run manifest: tracks stage status/input-hash/output-path.

See docs/02-architecture.md, "Idempotency and resumability". A stage is
considered done, and skipped on the next invocation, only if its recorded
output still exists on disk and its recorded input hash still matches --
otherwise it needs to run (again).
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

MANIFEST_FILENAME = "manifest.json"

STAGE_ORDER = ["ground", "script", "images", "motion", "voice", "assemble"]


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "run"


def hash_input(data: Any) -> str:
    """Stable hash of arbitrary JSON-serializable stage input."""
    canonical = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass
class StageRecord:
    status: str  # "done" or "failed"
    input_hash: str
    output_path: str | None
    updated_at: str
    error: str | None = None


@dataclass
class Manifest:
    run_id: str
    input: str
    created_at: str
    run_dir: Path
    stages: dict[str, StageRecord] = field(default_factory=dict)

    @property
    def path(self) -> Path:
        return self.run_dir / MANIFEST_FILENAME

    @classmethod
    def create(cls, runs_root: Path, society_and_period: str) -> Manifest:
        """Start a new run under runs_root, with a fresh run-id directory."""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        run_id = f"{_slugify(society_and_period)}-{timestamp}"
        run_dir = runs_root / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        manifest = cls(
            run_id=run_id,
            input=society_and_period,
            created_at=timestamp,
            run_dir=run_dir,
        )
        manifest.save()
        return manifest

    @classmethod
    def load(cls, run_dir: Path) -> Manifest:
        """Load an existing run's manifest.json, to resume it."""
        data = json.loads((run_dir / MANIFEST_FILENAME).read_text())
        stages = {name: StageRecord(**record) for name, record in data["stages"].items()}
        return cls(
            run_id=data["run_id"],
            input=data["input"],
            created_at=data["created_at"],
            run_dir=run_dir,
            stages=stages,
        )

    def save(self) -> None:
        data = {
            "run_id": self.run_id,
            "input": self.input,
            "created_at": self.created_at,
            "stages": {name: asdict(record) for name, record in self.stages.items()},
        }
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True))

    def needs_run(self, stage: str, input_data: Any) -> bool:
        """Whether `stage` must (re-)run given its current input."""
        record = self.stages.get(stage)
        if record is None or record.status != "done":
            return True
        if record.input_hash != hash_input(input_data):
            return True
        if record.output_path and not (self.run_dir / record.output_path).exists():
            return True
        return False

    def record_done(self, stage: str, input_data: Any, output_path: str) -> None:
        self.stages[stage] = StageRecord(
            status="done",
            input_hash=hash_input(input_data),
            output_path=output_path,
            updated_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
        )
        self.save()

    def record_failed(self, stage: str, input_data: Any, error: str) -> None:
        self.stages[stage] = StageRecord(
            status="failed",
            input_hash=hash_input(input_data),
            output_path=None,
            updated_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            error=error,
        )
        self.save()
