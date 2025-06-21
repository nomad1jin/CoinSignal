# autotrade/models.py
from pydantic import BaseModel

class UserSettings(BaseModel):
    max_daily_invest: int
    loss_cut: float
    take_profit: float
    max_coin_count: int
