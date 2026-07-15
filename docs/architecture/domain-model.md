# Domain Model

This document describes the future domain model for ValueWeave as India's Digital Economic Infrastructure. It is guidance only and does not imply immediate database schema changes.

## Core Domains

### District Intelligence

Purpose: help users understand where opportunities exist.

Future entities:
- District
- Industry
- Resource
- Infrastructure Asset
- Skill Demand
- Government Scheme
- District Opportunity Signal

### Industrial Readiness

Purpose: help users become capable of building.

Future entities:
- Skill
- Assessment
- Learning Path
- Training Program
- Certification
- Internship
- Apprenticeship
- Industrial Visit
- Mentor

### Collaboration & Capital

Purpose: help users find people, institutions, and resources.

Future entities:
- Collaborator Profile
- Co-founder Match
- Expert
- Mentor
- Investor
- Institution
- Community
- Relationship Request

### Digital Manufacturing Operating System

Purpose: help users build and operate manufacturing businesses.

Future entities:
- Product
- Manufacturing Guide
- Factory Plan
- Machinery
- Raw Material
- Supplier
- Production Process
- Compliance Item

### Industrial Scaling Resources

Purpose: help growing businesses become competitive.

Future entities:
- Automation Resource
- Robotics Provider
- ERP Tool
- Quality Standard
- Export Resource
- Logistics Provider
- Energy Resource
- Industrial Resource

### AI Intelligence Layer

Purpose: connect and optimize platform knowledge when the underlying data is mature.

Future entities:
- AI Advisor
- Recommendation
- Knowledge Graph Snapshot
- User Intent Signal
- Content Summary
- Advisory Session

## Design Notes

- Keep modules independently expandable.
- Prefer shared canonical entities over module-specific duplicates.
- Build public content and admin workflows before adding AI behavior.
- Avoid production tables until workflows and ownership are clear.
