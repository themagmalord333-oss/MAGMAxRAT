import os
import secrets
from fastapi import FastAPI, Request, HTTPException
from pymongo import MongoClient
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# --- CONFIGURATION ---
# Maine aapka MongoDB Link yahan daal diya hai direct connection ke liye
MONGO_URL = "mongodb+srv://rj5706603:O95nvJYxapyDHfkw@cluster0.fzmckei.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Aapki details
BOT_TOKEN = "8250278558:AAHwfvIetFcU9uXgQn44kbirCrvxgD6CZ3g"
OWNER_ID = 7727470646

# URLs
BASE_URL = "https://numb-api.vercel.app/get-info"
MY_RENDER_URL = "https://magmaxrich.onrender.com"  # Aapka Render URL

# --- DATABASE SETUP ---
try:
    client = MongoClient(MONGO_URL)
    db = client["MagmaApiDB"]
    keys_collection = db["api_keys"]
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")

app = FastAPI()

# --- BOT COMMANDS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Sirf Owner is bot ko use kar sakta hai.")
        return
    await update.message.reply_text(
        "🔥 **Magma API Manager**\n\n"
        "Commands:\n"
        "`/genkey <name> <limit>` - Naya API Key banayein\n"
        "`/info <key>` - Key ka detail dekhein\n"
        "`/del <key>` - Key delete karein",
        parse_mode="Markdown"
    )

async def generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    try:
        # User input: /genkey king_api 100
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("⚠️ Format: `/genkey <custom_name> <limit>`\nExample: `/genkey king_api 100`", parse_mode="Markdown")
            return

        custom_name = args[0]
        limit = int(args[1])
        
        # Unique Key Generate karo
        api_key = secrets.token_hex(8)

        # Database mein save karo
        new_entry = {
            "custom_name": custom_name,
            "api_key": api_key,
            "total_limit": limit,
            "used": 0,
            "status": "active"
        }
        keys_collection.insert_one(new_entry)

        msg = (
            f"✅ **API Generated Successfully!**\n\n"
            f"📛 **Name:** `{custom_name}`\n"
            f"🔑 **Key:** `{api_key}`\n"
            f"🔢 **Limit:** `{limit}`\n\n"
            f"🔗 **Your URL:**\n"
            f"`{MY_RENDER_URL}/{custom_name}/lookup?phone=NUMBER&key={api_key}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def check_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Key toh batao! `/info <key>`", parse_mode="Markdown")
        return

    key = context.args[0]
    data = keys_collection.find_one({"api_key": key})
    
    if not data:
        await update.message.reply_text("❌ Ye Key exist nahi karti.")
        return

    await update.message.reply_text(
        f"📊 **Key Info**\n\n"
        f"Name: `{data['custom_name']}`\n"
        f"Limit: `{data['total_limit']}`\n"
        f"Used: `{data['used']}`\n"
        f"Remaining: `{data['total_limit'] - data['used']}`",
        parse_mode="Markdown"
    )

# --- BOT SETUP (WEBHOOK) ---
ptb_app = ApplicationBuilder().token(BOT_TOKEN).build()
ptb_app.add_handler(CommandHandler("start", start))
ptb_app.add_handler(CommandHandler("genkey", generate_key))
ptb_app.add_handler(CommandHandler("info", check_info))

@app.on_event("startup")
async def startup_event():
    # Webhook set karein taaki Render par Bot chalta rahe
    webhook_url = f"{MY_RENDER_URL}/webhook"
    await ptb_app.bot.set_webhook(webhook_url)
    await ptb_app.initialize()
    await ptb_app.start()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, ptb_app.bot)
        await ptb_app.process_update(update)
    except Exception as e:
        print(f"Webhook Error: {e}")
    return {"status": "ok"}

@app.get("/")
def home():
    return {"message": "Magma API is Running via MongoDB!", "status": "Active"}

# --- MAIN API ENDPOINT ---
@app.get("/{custom_name}/lookup")
def api_lookup(custom_name: str, phone: str, key: str):
    # 1. Database Check
    user_data = keys_collection.find_one({"custom_name": custom_name, "api_key": key})

    if not user_data:
        raise HTTPException(status_code=403, detail="Invalid API Name or Key")

    if user_data["used"] >= user_data["total_limit"]:
        raise HTTPException(status_code=403, detail="Limit Expired! Buy more.")

    # 2. Original API Call
    params = {"phone": phone, "apikey": "worrior"}
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        # 3. Usage Count Badhao
        keys_collection.update_one(
            {"api_key": key},
            {"$inc": {"used": 1}}
        )

        return {
            "developer": "MAGMA_RICH",
            "api_name": custom_name,
            "requests_left": user_data["total_limit"] - (user_data["used"] + 1),
            "result": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))