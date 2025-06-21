# autotrade_router.py

from fastapi import APIRouter, Query
import time
from autotrade.trend import analyze_trend
from autotrade.crawling_data import twitter_search, fetch_reddit_posts
from autotrade.analyze_sentiment import build_coin_data_from_csv
from autotrade.automated_trading import evaluate_trades, execute_trades, get_current_holdings
from autotrade.user_router import user_settings_store

import logging

router = APIRouter()

# COIN_LIST = ['bitcoin', 'ethereum', 'solana', 'tron', 'dogecoin', 'xrp', 'ada', 'sui']
COIN_LIST = ['bitcoin', 'ethereum']

# coin_list를 두고 이에 대한 트렌드+크롤링+감정분석+자동매매
@router.post("/autotrade/start")
def start_autotrade():
    if "default" not in user_settings_store:
        return {"success": False, "message": "사용자 설정이 없습니다. 먼저 설정을 저장하세요.", "data": None}

    user_settings = user_settings_store["default"]
    holdings = get_current_holdings()

    all_coin_data = {}

    for coin in COIN_LIST:
        is_hot, trend_score = analyze_trend(coin)
        if not is_hot:
            continue    # 급상승 아니면 크롤링·감정분석 생략

        # 🔍 크롤링
        twitter_search(coin)
        fetch_reddit_posts(coin)

        # 📊 감정 분석 결과 저장
        coin_data = build_coin_data_from_csv(coin, trend_score, holdings)
        all_coin_data.update(coin_data)

##### 만약에 급상승 코인이 없으면, 그냥 아래 return을 하고 끝남. 크롤링과 감정분석 X
    if not all_coin_data:
        return {"success": False, "message": "📉 분석된 코인이 없습니다.", "data": None}

    # 💡 매수/매도 판단
    buy_order, sell_order = evaluate_trades(all_coin_data, user_settings)

    # 💰 실제 매매 실행
    execute_trades(buy_order, sell_order)

    return {
        "success": True,
        "message": "🚀 자동매매가 실행되었습니다.",
        "data": {
            "buy_order": buy_order,
            "sell_order": sell_order
        }
    }


@router.post("/autotrade/start/coin")
def start_autotrade_coin(coin: str = Query(..., description="코인 이름(예:bitcoin)")):
    if "default" not in user_settings_store:
        return {"success": False, "message": "사용자 설정이 없습니다. 먼저 설정을 저장하세요.", "data": None}

    coin = coin.strip().lower()
    user_settings = user_settings_store["default"]
    holdings = get_current_holdings()

    # 급상승할 때까지 반복
    max_retry = 10
    retry_delay = 60  # 60초 간격
    retry_count = 0

    while True:
        is_hot, trend_score = analyze_trend(coin)
        if is_hot:
            break

        retry_count += 1
        if retry_count >= max_retry:
            return {
                "success": False,
                "message": f"📉 [{coin}]은 {max_retry}회 확인했지만 급상승하지 않았습니다.",
                "data": None
            }

        print(f"🔁 [{coin}] 급상승 아님 → {retry_delay}초 후 재시도 ({retry_count}/{max_retry})")
        time.sleep(retry_delay)

    # 🔍 크롤링
    logging.info("\n🔥 급등한" f"{coin}코인의 트위터 데이터 크롤링")
    twitter_search(coin)
    logging.info("\n🔥 급등한" f"{coin}코인의 레딧 데이터 크롤링")
    fetch_reddit_posts(coin)

    # 📊 감정 분석
    coin_data = build_coin_data_from_csv(coin, trend_score, holdings)
    logging.info(f"[{coin}] 감정 분석 결과: {coin_data}")

    # 💡 매매 판단 + 실행
    buy_order, sell_order = evaluate_trades(coin_data, user_settings)
    execute_trades(buy_order, sell_order)

    return {
        "success": True,
        "message": f"🚀 자동매매가 [{coin}]에 대해 실행되었습니다.",
        "data": {
            "coin": coin,
            "buy_order": buy_order,
            "sell_order": sell_order
        }
    }



