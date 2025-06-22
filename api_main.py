from fastapi import FastAPI
from autotrade.dashboard_router import router as dashboard_router
from autotrade.user_router import router as user_router
from autotrade.autotrade_router import router as autotrade_router
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

# 라우터를 등록해줘야함
app.include_router(dashboard_router)
app.include_router(user_router)
app.include_router(autotrade_router)

@app.get("/")
def root():
    return {"message": "🚀 자동매매 API 서버 정상 작동 중"}