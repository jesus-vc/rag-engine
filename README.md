# Reusable RAG Engine

A modular Retrieval-Augmented Generation (RAG) engine designed to power question-answering services across multiple, independent knowledge bases.

## Overview

**rag-engine** provides a configurable pipeline for document ingestion, text chunking, vector embedding, semantic retrieval, and grounded LLM generation. The project emphasizes reusability, clean abstractions, and production-style deployment.

## Security Checks Across the SDLC

### 1. Pre-commit (Local)
**GitLeaks** provides local and offline scanning to catch secrets before they're committed:
- Helps debug false positives
- Tests new detection logic locally
- Command: `gitleaks detect --source .` scans using built-in default rules
- Optional: Use `--config .gitleaks.toml` for custom allowlists and rules

![Gitleaks Pre-commit Scan Example](images/gitleaks-precommit-scan.png)

### 2. Pre-push (GitHub)
**GitHub Push Protection** blocks real-looking secrets from known providers before they reach the repository history.
- Note: Push Protection will block if secrets exist in previous commits. In that scenario, one option is to remove the commits containing secrets from history through an interactive rebase. Or, if your secrets haven't been committed yet, stash your non-problematic files and commit them into a new branch from main. This second option is cleaner and avoids any risk of pushing secrets, but requires that your secrets haven't been committed yet.

![Secrets Example](images/secret-examples.png)

![GitHub Push Protection Example](images/github-push-protection.png)

### 3. Post-push (GitHub Actions)
- **GitLeaks GitHub Action** - Scans commits in pull requests and pushes to main
- **CodeQL** *(planned)* - Static code analysis for security vulnerabilities

---

## Roadmap: Future Security Enhancements
- Husky hooks with Playwright for automated security tests before commits and pushes 
- Source Stage
- Build Stage
- Release State

### 2 Types of Static Code Analysis (SCA)
    - Software Composition Analysis (SCA)
        - scann libraries (Software of Unknown Provenance).
    - Static Application Security Testing (SAST)
        - scans for coding errors. 

    - You want to run Static Code Analysis during Dev, Soruce, and Build stages. 
    
### Dev IDE Stage
    - IDE add-ons for Static Code Analysis
    - Secret Scanner
    - Pre-commit hooks
        - Secret scanning, linting
### Source Stage
    - Github Actions running Static Code Analysis, to detect new vulnerabilites.
### Build Stage
    - Static Code Analysis 
    - Software Bill of Materials (SBOM). Generating a list of all 3rd-party library versions in repository during build. Store SBOM (e.g. in S3 bucket) to quickly scan critical, zero-day vulnerabilities.
    - Software Composition Analysis can be performed on SBOM.
    - Note: New artifacts are created and derived outputs such as: /dist with minified JS/CSS derived from React code, Docker images derived from source code and Dockerfile, Java app.jar file derived from .java files.
### Test Stage
    - Dynamic App. Security Testing (DAST) to scan running applications and APIs.
### Release Stage
    - Scanning container images
    - Vulnerability scanning
### Reporting
    - Leverage scan results, SBOM
    - SLSA ("salsa")
        - framework to protect the integrity of the software supply chain.
        - Signed provenance. Cryptographically prove how an artifact was built, including the source, build system, and steps involved. It prevents tampering in the CI/CD pipeline, enables supply-chain trust, and allows us to enforce deployment policies so only verified, compliant artifacts reach production.
        - Protects agains build pipeline attacks such as someone building artifacts locally and sneaking them into prod, a compromised CI runner, malicious dependency injected at build time. Tools such as GitHub actions can generate provenance JSON. 