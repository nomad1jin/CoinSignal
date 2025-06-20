# from autotrade.trend import analyze_trend, get_trend
from autotrade.trend import analyze_trend, get_trend, twitter_search, fetch_reddit_posts
from autotrade.crawling_data import twitter_search, fetch_reddit_posts
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
    ['bitcoin', 'ethereum', 'ripple']
    # 'tether', 'solana'
    # ['dogecoin', 'USD Coin', 'ada', 'tron', 'chainlink'],
    # ['Stellar Lumens', 'sui', 'hedera', 'shiba inu'],
    # ['polkadot', 'Bitcoin Cash', 'uniswap', 'pepe', 'Near Protocol'],
    # ['Aave', 'Aptos', 'cardano', 'Ankr', 'Algorand'],
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
            if analyze_trend(coin):     # 🔍 트렌드 분석만
                hot_coins.append(coin)  # 🔥 급등한 코인만 수집

    # 급등 코인에 대해 감정 분석 수행
    for coin in hot_coins:
        logging.info("\n🔥 급등한" f"[{coin}]코인의 트위터 데이터 크롤링")
        twitter_search(coin)      
        logging.info("\n🔥 급등한" f"[{coin}]코인의 레딧 데이터 크롤링")
        fetch_reddit_posts(coin)
        coin_data = build_coin_data_from_csv(coin, get_trend(coin), holdings)
        logging.info(f"[{coin}] 감정 분석 결과: {coin_data}")
        all_coin_data.update(coin_data)

    logging.info(f"[all_coin_data] {all_coin_data}")
    return all_coin_data


def run_daily_autotrade():
    print(f"💰 자동매매 시작: {datetime.now()}")

    coin_data = run_once_trend_and_sentiment()

    if not coin_data:
        print("⚠ 매매할 코인 없음 (감정분석 결과 없음)")
        return

    buy_order, sell_order = evaluate_trades(coin_data, profile)
    execute_trades(buy_order, sell_order)


# ✅ 스케줄 등록
def main():
    # schedule.every().day.at("09:00").do(run_daily_autotrade)
    run_daily_autotrade()
    schedule.every(1).minutes.do(lambda: monitor_positions(profile))

    print("⏳ 자동매매 시스템 실행 중 (Ctrl+C로 종료)")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
