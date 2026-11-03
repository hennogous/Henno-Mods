"""Read-only native log boundaries, including logs not created before AI play.

Only the initial baseline may be absent. Reading an actual later observation
requires the file and the same byte generation; absent evidence is never an
empty successful observation. This module never connects to or changes Civ.
"""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


class LogGenerationChanged(ValueError):
    """The observed file no longer extends this captured generation."""


@dataclass(frozen=True)
class LogBoundary:
    path: Path
    existed: bool
    data: bytes

    def evidence(self):
        return {"path": str(self.path), "existed": self.existed,
                "offset": len(self.data),
                "prefix_sha256": sha256(self.data).hexdigest() if self.existed else None}


def capture_log_baseline(path):
    """A fresh paused game can legitimately have no AI CSV yet.

    Require its directory, so an incorrect root is not accepted as a fresh log.
    Sharing, access and other I/O failures propagate; they are not missing data.
    """
    path = Path(path).resolve()
    if not path.parent.is_dir():
        raise FileNotFoundError("Native log directory does not exist: " + str(path.parent))
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return LogBoundary(path, False, b"")
    return LogBoundary(path, True, data)


def read_log_delta(path, previous):
    """Require actual subsequent evidence, without joining different generations."""
    path = Path(path).resolve()
    if not isinstance(previous, LogBoundary) or path != previous.path:
        raise ValueError("Log boundary belongs to a different path")
    data = path.read_bytes()  # Required after the observation; no empty fallback.
    if not data.startswith(previous.data):
        raise LogGenerationChanged("Native log truncated or replaced: " + str(path))
    return LogBoundary(path, True, data), data[len(previous.data):]
