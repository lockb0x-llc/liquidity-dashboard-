from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from src.fetch_srf import fetch_srf_data
from api.dependencies import verify_api_key
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/srf", tags=["SRF"], dependencies=[Depends(verify_api_key)])

@router.get("/")
@cache(expire=3600)  # Cache for 1 hour
async def get_srf(days: int = 30):
    """
    Get SRF (Standing Repo Facility) data.
    """
    start_date = datetime.now() - timedelta(days=days)
    df = fetch_srf_data(start_date=start_date)
    if df is None:
        return {"error": "Failed to fetch data"}
    
    return df.to_dict(orient="records")
