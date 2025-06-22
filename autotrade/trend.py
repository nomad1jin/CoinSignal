# # trend.py
###경민
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

##파이트렌드 윤진
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


