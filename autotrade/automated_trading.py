import pyupbit
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import schedule
import logging

# tickers = pyupbit.get_tickers("KRW")	# KRW를 통해 거래되는 코인만 불러오기
# print(tickers)

# 로그 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("trade.log", encoding="utf-8"),
        logging.StreamHandler()  # 콘솔에도 출력됨
    ]
)

# 알파: 감정 점수 반영
# 베타: 상승률 반영 
# buy_limit_pct: 한 종목당 매수 비중
# max_daily_invest: 일일 투자 금액
# loss_cut: 손절 기준
# take_profit: 익절 기준
# max_coin_count: 종목 수 제한 

##### 1. 사용자 투자 성향 설정 #####
def get_default_profile(style):
    defaults = {
        "test": {
            "max_daily_invest": 5000, "loss_cut": -0.002, "take_profit": 0.003,
            "max_coin_count": 5
        },
        "neutral": {
            "max_daily_invest": 10000, "loss_cut": -0.05, "take_profit": 0.05,
            "max_coin_count": 5
        }
    }
    return defaults.get(style, defaults["neutral"])


def get_user_profile():
    style = input("투자 성향을 입력하세요 (test / neutral): ").strip().lower()
    if style not in ["test", "neutral"]:
        print("잘못된 입력입니다. 기본값 'neutral'이 사용됩니다.")
        style = "neutral"
    return get_default_profile(style)    


##### 2. 매매 판단 함수 #####
def evaluate_trades(coin_data, profile):

    # 트렌드는 반드시 0.3이 기준
    # 부정0 중립1 긍정2

    buy_order = {}
    sell_order = {}

    for coin, v in coin_data.items():
        trend = v["trend"]
        emotion = v["emotion"]
        holding = v["holding"]

        #매수 조건
        if trend > 0.2 and emotion == 2:
            buy_order[coin] = {"invest_krw": profile["max_daily_invest"] / profile["max_coin_count"]}

        #중립은 관망

        #매도 조건
        elif trend > 0.2 and emotion == 0 and holding:
            sell_order[coin] = {"sell_pct": 100.0}  #전량 매도

    return buy_order, sell_order


##### 3. 업비트 api 연동 #####
load_dotenv()
access = os.getenv("access")
secret = os.getenv("secret")
upbit = pyupbit.Upbit(access, secret)


def get_current_holdings():
    balances = upbit.get_balances()
    holdings = {}
    for b in balances:
        if b['currency'] == 'KRW' or float(b['balance']) == 0:
            continue
        holdings[b['currency'].lower()] = float(b['balance'])

    if not holdings:
        logging.info("보유한 종목이 없습니다.")    
    return holdings

def execute_trades(buy_order, sell_order):
    holdings = get_current_holdings()
    log_current_holdings(upbit)

    # 매수
    for coin, info in buy_order.items():
        krw_ticker = f"KRW-{coin.upper()}"
        amount = info["invest_krw"]  
        try:
            logging.info(f"[매수 시도] {coin} → {amount:,} KRW")
            resp = upbit.buy_market_order(krw_ticker, amount)
            logging.info(f"[매수 응답] {resp}")

        except Exception as e:
            logging.error(f"[매수 실패] {coin}: {e}")
        time.sleep(0.3)

    # 매도
    for coin, info in sell_order.items():
        coin_lc = coin.lower()
        if coin_lc in holdings:
            try:
                amt = holdings[coin_lc] * info["sell_pct"] / 100
                krw_ticker = f"KRW-{coin.upper()}"
                logging.info(f"[매도 시도] {coin} → {info['sell_pct']}% ({amt:.6f}개)")
                resp = upbit.sell_market_order(krw_ticker, amt)
                logging.info(f"[매도 응답] {resp}")

            except Exception as e:
                logging.error(f"[매도 실패] {coin}: {e}")
            time.sleep(0.3)

##### 손절/익절 감시 #####
def monitor_positions(style):
    print("📉 손절/익절 감시 중...")

    balances = upbit.get_balances()
    log_current_holdings(upbit)


    for b in balances:
        if b['currency'] == 'KRW' or float(b['balance']) == 0:
            continue
        ticker = f"KRW-{b['currency']}"
        try:
            current = pyupbit.get_current_price(ticker)
            avg = float(b['avg_buy_price'])
            profit = (current - avg) / avg
            if profit <= style["loss_cut"] or profit >= style["take_profit"]:
                upbit.sell_market_order(ticker, float(b['balance']))
                print(f"[자동매도] {ticker} 수익률: {profit:.2%}")
        except Exception as e:
            print(f"[감시 오류] {ticker}: {e}")
        time.sleep(0.3)

### 잔고 출력 ### 
def log_current_holdings(upbit):
    balances = upbit.get_balances()
    logging.info(f"[현재 보유 자산] {balances}")
    
    for b in balances:
        currency = b["currency"]
        balance = float(b["balance"])
        
        if currency == "KRW" or balance == 0:
            # logging.info("🚫 보유 중인 코인이 없습니다.")
            continue
        
        logging.info(f"{currency}: {balance:.6f}개")
