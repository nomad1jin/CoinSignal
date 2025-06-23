import re
from langdetect import detect, LangDetectException
from collections import Counter

# ✅ 필터링 함수들
def is_meaningless(text):
    text = str(text).strip()
    return len(text.split()) < 3 or not re.search(r'[A-Za-z]', text) or re.fullmatch(r'([ㅋㅎㅠ.!?])+', text)

def is_ad_or_spam(text):
    text = str(text).lower()
    spam_keywords = ["airdrop", "join", "discount", "giveaway", "telegram", "retweet", "free", "bonus", "ico"]
    return any(k in text for k in spam_keywords) or "http" in text or "www" in text or re.search(r'\S+@\S+\.\S+', text)

def is_hashtag_spam(text):
    return str(text).count("#") > 15

def contains_spam_domain(text):
    domains = ["bit.ly", "t.me", "coinpump.com", "shadycrypto.io", "pumpdump"]
    return any(domain in text for domain in domains)

def is_english(text):
    try:
        return detect(text) == "en"
    except LangDetectException:
        return False

def find_duplicate_messages(messages, min_count=2):
    counter = Counter(messages)
    return set([msg for msg, count in counter.items() if count >= min_count])

def build_cleaner(duplicate_texts):
    def is_clean(text):
        return (
            is_english(text)
            and not is_meaningless(text)
            and not is_ad_or_spam(text)
            and not is_hashtag_spam(text)
            and not contains_spam_domain(text)
            and text not in duplicate_texts
        )
    return is_clean

def clean_messages(messages):
    print("🧹 데이터 전처리 중")

    duplicates = find_duplicate_messages(messages)
    cleaner = build_cleaner(duplicates)

    total = len(messages)
    cleaned = [msg for msg in messages if cleaner(msg)]
    removed = total - len(cleaned)

    print(f"🧹 총 {total}개 중 {len(cleaned)}개 유지, {removed}개 제거됨")

    return cleaner, cleaned
