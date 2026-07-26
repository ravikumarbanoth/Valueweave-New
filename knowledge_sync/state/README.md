# knowledge_sync/state

Runtime state. Everything here is generated; nothing is source.

| File | Written by | Committed |
|---|---|---|
| `manifest.json` | every successful sync | **no** — belongs to a deployment, not the repo |
| `snapshots/<run_id>.json` | every run, before applying | no |
| `sync_log.jsonl` | every run, append-only | no |

A missing manifest is not an error: change detection treats it as "nothing has
ever been synced", so the first run is a full insert. That is the correct
behaviour for a fresh environment.
