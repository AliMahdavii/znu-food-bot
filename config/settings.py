import os

from dotenv import load_dotenv


load_dotenv()


ZNU_USERNAME = os.getenv("ZNU_USERNAME")
ZNU_PASSWORD = os.getenv("ZNU_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

EDGE_PATH = os.getenv("EDGE_PATH")

ZNU_URL = "https://student.znu.ac.ir/identity/login"
