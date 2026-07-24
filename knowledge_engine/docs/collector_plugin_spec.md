# Collector & Parser Plugin Specification

Covers modules 1 (Collector Engine, `collectors/`) and 2 (Parser Engine, `parsers/`) together, since
they share one design principle: a Collector fetches, a Parser interprets, and neither depends on the
other's implementation — any Parser can consume payloads from any Collector that produces a
compatible payload shape.

## 1. The Collector Interface

Every collector implements `collectors.base.BaseCollector`:

```python
class BaseCollector(ABC):
    name: str        # registered name, e.g. "csv_collector"
    version: str     # semantic version of this collector implementation

    @abstractmethod
    def fetch(self, source: str, **kwargs: Any) -> FetchResult: ...

    def supports(self, source: str) -> bool: ...   # optional auto-detection hint
```

### Contract

- `fetch()` must **never raise** for expected failure modes (network error, missing file, HTTP
  4xx/5xx). It must catch them and return a `FetchResult(status="error", error=<message>)`. This lets
  a caller run a batch of collector calls and get a full report of what succeeded/failed rather than
  aborting on the first failure.
- `fetch()` must **not interpret** the payload. A CSV collector returns the raw text; it does not
  parse rows. Interpretation is the Parser Engine's job — this separation is what lets a `JSONParser`
  serve payloads from a local-file `JSONCollector` today and, say, an S3-backed collector added later
  without any change to `JSONParser`.
- `fetch()` must **not call any AI model**. If a source cannot be fetched without AI-assisted
  interpretation to know what to ask for, it doesn't belong in this interface — see
  `ai_integration_plan.md`.
- `supports(source)` defaults to `False` (never auto-selected). Override it only when a source string
  unambiguously identifies your collector (e.g. `CSVCollector.supports` checks for a `.csv`
  extension). `CollectorRegistry.autodetect()` raises if zero or more than one collector claims
  support for a given source, rather than guessing.

### FetchResult

```python
@dataclass
class FetchResult:
    payload: Any                  # raw payload; shape depends on the collector
    source_url: str
    collector_name: str
    collector_version: str
    fetched_at: datetime
    status: str                   # "ok" | "error"
    error: Optional[str]
    metadata: dict[str, Any]      # collector-specific extras (HTTP status, file size, etc.)
```

`FetchResult.collector_label` (`"{name}/{version}"`) is what a caller passes as
`ProvenanceRecord.collector` — see `provenance_spec.md`.

## 2. Built-In Collectors

| Collector | Source types | Payload type | Auto-detected by |
|---|---|---|---|
| `CSVCollector` | local file or http(s) URL | `str` (decoded text) | `.csv` extension |
| `JSONCollector` | local file or http(s) URL | `str` (decoded text) | `.json` extension |
| `XMLCollector` | local file or http(s) URL | `str` (decoded text) | `.xml` extension |
| `RSSCollector` | local file or http(s) URL | `str` (decoded text) | `.rss`/`.atom` extension, or "rss"/"feed" in the URL |
| `APICollector` | http(s) URL | decoded JSON (`dict`/`list`), with optional multi-page collection | never (must be requested by name — pagination/auth needs are API-specific) |

All five are stdlib-only (`urllib.request`, `csv`, `json`, `xml.etree.ElementTree`) — no third-party
HTTP or parsing library is required to run this foundation.

## 3. Adding a New Collector Plugin

1. Subclass `BaseCollector`, set `name` and `version`, implement `fetch()`.
2. Register it: `default_registry.register(MyCollector())`, or use a private
   `CollectorRegistry()` in a test to avoid polluting the process-wide default.
3. Nothing else changes — no other module imports collectors by class name; everything goes through
   `CollectorRegistry.get(name)` or `.autodetect(source)`.

Planned future collectors (not implemented in this release, see `ROADMAP.md`): an S3/blob-storage
collector, a database-query collector, and the AI-assisted PDF/news/webpage collectors described in
`ai_integration_plan.md`.

## 4. The Parser Interface

Every parser implements `parsers.base.BaseParser`:

```python
class BaseParser(ABC):
    name: str
    version: str

    @abstractmethod
    def parse(self, payload: Any, **kwargs: Any) -> list[dict[str, Any]]: ...
```

### Contract

- `parse()` **must raise `ParseError`** (not return `[]`) when the payload cannot be interpreted at
  all — a caller needs to distinguish "parsed successfully, zero records" from "parsing failed."
- `parse()` returns flat `dict` records — no nested structures. A source with genuinely nested data
  (e.g. an API response with a list of objects, each containing a list of tags) should be flattened
  by the parser (join tags into a `"; "`-separated string, for example) or the caller should request
  a `records_path` that points at the already-flat level. Nested dicts should not be left as dict
  values, since every downstream module (Validation, Provenance, Package Builder) expects a flat
  record shape matching a package CSV row.
- `parse()` performs **no AI inference** and attaches **no provenance** — provenance is the
  Provenance Engine's job, applied after parsing (see `provenance_spec.md`).

## 5. Built-In Parsers

| Parser | Input shape | Notes |
|---|---|---|
| `CSVParser` | `str` | Uses `csv.DictReader`; raises `ParseError` if there's no header row. |
| `JSONParser` | `str`, `dict`, or `list` | Accepts already-decoded JSON (e.g. from `APICollector`). Auto-locates a single list-valued top-level key, or accepts an explicit `records_path` (dot-separated) to disambiguate. |
| `XMLParser` | `str` | Auto-detects the most common repeated child-element tag as the record boundary, or accepts an explicit `record_tag`. Flattens each record element's children into dict keys; attributes become `@`-prefixed keys. |
| `RSSParser` | `str` | Namespace-agnostic: finds `<item>` (RSS 2.0) or `<entry>` (Atom) elements regardless of default namespace. |
| `HTMLTableParser` | `str` | Stdlib `html.parser`-based; extracts one `<table>` (by index) using the first row as headers. Does not handle colspan/rowspan merging or nested tables — such pages are deferred to the AI-assisted extractor (see `ai_integration_plan.md`), not handled by growing this into a layout engine. |
| `PDFParser` | n/a | **Placeholder.** `parse()` raises `NotImplementedError` unconditionally. See `ai_integration_plan.md`. |

## 6. Testing Requirements for a New Collector/Parser

Every built-in collector and parser has a corresponding case in `tests/test_collectors_parsers.py`
covering: the happy path against a local fixture, at least one malformed-input case that raises the
expected error type, and (for collectors) the error-not-exception contract for a missing source.
A new plugin should follow the same pattern before being registered as a default.
