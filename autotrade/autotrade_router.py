# autotrade_router.py

from fastapi import APIRouter, Query
import time
from datetime import datetime
from autotrade.trend import analyze_trend
from autotrade.crawling_data import twitter_search, fetch_reddit_posts, save_merged_data
from autotrade.analyze_sentiment import build_coin_data_from_csv
from autotrade.automated_trading import evaluate_trades, execute_trades, get_current_holdings
from autotrade.user_router import user_settings_store

import logging

router = APIRouter()

# COIN_LIST = ['bitcoin', 'ethereum', 'solana', 'tron', 'dogecoin', 'xrp', 'ada', 'sui']
COIN_LIST = ['bitcoin']

# 진행중인 단계 - 전역 상태 저장 딕셔너리
autotrade_status = {
    "stage": "대기 중",
    "coin": None,
    "retry": 0,
    "last_updated": str(datetime.now())
}

def update_status(stage, coin=None, retry=0):
    autotrade_status["stage"] = stage
    autotrade_status["coin"] = coin
    autotrade_status["retry"] = retry
    autotrade_status["last_updated"] = str(datetime.now())


# coin_list를 두고 이에 대한 트렌드+크롤링+감정분석+자동매매
@router.post("/autotrade/start")
def start_autotrade():
    if "default" not in user_settings_store:
        return {"success": False, "message": "사용자 설정이 없습니다. 먼저 설정을 저장하세요.", "data": None}

    user_settings = user_settings_store["default"]
    holdings = get_current_holdings()
    # 임시 테스트용 코드
    TEST_MODE = True   # ← 나중에 False로만 바꾸면 끝

    all_coin_data = {}

    for coin in COIN_LIST:
        if TEST_MODE:
            is_hot, trend_score = True, 100
        else:
            is_hot, trend_score = analyze_trend(coin)
        if not is_hot:
            continue    # 급상승 아니면 크롤링·감정분석 생략

        # 🔍 크롤링
        logging.info("\n🔥 급등한" f"{coin}코인의 트위터 데이터 크롤링")
        update_status("트위터 크롤링 중", coin)
        tweets = twitter_search(coin)

        logging.info("\n🔥 급등한" f"{coin}코인의 레딧 데이터 크롤링")
        update_status("레딧 크롤링 중", coin)
        reddits = fetch_reddit_posts(coin)

        save_merged_data(coin, tweets, reddits)

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
    # 임시 테스트용 코드
    TEST_MODE = True   # ← 나중에 False로만 바꾸면 끝

    # 급상승할 때까지 반복
    max_retry = 10
    retry_delay = 60  # 60초 간격
    retry_count = 0

    while True:
        update_status("트렌드 분석 중", coin=coin, retry=retry_count)
        if TEST_MODE:
            is_hot, trend_score = True, 100
        else:
            is_hot, trend_score = analyze_trend(coin)
        if is_hot:
            break

        retry_count += 1
        if retry_count >= max_retry:
            update_status("급상승 실패", coin=coin, retry=retry_count)
            return {
                "success": False,
                "message": f"📉 [{coin}]은 {max_retry}회 확인했지만 급상승하지 않았습니다.",
                "data": None
            }

        print(f"🔁 [{coin}] 급상승 아님 → {retry_delay}초 후 재시도 ({retry_count}/{max_retry})")
        update_status("급상승 아님 → 60초 후 재시도", coin=coin, retry=retry_count)
        time.sleep(retry_delay)

    # 🔍 크롤링
    logging.info("\n🔥 급등한" f"{coin}코인의 트위터 데이터 크롤링")
    update_status("트위터 크롤링 중", coin)
    tweets = twitter_search(coin)

    logging.info("\n🔥 급등한" f"{coin}코인의 레딧 데이터 크롤링")
    update_status("레딧 크롤링 중", coin)
    reddits = fetch_reddit_posts(coin)

    save_merged_data(coin, tweets, reddits)

    # 📊 감정 분석  
    update_status("감정 분석 중", coin)
    coin_data = build_coin_data_from_csv(coin, trend_score, holdings)
    logging.info(f"[{coin}] 감정 분석 결과: {coin_data}")

    # 💡 매매 판단 + 실행
    update_status("매매 판단 중", coin)
    buy_order, sell_order = evaluate_trades(coin_data, user_settings)

    update_status("매매 실행 중", coin)
    execute_trades(buy_order, sell_order)

    update_status("자동매매 완료", coin)

    return {
        "success": True,
        "message": f"🚀 자동매매가 [{coin}]에 대해 실행되었습니다.",
        "data": {
            "coin": coin,
            "buy_order": buy_order,
            "sell_order": sell_order
        }
    }

    
### 현재 실행 상태 get
@router.get("/autotrade/status")
def get_autotrade_status():
    return {
        "success": True,
        "message": "현재 자동매매 상태입니다.",
        "data": autotrade_status
    }




