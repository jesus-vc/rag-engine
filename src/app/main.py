import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import Query

# Environment-based configuration
APP_NAME = os.getenv("APP_NAME", "rag-engine")
APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "0.2.0")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)


@app.get("/")
def root():
    return HTMLResponse(
        """
      <form action="/login" method="post">
        <input name="username" />
        <input name="password" />
      </form>
    """
    )


@app.get("/version")
def version_info():
    return {"app": APP_NAME, "version": APP_VERSION}


@app.get("/health")
def health_check():
    """
    Health check endpoint used by:
    - CI tests
    - Fly.io health checks
    - Humans verifying the service is alive
    """
    return {
        "status": "ok",
        "app": APP_NAME,
        "env": APP_ENV,
        "version": APP_VERSION,
    }


# /login gives ZAP scanner parameterized input, auth logic to attack, credential handling patterns
@app.post("/login")
def login(username: str = Query(...), password: str = Query(...)):
    if username == "admin" and password == "password":
        return {"token": "test-token"}
    return {"error": "invalid credentials"}, 401


# Zap scanner should trigger missing auth checks (CWE-862)
@app.get("/secure-data")
def secure_data(token: str | None = None):
    if token != "test-token":
        return {"error": "unauthorized"}, 401
    return {"data": "classified"}


# Zap scanner should trigge XSS finding
# Zap schould try to inject:
# <script>alert(1)</script>
# SQL-like payloads
# Encoding tricks
@app.get("/echo")
def echo(q: str):
    return {"echo": q}


# Insecure test code - do not use in production
def unsafe():
    eval("print('hello')")
