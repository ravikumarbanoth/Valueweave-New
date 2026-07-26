# ValueWeave.in

## Vision
ValueWeave is a Bharat-first startup collaboration platform.

Goal:
- Discover business opportunities
- Discover business ideas
- Find collaborators
- Build startup teams
- Enable district-level entrepreneurship

Current evolution:

ValueWeave is transitioning from:

"Find collaborators"

to

"Find what to build + find who to build it with"

## Tech Stack

Frontend:
- Next.js 14
- React
- Tailwind CSS

Deployment:
- Vercel

Repository Structure

frontend/
├── app/
├── components/
├── lib/
├── public/

## Current Modules

### Opportunities
Users can:
- Post opportunities
- Discover collaborators

### Idea Library
Users can:
- Browse business ideas
- View idea details
- Explore investment requirements
- View team roles
- Create opportunities from ideas

## Current Known Issues

1. Duplicate footer sections
   - Footer A contains:
     - Terms
     - Privacy Policy
     - Contact links

   - Footer B contains:
     - YouTube
     - Instagram
     - X/Twitter
     - Social links

Need:
- Single unified footer

2. Routing consistency review

3. Component duplication review

4. Build stability review

5. Mobile responsiveness review

6. Dead code detection

7. Unused components detection

8. Unused routes detection

## Design Constraints

IMPORTANT:

Do NOT redesign ValueWeave.

Preserve:
- Colors
- Typography
- Layout
- Branding
- Navigation

Improve architecture only.

## Desired Outcome

ValueWeave should become:

- Startup collaboration platform
- Business idea discovery platform
- District opportunity engine
- Future AI-powered entrepreneurship ecosystem# Here are your Instructions

---

## Knowledge Platform (v2.2)

Beyond the frontend, this repository holds the ValueWeave knowledge platform: eight
released data packages, a derived knowledge graph over them, and the infrastructure that
serves and governs both.

| Layer | Path | What it is |
|---|---|---|
| Packages | `packages/` | 8 released packages, 77 datasets, 2,299 rows, full provenance |
| Knowledge graph | `knowledge_graph/` | 647 entities, 865 relationships, derived from the packages (ADR-001) |
| Knowledge Engine | `knowledge_engine/` | Collect → parse → validate → provenance → build → version (VKE v0.1.0) |
| Query engine | `query_engine/` | Traversal library and five named business questions |
| **REST API** | `api/` | 10 read-only endpoints over the graph |
| **Search** | `search/` | Exact, prefix, alias and fuzzy search across 1,747 documents |
| **Stewardship** | `stewardship/` | Seven-state review lifecycle with an append-only ledger |
| Governance | `governance/` | 6 ADRs, ownership registry, data governance |
| Tests | `tests/` | 248 tests across 8 suites |

### Quick start

```bash
python3 -m api                          # REST API on 127.0.0.1:8000
python3 -m search.cli "turmeric"        # search the graph
python3 -m stewardship.cli status       # verification state
python3 knowledge_graph/validate_graph.py   # 11 integrity checks
python3 tests/run_all.py                # full test suite
```

### Documentation

| Document | Question it answers |
|---|---|
| [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) | What can I call, and what comes back? |
| [`docs/SEARCH_GUIDE.md`](docs/SEARCH_GUIDE.md) | How does matching work, and how do I turn approximation off? |
| [`docs/KNOWLEDGE_ENGINE.md`](docs/KNOWLEDGE_ENGINE.md) | What is the engine, and is it compatible? |
| [`docs/OWNERSHIP_FINAL.md`](docs/OWNERSHIP_FINAL.md) | Who owns which entity type, and how is that enforced? |
| [`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md) | What changed in v2.2, and what must I do? |
| [`docs/TESTING_GUIDE.md`](docs/TESTING_GUIDE.md) | How do I run and extend the tests? |
| [`audit/reports/EXECUTIVE_SUMMARY.md`](audit/reports/EXECUTIVE_SUMMARY.md) | Where does the platform actually stand? |

### The one thing to know before using this data

**Zero of 2,299 rows have been reviewed by a human.** Every row is `VST-NEEDS_REVIEW`.
Confidence scores estimate the strength of a source, not the correctness of a fact. The
API returns that warning on every single response, and it is computed from the data, so
it will disappear on its own when it stops being true.
