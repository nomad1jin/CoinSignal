from fastapi import FastAPI, APIRouter
from autotrade.trend import get_trend_top5

router = APIRouter()

@router.get("/trending")
def get_trending():
    # coin_list = ['bitcoin', 'ethereum', 'tether', 'ripple', 'solana', 'USD Coin', 'tron', 'dogecoin', 'ada', 'sui']
    coin_list = ['solana', 'ada', 'tron']
    top5 = get_trend_top5(coin_list)
    return {
        "success": True,
        "message": "지금 핫한 코인 top5", 
        "data": top5
    }