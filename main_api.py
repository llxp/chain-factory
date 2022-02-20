from logging import info
from os import getenv


if __name__ == "__main__":
    import uvicorn
    host = getenv('HOST', '0.0.0.0')
    port = getenv('PORT', '8005')
    info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "api.main:app",
        host=host,
        port=int(port),
        log_level="debug",
        reload=True,
    )
