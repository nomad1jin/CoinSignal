import pyupbit
from dotenv import load_dotenv
import os 

load_dotenv()
access = os.getenv("access")
secret = os.getenv("secret")
upbit = pyupbit.Upbit(access, secret)

balances = upbit.get_balances()
print(f"[현재 보유 자산] {balances}")