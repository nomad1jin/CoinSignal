from fastapi import FastAPI
from autotrade.dashboard_router import router as dashboard_router
from autotrade.user_router import router as user_router
from autotrade.autotrade_router import router as autotrade_router

app = FastAPI(
    title="AutoTrading API",
    description="트렌드 기반 자동매매 시스템 API",
    version="1.0"
)

# 라우터를 등록해줘야함
app.include_router(dashboard_router)
app.include_router(user_router)
app.include_router(autotrade_router)

@app.get("/")
def root():
    return {"message": "🚀 자동매매 API 서버 정상 작동 중"}