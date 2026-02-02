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
