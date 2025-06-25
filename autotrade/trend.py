# # trend.py
# ###경민

# ✅ pytrends 사용해서 시계열 검색량 받아오는 함수
from pytrends.request import TrendReq
import pandas as pd
import time

def get_trend_series(keyword: str, timeframe: str = "now 1-d", max_retries=3):
    pytrends = TrendReq(hl="ko", tz=540)
    attempt, delay = 0, 60

    while attempt < max_retries:
        try:
            pytrends.build_payload([keyword], timeframe=timeframe)
            data = pytrends.interest_over_time()
            if not data.empty:
                return data[keyword]
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

# ✅ 최근 평균 vs 전체 평균 비교 → 30% 이상이면 급상승 판단
def analyze_trend(coin, ratio_threshold=1.3, recent_points=6):
    print(f"\n🔍 {coin} 트렌드 분석 시작")

    trend_series = get_trend_series(coin)
    if trend_series.empty or len(trend_series) < recent_points + 10:
        print(f"⚠️ {coin} 데이터 수집 실패 또는 부족")
        return False, 0.0

    full_avg = trend_series.mean()
    recent_avg = trend_series[-recent_points:].mean()

    print(f" - 전체 평균: {full_avg:.2f}")
    print(f" - 최근 평균(최근 {recent_points}개): {recent_avg:.2f}")

    if recent_avg >= full_avg * ratio_threshold:
        print(f"🚀 급상승 감지! (최근 평균이 30% 이상 증가)")
        return True, trend_series.iloc[-1]
    else:
        print(f"🟢 평소 수준입니다.")
        return False, trend_series.iloc[-1]
    

    """
    각 코인의 최근 검색량을 기준으로 내림차순 정렬하여 상위 top_k 코인을 반환
    """
def get_trend_top5(coin_list, top_k=5):
    trend_scores = []

    for coin in coin_list:
        series = get_trend_series(coin)
        if series.empty:
            continue
        recent_value = series.iloc[-1]
        trend_scores.append((coin, recent_value))

    trend_scores.sort(key=lambda x: x[1], reverse=True)

    # ✅ 'score'라는 키로 변환해서 리턴
    return [
        {"coin": coin, "score": float(value)}  # float 변환으로 JSON 직렬화 안전
        for coin, value in trend_scores[:top_k]
    ]



# from pytrends.request import TrendReq

# def analyze_trend(coin):
#     pytrends = TrendReq(hl="ko", tz=540)
#     try:
#         pytrends.build_payload([coin], timeframe="now 1-d", geo="", gprop="")
#         df = pytrends.interest_over_time()

#         if df.empty:
#             print(f"⚠️ {coin} 검색 데이터 없음")
#             return False, 0.0
        
#         avg_score = df[coin].mean()
#         print(f"📊 {coin} 오늘 평균 검색량: {avg_score:.2f}")
#         return True, avg_score
    
#     except Exception as e:
#         print(f"❌ {coin} pytrends 오류: {e}")
#         return False, 0.0
    
# import requests
# import os
# from dotenv import load_dotenv
# from autotrade.crawling_data import twitter_search, fetch_reddit_posts

# load_dotenv()
# SERPAPI_API_KEY = os.getenv("SERP_API_KEY")
# THRESHOLD_PERCENT = 30

# #코인의 지금 검색량 반환 
# def get_trend(coin):
#     url = "https://serpapi.com/search"
#     params = {
#         "engine": "google_trends",
#         "q": coin,
#         "geo": "",
#         "date": "now 1-d",
#         "data_type": "TIMESERIES", 
#         "api_key": SERPAPI_API_KEY
#     }

#     try:
#         res = requests.get(url, params=params)
#         data = res.json()

#         timeline = data.get("interest_over_time", {}).get("timeline_data", [])
#         if len(timeline) < 3:
#             print(f"⚠️ {coin}: 시간별 검색량 데이터가 부족합니다.")
#             return False, 0.0

#         # 시간별 검색량 수치 리스트
#         values = [point["values"][0]["extracted_value"] for point in timeline]
#         latest_val = values[-1]

#         print(f"🔎 [{coin}] 최신 시점 검색량: {latest_val}")

#         return latest_val

#     except Exception as e:
#         print(f"{coin} 검색량 분석 중 오류 발생: {e}")
#         return None

# def analyze_trend(coin):
#     """
#     SerpApi를 통해 최근 24시간(now 1-d)의 시간별 검색량 데이터를 가져와
#     평균 대비 최신 시점 수치가 30% 이상 상승했는지 분석함.
#     조건 만족 시 Reddit 및 Twitter 크롤링 실행 후 자동매매 트리거로 연결되도록 설정.
#     """
#     url = "https://serpapi.com/search"
#     params = {
#         "engine": "google_trends",
#         "q": coin,
#         "geo": "",
#         "date": "now 1-d",  # 최근 24시간
#         "data_type": "TIMESERIES",  # 시계열 데이터
#         "api_key": SERPAPI_API_KEY
#     }

#     print("\n🔍 트렌드 분석 시작")
#     try:
#         res = requests.get(url, params=params)
#         data = res.json()

#         timeline = data.get("interest_over_time", {}).get("timeline_data", [])
#         if len(timeline) < 3:
#             print(f"⚠️  {coin}: 시간별 검색량 데이터가 부족합니다.")
#             return False, 0.0

#         # 시간별 검색량 수치 리스트
#         values = [point["values"][0]["extracted_value"] for point in timeline]

#         # 평균은 마지막 값 제외한 평균으로 계산
#         avg_val = sum(values[:-1]) / (len(values) - 1)
#         latest_val = values[-1]
#         change = ((latest_val - avg_val) / avg_val) * 100 if avg_val > 0 else 0

#         # 결과 출력
#         print(f"\n📈 {coin} 검색량 변화 📉")
#         print(f" - 24시간 평균 검색량: {avg_val:.2f}")
#         print(f" - 최신 시점 검색량: {latest_val}")
#         print(f" - 변화율: {change:.2f}%")

#         if change >= THRESHOLD_PERCENT:
#             print(f"🚀 {coin} 검색량 급등 감지!")
#             return True, latest_val

#         return False, 0.0

#     except Exception as e:
#         print(f"❌ {coin} 분석 중 오류 발생: {e}")
#         return False, 0.0


# def get_trend_top5(coin_list):
#     results = []

#     for coin in coin_list:
#         latest_val = get_trend(coin)  
#         if latest_val is None:
#             continue
#         results.append((coin, float(latest_val)))

#     # 내림차순 정렬
#     results.sort(key=lambda x: x[1], reverse=True)

#     # 상위 5개 반환
#     top5 = [{"coin": coin, "score": score} for coin, score in results[:5]]
#     return top5



# # #파이트렌드 윤진
# # trend.py (검색량 트렌드 관련 함수만)
# import requests
# import os
# from dotenv import load_dotenv
# from autotrade.crawling_data import twitter_search, fetch_reddit_posts
# from pytrends.request import TrendReq
# import time
# import pandas as pd


# load_dotenv()
# THRESHOLD_PERCENT = 30

# # 구글트렌드 시계열 데이터를 가져오는 함수 
# def get_trend_series(keyword: str, timeframe: str, max_retries=3):
#     pytrends = TrendReq(hl="ko", tz=540)
#     attempt, delay = 0, 60

#     while attempt < max_retries:
#         try:
#             pytrends.build_payload([keyword], timeframe=timeframe, geo="", gprop="")
#             data = pytrends.interest_over_time()
#             if not data.empty:
#                 return data[keyword]  # 시계열 시리즈 반환
#             else:
#                 return pd.Series()
#         except Exception as e:
#             print(f"[Google Trends 오류] {e} - {delay}초 후 재시도")
#             if "429" in str(e):
#                 time.sleep(delay)
#                 delay = min(delay * 2, 600)
#             else:
#                 break
#         attempt += 1
#     return pd.Series()

# def analyze_trend(coin):
#     print("\n\n🔍 트렌드 분석 시작")

#     trend_series = get_trend_series(coin, "now 1-d")  # 최근 1일치 데이터
#     if trend_series.empty or len(trend_series) < 25:
#         print(f"⚠️ {coin} 데이터 수집 실패 또는 부족")
#         return False, 0.0

#     now = trend_series.iloc[-1]
#     val_1h_ago = trend_series.iloc[-7]  # 약 1시간 전 (5~7개마다 1시간 간격)
#     val_4h_ago = trend_series.iloc[-28] if len(trend_series) >= 29 else trend_series.iloc[0]
#     # val_24h_ago = trend_series.iloc[0]

#     # 변화율 계산
#     def rate(now, past):
#         return ((now - past) / past) * 100 if past else 0

#     change_1h = rate(now, val_1h_ago)
#     change_4h = rate(now, val_4h_ago)
#     # change_24h = rate(now, val_24h_ago)

#     # 🔹 출력
#     print(f"\n📈 {coin} 검색량 변화 📉")
#     print(f" - 현재: {now}, 1시간 전: {val_1h_ago}, 4시간 전: {val_4h_ago}")
#     print(f" - 1시간 변화율: {change_1h:.2f}%, 4시간 변화율: {change_4h:.2f}%")

#     # if change_1h > THRESHOLD_PERCENT or change_4h > THRESHOLD_PERCENT:
#     #     print(f"🚀 {coin} 급상승!")
#     if change_1h > THRESHOLD_PERCENT:
#         print(f"🚀 {coin} 급상승 (최근 1시간 기준)!")
#         return True, now
#     elif change_1h > 0 and change_4h > THRESHOLD_PERCENT:
#         print(f"🚀 {coin} 급상승 (최근 4시간 기준)!")
#         return True, now

#     return False, 0.0


# def get_trend_top5(coin_list):
#     results = []

#     for coin in coin_list:
#         trend_series = get_trend_series(coin, "now 1-d")  # 최근 1일치 데이터
#         if trend_series.empty or len(trend_series) < 25:
#             print(f"⚠️ {coin} 데이터 수집 실패 또는 부족")
#             continue

#         now = trend_series.iloc[-1]
#         results.append((coin, float(now)))

#     # 내림차순 정렬
#     results.sort(key=lambda x: x[1], reverse=True)

#     # 상위 5개 반환
#     top5 = [{"coin": coin, "score": score} for coin, score in results[:5]]
#     return top5



####문곤 오빠
# from pytrends.request import TrendReq
# import time
# THRESHOLD_PERCENT = 30
# TIMEFRAMES = {
#     "1시간 전": "now 1-H",
#     "4시간 전": "now 4-H",
#     "24시간 전": "now 1-d"
# }

# def get_trend_data(keyword, timeframe, max_retries=5):
#     """ Google 트렌드 데이터를 가져옴 (429 오류 대비) """
#     pytrends = TrendReq(hl="ko", tz=540)
#     attempt, delay = 0, 60
    
#     while attempt < max_retries:
#         try:
#             pytrends.build_payload([keyword], timeframe=timeframe, geo="", gprop="")
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
#     trend_data = {label: get_trend_data(coin, tf) for label, tf in TIMEFRAMES.items()}
    
#     if any(v is None for v in trend_data.values()):
#         print(f"⚠ {coin} 데이터 수집 실패")
#         return False, 0.0
    
#     val_1h, val_4h, val_24h = trend_data["1시간 전"], trend_data["4시간 전"], trend_data["24시간 전"]
#     if val_24h == 0:
#         return False, 0.0
    
#     change_1h = ((val_1h - val_24h) / val_24h) * 100
#     change_4h = ((val_4h - val_24h) / val_24h) * 100
    
#     # 🔹 검색량 변화 정보 출력
#     print(f"\n📈 {coin} 검색량 변화 📉")
#     print(f" - 1시간 전 대비 변화율: {change_1h:.2f}%")
#     print(f" - 4시간 전 대비 변화율: {change_4h:.2f}%")
#     print(f" - 24시간 전 검색량: {val_24h}, 1시간 전: {val_1h}, 4시간 전: {val_4h}")
    
#     if change_1h > THRESHOLD_PERCENT:
#         print(f"🚀 {coin} 급상승 (최근 1시간 기준)!")
#         return True, change_1h
#     elif change_4h > THRESHOLD_PERCENT:
#         print(f"🚀 {coin} 급상승 (최근 4시간 기준)!")
#         return True, change_4h
    
#     return False, 0.0


# # ###예지언니
# # # trend.py (SerpApi 기반 하루 단위 분석)

# import requests
# import os
# from autotrade.crawling_data import twitter_search, fetch_reddit_posts
# from dotenv import load_dotenv

# load_dotenv()

# SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
# THRESHOLD_PERCENT = 30

# # 🔹 더미로라도 추가해줘야 main.py가 import 오류 안남
# # def get_trend_series(keyword: str, geo="KR"):
# #     # 더미 구현 - main.py에서 사용하지 않아도 import 요구해서 넣어줌
# #     return None

# def get_trend_score(keyword, geo="KR"):
#     url = "https://serpapi.com/search"
#     params = {
#         "engine": "google_trends",
#         "q": keyword,
#         "geo": "",
#         "api_key": SERPAPI_API_KEY,
#         "date": "today 1-m"
#     }
#     try:
#         res = requests.get(url, params=params)
#         data = res.json()
#         timeline = data.get("interest_over_time", {}).get("timeline_data", [])
#         if len(timeline) < 2:
#             return None

#         today_entry = timeline[-1]
#         yesterday_entry = timeline[-2]

#         # ✅ 하루 단위인지 확인
#         if "at" in today_entry["date"]:
#             print("⚠️ 경고: 하루 단위가 아닌 시간 단위 결과입니다. 분석 제외.")
#             return NoneS

#         score_today = today_entry["values"][0]["extracted_value"]
#         score_yesterday = yesterday_entry["values"][0]["extracted_value"]

#         date_today = today_entry["date"]
#         date_yesterday = yesterday_entry["date"]

#         change = ((score_today - score_yesterday) / max(1, score_yesterday)) * 100

#         return {
#             "score_today": score_today,
#             "score_yesterday": score_yesterday,
#             "date_today": date_today,
#             "date_yesterday": date_yesterday,
#             "change_percent": round(change, 2)
#         }
#     except Exception as e:
#         print(f"SerpApi 트렌드 조회 오류: {e}")
#         return None


# def analyze_trend(coin):
#     print("\n\n🔍 트렌드 분석 시작 (하루 단위)")
#     trend = get_trend_score(coin, geo="KR")
#     if not trend:
#         print(f"⚠️ {coin} 트렌드 정보 없음")
#         return False, 0.0

#     print(f"\n📈 [{coin}] 검색량 변화")
#     print(f" - 어제 {trend['date_yesterday']}: {trend['score_yesterday']}")
#     print(f" - 오늘 {trend['date_today']}: {trend['score_today']}")
#     print(f" - 상승률: {trend['change_percent']:.2f}%")

#     if trend["change_percent"] > THRESHOLD_PERCENT:
#         print(f"🚀 {coin} 검색량 급등!")
#         return True, trend["score_today"]

#     return False, trend["score_today"]



# def get_trend_top5(coin_list):
#     results = []

#     for coin in coin_list:
#         trend_data = get_trend_score(coin, geo="KR")
#         if not trend_data:
#             print(f"⚠️ {coin} 트렌드 정보 없음 또는 오류 발생")
#             continue

#         score = trend_data.get("score_today", 0)
#         change = trend_data.get("change_percent", 0)
#         results.append({
#             "coin": coin,
#             "score": score,
#             "change_percent": change
#         })

#     # 점수 기준 내림차순 정렬
#     results.sort(key=lambda x: x["score"], reverse=True)

#     # 상위 5개 반환
#     top5 = [{"coin": coin, "score": score} for coin, score in results[:5]]
#     return top5