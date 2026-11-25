# Development log

## 2026-11-24 08:24 CET — Standalone GPU Compare

- Extracted the GPU benchmark application into its own repository, Python package, session protocol, Docker Compose project and deployable Stockholm stack with a dedicated Express cluster.
- Verified 31 Python tests using PostgreSQL and the local AWS emulator, three browser tests including mobile, eight mocked Terraform plans, Ruff, TypeScript and the production builds. The Docker application serves the comparison directly on port 5180.
- Real hardware results and the live AWS endpoint require deployment and provider credentials.

## 2026-11-25 08:03 CET — Aurora Data API readiness

During initial Stockholm provisioning, Aurora reported that the HTTP endpoint was enabled before Data API accepted SQL. Preparation now retries only its read-only SELECT 1 probe on that specific propagation error for up to three minutes. Other errors surface immediately. Verified the real connection to the dedicated cluster, all 13 preparation tests, and Ruff.

## 2026-11-25 08:09 CET — Public AWS deployment

- Deployed the independent Stockholm stack, applied the database migrations and published the production web build. Terraform reported no outstanding changes after deployment. [Public demo](https://dkvxgcdy40zyv.cloudfront.net)
- Verified the deployed JavaScript against the build and tested the empty comparison, provider status, disabled rental button and mobile layout in Chromium. The API returned an empty list of real reports. Paid rentals are disabled and the watchdog reported that the provider is unconfigured.
- One initial session deletion returned HTTP 503. Three subsequent public session lifecycles completed. The API rejected a missing CSRF token, a foreign origin and reuse of a revoked cookie.
