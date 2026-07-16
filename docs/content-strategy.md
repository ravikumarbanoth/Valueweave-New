# ValueWeave Content Strategy

This document explains how the Phase 3 static knowledge layer should grow into a durable content and intelligence system without forcing another redesign.

## Knowledge Layer Architecture

The current knowledge layer is intentionally static and lightweight.

Current location:

```text
frontend/data/
```

Datasets:
- `districts.json`
- `industries.json`
- `manufacturing.json`
- `products.json`
- `training.json`
- `skills.json`
- `schemes.json`

Supporting code:
- `frontend/lib/static-knowledge.js`
- `frontend/components/platform/KnowledgeSearch.jsx`
- `frontend/app/knowledge/[type]/[slug]/page.js`

The goal is to let ValueWeave publish useful knowledge immediately while preserving a clean path toward Supabase-backed content later.

## Static-to-Supabase Migration Strategy

### Stage 1: Static Knowledge

Use local JSON files for early knowledge content, homepage previews, lightweight search, and proof of structure.

Use this stage for:
- Content validation
- Navigation validation
- User understanding
- SEO/GEO preview structure
- Admin planning

### Stage 2: Admin-Managed Content

Once content types stabilize, move high-change datasets into Supabase and admin CMS workflows.

Likely first migrations:
- District profiles
- Industries
- Schemes
- Training pathways
- Manufacturing opportunities

### Stage 3: Relationship Layer

After multiple datasets are reliable, introduce explicit relationships.

Examples:
- District to Industry
- Industry to Skill
- Skill to Training
- Scheme to Opportunity
- Product to Manufacturing Guide

### Stage 4: AI-Ready Knowledge Graph

Only after content quality and relationships are reliable should AI advisors use the knowledge layer.

AI must depend on reviewed knowledge, not replace it.

## Content Standards

Every knowledge item should have:
- Stable slug
- Clear title/name
- Short summary or description
- Practical user relevance
- Module/category alignment
- Investment or readiness context where useful
- Required skills where applicable
- Clear source or owner in future CMS stages

Avoid:
- Fake precision
- Unsupported claims
- Overly generic descriptions
- Duplicate content across modules
- AI-generated content without human review

## Future AI Integration

Future AI systems should read from structured, reviewed content.

AI-ready content should include:
- Key takeaways
- Who should use this
- District relevance
- Investment range
- Skill requirements
- Related schemes
- Related training paths
- Related opportunities

AI advisors should be introduced only after:
- Content ownership is clear
- Source quality is reviewed
- User permissions are defined
- Advice boundaries are documented

## Content Ownership

Recommended future ownership model:

- District content: platform editorial/admin team
- Industry content: domain experts and reviewed contributors
- Training content: admin team plus verified partners
- Scheme content: admin team with periodic review
- Manufacturing content: operators, mentors, and verified experts
- Product content: platform editorial team with expert review

## Maintenance Guidelines

- Review high-impact content quarterly.
- Review schemes whenever government rules change.
- Mark outdated content clearly.
- Keep static JSON content small and representative.
- Move frequently changing content to Supabase.
- Keep public pages usable even when backend content is unavailable.

## Long-Term Principle

The homepage should remain the permanent gateway to the ValueWeave ecosystem. New infrastructure modules should plug into the same architecture through data, route, navigation, and relationship additions rather than another redesign.
