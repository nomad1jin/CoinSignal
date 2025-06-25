# from autotrade.trend import analyze_trend, get_trend
from autotrade.trend import analyze_trend
from autotrade.crawling_data import save_merged_data, twitter_search, fetch_reddit_posts
from autotrade.analyze_sentiment import build_coin_data_from_csv
from autotrade.automated_trading import get_user_profile, evaluate_trades, execute_trades, get_current_holdings, monitor_positions

from datetime import datetime
import time
import schedule
import logging
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# 로그 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("trade.log", encoding="utf-8"),
        logging.StreamHandler()  # 콘솔에도 출력됨
    ]
)

COIN_LISTS = [
    # ['bitcoin', 'ethereum'],
    # ['tether', 'ripple', 'solana']
    # ['USD Coin', 'tron']
    ['USD Coin', 'tron', 'dogecoin', 'ada', 'sui']
]

# 전역 변수
profile = get_user_profile()
holdings = get_current_holdings()

def run_once_trend_and_sentiment():
    """트렌드 분석 + 크롤링 + 감정분석을 하루 한 번만 실행"""

    all_coin_data = {}
    hot_coins = []

    # 트렌드 분석 → 급등한 코인 수집
    for coin_list in COIN_LISTS:
        for coin in coin_list:
            is_hot, trend_score = analyze_trend(coin)   #급상승한 boolean, 트렌드 점수 
            if is_hot:
                hot_coins.append((coin, trend_score))

    # 급등 코인에 대해 감정 분석 수행
    for coin, trend_score in hot_coins:
        logging.info("\n🔥 급등한" f"[{coin}]코인의 트위터 데이터 크롤링")
        tweets = twitter_search(coin)      
        logging.info("\n🔥 급등한" f"[{coin}]코인의 레딧 데이터 크롤링")
        reddits = fetch_reddit_posts(coin)
        
        save_merged_data(coin, tweets, reddits)
    
        coin_data = build_coin_data_from_csv(coin, trend_score, holdings)
        logging.info(f"[{coin}] 감정 분석 결과: {coin_data}")
        all_coin_data.update(coin_data)

    logging.info(f"[all_coin_data] {all_coin_data}")
    return all_coin_data


def run_daily_autotrade():
    coin_data = run_once_trend_and_sentiment()

    if not coin_data:
        print("⚠️ 매매할 코인 없음 (감정분석 결과 없음)")
        return

    print(f"💰 자동매매 시작: {datetime.now()}")
    buy_order, sell_order = evaluate_trades(coin_data, profile)
    execute_trades(buy_order, sell_order)


def combined_task():
    run_daily_autotrade()       # 트렌드분석 + 크롤링 + 감정분석 + 자동매수,매도
    monitor_positions(profile)      # 손절/익절 모니터링 


# ✅ 스케줄 등록
def main():
    # schedule.every().day.at("09:00").do(run_daily_autotrade)
    # schedule.every(1).minutes.do(run_daily_autotrade)
    # schedule.every(10).seconds.do(run_daily_autotrade)
    # schedule.every(10).seconds.do(lambda: monitor_positions(profile))
    schedule.every(10).seconds.do(combined_task)

    print("⏳ 자동매매 시스템 실행 중 (Ctrl+C로 종료)")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
