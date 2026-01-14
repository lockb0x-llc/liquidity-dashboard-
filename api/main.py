from fastapi import FastAPI
from api.routers import onrrp, sofr, reserves, treasury, srf
from api.dependencies import init_cache
import uvicorn
import os

app = FastAPI(
    title="Liquidity Stress API",
    description="API for Federal Reserve and Treasury liquidity indicators.",
    version="1.0.0"
)

# Startup event to initialize cache
@app.on_event("startup")
async def startup():
    await init_cache()

# Include routers
app.include_router(onrrp.router)
app.include_router(sofr.router)
app.include_router(reserves.router)
app.include_router(treasury.router)
app.include_router(srf.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
