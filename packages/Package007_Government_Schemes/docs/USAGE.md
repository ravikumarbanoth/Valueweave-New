# Usage — Package007_Government_Schemes v1.0.0

Query recipes for the questions this package was built to answer, and the traps to avoid.

## Before you query: four rules

**1. Filter the sentinel, always.** `PENDING_VERIFICATION` occupies cells in otherwise-numeric
columns. Any cast or aggregate that does not exclude it will error or skew.

```sql
-- WRONG
SELECT AVG(CAST(benefit_quantum AS NUMERIC)) FROM scheme_benefits;

-- RIGHT (returns NULL here — nearly every row is sentinelled, by design)
SELECT AVG(CAST(benefit_quantum AS NUMERIC))
FROM scheme_benefits WHERE benefit_quantum <> 'PENDING_VERIFICATION';
```

**2. Never quote an amount from this package.** No monetary figure is asserted anywhere. Join to
`government_schemes.official_portal` and send the user there.

**3. This narrows a candidate set; it does not decide eligibility.** Thresholds are qualitative
("below the prescribed ceiling"), never numeric.

**4. `related_scheme_ids` is semicolon-delimited.** Split it before joining.

## Recipe 1 — Which schemes am I eligible for?

The core query. Build a profile, then find schemes whose *mandatory* criteria the profile does not
violate:

```sql
WITH profile AS (
  SELECT 'Category'   AS criterion_type, 'SC'      AS value
  UNION ALL SELECT 'Occupation', 'Farmer'
  UNION ALL SELECT 'Land Holding', 'Small'
),
blocking AS (                       -- mandatory criteria on axes the profile has no answer for
  SELECT DISTINCT e.scheme_id
  FROM eligibility_criteria e
  WHERE e.is_mandatory = 'Yes'
    AND e.criterion_type NOT IN (SELECT criterion_type FROM profile)
    AND e.criterion_type IN ('Category','Occupation','Land Holding','Gender','Business Size')
)
SELECT s.scheme_id, s.scheme_name, s.category_name, s.official_portal
FROM government_schemes s
WHERE s.status = 'Active'
  AND s.scheme_id NOT IN (SELECT scheme_id FROM blocking)
ORDER BY s.category_name, s.scheme_name;
```

`is_mandatory` is doing the work. A criterion marked `No` affects benefit *quantum*, not
qualification — SMAM's category criterion changes the subsidy percentage but not whether you
qualify. Treating it as a gate produces false exclusions.

## Recipe 2 — Everything about one scheme

```sql
SELECT s.scheme_name, s.ministry, s.objective, s.coverage,
       s.application_mode, s.official_portal, s.also_in_package
FROM government_schemes s WHERE s.short_name = 'PM-KISAN';

SELECT criterion_type, criterion_value, is_mandatory, verification_document_hint
FROM eligibility_criteria WHERE scheme_short_name = 'PM-KISAN';

SELECT benefit_type, benefit_description, disbursement_mode, frequency
FROM scheme_benefits WHERE scheme_short_name = 'PM-KISAN';

SELECT step_number, step_name, channel, responsible_actor, output_of_step
FROM application_process WHERE scheme_short_name = 'PM-KISAN' ORDER BY step_number::INT;
```

Note `ORDER BY step_number::INT` — it is stored as text, so a plain sort gives 1, 10, 2.

## Recipe 3 — Document checklist for a scheme

```sql
SELECT DISTINCT d.document_name, d.issuing_authority,
       d.digilocker_available, e.is_mandatory
FROM eligibility_criteria e
JOIN required_documents d
  ON e.verification_document_hint = d.document_name
   OR d.document_name LIKE '%' || e.verification_document_hint || '%'
WHERE e.scheme_short_name = 'PMEGP'
ORDER BY e.is_mandatory DESC, d.document_name;
```

V8 guarantees every non-sentinel `verification_document_hint` matches a real
`required_documents` row, so this join cannot silently drop criteria.

## Recipe 4 — Schemes for a beneficiary group

`scheme_categories` mixes three axes. Filter on `category_group` to get the one you want:

```sql
-- Who qualifies (Women, Youth, SC, ST, BC, Minorities, Senior Citizens, PwD)
SELECT s.scheme_name, s.short_name, c.category_name
FROM government_schemes s JOIN scheme_categories c USING (category_id)
WHERE c.category_group = 'Beneficiary Group';

-- What domain (Education, Healthcare, Agriculture, MSME, Housing, …)
--   → c.category_group = 'Sector'
-- What mechanism (Insurance, Financial Inclusion)
--   → c.category_group = 'Instrument'
```

**Caveat:** categories are not mutually exclusive. A women's MSME scheme is legitimately both
`cat-005` and `cat-006`, but each scheme carries one dominant category. Counting schemes per
category **understates cross-cutting reach** — Stand-Up India sits under Scheduled Castes but
serves women equally.

## Recipe 5 — Schemes by benefit type

```sql
SELECT b.benefit_type, COUNT(DISTINCT b.scheme_id) AS schemes,
       STRING_AGG(DISTINCT b.scheme_short_name, ', ' ORDER BY b.scheme_short_name) AS list
FROM scheme_benefits b
GROUP BY b.benefit_type ORDER BY schemes DESC;
```

Multi-component schemes appear under several types — PM Vishwakarma under Training, Equipment
Support and Loan. That is the intended structure, not duplication.

## Recipe 6 — District-level access route

```sql
SELECT d.district_name, d.dist_ref, d.state_scope,
       d.scheme_short_name, d.district_level_agency, d.application_channel
FROM district_scheme_mapping d
WHERE d.district_name = 'Nalgonda'
ORDER BY d.scheme_short_name;
```

Returns the 5 district-delivered schemes and which office to approach. The other 35 registry
schemes are nationally administered with no district-mediated step — their absence here is
deliberate, not a gap.

`district_specific_variation` is sentinelled on all 305 rows: whether benefit or capacity actually
differs in that district was not confirmable.

## Recipe 7 — Profile-based recommendations

```sql
SELECT r.priority_rank, r.scheme_short_name, r.priority_score,
       r.recommendation_basis, r.suggested_next_scheme_id, r.future_opportunity
FROM scheme_ai_recommendations r
WHERE r.profile_code = 'PROF-FARMER-SMALL'
ORDER BY r.priority_rank::INT;
```

Available profiles:

| Profile code | Archetype |
|---|---|
| `PROF-STUDENT-SC` | SC student entering higher education |
| `PROF-STUDENT-CLASS8` | Class VIII student, low-income household |
| `PROF-FARMER-SMALL` | Small farmer, rice and chilli, Telangana |
| `PROF-FARMER-ORGANIC` | Farmer converting to organic turmeric |
| `PROF-WOMAN-ENTREPRENEUR` | Woman first-time food processing entrepreneur |
| `PROF-YOUTH-RURAL` | Rural youth, class XII, seeking employment |
| `PROF-ARTISAN` | Traditional carpenter, own-account |
| `PROF-URBAN-POOR-FAMILY` | Urban EWS family, no insurance or housing |
| `PROF-SENIOR-CITIZEN` | Rural BPL citizen aged 68 |
| `PROF-TECH-STARTUP` | Pre-revenue DPIIT-recognised startup |

**Read `recommendation_basis`, not just `priority_score`.** The score is a designed heuristic with
no empirical calibration — confidence is 60 on every row, the lowest in the package. The basis
sentence is what makes it auditable.

`suggested_next_scheme_id` encodes real sequencing: PMJDY before any DBT scheme, PM-KISAN before
KCC, basic training before advanced.

## Recipe 8 — Following the recommendation chain

```sql
WITH RECURSIVE chain AS (
  SELECT scheme_id, suggested_next_scheme_id, 1 AS depth,
         scheme_short_name::TEXT AS path
  FROM scheme_ai_recommendations
  WHERE profile_code = 'PROF-URBAN-POOR-FAMILY' AND priority_rank = '1'
  UNION ALL
  SELECT r.scheme_id, r.suggested_next_scheme_id, c.depth + 1,
         c.path || ' → ' || r.scheme_short_name
  FROM chain c
  JOIN scheme_ai_recommendations r ON r.scheme_id = c.suggested_next_scheme_id
  WHERE c.suggested_next_scheme_id <> 'PENDING_VERIFICATION' AND c.depth < 5
)
SELECT path, depth FROM chain ORDER BY depth DESC LIMIT 1;
```

## Recipe 9 — Cross-package: schemes for a crop

```sql
SELECT a.scheme_short_name, a.farm_activity, a.farmer_category,
       s.official_portal, a.package005_scheme_id
FROM agriculture_scheme_mapping a
JOIN government_schemes s ON s.scheme_id = a.scheme_id
WHERE a.package005_crop_name = 'Chilli';
```

With Package005 loaded, join through to crop agronomy:

```sql
SELECT a.scheme_short_name, c.crop_name, c.season, c.major_districts
FROM agriculture_scheme_mapping a
JOIN package005.crops c ON c.crop_id = a.package005_crop_id
WHERE a.package005_crop_id <> 'PENDING_VERIFICATION';
```

Crop-agnostic schemes (PM-KISAN, Soil Health Card) carry the crop sentinel deliberately — support
is per landholding, not per crop.

## Recipe 10 — Cross-package: schemes for a skill

```sql
SELECT k.scheme_short_name, k.package006_skill_name,
       k.package006_certification_name, k.package006_provider_name
FROM skill_scheme_mapping k
WHERE k.package006_skill_id <> 'PENDING_VERIFICATION';
```

Certification and provider links are sparse (4 and 3 of 12) because most scheme-to-skill
relationships do not run through one named certificate or one named provider.

## Recipe 11 — Which bank delivers this scheme?

```sql
SELECT institution_name, institution_type, ownership, official_website
FROM financial_institutions
WHERE scheme_roles LIKE '%PMEGP%';
```

Institution-*type* rows (Regional Rural Banks, cooperatives, PACS, Small Finance Banks) sentinel
`official_website` — they describe categories, not named entities.

## Recipe 12 — Provenance audit

```sql
SELECT data_source, COUNT(*) AS rows,
       MIN(confidence_score::INT) AS lo, MAX(confidence_score::INT) AS hi
FROM government_schemes GROUP BY data_source ORDER BY rows DESC;
```

No score exceeds 85 anywhere (observed max 78). Every row is `VST-NEEDS_REVIEW` — **nothing has had
human sign-off.**

## Traps, collected

| Trap | Consequence | Guard |
|---|---|---|
| Casting sentinel columns | Error or silent zero | `WHERE col <> 'PENDING_VERIFICATION'` |
| Quoting a benefit amount | You will quote nothing, or a NULL | Link to `official_portal` |
| Treating `is_mandatory = No` as a gate | False exclusions | Only `Yes` blocks eligibility |
| `ORDER BY step_number` as text | 1, 10, 2 ordering | Cast to `INT` |
| Joining `related_scheme_ids` directly | No match — it is a delimited list | Split on `;` first |
| Counting schemes per category | Understates cross-cutting reach | Each scheme has one dominant category |
| Trusting `priority_score` as evidence | Unfounded ranking | Heuristic only; read `recommendation_basis` |
| Assuming a sentinel FK means no real relationship | Missed link | It means no counterpart in that package's *current version* |
| Expecting all 40 schemes in `district_scheme_mapping` | Apparent gap | Only 5 have a district-mediated step |
| Expecting state schemes | Nothing returned | All 40 are Central; state slices are in Package002/003/004 |

## Re-validating after a local change

```bash
cd packages/Package007_Government_Schemes
python3 validate.py     # exit 0 = clean
```

V8 and V9 catch stale denormalised names and broken cross-package ids — both easy to introduce by
hand-editing and hard to spot by eye.
