# ValueWeave Database Roadmap

This document outlines the future data model for ValueWeave as India's Digital Economic Infrastructure. It is planning-only and does not create production tables, migrations, policies, or seed data.

## Principles

- Keep the platform schema-first and modular.
- Add production tables only when the matching product workflow is ready.
- Prefer stable shared entities over one-off feature tables.
- Model relationships explicitly so future AI, recommendations, search, and GEO systems can reason over the platform.
- Preserve existing authentication, profiles, opportunities, collaboration, research, analytics, and admin systems.

## Future Core Entities

### District

Represents a local economic geography.

Potential fields:
- `id`
- `name`
- `slug`
- `state`
- `region`
- `population_band`
- `summary`
- `economic_profile`
- `infrastructure_notes`
- `status`

Relationships:
- District has many Industries.
- District has many Skills.
- District has many Opportunities.
- District has many Resources.
- District has many Government Schemes.

### Industry

Represents a sector or cluster active in one or more districts.

Potential fields:
- `id`
- `name`
- `slug`
- `category`
- `description`
- `readiness_level`
- `growth_signal`

Relationships:
- Industry belongs to many Districts.
- Industry requires many Skills.
- Industry maps to many Opportunities.
- Industry uses many Resources, Suppliers, Machinery, and Training programs.

### Skill

Represents a practical capability needed by workers, founders, and businesses.

Potential fields:
- `id`
- `name`
- `slug`
- `skill_type`
- `difficulty`
- `description`
- `assessment_available`

Relationships:
- Skill belongs to many Industries.
- Skill belongs to many Training programs.
- Skill maps to Opportunities, Mentors, and Certifications.

### Training

Represents courses, certifications, apprenticeships, internships, industrial visits, or readiness programs.

Potential fields:
- `id`
- `title`
- `slug`
- `training_type`
- `provider_name`
- `duration`
- `cost_band`
- `delivery_mode`
- `district_id`
- `status`

Relationships:
- Training teaches many Skills.
- Training can be linked to Industries and Districts.
- Training may produce Certifications.

### Mentor

Represents experienced people who can guide founders, students, and operators.

Potential fields:
- `id`
- `profile_id`
- `mentor_type`
- `industries`
- `districts`
- `availability_status`
- `verification_status`

Relationships:
- Mentor belongs to a Profile.
- Mentor supports many Industries, Skills, Districts, and Opportunities.

### Manufacturer

Represents a manufacturing unit, factory, workshop, or production partner.

Potential fields:
- `id`
- `name`
- `slug`
- `district_id`
- `industry_id`
- `capabilities`
- `capacity_band`
- `certifications`
- `verification_status`

Relationships:
- Manufacturer operates in a District.
- Manufacturer supports Industries and Products.
- Manufacturer uses Machinery, Raw Materials, Suppliers, and Compliance records.

### Supplier

Represents raw material, component, logistics, equipment, or service suppliers.

Potential fields:
- `id`
- `name`
- `slug`
- `supplier_type`
- `district_id`
- `industries`
- `contact_policy`
- `verification_status`

Relationships:
- Supplier supports many Industries, Manufacturers, and Opportunities.
- Supplier may provide Raw Materials, Machinery, or Services.

### Machinery

Represents equipment needed for production.

Potential fields:
- `id`
- `name`
- `slug`
- `category`
- `industry_id`
- `investment_band`
- `usage_notes`
- `supplier_count`

Relationships:
- Machinery belongs to Industries.
- Machinery is supplied by Suppliers.
- Machinery supports Manufacturing Guides and Roadmaps.

### Investor

Represents capital providers and funding institutions.

Potential fields:
- `id`
- `name`
- `slug`
- `investor_type`
- `ticket_size_band`
- `sector_focus`
- `district_focus`
- `verification_status`

Relationships:
- Investor maps to Industries, Opportunities, Districts, and Founder Profiles.

### Opportunity

Represents business opportunities, collaboration posts, local demand signals, and future economic openings.

Potential fields:
- `id`
- `title`
- `slug`
- `opportunity_type`
- `district_id`
- `industry_id`
- `investment_band`
- `skill_requirements`
- `readiness_level`
- `status`

Relationships:
- Opportunity belongs to District and Industry.
- Opportunity requires Skills.
- Opportunity can connect to Mentors, Investors, Manufacturers, Suppliers, Schemes, and Training.

## Relationship Model

A future relationship table can connect entities without creating rigid dependencies too early.

Potential fields:
- `id`
- `source_type`
- `source_id`
- `target_type`
- `target_id`
- `relationship_type`
- `strength`
- `notes`

Example relationship types:
- `district_has_industry`
- `industry_requires_skill`
- `skill_taught_by_training`
- `opportunity_needs_supplier`
- `manufacturer_uses_machinery`
- `mentor_guides_industry`
- `scheme_supports_opportunity`

## Module Mapping

### District Intelligence

Future entities:
- District
- Industry
- Skill
- Resource
- Scheme
- Opportunity

### Industrial Readiness

Future entities:
- Skill
- Training
- Certification
- Internship
- Apprenticeship
- Industrial Visit
- Mentor

### Collaboration / Network

Future entities:
- Mentor
- Investor
- Institution
- Community
- Collaborator Profile
- Relationship Request

### Manufacturing

Future entities:
- Manufacturer
- Supplier
- Machinery
- Raw Material
- Manufacturing Guide
- Compliance Item

### Scale

Future entities:
- Automation Tool
- Robotics Provider
- ERP Provider
- Quality Standard
- Export Support
- Logistics Provider
- Energy Resource

### AI Intelligence Layer

Future entities:
- AI Recommendation
- Advisory Session
- Knowledge Graph Snapshot
- User Intent Signal
- Content Summary

These should depend on stable platform entities and should not be implemented until the underlying human-readable workflows are mature.

## Rollout Recommendation

1. Stabilize public route architecture and navigation.
2. Add admin CMS only for content that is actively managed.
3. Add canonical entity tables one module at a time.
4. Add relationships once at least three entity types are populated.
5. Add AI and recommendation systems only after structured data quality is strong.
