# Security Tool Correlation POC

**⚠️ WARNING: This is a deliberately vulnerable application for security testing. DO NOT deploy to production.**

## Purpose

Demonstrates how correlating findings from multiple security tools reveals critical exploit chains that individual tools might not highlight.

## The Vulnerability Chain

### Code-Level Vulnerability (Semgrep)
- **Finding**: Command injection in `/ping` endpoint
- **Severity**: High
- **Reachability**: Yes (network-exposed, no authentication)
- **Source**: `request.args.get("host")`
- **Sink**: `os.popen()`

### Container-Level Weaknesses (Trivy)
- **Finding**: Container runs as root
- **Finding**: Outdated base image with known CVEs (bash, coreutils, glibc)
- **Severity**: Medium (individually)

### Correlated Risk: CRITICAL
When combined:
1. Attacker injects commands via `/ping?host=; malicious_command`
2. Commands execute as **root** inside container
3. Vulnerable OS binaries available for exploitation
4. Full container compromise possible

**Individual findings**: High + Medium  
**Correlated risk**: **CRITICAL** (complete exploit chain)

## Setup & Testing

### 1. Install Tools
```bash
# Semgrep
pip install semgrep

# Trivy (macOS)
brew install trivy
```

### 2. Run Semgrep Scan
```bash
cd vuln-poc
semgrep --config semgrep-rules.yaml app.py
```

**Expected Output**:
- Command injection finding at line 13
- Taint flow: request.args.get → os.popen
- Severity: ERROR

### 3. Build & Scan Container
```bash
# Build vulnerable image
docker build -t vuln-poc:latest .

# Scan with Trivy
trivy image vuln-poc:latest
```

**Expected Output**:
- OS package CVEs (bash, glibc, etc.)
- Misconfiguration: runs as root
- Medium/High severity findings

### 4. Test Exploitation (Local Only!)
```bash
# Run container
docker run -p 5000:5000 vuln-poc:latest

# Benign test
curl "http://localhost:5000/ping?host=google.com"

# Malicious payload (command injection)
curl "http://localhost:5000/ping?host=127.0.0.1;id"
# Output shows: uid=0(root) - proves root execution

# Cleanup
docker stop $(docker ps -q --filter ancestor=vuln-poc:latest)
```

## Correlation Analysis

### Risk Scoring Matrix

| Code Vuln | Container Risk | Auth Required | Combined Risk |
|-----------|---------------|---------------|---------------|
| Command Injection | Runs as root | No | **CRITICAL** |
| Command Injection | Non-root user | No | HIGH |
| Command Injection | Runs as root | Yes | HIGH |
| None | Runs as root | N/A | MEDIUM |

### Mitigation Impact

**Fix 1: Input validation** (breaks exploit chain)
```python
import shlex
host = shlex.quote(request.args.get("host"))
```
Result: Code vuln eliminated → Risk drops to MEDIUM

**Fix 2: Non-root container** (reduces blast radius)
```dockerfile
USER appuser
```
Result: Container compromise limited → Risk drops to HIGH

**Both fixes**: Risk drops to LOW

## Interview Talking Points

> "I built a POC demonstrating security tool correlation. Individually, Semgrep found command injection and Trivy found container weaknesses—both common findings. By correlating them, I showed that an unauthenticated attacker could achieve root-level RCE, elevating the risk from 'high' to 'critical'. This demonstrates understanding of attack chains beyond individual tool outputs."

## Key Learnings

1. **Tools have blind spots** - Semgrep doesn't know runtime context, Trivy doesn't know code paths
2. **Context elevates risk** - Same code vuln has different risk based on deployment
3. **Defense in depth works** - Breaking any link in the chain significantly reduces risk
4. **Correlation requires intelligence** - Automated tools need human analysis to reveal chains

## Cleanup

```bash
# Remove container
docker rmi vuln-poc:latest

# This POC should never leave your local machine
```
