#!/usr/bin/env python3
"""
Security Finding Correlation Script

Demonstrates how combining code-level (Semgrep) and runtime (Trivy) findings 
reveals critical exploit chains that individual tools might not highlight.
"""
import json


def load_semgrep_findings():
    """Load Semgrep JSON report"""
    with open("reports/semgrep-report.json") as f:
        data = json.load(f)
    return data.get("results", [])


def load_trivy_findings():
    """Load Trivy JSON report"""
    with open("reports/trivy-report.json") as f:
        data = json.load(f)
    # Trivy structure: Results[0].Vulnerabilities and Misconfigurations
    if data.get("Results"):
        return data["Results"][0]
    return {}


def analyze_correlation():
    """Correlate findings to identify exploit chains"""

    print("=" * 70)
    print("SECURITY FINDING CORRELATION ANALYSIS")
    print("=" * 70)
    print()

    # Load findings
    semgrep_findings = load_semgrep_findings()
    trivy_data = load_trivy_findings()

    # Code-level vulnerabilities
    print("📋 CODE-LEVEL FINDINGS (Semgrep)")
    print("-" * 70)
    code_vulns = []
    for finding in semgrep_findings:
        vuln_type = finding.get("check_id", "unknown")
        severity = finding.get("extra", {}).get("severity", "UNKNOWN")
        line = finding.get("start", {}).get("line", "?")

        print(f"  ✗ {vuln_type}")
        print(f"    Location: app.py:{line}")
        print(f"    Severity: {severity}")
        print("    Reachable: Yes (network-exposed endpoint)")
        print()

        code_vulns.append(
            {
                "type": "command_injection",
                "severity": severity,
                "reachable": True,
                "auth_required": False,
            }
        )

    # Container-level findings
    print("🐳 CONTAINER-LEVEL FINDINGS (Trivy)")
    print("-" * 70)

    runs_as_root = False
    os_cves = []

    # Check misconfigurations
    misconfigs = trivy_data.get("Misconfigurations", [])
    for misconfig in misconfigs:
        if "root" in misconfig.get("Title", "").lower():
            runs_as_root = True
            print("  ✗ Container runs as root")
            print("    Severity: MEDIUM")
            print()

    # Check OS vulnerabilities
    vulns = trivy_data.get("Vulnerabilities", [])
    if vulns:
        print(f"  ✗ {len(vulns)} OS package vulnerabilities")
        # Sample a few critical ones
        critical = [v for v in vulns if v.get("Severity") == "CRITICAL"][:3]
        for vuln in critical:
            pkg = vuln.get("PkgName", "unknown")
            cve = vuln.get("VulnerabilityID", "unknown")
            print(f"    - {cve} in {pkg}")
            os_cves.append(cve)
        print()

    # CORRELATION ANALYSIS
    print("=" * 70)
    print("🔗 CORRELATION ANALYSIS - EXPLOIT CHAIN DETECTION")
    print("=" * 70)
    print()

    if code_vulns and runs_as_root:
        print("⚠️  CRITICAL RISK DETECTED")
        print()
        print("Exploit Chain:")
        print("  1. Attacker sends malicious input to /ping endpoint")
        print("  2. Command injection executes arbitrary OS commands")
        print("  3. Commands execute as ROOT inside container")
        print("  4. Vulnerable OS packages available for exploitation")
        print()
        print("Impact: FULL CONTAINER COMPROMISE")
        print()
        print("Risk Escalation:")
        print("  • Code vulnerability alone: HIGH")
        print("  • Container misconfiguration alone: MEDIUM")
        print("  • Combined (correlated): CRITICAL ⚠️")
        print()

        # Mitigation recommendations
        print("Mitigation Priority:")
        print("  1. Fix command injection (breaks exploit chain)")
        print("  2. Run container as non-root user (reduces blast radius)")
        print("  3. Update vulnerable OS packages")
        print()

        return "CRITICAL"
    else:
        print("ℹ️  No critical exploit chains detected")
        return "MEDIUM"


if __name__ == "__main__":
    try:
        risk_level = analyze_correlation()
        print("=" * 70)
        print(f"OVERALL RISK LEVEL: {risk_level}")
        print("=" * 70)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure to run semgrep and trivy scans first:")
        print(
            "  semgrep --config semgrep-rules.yaml --json --output reports/semgrep-report.json app.py"
        )
        print(
            "  trivy image --format json --output reports/trivy-report.json vuln-poc:latest"
        )
