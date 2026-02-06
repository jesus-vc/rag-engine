# Mitigation Guide

## Vulnerability: Command Injection + Root Container

### Current Risk: CRITICAL
- Command injection in code (Semgrep)
- Container runs as root (Trivy)
- Combined: Full container compromise possible

---

## Fix #1: Eliminate Command Injection (PRIMARY)

### Before (Vulnerable):
```python
host = request.args.get("host")
return os.popen(f"ping -c 1 {host}").read()
```

### After (Fixed - Option A: Input Validation):
```python
import shlex

host = request.args.get("host")
safe_host = shlex.quote(host)  # Escapes shell metacharacters
return os.popen(f"ping -c 1 {safe_host}").read()
```

### After (Fixed - Option B: No Shell):
```python
import subprocess

host = request.args.get("host")
result = subprocess.run(
    ["ping", "-c", "1", host],
    shell=False,  # No shell = no injection
    capture_output=True,
    timeout=5
)
return result.stdout.decode()
```

**Impact**: Breaks the exploit chain → Risk drops to MEDIUM

---

## Fix #2: Run Container as Non-Root (SECONDARY)

### Before (Vulnerable Dockerfile):
```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
USER root  # ❌ INSECURE
CMD ["python", "app.py"]
```

### After (Fixed Dockerfile):
```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser  # ✅ SECURE
CMD ["python", "app.py"]
```

**Impact**: Limits blast radius → Even if exploited, not root

---

## Fix #3: Update Base Image

### Before:
```dockerfile
FROM python:3.8-slim  # Old, has CVEs
```

### After:
```dockerfile
FROM python:3.12-slim  # Latest, fewer CVEs
```

**Impact**: Reduces OS-level vulnerabilities

---

## Combined Fix (Defense in Depth)

Apply ALL THREE fixes:

1. ✅ No command injection (secure code)
2. ✅ Non-root user (container hardening)
3. ✅ Updated base image (reduced attack surface)

**Result**: Risk drops from CRITICAL to LOW

---

## Verification

### Test that injection no longer works:
```bash
# Build fixed image
docker build -t vuln-poc:fixed -f Dockerfile.fixed .

# Run it
docker run -d -p 5002:5000 vuln-poc:fixed

# Try to exploit (should fail)
curl "http://localhost:5002/ping?host=127.0.0.1;id"
# No longer shows uid=0(root) or executes id command

# Verify runs as non-root
docker exec $(docker ps -q --filter ancestor=vuln-poc:fixed) whoami
# Should show: appuser (not root)
```

### Re-scan with tools:
```bash
# Semgrep should show no findings
semgrep --config semgrep-rules.yaml app-fixed.py

# Trivy should not flag root user
trivy image vuln-poc:fixed
```
