from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from src.fetch_treasury import fetch_treasury_data
from api.dependencies import verify_api_key
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/treasury", tags=["Treasury"], dependencies=[Depends(verify_api_key)])

@router.get("/")
@cache(expire=3600)  # Cache for 1 hour
async def get_treasury(days: int = 30):
    """
    Get Treasury auction data.
    """
    start_date = datetime.now() - timedelta(days=days)
    df = fetch_treasury_data(start_date=start_date)
    if df is None:
        return {"error": "Failed to fetch data"}
    
    return df.to_dict(orient="records")
