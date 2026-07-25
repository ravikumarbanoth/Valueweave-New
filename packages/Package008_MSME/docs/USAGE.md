# Usage — Package008_MSME v1.0.0

Query recipes for the questions this package was built to answer, and the traps to avoid.

## Before you query: four rules

**1. Filter the sentinel, always.**

```sql
-- WRONG: errors, or silently coerces
SELECT AVG(CAST(investment_range AS NUMERIC)) FROM msme_businesses;

-- RIGHT: but returns NULL — every row is sentinelled, by design
SELECT AVG(CAST(investment_range AS NUMERIC)) FROM msme_businesses
WHERE investment_range <> 'PENDING_VERIFICATION';
```

**2. Never quote an investment figure from this package.** None exists. Use
`udyam_classification` for the statutory band, and join to Package004 via `industry_mapping` for
the opportunities that have sourced investment detail.

**3. Ordinal columns rank, they do not measure.** `risk_level = 'High'` means higher than Medium,
not any specific probability. Do not average them, and do not convert them to numbers.

**4. A sentinel in a `package0NN_*_id` column is a statement about the upstream package**, not
about this relationship. The relationship is still real — see `machinery_name` or `skill_role` for
what it is.

## Recipe 1 — Which business can I start?

The core query. Filter on the closed-domain columns (all enforced by V12):

```sql
SELECT b.business_id, b.business_name, c.category_name, m.business_model_name,
       b.udyam_classification, b.difficulty, b.risk_level, b.employment_generation
FROM msme_businesses b
JOIN msme_categories c USING (category_id)
JOIN business_models  m USING (business_model_id)
WHERE b.udyam_classification = 'Micro'
  AND b.difficulty IN ('Easy', 'Moderate')
  AND b.risk_level IN ('Low', 'Medium')
  AND b.district_suitability IN ('Rural', 'Both')
ORDER BY b.business_name;
```

Swap the filters for the profile you care about. `district_suitability = 'Variable'` means it
depends on specifics, not that it is unsuitable everywhere.

## Recipe 2 — Everything about one business

```sql
-- The business itself
SELECT * FROM msme_businesses WHERE business_id = 'mb-004';

-- What plant it needs
SELECT machinery_name, machinery_role, investment_category, is_essential,
       package005_machinery_id
FROM machinery_mapping WHERE business_id = 'mb-004';

-- What it consumes
SELECT raw_material_name, material_class, supplier_type,
       availability, seasonality, price_volatility
FROM raw_material_mapping WHERE business_id = 'mb-004';

-- Which schemes support it (join to Package007 for the actual benefit)
SELECT package007_scheme_short_name, relevance, applicable_stage, support_nature
FROM scheme_mapping WHERE business_id = 'mb-004' ORDER BY relevance;

-- Who you need to hire
SELECT package006_skill_name, skill_role, criticality, who_needs_it
FROM skill_mapping WHERE business_id = 'mb-004' ORDER BY criticality;

-- Where it fits
SELECT district_name, state, suitability_basis, resource_strength, market_access_score
FROM district_business_mapping WHERE business_id = 'mb-004';

-- Investment characteristics
SELECT * FROM investment_intelligence WHERE business_id = 'mb-004';
```

## Recipe 3 — The full cross-package join

This is what the package is for. Crop → business → scheme → skill → district in one path, with
none of those domains duplicated:

```sql
SELECT b.business_name,
       p5c.crop_name,                    -- from Package005
       p7.scheme_name,                   -- from Package007
       p6.skill_name,                    -- from Package006
       p1.district_name                  -- from Package001
FROM msme_businesses b
LEFT JOIN agriculture_business_mapping abm ON abm.business_id = b.business_id
LEFT JOIN package005.crops p5c           ON p5c.crop_id = abm.package005_crop_id
LEFT JOIN scheme_mapping sm              ON sm.business_id = b.business_id
LEFT JOIN package007.government_schemes p7 ON p7.scheme_id = sm.package007_scheme_id
LEFT JOIN skill_mapping km               ON km.business_id = b.business_id
LEFT JOIN package006.skills p6           ON p6.skill_id = km.package006_skill_id
LEFT JOIN district_business_mapping dbm  ON dbm.business_id = b.business_id
LEFT JOIN package001.district p1          ON p1.dist_id = dbm.package001_dist_id
WHERE b.business_id = 'mb-004';
```

Use `LEFT JOIN` throughout — not every business has every mapping, and the sentinels will not match
an inner join.

## Recipe 4 — Licence checklist

`license_compliance` is not linked per business (licence applicability depends on scale, location
and product, which the package does not assert per row). Filter on `applicability` instead:

```sql
SELECT license_name, issuing_authority, jurisdiction, renewal_cycle, online_application
FROM license_compliance
WHERE applicability ILIKE '%food%' OR license_name IN ('Udyam Registration', 'GST Registration')
ORDER BY jurisdiction, license_name;
```

Every MSME needs Udyam (for scheme access) and, above threshold, GST. Beyond those, read
`applicability` — it states who actually needs each one.

## Recipe 5 — Which schemes support which businesses

```sql
SELECT sm.package007_scheme_short_name AS scheme,
       COUNT(*) AS businesses,
       STRING_AGG(sm.business_name, ', ' ORDER BY sm.business_name) AS list
FROM scheme_mapping sm
WHERE sm.relevance = 'Primary'
GROUP BY sm.package007_scheme_short_name
ORDER BY businesses DESC;
```

`relevance = 'Primary'` means the scheme is a core support route; `'Secondary'` means useful but
not the main path. Neither means any given applicant qualifies — Package007 holds eligibility, and
even there thresholds are qualitative.

## Recipe 6 — Skill demand across the catalogue

```sql
SELECT km.package006_skill_name AS skill,
       COUNT(DISTINCT km.business_id) AS businesses,
       SUM(CASE WHEN km.criticality = 'Essential' THEN 1 ELSE 0 END) AS essential_for
FROM skill_mapping km
WHERE km.package006_skill_id <> 'PENDING_VERIFICATION'
GROUP BY km.package006_skill_name
ORDER BY businesses DESC;
```

To find the **gaps** — requirements with no Package006 skill record — invert the filter:

```sql
SELECT business_name, skill_role, who_needs_it
FROM skill_mapping
WHERE package006_skill_id = 'PENDING_VERIFICATION';
```

That returns seven rows. They are a documented coverage request to Package006, not missing data.

## Recipe 7 — District opportunity profile

```sql
SELECT d.business_name, d.suitability_basis,
       d.resource_strength, d.market_access_score,
       b.udyam_classification, b.difficulty
FROM district_business_mapping d
JOIN msme_businesses b USING (business_id)
WHERE d.district_name = 'Nizamabad'
ORDER BY d.resource_strength DESC;
```

Read `suitability_basis` — it names the documented characteristic behind the claim. Absence of a
district-business pair is not evidence of unsuitability; only 32 pairs are asserted.

## Recipe 8 — Comparative investment screening

```sql
SELECT ii.business_name, ii.investment_band, ii.capex_intensity,
       ii.working_capital_intensity, ii.roi_category, ii.payback_category,
       ii.scalability, ii.composite_risk, ii.future_outlook, ii.key_success_factor
FROM investment_intelligence ii
WHERE ii.investment_band = 'Micro'
  AND ii.roi_category = 'Attractive'
  AND ii.composite_risk IN ('Low', 'Medium')
ORDER BY ii.scalability DESC;
```

**Every field here is ordinal.** `roi_category = 'Attractive'` is a judgement, not a return
percentage; `payback_category = 'Short'` is not a number of months. Use this to shortlist for
further diligence, never to underwrite.

`key_success_factor` is the most useful column — it names the single variable that most determines
outcome for that business.

## Recipe 9 — Export-capable businesses

```sql
SELECT e.business_name, e.export_product, e.destination_markets,
       e.required_certifications, e.export_readiness_barrier, e.promotion_body
FROM export_opportunities e
JOIN msme_businesses b USING (business_id)
WHERE b.export_potential IN ('High', 'Very High')
ORDER BY e.business_name;
```

`export_readiness_barrier` is the field to act on. For garments it is social compliance audit
readiness, not product quality; for software there is no physical certification at all.

## Recipe 10 — AI adoption shortlist for a business

`ai_business_tools` is not linked per business. Match on the business's `ai_readiness` and the
tool's `implementation_complexity`:

```sql
SELECT t.tool_class, t.function_area, t.expected_benefit,
       t.adoption_maturity_india, t.implementation_complexity
FROM ai_business_tools t
WHERE t.msme_relevance IN ('High', 'Very High')
  AND t.implementation_complexity = 'Low'
ORDER BY t.adoption_maturity_india DESC;
```

Start with low-complexity, high-maturity tools (accounting, generative AI for content, digital
marketing). Predictive maintenance and AI quality inspection are high-relevance but high-complexity
— justifiable only at scale.

## Recipe 11 — Which machinery does Package005 already hold?

The normalization rule made visible:

```sql
SELECT machinery_name, COUNT(*) AS used_by_businesses,
       MAX(package005_machinery_id) AS p005_id
FROM machinery_mapping
WHERE package005_machinery_id <> 'PENDING_VERIFICATION'
GROUP BY machinery_name ORDER BY used_by_businesses DESC;
```

Ten machines resolve. Join through to Package005 for their automation level and subsidy scheme —
which Package008 deliberately does not restate:

```sql
SELECT mm.business_name, mm.machinery_name,
       p5.automation_level, p5.subsidy_scheme   -- from Package005
FROM machinery_mapping mm
JOIN package005.farm_machinery p5 ON p5.machinery_id = mm.package005_machinery_id;
```

## Recipe 12 — Provenance audit

```sql
SELECT data_source, COUNT(*) AS rows,
       MIN(confidence_score::INT) AS lo, MAX(confidence_score::INT) AS hi
FROM msme_businesses GROUP BY data_source ORDER BY rows DESC;
```

No score exceeds 85 anywhere (observed max 78). Every row is `VST-NEEDS_REVIEW` — **nothing has had
human sign-off.**

## Traps, collected

| Trap | Consequence | Guard |
|---|---|---|
| Casting `investment_range` | Error or NULL on every row | It is sentinelled everywhere; use `udyam_classification` |
| Averaging ordinal columns | Meaningless number | They rank, they do not measure |
| Reading `roi_category` as a return | Unfounded financial claim | It is a judgement; no percentage exists |
| `INNER JOIN` across mappings | Silently drops businesses | Use `LEFT JOIN`; not every business has every mapping |
| Treating a sentinel FK as "no relationship" | Missed link | It means the upstream package lacks the record; the relationship is in `machinery_name` / `skill_role` |
| `ORDER BY employment_generation` | String sort on `'6-15'` | Split on `-` and cast first |
| Expecting all 40 businesses in `industry_mapping` | Apparent gap | Only 19 have a Package004 counterpart |
| Expecting a licence list per business | Nothing returned | `license_compliance` is filtered on `applicability`, not joined per business |
| Persisting upstream columns into your own Package008 tables | Recreates the duplication the package prevents | Keep it a view — see `docs/IMPORT_GUIDE.md` §5 |

## Re-validating after a local change

```bash
cd packages/Package008_MSME
python3 validate.py     # exit 0 = clean
```

V8 and V9 catch stale denormalised names and broken upstream ids. V13 catches a column that
restates upstream data — the one mistake that is easy to make while "improving" the schema.
