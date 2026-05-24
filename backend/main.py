from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import upload, analyze, violations, dashboard, sync
from config import settings

app = FastAPI(
    title="Regulatory Compliance Intelligence Engine",
    description="AI-powered compliance analysis for RBI circulars and internal SOPs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(violations.router, prefix="/api", tags=["Violations"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(sync.router, prefix="/api", tags=["RBI Sync"])


@app.get("/")
async def root():
    return {"message": "Regulatory Compliance Intelligence Engine API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
