from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="BikeStop")

@app.get("/api/health")
def health():
    return {"ok": True}

FRONTEND_DIST = os.getenv("FRONTEND_DIST", "frontend_dist")
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index_path)
