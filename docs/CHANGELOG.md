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

## 2026-11-25 08:16 CET — Examples for the public demo

Added a double-clickable German quick test and a plain-text copy of the five public benchmark prompts under `examples/`. Verified all three links in Chromium, checked the offer status and empty comparison against the live demo, and matched every prompt to the deployed protocol. The test session was deleted after verification.

## 2026-11-25 18:30 CET — Live Vast.ai offers on AWS

Connected the offer search and watchdog inventory to Vast.ai through AWS Secrets Manager. CloudFront served the verified production build. The watchdog recorded a healthy heartbeat with no GPU Compare instances. Rental admission remains disabled.

After RDS confirmed that Aurora had paused, one click in a new Chromium session loaded 50 live offers. Four read requests received temporary HTTP 503 responses while the database resumed. The client honored the retry delay before creating one session. Selecting a GPU showed its VRAM and hourly price, and the rental button stayed disabled. Verified the mobile layout and session deletion. All four local browser tests, focused Python checks, Ruff, TypeScript and the production build passed.

## 2026-11-25 21:24 CET — GitHub project title

Set the README heading to the English portfolio title. Verified that the existing public GitHub repository uses the same source history as the local checkout.
