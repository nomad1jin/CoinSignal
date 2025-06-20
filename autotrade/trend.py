# trend.py (검색량 트렌드 관련 함수만)
import requests
import os
from dotenv import load_dotenv
from autotrade.crawling_data import twitter_search, fetch_reddit_posts
from pytrends.request import TrendReq
import time
import pandas as pd


load_dotenv()
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
THRESHOLD_PERCENT = 20

# 구글트렌드 시계열 데이터를 가져오는 함수 
def get_trend_series(keyword: str, timeframe: str, max_retries=3):
    pytrends = TrendReq(hl="ko", tz=540)
    attempt, delay = 0, 60

    while attempt < max_retries:
        try:
            pytrends.build_payload([keyword], timeframe=timeframe, geo="", gprop="")
            data = pytrends.interest_over_time()
            if not data.empty:
                return data[keyword]  # 시계열 시리즈 반환
            else:
                return pd.Series()
        except Exception as e:
            print(f"[Google Trends 오류] {e} - {delay}초 후 재시도")
            if "429" in str(e):
                time.sleep(delay)
                delay = min(delay * 2, 600)
            else:
                break
        attempt += 1
    return pd.Series()



def analyze_trend(coin):
    print("\n\n🔍 트렌드 분석 시작")

    trend_series = get_trend_series(coin, "now 1-d")  # 최근 1일치 데이터
    if trend_series.empty or len(trend_series) < 25:
        print(f"⚠️ {coin} 데이터 수집 실패 또는 부족")
        return False, 0.0

    now = trend_series.iloc[-1]
    val_1h_ago = trend_series.iloc[-7]  # 약 1시간 전 (5~7개마다 1시간 간격)
    val_4h_ago = trend_series.iloc[-28] if len(trend_series) >= 29 else trend_series.iloc[0]
    # val_24h_ago = trend_series.iloc[0]

    # 변화율 계산
    def rate(now, past):
        return ((now - past) / past) * 100 if past else 0

    change_1h = rate(now, val_1h_ago)
    change_4h = rate(now, val_4h_ago)
    # change_24h = rate(now, val_24h_ago)

    # 🔹 출력
    print(f"\n📈 {coin} 검색량 변화 📉")
    print(f" - 현재: {now}, 1시간 전: {val_1h_ago}, 4시간 전: {val_4h_ago}")
    print(f" - 1시간 변화율: {change_1h:.2f}%, 4시간 변화율: {change_4h:.2f}%")

    # if change_1h > THRESHOLD_PERCENT or change_4h > THRESHOLD_PERCENT:
    #     print(f"🚀 {coin} 급상승!")
    if change_1h > THRESHOLD_PERCENT:
        print(f"🚀 {coin} 급상승 (최근 1시간 기준)!")
        return True, now
    elif change_1h > 0 and change_4h > THRESHOLD_PERCENT:
        print(f"🚀 {coin} 급상승 (최근 4시간 기준)!")
        return True, now

    return False, 0.0



# ### 트렌드 수치 반환 
# def get_trend(coin: str) -> float:
#     """
#     현재 시점의 검색량을 기반으로 정규화된 트렌드 점수를 반환합니다.
#     - 기준: 4시간 전 데이터
#     """
#     val_4h = get_trend_data(coin, TIMEFRAMES["4시간 전"])
    
#     if val_4h is None:
#         print(f"⚠️ {coin}의 트렌드 점수 없음")
#         return 0.0

#     # 점수는 0~100 범위, 정규화 (예: 36 → 0.36)
#     return round(val_4h / 100, 2)

# def get_trend_data(keyword, timeframe, max_retries=5):
#     """ Google 트렌드 데이터를 가져옴 (429 오류 대비) """
#     pytrends = TrendReq(hl="ko", tz=540)    #한국시간대 기준 트렌드 데이터 요청임 
#     attempt, delay = 0, 60
    
#     while attempt < max_retries:
#         try:
#             pytrends.build_payload([keyword], timeframe=timeframe, geo="", gprop="")    #여긴 지역 전국으로 잘 되어있네
#             data = pytrends.interest_over_time()
#             return data.iloc[-1][keyword] if not data.empty else 0
#         except Exception as e:
#             print(f"[Google Trends 오류] {e} - {delay}초 후 재시도")
#             if "429" in str(e):
#                 time.sleep(delay)
#                 delay = min(delay * 2, 600)
#             else:
#                 break
#         attempt += 1
#     return 0

# def analyze_trend(coin):
#     """ 코인 검색량을 분석하고 급상승 여부 판별 """
#     print("\n\n🔍 트렌드 분석 시작")
#     trend_data = {label: get_trend_data(coin, tf) for label, tf in TIMEFRAMES.items()}
    
#     if any(v is None for v in trend_data.values()):
#         print(f"⚠️ {coin} 데이터 수집 실패")
#         return False
    
#     val_1h, val_4h, val_24h = trend_data["1시간 전"], trend_data["4시간 전"], trend_data["24시간 전"]
#     if val_24h == 0:
#         return False
    
#     change_1h = ((val_1h - val_24h) / val_24h) * 100
#     change_4h = ((val_4h - val_24h) / val_24h) * 100
    
#     # 🔹 검색량 변화 정보 출력
#     print(f"\n📈 {coin} 검색량 변화 📉")
#     print(f" - 1시간 전 대비 변화율: {change_1h:.2f}%")
#     print(f" - 4시간 전 대비 변화율: {change_4h:.2f}%")
#     print(f" - 24시간 전 검색량: {val_24h}, 1시간 전: {val_1h}, 4시간 전: {val_4h}")
    
#     if change_1h > THRESHOLD_PERCENT or change_4h > THRESHOLD_PERCENT:
#         print(f"🚀 {coin} 급상승! (1시간: {change_1h:.2f}%, 4시간: {change_4h:.2f}%)")
#         # twitter_search(coin)
#         # fetch_reddit_posts(coin)
#         # print("📊 감정 분석 중...\n🤖 자동매매 실행 중...")
#         return True
    
#     return False

### serpapi
# def get_trend_score(keyword, geo="KR"):
#     url = "https://serpapi.com/search"
#     params = {
#         "engine": "google_trends",
#         "q": keyword,
#         "geo": geo,
#         "api_key": SERPAPI_API_KEY
#     }
#     try:
#         res = requests.get(url, params=params)
#         data = res.json()
#         timeline = data.get("interest_over_time", {}).get("timeline_data", [])
#         if timeline:
#             today_entry = timeline[-1]
#             prev_entry = timeline[-2] if len(timeline) > 1 else None

#             score_today = today_entry["values"][0]["extracted_value"]
#             date_today = today_entry["date"]
#             if prev_entry:
#                 score_prev = prev_entry["values"][0]["extracted_value"]
#                 date_prev = prev_entry["date"]
#             else:
#                 score_prev, date_prev = 0, ""
#             return {
#                 "score_today": score_today,
#                 "score_prev": score_prev,
#                 "date_today": date_today,
#                 "date_prev": date_prev
#             }
#         else:
#             return None
#     except Exception as e:
#         print(f"SerpApi 스캔 오류: {e}")
#         return None

# ### 검색량 트렌드 조회
# def get_trend(score_today, score_prev):
#     if score_prev == 0:
#         return None
#     return ((score_today - score_prev) / max(1, score_prev)) * 100

# ### 트렌드 분석 후 감정분석 실행 
# def analyze_trend(coin):
#     trend = get_trend_score(coin, geo="us")
#     if not trend:
#         print(f"⚠ {coin} 트렌드 정보 없음")
#         return False

#     score_today = trend["score_today"]
#     score_prev = trend["score_prev"]
#     date_today = trend["date_today"]
#     date_prev = trend["date_prev"]

#     print(f"\n📈 {coin} 검색량 변화 분석")
#     print(f" - {date_prev}: {score_prev} → {date_today}: {score_today}")

#     change = get_trend(score_today, score_prev)
#     if change is None:
#         print(f" - 비교 기준 부족 (최초 기록)")
#         return False

#     change = ((score_today - score_prev) / max(1, score_prev)) * 100
#     print(f" - 변화율: {change:.2f}%")

#     if change > THRESHOLD_PERCENT:
#         print(f"🚀 {coin} 검색량 급등! 자동 분석 시작")
#         twitter_search(coin)
#         fetch_reddit_posts(coin)
#         print("📊 감정 분석 중...\n🤖 자동매매 실행 중...")
#         return True

#     return False