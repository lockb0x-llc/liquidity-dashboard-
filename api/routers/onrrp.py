from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from src.fetch_onrrp import fetch_onrrp_data
from api.dependencies import verify_api_key
import pandas as pd

router = APIRouter(prefix="/api/v1/onrrp", tags=["ON RRP"], dependencies=[Depends(verify_api_key)])

@router.get("/")
@cache(expire=3600)  # Cache for 1 hour
async def get_onrrp(mode: str = "last_n", last_n: int = 30):
    """
    Get ON RRP data.
    """
    df = fetch_onrrp_data(mode=mode, last_n=last_n)
    if df is None:
        return {"error": "Failed to fetch data"}
    
    # Convert DataFrame to JSON serializable format
    # FastAPI automatically converts dict to JSON
    return df.to_dict(orient="records")
