from fastapi import FastAPI
import asyncio
import logging
from autotrade.dashboard_router import router as dashboard_router
from autotrade.user_router import router as user_router
from autotrade.autotrade_router import router as autotrade_router
from autotrade.automated_trading import monitor_positions
from autotrade.user_router import user_settings_store
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="AutoTrading API",
    description="트렌드 기반 자동매매 시스템 API",
    version="1.0"
)

# 허용할 origin 리스트
origins = [
    "http://localhost:3000",  # 프론트엔드 주소 (React dev server)
    # 배포 시엔 실제 도메인도 추가
]

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 허용할 origin 리스트
origins = [
    "http://localhost:3000",  # 프론트엔드 주소 (React dev server)
    # 배포 시엔 실제 도메인도 추가
]

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터를 등록해줘야함
app.include_router(dashboard_router)
app.include_router(user_router)
app.include_router(autotrade_router)

@app.get("/")
def root():
    return {"message": "🚀 자동매매 API 서버 정상 작동 중"}


async def background_monitor():
    while True:
        user_settings = user_settings_store.get("default")

        if user_settings is None:
            logging.warning("[감시 대기] 사용자 설정 없음. POST /user/info 필요")
        else:
            try:
                logging.info("[감시 시작] 사용자 설정 기반으로 monitor_positions 실행")
                monitor_positions(user_settings)  # 1회 실행
            except Exception as e:
                logging.error(f"[감시 오류] monitor_positions 실패: {e}")

        await asyncio.sleep(60)  # 1분 주기로 반복

### 서버가 켜지면 자동 실행되는 서버 이벤트 
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_monitor())