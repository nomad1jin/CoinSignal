from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
import os
from collections import Counter

#모델 경로
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

def analyze_sentiments(texts: list[str]) -> tuple[int, dict]:
    results = []
    for text in texts:
        pred = analyze_sentiment(text[:512])  # 길이 제한은 유지
        results.append(pred)

    if not results:
        return 1, {"positive": 0, "neutral": 0, "negative": 0}

    count = Counter(results)
    counts_dict = {
        "negative": count.get(0, 0),
        "neutral": count.get(1, 0),
        "positive": count.get(2, 0)
    }

    final_label = max(count, key=count.get)
    return final_label , counts_dict

def build_coin_data_from_csv(coin_name: str, trend_score: float, holdings: dict):
    print("\n📊 감정 분석 중...")
    # 트렌드 점수 0~1로 정규화
    trend_normalized = float(round(trend_score / 100, 2))
    coin_key = coin_name.lower()    #보유중인지 

    # 데이터 로딩
    merged_df = pd.read_csv(f"{coin_name}_merged_data.csv")

    try:
        merged_df = pd.read_csv(f"{coin_name}_merged_data.csv")
        texts = merged_df["Content"].dropna().tolist()
    except Exception as e:
        print(f"[오류] {coin_name}_merged_data.csv 로딩 실패: {e}")
        return {}

    # 감정 분석 실행
    emotion_label, emotion_counts = analyze_sentiments(texts)

    # coin_data 딕셔너리 반환
    return {
        coin_key: {
            "trend": trend_normalized,
            "emotion": emotion_label,
            "emotion_counts": emotion_counts,
            "holding": coin_key in holdings
        }
    }
