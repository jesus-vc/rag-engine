"""
Deliberately vulnerable Flask app for security tool correlation POC.
DO NOT USE IN PRODUCTION.

Demonstrates: Command injection vulnerability + container security issues
"""
from flask import Flask, request
import os

app = Flask(__name__)


@app.route("/ping")
def ping():
    """Vulnerable endpoint - accepts user input without validation"""
    host = request.args.get("host")
    # VULNERABLE: User input flows directly to shell command
    return os.popen(f"ping -c 1 {host}").read()


@app.route("/")
def index():
    return "Vulnerable POC App - Use /ping?host=example.com"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
