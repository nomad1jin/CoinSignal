import praw
import requests
import pandas as pd
import time
import csv
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# ✅ Colab용 WebDriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🔹 Reddit API 인증 정보
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT")
X_EMAIL = os.getenv("X_EMAIL")
X_PASSWORD = os.getenv("X_PASSWORD")


def twitter_search(coin):
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # 필요시 사용

    driver = uc.Chrome(options=options)

    try:
        # ✅ 로그인 페이지로 이동
        driver.get("https://x.com/login")
        time.sleep(3)
        
        # 첫 번째 입력 (이메일 입력)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        ).send_keys(X_EMAIL, Keys.RETURN)
        time.sleep(3)

        # ⚠️ 비정상 접근 감지 시 두 번째 입력 필요
        try:
            second_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            second_input.clear()
            second_input.send_keys(X_EMAIL, Keys.RETURN)
            time.sleep(3)
        except:
            pass  # 두 번째 입력이 필요 없는 경우 무시

        # ✅ 비밀번호 입력
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(X_PASSWORD, Keys.RETURN)
        time.sleep(3)

        # 이후 탐색 페이지 진입
        driver.get("https://x.com/explore")
        time.sleep(3)

        # 검색창 입력
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@data-testid='SearchBox_Search_Input']"))
        )
        search_input.clear()
        search_input.send_keys(coin)
        search_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # 최신 트윗 탭 클릭
        try:
            latest_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Latest')]"))
            )
            latest_tab.click()
            time.sleep(3)
        except:
            print("⚠ 최신 트윗 탭 클릭 실패")

        tweet_data = set()
        for _ in range(10):
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for article in soup.find_all("article"):
                try:
                    name_spans = article.find_all("span")
                    display_name, username = "", ""
                    for span in name_spans:
                        text = span.get_text(strip=True)
                        if text.startswith("@") and not username:
                            username = text
                        elif not text.startswith("@") and not display_name:
                            display_name = text
                        if display_name and username:
                            break

                    tweet_div = article.find("div", {"data-testid": "tweetText"})
                    if tweet_div and display_name and username:
                        tweet_text = " ".join(span.get_text(strip=True) for span in tweet_div.find_all("span"))
                        tweet_data.add((coin, display_name, username, tweet_text))
                except:
                    continue
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        all_tweets = list(tweet_data)[:200]
        with open("tweets_data.csv", "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Coin", "DisplayName", "Username", "Tweet"])
            writer.writerows(all_tweets)

        print(f"📄 Twitter 크롤링 완료 ({len(all_tweets)}개 트윗 저장)")

    except Exception as e:
        print(f"❌ Twitter 크롤링 오류: {e}")
    finally:
        driver.quit()


def fetch_reddit_posts(coin, limit=200, days=30):
    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    results = []
    subreddit = reddit.subreddit('all')

    try:
        for post in subreddit.search(coin, limit=limit, sort='new', time_filter='day'):
            # ✅ timezone-aware datetime으로 변환
            post_date = pd.to_datetime(post.created_utc, unit='s', utc=True)

            if post_date < cutoff_date:
                continue

            post_content = f"{post.title} {post.selftext}"
            if coin.lower() in post_content.lower():
                results.append({
                    'Coin': coin,
                    'Type': 'Post',
                    'Author': post.author.name if post.author else 'Unknown',
                    'Content': post_content
                })

            post.comments.replace_more(limit=0)
            for comment in post.comments:
                if coin.lower() in comment.body.lower():
                    results.append({
                        'Coin': coin,
                        'Type': 'Comment',
                        'Author': comment.author.name if comment.author else 'Unknown',
                        'Content': comment.body
                    })

    except Exception as e:
        print(f"⚠️ Reddit 데이터 수집 오류: {e}")

    if results:
        pd.DataFrame(results).to_csv("reddit_data.csv", index=False, encoding="utf-8-sig", errors='ignore')
        print(f"📄 Reddit 데이터 저장 완료 ({len(results)}개)")