# Development log

## 2026-11-24 08:24 CET — Standalone GPU Compare

- Extracted the GPU benchmark application into its own repository, Python package, session protocol, Docker Compose project and deployable Stockholm stack with a dedicated Express cluster.
- Verified 31 Python tests using PostgreSQL and the local AWS emulator, three browser tests including mobile, eight mocked Terraform plans, Ruff, TypeScript and the production builds. The Docker application serves the comparison directly on port 5180.
- Real hardware results and the live AWS endpoint require deployment and provider credentials.
