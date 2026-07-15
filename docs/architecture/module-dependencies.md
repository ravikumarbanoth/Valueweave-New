# Module Dependencies

This document explains how ValueWeave modules should depend on each other over time.

## Dependency Principles

- Modules should be independently expandable.
- Shared entities should live in common libraries or future canonical tables.
- Avoid direct circular dependencies between feature modules.
- Public pages can link across modules before backend relationships exist.
- AI should depend on mature content, not the other way around.

## Recommended Dependency Direction

1. District Intelligence
2. Industrial Readiness
3. Collaboration & Capital
4. Digital Manufacturing Operating System
5. Industrial Scaling Resources
6. AI Intelligence Layer

## Module Notes

### District Intelligence

Provides local economic context to all other modules.

Depends on:
- Static district data today
- Future district, industry, resource, scheme, and opportunity entities

### Industrial Readiness

Depends on district and industry context to explain what skills matter.

Future outputs:
- Skill gaps
- Learning paths
- Training matches

### Collaboration & Capital

Depends on user profiles and future relationship mapping.

Future outputs:
- Co-founder discovery
- Mentor matching
- Investor and institution discovery

### Manufacturing

Depends on district, industry, readiness, and network modules.

Future outputs:
- Manufacturing guides
- Supplier paths
- Machinery planning
- Compliance support

### Scale

Depends on manufacturing maturity and operational data.

Future outputs:
- Quality resources
- Export readiness
- Logistics support
- Automation guidance

### AI Intelligence Layer

Depends on every prior module and should not become a source of truth by itself.

Future outputs:
- Explanatory recommendations
- Advisor flows
- Optimization suggestions

## Current Implementation Boundary

The current product should expose routes, navigation, placeholder dashboards, and documentation only. Business logic, database schema changes, APIs, authentication changes, and AI implementation are intentionally deferred.
