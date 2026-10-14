"""Freeze a read-only MAB runtime DB and its CSC rule inventory before migration."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(args.database.resolve().as_uri() + "?mode=ro", uri=True)
    source.row_factory = sqlite3.Row
    snapshot = args.output / "mab-DebugGameplay.sqlite"
    with sqlite3.connect(snapshot) as destination:
        source.backup(destination)
    rules = [dict(r) for r in source.execute(
        "SELECT * FROM Ruivo_New_Adjacency WHERE ID LIKE 'CSC_%' ORDER BY ID")]
    fixture = {
        "referenceCommit": "d852b8466cf7152f4fd76cacec5fa8c2084d7c0a",
        "databaseSha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        "databaseTimestamp": args.database.stat().st_mtime,
        "evidence": "Cached gameplay database; NOT a captured gameplay or UI parity result.",
        "rules": rules,
    }
    args.fixture.parent.mkdir(parents=True, exist_ok=True)
    args.fixture.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    print(f"Captured {len(rules)} CSC rules; snapshot: {snapshot}")
    print("Source kinds:", sorted({r["AdjacencyType"] for r in rules}))
    print("Modifier-owner scopes:", sorted({(r["ModifierOwner"], r["CollectionType"]) for r in rules}))


if __name__ == "__main__":
    main()
