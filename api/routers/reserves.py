from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from src.fetch_reserves import fetch_reserves_data
from api.dependencies import verify_api_key
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/reserves", tags=["Reserves"], dependencies=[Depends(verify_api_key)])

@router.get("/")
@cache(expire=86400)  # Cache for 24 hours (Reserves are weekly)
async def get_reserves(days: int = 90):
    """
    Get Bank Reserves data.
    """
    start_date = datetime.now() - timedelta(days=days)
    df = fetch_reserves_data(start_date=start_date)
    if df is None:
        return {"error": "Failed to fetch data"}
    
    return df.to_dict(orient="records")
