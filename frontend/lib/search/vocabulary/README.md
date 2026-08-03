# The multilingual vocabulary

`concepts.js` is the table that lets a student search in English, Telugu or Tanglish and
get the same answer. It is **data**. You do not need to understand the search engine to
add a term to it, and you should not have to read JavaScript to do so either — it is a
list of objects, one per concept, and the only punctuation that matters is the comma.

```bash
python3 tests/run_all.py --suite multilingual     # 22 checks over this file
```

---

## What a concept is

A thing a person can want. Not an entity, not a row in the graph — a *want*. "Electrician"
is a concept; the graph answers it with a skill, two business opportunities, a
certification and a training provider, and the student never needs to know that.

```js
{
  "id": "electrician",
  "en_canonical": "electrician",
  "en": ["electrical services", "wireman", "domestic wiring", "electrical contractor"],
  "te": ["ఎలక్ట్రిషియన్", "వైర్‌మ్యాన్", "విద్యుత్ పనులు", "కరెంట్ పని"],
  "tanglish": ["current pani"],
  "expands_to": ["electrical", "wiring", "wireman", "domestic wiring",
                 "power distribution", "electrical panel", "industrial electrician"]
}
```

| field | what goes in it |
|---|---|
| `id` | stable key, lower-case, hyphens. **Never rename or reuse one** — analytics and saved searches key on it. |
| `en_canonical` | what we say back to the reader, and the term the ranker is handed as though it had been typed. |
| `en` | English synonyms and trade names. |
| `te` | Telugu script. |
| `tanglish` | romanised Telugu that transliteration does **not** already produce. |
| `expands_to` | English terms to *also* search for. |

---

## Four rules, all of them enforced by a test

**1. Every `expands_to` term must reach something we actually hold.**
An expansion that matches no entity costs a query and returns silence — and it does it
invisibly, which is worse. `test_every_expansion_reaches_a_live_entity` fails the build.
A term counts as reachable if it matches an entity *name* or an entity *type*: no row is
called "government scheme", but that is the humanised `GovernmentScheme` type and
matching it returns all forty.

**2. Do not add a Tanglish spelling that transliteration already gives you.**
`రైతు` transliterates to `raitu` automatically, so `"tanglish": ["raitu"]` is a second
place to maintain the same fact. Sixty-seven such rows were written and deleted in the
first draft of this file. `tanglish` is for words transliteration cannot reach —
`paala parishrama` (milk industry, where the Telugu we hold is `పాడి పరిశ్రమ`),
`current pani`, `mestri`.

Nor do you need to enumerate misspellings. `elektrishian`, `electrishan` and
`elektrisian` all reduce to the same consonant skeleton as `electrician` and are handled
without a row.

**3. `te` must be Telugu script.** A Latin string in that column will never be reached
that way and misleads the next person about what the column is for.

**4. No two concepts may share a phonetic key.** A collision silently disables one
concept's Tanglish path. `raitu` (farmer) and `rayiti` (subsidy) both reduce to `rt`,
which is why the skeleton has a minimum length — but if the test tells you two concepts
clash, one of them needs a different word, not a wider net.

---

## What must NOT go in here

**Proper nouns spelled the same in both scripts.** Districts especially. `మెదక్`
transliterates to `medak` by a character pass, so all 61 districts work with no rows at
all — and a row per district is 61 places for the sixty-second to be forgotten. There is
a test (`test_the_district_is_not_in_the_concept_table`) whose only job is to fail if
somebody "fixes" Telugu districts by adding data, because that would mean transliteration
has quietly stopped working and nobody noticed.

**Anything you have not checked.** This is a search convenience, not research, so it does
not carry the provenance rules a package dataset does — but a wrong Telugu spelling is a
term that silently never fires, and the test suite cannot tell you that a word is wrong,
only that it is unreachable.

---

## Adding a term

1. Add or edit the concept in `concepts.js`.
2. `python3 tests/run_all.py --suite multilingual`
3. If `expands_to` fails, we do not hold what you are pointing at. Point at something we
   do hold, or leave the concept out and let the no-results guide offer to research it —
   an honest gap beats a search that appears to work and returns nothing.

## Where it is used

`lib/search/multilingual.js` builds three indexes from this file at module load — by
alias, by phonetic key, by id — and `lib/search-vocabulary.js` merges the result into
`expandQuery`. Nothing downstream of `expandQuery` knows there is more than one language.
The ranking ladder, the typo budget, the acronym table and the diversify pass are all
exactly what they were.
