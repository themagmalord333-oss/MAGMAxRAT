# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Credentials
    TOKEN = os.getenv("BOT_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID"))
    ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    
    # Bot Settings
    BOT_USERNAME = ""  # @BotFather से मिलेगा
    BOT_NAME = "YourBotName"
    
    # Webhook Settings (Optional)
    WEBHOOK = False
    PORT = 8443
    URL = "https://yourdomain.com"
    
    # Features
    ALLOW_EXCL = True  # ! और / दोनों कमांड्स
    DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en")
    
    # Database
    DB_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "bot.log"
    
    # Security
    RATE_LIMIT = 10  # Messages per second per chat
    
config = Config()