# ValueWeave Data Packages

The `packages/` directory is the canonical source for ValueWeave data packages. Packages are curated, versioned knowledge bundles that can be reviewed, released, archived, and integrated into the platform without changing the application architecture each time a new domain is added.

## Purpose

ValueWeave is evolving into India's Digital Economic Infrastructure. The package system gives the repository a disciplined way to manage domain knowledge such as geography, education, healthcare, industries, agriculture, skills, government schemes, and MSME resources.

Packages should be used for:

- Curated source data and knowledge assets.
- Versioned domain releases.
- Import-ready content prepared before platform integration.
- Documentation of package scope, ownership, and lifecycle.
- Auditable handoff between content preparation and product implementation.

## Versioning Philosophy

Released packages are immutable. Once a package version is released, its contents should not be edited in place except for exceptional repository hygiene fixes that do not change meaning.

Future changes should be introduced as new versioned releases, for example:

- `Package001_Geography_v1.0.0`
- `Package001_Geography_v1.1.0`
- `Package001_Geography_v2.0.0`

Use semantic versioning principles:

- Patch versions for corrections that do not change structure or meaning.
- Minor versions for additive, backward-compatible content updates.
- Major versions for structural changes, breaking schema changes, or significant content model revisions.

## Naming Convention

Top-level package folders use this format:

```text
PackageNNN_Domain_Name
```

Release archives should use this format:

```text
PackageNNN_Domain_Name_vMAJOR.MINOR.PATCH.zip
```

Examples:

```text
Package001_Geography
Package001_Geography_v1.0.0.zip
Package007_Government_Schemes
```

Guidelines:

- Use a three-digit package number.
- Use title case domain names with underscores between words.
- Keep package numbers stable forever.
- Do not reuse retired package numbers for a different domain.

## Package Lifecycle

1. **Planned**: Package folder exists with a README and expected scope.
2. **Prepared**: Content is assembled locally or in a staging area.
3. **Released**: A versioned archive or versioned package contents are added.
4. **Reviewed**: Schema, content quality, and integration readiness are checked.
5. **Integrated**: Platform code consumes the package through documented import or static data workflows.
6. **Archived**: Older releases remain available for audit and rollback context.

## Guidelines for Adding New Packages

When adding a new package:

1. Create a top-level folder using the naming convention.
2. Add a `README.md` explaining purpose, expected contents, versioning, and status.
3. Do not add `.gitkeep` files. Use README files so empty packages remain self-documenting.
4. Keep source data, manifests, changelogs, and release notes inside the package folder when applicable.
5. Treat released package contents as immutable.
6. Introduce future changes through new versioned releases.
7. Do not mix unrelated domains inside one package.
8. Do not integrate package contents into application code until the release has been reviewed.

## Current Package Index

| Package | Domain | Status |
| --- | --- | --- |
| Package001_Geography | Geography | Prepared for first release upload |
| Package002_Education | Education | Empty placeholder |
| Package003_Healthcare | Healthcare | Empty placeholder |
| Package004_Industries | Industries | Empty placeholder |
| Package005_Agriculture | Agriculture | Empty placeholder |
| Package006_Skills | Skills | Empty placeholder |
| Package007_Government_Schemes | Government Schemes | Empty placeholder |
| Package008_MSME | MSME | Empty placeholder |
