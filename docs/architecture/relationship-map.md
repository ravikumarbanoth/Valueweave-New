# Relationship Map

This document outlines how future ValueWeave entities should connect. It is planning-only.

## Primary Relationships

- District has many Industries.
- District has many Resources.
- District has many Skill Demands.
- District has many Government Schemes.
- District has many Opportunity Signals.
- Industry requires many Skills.
- Industry uses Machinery, Raw Materials, Suppliers, and Compliance Items.
- Skill is developed through Training, Certifications, Internships, Apprenticeships, and Mentors.
- Opportunity belongs to a District and Industry.
- Opportunity requires Skills and Collaborators.
- Manufacturer operates in a District and Industry.
- Manufacturer uses Suppliers, Machinery, Raw Materials, and Production Processes.
- Investor supports Industries, Districts, Opportunities, and Manufacturers.
- Mentor supports Skills, Industries, Districts, and Opportunities.

## Relationship Types

Suggested future relationship labels:
- `district_has_industry`
- `district_has_resource`
- `district_needs_skill`
- `district_supports_scheme`
- `industry_requires_skill`
- `industry_uses_machinery`
- `skill_taught_by_training`
- `opportunity_requires_skill`
- `opportunity_needs_collaborator`
- `manufacturer_uses_supplier`
- `mentor_guides_skill`
- `investor_funds_industry`

## Implementation Guidance

- Introduce relationships only after at least three entity types contain reliable content.
- Keep relationship strength and evidence fields optional at first.
- Expose relationships to GEO and AI-readable summaries before using them for automated recommendations.
