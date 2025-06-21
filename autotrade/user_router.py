from fastapi import APIRouter
from autotrade.models import UserSettings

router = APIRouter()

user_settings_store = {}

@router.post("/user/info")
def update_user_info(settings: UserSettings):
    user_settings_store["default"] = settings.dict()
    return {
        "success": True, 
        "message": "사용자 설정이 업데이트되었습니다.",
        "data": settings
    }

@router.get("/user/info")
def get_user_info():
    if "default" not in user_settings_store:
        return {
            "success": False,
            "message": "저장된 설정이 없습니다.",
            "data": None
        }

    return {
        "success": True,
        "message": "사용자 설정 조회 성공",
        "data": user_settings_store["default"]
    }
