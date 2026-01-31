import os
from fastapi import FastAPI

# Environment-based configuration
APP_NAME = os.getenv("APP_NAME", "rag-engine")
APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "0.2.0")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)


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
