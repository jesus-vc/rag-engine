# Reusable RAG Engine

A modular Retrieval-Augmented Generation (RAG) engine designed to power question-answering services across multiple, independent knowledge bases.

## Overview

**rag-engine** provides a configurable pipeline for document ingestion, text chunking, vector embedding, semantic retrieval, and grounded LLM generation. The project emphasizes reusability, clean abstractions, and production-style deployment.

## Security Gates Across the SDLC

**Strategy:** Fast feedback for developers + comprehensive deep scans off the critical path.
- **PRs get fast checks** (~1-2 min) - Secrets, high-signal SAST, Python security, linting
- **Post-merge runs moderate checks** (~3-4 min) - PR checks + dependency scanning
- **Nightly deep scans** (15-30 min) - Full rulesets, comprehensive SCA, container/IaC scanning, deep fuzzing
- **Production gate is fast** (~1-2 min) - Critical checks only (dependency scans run nightly)

This keeps developers productive (no 15-minute PR wait times) while maintaining comprehensive security coverage through nightly deep scans.

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

### 3. Staging Branch: Fast PR Checks + Post-Merge Validation

**Strategy:** Fast feedback on PRs (< 3 min) keeps developers productive. Deep comprehensive scans run nightly when no one's waiting.

#### 3a. Pull Request: Fast Security Gate ✅
**Trigger:** PRs to `staging` branch
**Purpose:** Quick safety check - is this safe to merge RIGHT NOW?
**Workflow:** [pr-fast-checks.yml](.github/workflows/pr-fast-checks.yml)
**Time:** ~1-2 minutes

**Fast Guardrails:**
- **✅ Gitleaks** - Secrets scan (~10 seconds)
- **✅ Semgrep** - High-signal SAST with `p/ci` ruleset (~30 seconds)
- **✅ Bandit** - Python SAST, high severity only (~15 seconds)
- **✅ Ruff** - Fast Python linting (~5 seconds)
- **✅ CodeQL** *(GitHub Security UI)* - Advanced semantic SAST using data flow analysis. Enabled via GitHub Security settings (not a workflow file). Tracks how tainted data flows through code to detect complex multi-step vulnerabilities that pattern-matching tools miss. Runs automatically on PRs and pushes. Free for public repositories.
- **❌ Lightweight Fuzzing** *(planned)* - 5-15 minute fuzzing focused on new endpoints/functions introduced in the PR

**SARIF Upload:** Results uploaded to GitHub Security tab for tracking.

#### 3b. Post-Merge: Moderate Security Validation ✅
**Trigger:** Push to `staging` branch (after PR merge)
**Purpose:** Moderate checks before staging deployment
**Workflow:** [staging-post-merge.yml](.github/workflows/staging-post-merge.yml)
**Time:** ~3-4 minutes

**Additional Checks:**
- All PR checks (Gitleaks, Semgrep, Bandit, Ruff)
- **✅ pip-audit** - Fast Python dependency vulnerability scan (~1-2 minutes)

**Blocks Deployment:** If checks fail, deployment to staging environment is blocked via workflow dependency.

#### 3c. Nightly: Deep Comprehensive Scans ✅
**Trigger:** Scheduled daily at 2 AM
**Purpose:** Deep security analysis when no one's waiting on feedback
**Workflow:** [nightly-deep-scan.yml](.github/workflows/nightly-deep-scan.yml)
**Time:** 15-30 minutes

**Comprehensive Scanning:**
- **✅ Semgrep Full Rulesets** - `p/r2c-security-audit`, `p/secrets`, `p/python`, `p/docker` (comprehensive rule coverage)
- **✅ Bandit All Severities** - Low, medium, and high severity findings
- **✅ pip-audit** - Complete Python dependency audit
- **✅ OWASP Dependency-Check** - Comprehensive SCA covering all ecosystems and transitive dependencies
- **✅ Trivy** - Container, IaC, and filesystem scanning for vulnerabilities, misconfigurations, and secrets
- **❌ Deep Fuzzing** *(planned)* - 1-2 hour fuzzing against dedicated ephemeral environment with comprehensive API fuzzing, property-based testing, and mutation-based fuzzing

**SARIF Upload:** All findings uploaded to GitHub Security tab for centralized tracking.

**Build Artifact Security** ❌ *(planned)*
- **❌ Syft** - SBOM generation (CycloneDX, SPDX formats)
- **❌ Grype** - SBOM-based vulnerability scanning of built artifacts
- **Note:** Trivy already provides container/IaC scanning in nightly scans

### 4. Staging Environment: Runtime Testing (DAST + Fuzzing)

**Trigger:** After successful deployment to staging environment (production mirror)

**Purpose:** Detect runtime vulnerabilities that only manifest in running applications. High/Critical findings block staging → production promotion.

#### Dynamic Application Security Testing
[deploy-staging-scan.yml](.github/workflows/deploy-staging-scan.yml) runs security scans against live staging environment:

- **✅ OWASP ZAP** - Containerized DAST scanner that performs automated security testing against `https://rag-engine-staging.fly.dev`. Detects runtime vulnerabilities including XSS, SQL injection, authentication bypasses, insecure configurations, and authorization flaws that static analysis cannot find.

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

**Note:** Falco runtime monitoring would run continuously ON the staging Fly.io environment (not as a GitHub Action workflow)

**Merge Gate:** High and Critical severity findings must be fixed before merging `staging` → `main` branch.

### 5. Production Branch: Fast Critical Security Gate & Deployment

**Trigger:** Merges from `staging` → `main` branch (production)

**Purpose:** Fast final safety net before production deployment. Re-runs critical checks only (no slow dependency scans - those run nightly).

**Workflow:** [deploy.yml](.github/workflows/deploy.yml)
**Time:** ~1-2 minutes

#### Critical Checks Only ✅
- **✅ Gitleaks** - Final secret scan before production (~10 seconds)
- **✅ Semgrep** - Critical SAST with `p/ci` ruleset (~30 seconds)
- **✅ Bandit** - Python security, high severity only (~15 seconds)

**Rationale for Fast Checks:**
- **No slow dependency scans** - pip-audit and OWASP Dependency-Check run nightly (comprehensive) and on staging (moderate). Production gate only re-runs critical fast checks to avoid deployment delays.
- **Defense-in-depth** - Protects against:
  - Direct commits to main (bypassing staging)
  - Time-gap vulnerabilities (new critical issues between staging merge and production push)
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
