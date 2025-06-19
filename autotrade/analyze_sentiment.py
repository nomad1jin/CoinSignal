from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
import os

#모델 경로
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "finetuned_fa_model")
# MODEL_PATH = os.path.abspath(MODEL_PATH)  # 절대경로로 변환
MODEL_PATH = "C:/상명대/2025 1학기/미래설계/자동매매_윤진/autotrade/finetuned_fa_model"


#1. 모델 로드
tokenizer =  AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

#2. 감정 분석 함수
def analyze_sentiment(text: str) -> int:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        pred = torch.argmax(probs, dim=1).item()
    return pred

def analyze_sentiments(texts: list[str]) -> int:
    results = []
    for text in texts[:250]:  # 최대 250개 
        pred = analyze_sentiment(text[:512])  # 길이 제한
        results.append(pred)

    if not results:
        return 1  # 중립 기본값
    return max(set(results), key=results.count)  # 최빈값 반환

def build_coin_data_from_csv(coin_name: str, trend_score: float, holdings: dict):
    print("\n📊 감정 분석 중...")
    # 트렌드 점수 0~1로 정규화
    trend_normalized = round(trend_score / 100, 2)
    coin_key = coin_name.lower()    #보유중인지 

    # 데이터 로딩
    tweet_df = pd.read_csv("tweets_data.csv")
    reddit_df = pd.read_csv("reddit_data.csv")

    # 텍스트 추출
    all_texts = []

    try:
        tweet_rows = tweet_df[tweet_df["Coin"].str.lower() == coin_name.lower()]
        tweet_texts = tweet_rows["Tweet"].dropna().tolist()
        all_texts.extend(tweet_texts)
    except Exception as e:
        print(f"❌ 트윗 파일 로딩 오류: {e}")

    # 레딧 데이터 읽기 + 필터 + 'Content' 컬럼 사용
    try:
        reddit_rows = reddit_df[reddit_df["Coin"].str.lower() == coin_name.lower()]
        reddit_texts = reddit_rows["Content"].dropna().tolist()
        all_texts.extend(reddit_texts)
    except Exception as e:
        print(f"❌ 레딧 파일 로딩 오류: {e}")

    # 감정 분석
    emotion_label = analyze_sentiments(all_texts)

    # coin_data 딕셔너리 반환
    return {
        coin_name.lower(): {
            "trend": trend_normalized,
            "emotion": emotion_label,
            "holding": coin_key in holdings
        }
    }

