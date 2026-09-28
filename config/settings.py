import os

from dotenv import load_dotenv


load_dotenv()


ZNU_USERNAME = os.getenv("ZNU_USERNAME")
ZNU_PASSWORD = os.getenv("ZNU_PASSWORD")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

ZNU_URL = "https://food.znu.ac.ir/"
