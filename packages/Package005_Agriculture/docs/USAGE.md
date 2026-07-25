# Usage — Package005_Agriculture v1.0.0

Query patterns, join recipes and the traps to avoid when consuming this package.

## Load order

Load in dependency order. This is `import_order` in `package_manifest.json`:

```
1  crop_categories          (no dependencies)
2  soil_types               (no dependencies)
3  climate_zones            (no dependencies)
4  crops                    → crop_categories
5  crop_soil_mapping        → crops, soil_types
6  crop_climate_mapping     → crops, climate_zones
7  farm_machinery           (independent)
8  agri_processing_opportunities (independent)
9  farmer_producer_organizations (independent)
10 agriculture_training     (independent)
11 agriculture_schemes      (independent)
12 crop_disease_management  (independent)
13 market_linkages          (independent)
14 export_opportunities     (independent)
15 ai_precision_agriculture (independent)
16 agri_business_mapping    → crops, agri_processing_opportunities,
                              Package004_Industries, Package006_Skills_and_Training
```

`agri_business_mapping` is last because it depends on two **external** packages. If you are
loading Package005 standalone, load it but treat `package004_opportunity_name` and
`package006_skill_id` as unresolved text until those packages are present.

## Before you query: three rules

**1. Filter the sentinel, always.** `PENDING_VERIFICATION` is a bare string in otherwise
numeric columns. Any aggregation that does not exclude it will either error on cast or silently
skew.

```sql
-- WRONG: errors, or coerces to 0 depending on your engine
SELECT AVG(CAST(investment_inr AS BIGINT)) FROM farm_machinery;

-- RIGHT: but note this returns NULL here, because every row is sentinelled
SELECT AVG(CAST(investment_inr AS BIGINT))
FROM farm_machinery
WHERE investment_inr <> 'PENDING_VERIFICATION';
```

**2. Never average `avg_yield_tons_per_ha` across crops.** The column is not
cross-comparable — cotton is lint, turmeric is dry rhizome, ginger is fresh, coconut is
sentinelled because its unit is nuts per palm. A cross-crop mean is a meaningless number.

**3. `suitability_score` is ordinal, within-crop.** Use it to rank soils *for a crop*. Do not
use it to compare "how suitable" two different crops are.

## Recipe 1 — What can I grow on my soil in my climate?

The core screening query. Join both mapping tables on `crop_id`:

```sql
SELECT c.crop_name,
       c.season,
       c.duration_days,
       cs.suitability_score,
       cs.suitability_level,
       cc.yield_potential,
       cc.risk_level,
       cc.primary_climatic_risk
FROM crops c
JOIN crop_soil_mapping    cs ON cs.crop_id = c.crop_id
JOIN crop_climate_mapping cc ON cc.crop_id = c.crop_id
WHERE cs.soil_id        = 'st-001'   -- Black Soil
  AND cc.climate_zone_id = 'cz-005'  -- Semi-arid
ORDER BY cs.suitability_score DESC;
```

Read `primary_climatic_risk` before acting on a high suitability score. A crop can be Optimal
on soil and still carry a named failure mode in that zone.

## Recipe 2 — Full value chain for one crop

This is what the package is for: crop → processing → business → skill, in one query.

```sql
SELECT c.crop_name,
       c.export_potential,
       c.processing_potential,
       p.opportunity_name       AS processing_route,
       p.licenses_required,
       p.linked_scheme,
       m.package004_opportunity_name AS business_opportunity,
       m.package006_skill_name       AS required_skill,
       m.value_add_stage
FROM crops c
JOIN agri_business_mapping m ON m.crop_id = c.crop_id
JOIN agri_processing_opportunities p
     ON p.opportunity_id = m.processing_opportunity_id
WHERE c.crop_name = 'Turmeric';
```

For turmeric this resolves cleanly: Turmeric Powder Unit → *Turmeric Processing &
Powder-Making Unit* (a real Package004 row) → *Food Processing & Preservation* (a real
Package006 skill UUID).

For rice it resolves partially: Rice Mill → `PENDING_VERIFICATION` → *Food Processing &
Preservation*. Package004 v1.0.0 has no rice-milling opportunity. Handle that:

```sql
SELECT c.crop_name,
       p.opportunity_name,
       CASE WHEN m.package004_opportunity_name = 'PENDING_VERIFICATION'
            THEN NULL ELSE m.package004_opportunity_name END AS business_opportunity
FROM crops c
JOIN agri_business_mapping m ON m.crop_id = c.crop_id
JOIN agri_processing_opportunities p ON p.opportunity_id = m.processing_opportunity_id;
```

## Recipe 3 — Crops with both export and processing upside

```sql
SELECT crop_name, category_name, major_states, major_districts, confidence_score
FROM crops
WHERE export_potential    IN ('High', 'Very High')
  AND processing_potential IN ('High', 'Very High')
  AND major_districts <> 'PENDING_VERIFICATION'
ORDER BY category_name, crop_name;
```

The `major_districts` filter restricts to crops with a documented Telangana/Andhra Pradesh
footprint — useful when the output has to be locally actionable.

## Recipe 4 — Crop-only view (excluding production systems and allied activities)

`crop_categories` deliberately mixes botanical groups, production systems and allied
activities. Filter on `category_group`:

```sql
SELECT * FROM crop_categories
WHERE category_group IN ('Field Crops', 'Horticulture', 'Plantation');
-- 12 of 24 rows

-- The other twelve:
--   Production System (4): Organic Farming, Protected Cultivation, Hydroponics, Aquaponics
--   Allied (8): Forest Produce, Sericulture, Apiculture, Mushroom,
--               Fisheries, Livestock, Poultry, Dairy
```

Only the 12 crop-bearing categories have rows in `crops.csv`. The 8 allied categories have no
entity dataset in v1.0.0 — that is the main v1.1.0 gap.

## Recipe 5 — Machinery by subsidy scheme

Cost fields are sentinelled, so the useful axis is which scheme funds what:

```sql
SELECT subsidy_scheme,
       COUNT(*) AS machinery_types,
       STRING_AGG(machinery_name, ', ' ORDER BY machinery_name) AS covered
FROM farm_machinery
WHERE subsidy_scheme <> 'PENDING_VERIFICATION'
GROUP BY subsidy_scheme
ORDER BY machinery_types DESC;
```

## Recipe 6 — Technology readiness, honestly sorted

```sql
SELECT technology_name,
       current_adoption_india,
       ai_readiness_level,
       primary_constraint,
       confidence_score
FROM ai_precision_agriculture
ORDER BY confidence_score DESC;
```

Reading this table correctly matters. Rows at the bottom (farm robotics, autonomous tractors,
digital twin — confidence 50–52) describe **research and pilot stages in India, not products
you can buy**. The low confidence is the finding, not a data quality problem. `primary_constraint`
tells you why each one is stuck: DGCA licensing, rural connectivity, ground-truth data scarcity,
average holding size.

## Recipe 7 — Disease exposure for a crop

`crop_disease_management.affected_crops` is free text, not an FK, because these pathogens have
host ranges wider than the 45 crops here. Match with `LIKE`:

```sql
SELECT disease_name, disease_type, symptom_description,
       chemical_treatment, biological_treatment, ai_detection_possible
FROM crop_disease_management
WHERE affected_crops LIKE '%Rice%';
```

`chemical_treatment` lists **named actives, not doses**. Confirm current CIB&RC label approval
before any application recommendation reaches a farmer.

## Recipe 8 — Joining to Package001_Geography

There is no `dist_id` foreign key. `crops.major_districts` is a comma-separated free-text list.
A join is possible but is your decision and your risk:

```sql
-- Consumer-side join; verify results, do not assume completeness
SELECT c.crop_name, d.district_name, d.dist_ref, d.st_id
FROM crops c
JOIN package001.district d
  ON POSITION(d.district_name IN c.major_districts) > 0
WHERE c.major_districts <> 'PENDING_VERIFICATION';
```

Caveats: substring matching produces false positives on district names that are substrings of
others; the field lists only districts *publicly and specifically* associated with the crop, so
absence is not evidence the crop is not grown there; and 13 of 45 crops are sentinelled here.

## Recipe 9 — Cross-package skill demand from agriculture

Which Package006 skills does the agriculture value chain actually demand?

```sql
SELECT m.package006_skill_name,
       COUNT(DISTINCT m.crop_id)   AS crops_served,
       COUNT(*)                    AS mapping_rows
FROM agri_business_mapping m
GROUP BY m.package006_skill_name
ORDER BY mapping_rows DESC;
```

All 30 rows resolve to real Package006 UUIDs, so this join is safe. Four skills are referenced;
Food Processing & Preservation dominates, which is the expected shape — most agricultural
value addition is food processing.

## Recipe 10 — Provenance audit

Every dataset carries the same six provenance columns, so you can audit uniformly:

```sql
SELECT 'crops' AS dataset, data_source, COUNT(*) AS rows,
       MIN(confidence_score) AS conf_min, MAX(confidence_score) AS conf_max
FROM crops GROUP BY data_source
UNION ALL
SELECT 'agriculture_schemes', data_source, COUNT(*),
       MIN(confidence_score), MAX(confidence_score)
FROM agriculture_schemes GROUP BY data_source
ORDER BY dataset, rows DESC;
```

No `confidence_score` exceeds 85 anywhere (policy ceiling); the observed maximum is 78. Every
row is `VST-NEEDS_REVIEW` — **nothing in this package has had human data-steward sign-off.**
Treat it as reviewed-by-machine only.

## Traps, collected

| Trap | Consequence | Guard |
|---|---|---|
| Casting sentinel columns to numeric | Error or silent zero | `WHERE col <> 'PENDING_VERIFICATION'` |
| Averaging yield across crops | Meaningless figure | Compare within a crop only |
| Comparing `suitability_score` across crops | Wrong ranking | Ordinal, within-crop only |
| Trusting a scheme benefit amount | Stale by budget cycle | Re-verify at the scheme portal |
| Treating chemical actives as doses | Unsafe recommendation | Check current CIB&RC label |
| Assuming `crop_categories` = crops | 12 of 24 rows are not crop groups | Filter `category_group` |
| Assuming a sentinel FK means "no link exists in reality" | Missed opportunity | It means no counterpart in that package's *current version* |
| Using the 8-zone climate model for site recommendation | Over-precise | It is a screening tool; NARP has 127 zones |

## Re-validating after any local change

```bash
cd packages/Package005_Agriculture
python3 validate.py     # exit 0 = clean
```

If you edit a CSV by hand, run this. V8 will catch a `crop_id` that no longer resolves or a
denormalised `crop_name` that no longer agrees with `crops.csv` — a hazard that is easy to
introduce and hard to spot by eye.
