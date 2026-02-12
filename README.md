# Reusable RAG Engine

A modular Retrieval-Augmented Generation (RAG) engine designed to power question-answering services across multiple, independent knowledge bases.

## Overview

**rag-engine** provides a configurable pipeline for document ingestion, text chunking, vector embedding, semantic retrieval, and grounded LLM generation. The project emphasizes reusability, clean abstractions, and production-style deployment.

## Security Gates Across the SDLC

**Strategy:** Fast feedback for developers + comprehensive deep scans off the critical path + required production gate.
- **PRs get fast security checks** (~1 min) - Secrets, SAST, Python security, linting
- **Post-merge auto-deploys to staging** - No additional checks (all validations passed in PR)
- **Nightly deep scans** (15-30 min) - Full rulesets, comprehensive SCA, container/IaC scanning, deep fuzzing. **Required gate before production deployment** (only fails on critical/high)
- **Production deployment is fast** (~1-2 min) - Functional tests only (all security gates passed via nightly deep scan requirement)

This keeps developers productive with **single-pass PR checks** while eliminating redundant scans and maintaining comprehensive security coverage through nightly deep scans that double as production gates.

### 1. Local: Pre-commit Hooks ✅
**Pre-commit hooks** run automatically on every commit to catch issues before they enter version control. Configured via [.pre-commit-config.yaml](.pre-commit-config.yaml):

**✅ Gitleaks** - Detects hardcoded secrets (API keys, tokens, passwords) in staged changes
- Scans only uncommitted files for fast feedback (< 1 second)
- Uses [default rules](https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml) with optional custom config via `.gitleaks.toml`
- Redacts secrets in output to prevent exposure in logs
- Test locally: `pre-commit run gitleaks --files <file>`

**✅ Semgrep** - Multi-language SAST for security vulnerabilities and code quality issues
- Uses `p/ci` ruleset (high-signal, low-false-positive rules optimized for CI)
- Detects SQL injection, XSS, insecure deserialization, and more across multiple languages
- Complementary to Bandit with broader language coverage and different detection patterns
- Defense-in-depth approach: both tools catch issues the other might miss

**✅ Bandit** - Python-specific security linting
- Deep Python security knowledge (unsafe pickle, weak crypto, hardcoded passwords, SQL injection)
- Configured for high-severity issues only to avoid noise
- Scans `src/` directory recursively
- Specialized Python anti-pattern detection complementing Semgrep's broader approach

**✅ Pre-commit-hooks** - Basic file hygiene checks
- `check-yaml`: Validates YAML syntax (prevents broken config files)
- `end-of-file-fixer`: Ensures files end with newline (POSIX standard)
- `trailing-whitespace`: Removes trailing spaces (prevents noisy diffs)
- Works on all file types (YAML, Markdown, Python, etc.)

**✅ Ruff** - Fast Python linter and formatter
- Lints and auto-fixes code quality issues (unused imports, undefined names)
- Formats code for consistency (replaces Black)
- Runs in milliseconds (100x faster than traditional tools)

**Installation:**
```bash
pre-commit install  # Installs hooks to run automatically on commit
pre-commit run --all-files  # Manually run all hooks on entire codebase
```

**❌ Husky + Playwright** *(planned)* - Automated security testing framework for pre-commit hooks. Would execute Playwright-based security tests locally before commits, ensuring security checks run even before code reaches the repository.

### 2. Pre-push: GitHub Protection ✅
**GitHub Push Protection** blocks real-looking secrets from known providers before they reach the repository history.
- Note: Push Protection will block if secrets exist in previous commits. In that scenario, one option is to remove the commits containing secrets from history through an interactive rebase. Or, if your secrets haven't been committed yet, stash your non-problematic files and commit them into a new branch from main. This second option is cleaner and avoids any risk of pushing secrets, but requires that your secrets haven't been committed yet.

![Secrets Example](images/secret-examples.png)

![GitHub Push Protection Example](images/github-push-protection.png)

### 3. Staging Branch: Fast PR Checks + Nightly Validation

**Strategy:** Single comprehensive PR check → immediate deployment on merge. Deep scans run nightly off the critical path.

#### 3a. Pull Request: Fast Security Gate ✅
**Trigger:** PRs to `staging` branch
**Purpose:** Complete security validation before merge - is this safe to merge AND deploy?
**Workflow:** [pr-fast-checks.yml](.github/workflows/pr-fast-checks.yml)
**Time:** ~1 minute

**Fast Guardrails:**
- **✅ Gitleaks** - Secrets scan (~10 seconds)
- **✅ Semgrep** - High-signal SAST with `p/ci` ruleset (~30 seconds)
- **✅ Bandit** - Python SAST, high severity only (~15 seconds)
- **✅ Ruff** - Fast Python linting (~5 seconds)
- **✅ CodeQL** *(GitHub Security UI)* - Advanced semantic SAST using data flow analysis. Enabled via GitHub Security settings (not a workflow file). Tracks how tainted data flows through code to detect complex multi-step vulnerabilities that pattern-matching tools miss. Runs automatically on PRs and pushes. Free for public repositories.
- **❌ Lightweight Fuzzing** *(planned)* - 5-15 minute fuzzing focused on new endpoints/functions introduced in the PR

**SARIF Upload:** Results uploaded to GitHub Security tab for tracking.

**Gate:** All checks must pass before PR can be merged. Once merged, code automatically deploys to staging (no additional security gate).

#### 3b. Nightly: Deep Comprehensive Scans + Production Gate ✅
**Trigger:**
- Push to `staging` branch (required gate before merging to main/production)
- Scheduled daily at 2 AM (comprehensive analysis)
- Manual via workflow_dispatch

**Purpose:** Deep security analysis when no one's waiting on feedback + required gating check before production deployment

**Workflow:** [nightly-deep-scan.yml](.github/workflows/nightly-deep-scan.yml)

**Time:** 15-30 minutes

**Gate Requirement:** Branch protection requires this workflow to pass before staging → main merges. **Only fails on CRITICAL/HIGH severity findings** (medium/low findings are reported but don't block production).

**Comprehensive Scanning:**
- **✅ Semgrep Full Rulesets** - `p/r2c-security-audit`, `p/secrets`, `p/python`, `p/docker` (fails on ERROR severity only)
- **✅ Bandit High Severity** - High severity findings only (critical security issues)
- **✅ OWASP Dependency-Check** - Comprehensive SCA with CVSS 7.0+ threshold (high/critical CVEs)
- **✅ Trivy Critical/High** - Container, IaC, and filesystem scanning for critical/high vulnerabilities
- **✅ OWASP ZAP High Alerts** - Deep DAST scan against staging environment (fails on high/medium alerts)
- **❌ Deep Fuzzing** *(planned)* - 1-2 hour fuzzing against dedicated ephemeral environment with comprehensive API fuzzing, property-based testing, and mutation-based fuzzing

**SARIF Upload:** All findings (including medium/low) uploaded to GitHub Security tab for centralized tracking.

**Production Gate Philosophy:** This workflow serves dual purposes:
1. **Scheduled deep analysis** - Runs nightly at 2 AM for comprehensive security review
2. **Production deployment gate** - Runs when changes are pushed to staging (typically after PR merge), must pass before staging → main merge allowed

Only critical/high severity findings block production deployment, ensuring security-critical issues are caught while allowing teams to address lower-severity findings without blocking releases.

**Build Artifact Security** ❌ *(planned)*
- **❌ Syft** - SBOM generation (CycloneDX, SPDX formats)
- **❌ Grype** - SBOM-based vulnerability scanning of built artifacts
- **Note:** Trivy already provides container/IaC scanning in nightly scans

### 4. Staging Environment: Nightly DAST + Fuzzing

**Trigger:** Scheduled nightly at 5:30 PM PST (testing) / 2 AM (production)

**Purpose:** Deep runtime security testing against staging environment when no one's waiting on deployment.

#### Dynamic Application Security Testing (Nightly)
Included in [nightly-deep-scan.yml](.github/workflows/nightly-deep-scan.yml):

- **✅ OWASP ZAP Deep Scan** - Comprehensive DAST against `https://rag-engine-staging.fly.dev`. Performs thorough automated security testing to detect runtime vulnerabilities including XSS, SQL injection, authentication bypasses, insecure configurations, and authorization flaws that static analysis cannot find.

**Why Nightly?** DAST scans can take 5-15+ minutes for thorough coverage. Running nightly keeps deployment fast (~immediate) while ensuring comprehensive runtime testing happens off the critical path.

#### Fuzzing Strategy ❌ *(planned)*
Multi-tier fuzzing approach testing application behavior under unexpected inputs:

**Lightweight PR Fuzzing (5-15 minutes)**
- Runs during PR fast checks (see Section 3a)
- Focuses on new endpoints/functions introduced in the PR
- Quick smoke test for obvious input validation bugs

**Nightly Deep Fuzzing (1-2 hours)**
- Runs in [nightly-deep-scan.yml](.github/workflows/nightly-deep-scan.yml) against dedicated ephemeral environment
- Comprehensive API fuzzing (REST, GraphQL endpoints)
- Property-based testing with hypothesis/schemathesis
- Mutation-based fuzzing (AFL++, libFuzzer for Python C extensions)
- Collects crash reports and coverage data
- Environment automatically torn down after fuzzing

**Benefits:** Discovers edge cases, input validation bugs, crashes, and unexpected behavior that static analysis and scripted DAST cannot find.

**Deployment:** Merging to staging triggers [deploy-staging.yml](.github/workflows/deploy-staging.yml) which immediately deploys to Fly.io staging environment.

**Note:** Falco runtime monitoring would run continuously ON the staging Fly.io environment (not as a GitHub Action workflow)

### 5. Production Branch: Deployment Only (Security Gates Already Passed)

**Trigger:** Merges from `staging` → `main` branch (production)

**Purpose:** Deploy to production immediately - all security gates already passed via nightly-deep-scan.yml requirement.

**Workflow:** [deploy.yml](.github/workflows/deploy.yml)

**Time:** ~1-2 minutes

**Steps:**
- **✅ pytest** - Functional test suite validation (~30-60 seconds)
- **✅ Fly.io deployment** - Deploy to production (~30-60 seconds)

**Security Philosophy:**
- **No redundant security checks** - Branch protection requires nightly-deep-scan.yml to pass before allowing staging → main merge
- **Trust but verify architecture** - All critical/high security findings already validated by production gate
- **Fast deployment** - Zero security scan overhead, only functional testing before production push

**Protection Layers:**
1. PR to staging: Fast comprehensive checks (pr-fast-checks.yml)
2. Staging → main: Deep security scan required (nightly-deep-scan.yml) - **MUST PASS**
3. Main deploy: Functional tests only (deploy.yml)
  - Human error in merge process

**SARIF Upload:** Results uploaded to GitHub Security tab with `semgrep-production` category.

#### Supply Chain Attestation ❌ *(planned)*
- **❌ SLSA Provenance** - Generate cryptographic proof of how the production artifact was built, including source commit, build system, and build steps. GitHub Actions can generate signed provenance JSON attesting that "this production deployment came from staging branch X at commit Y, built by GitHub runner Z". Enables verification that artifacts weren't tampered with and prevents deployment of locally-built artifacts that bypass CI/CD pipeline.

**Deployment:** If all checks pass, auto-deploy to Fly.io production environment.

### 6. Production Environment: Runtime Monitoring ❌ *(planned)*

**Purpose:** Continuous monitoring of production environment to detect active exploitation attempts and suspicious behavior in real-time.

#### Runtime Threat Detection
- **❌ Falco** - CNCF-graduated eBPF-based runtime security monitoring deployed ON production Fly.io environment (as sidecar container or VM agent). Monitors kernel-level events in real-time with minimal overhead to detect:
  - Reverse shell attempts
  - Privilege escalation
  - Crypto mining activity
  - Unauthorized file access
  - Container escape attempts
  - Suspicious network connections

**Deployment:** Runs continuously as infrastructure-level monitoring (not a GitHub Action). Alerts integrate with incident response stack (Slack, PagerDuty, CloudWatch).

**Key Difference from DAST:** ZAP (Section 4) actively probes for vulnerabilities in staging. Falco (Section 6) passively monitors for active attacks in production.
