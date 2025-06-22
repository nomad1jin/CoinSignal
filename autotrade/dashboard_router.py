from fastapi import FastAPI, APIRouter
from autotrade.trend import get_trend_top5
import pyupbit
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
upbit = pyupbit.Upbit(os.getenv("access"), os.getenv("secret"))

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

@router.get("/performance")
def get_investment_performance():
    balances = upbit.get_balances() #잔액
    profit_krw = 0  #원화 이익
    total_invest = 0    #총 투자금액

    for b in balances:
        if b['currency'] == 'KRW' or float(b['balance']) == 0:
            continue
        ticker = f"KRW-{b['currency']}"
        try:
            current_price = pyupbit.get_current_price(ticker)
            avg_price = float(b['avg_buy_price'])
            amount = float(b['balance'])

            profit = (current_price - avg_price) * amount   #(현재가-평균매입가) * 수량
            profit_krw += profit    
            total_invest += avg_price * amount  #총 투자금액: 평균가 * 수량
        except:
            continue

    rate = round((profit_krw / total_invest) * 100, 2) if total_invest else 0
    return {
        "success": True,
        "message": "투자 현황 - 최근 7일 수익률", 
        "data": {
            "return_rate": rate,
            "return_krw": int(profit_krw)
        }
    }

@router.get("/allocation")
def get_allocation():
    balances = upbit.get_balances()
    allocation = {}     #원그래프 할당
    total_krw = 0   #총 투자 금액

    for b in balances:
        currency = b["currency"]
        if float(b["balance"]) == 0:
            continue

        if currency == "KRW":
            krw_val = float(b["balance"])
            allocation["현금"] = krw_val
            total_krw += krw_val
        else:
            ticker = f"KRW-{currency}"
            try:
                current_price = pyupbit.get_current_price(ticker)
                value = float(b["balance"]) * current_price
                allocation[currency] = value
                total_krw += value
            except:
                continue

    result = [
        {
            #이렇게 나올예정
            #{"coin": "비트코인", "percent": 50.8, "value": 488000}
            "coin": coin,
            "percent": round(value / total_krw * 100, 1),
            "value": int(value)
        } for coin, value in allocation.items()
    ]
    return {
        "success": True,
        "message": "투자 비중 - 원그래프", 
        "data": {
            "total_value": int(total_krw),
            "allocation": sorted(result, key=lambda x: -x["percent"])
        }

    }


@router.get("/history")
def get_recent_order():
    try: 
        orders = upbit.get_order_list(state="done", kind="normal")

        recent = []
        for order in sorted(orders, key=lambda x: x["created_at"], reverse=True)[:5]:
            recent.append({
                "coin": order["market"].replace("KRW-", ""),
                "side": "매수" if order["side"] == "bid" else "매도",
                "price": float(order["price"]),
                "volume": float(order["volume"]),
                "total": float(order["price"]) * float(order["volume"]),
                "time": order["created_at"]
            })

        return {
            "success": True,
            "message": "최근 체결 내역 5개",
            "data": recent
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"체결 내역 조회 실패: {str(e)}",
            "data": None
        }