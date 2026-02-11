from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI(title="MAGMAxRICH API")

BASE_URL = "https://numb-api.vercel.app/get-info"
API_KEY = "worrior"

@app.get("/")
def home():
    return {"message": "Welcome to MAGMAxRICH API", "status": "Active"}

@app.get("/magma/lookup")
def lookup_number(phone: str):
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number mangta hai!")

    params = {"phone": phone, "apikey": API_KEY}
    
    try:
        # 1. Pehle Data mangwaya
        response = requests.get(BASE_URL, params=params)
        original_data = response.json()
        
        # 2. Ab hum Data ko MODIFY karenge (Naam Badlenge)
        # Hum check kar rahe hain ki kya data sahi aaya hai?
        if "data" in original_data:
            # Yahan humne purana naam hata kar apna daal diya
            original_data["data"]["API BY"] = "@Anysnapsupport"
            original_data["data"]["Owner"] = "@MAGMAxRICH"
            
        # 3. Ab badla hua data user ko dikhayenge
        return {
            "api_name": "MAGMAxRICH",
            "result": original_data
        }
        
    except Exception as e:
        return {"error": str(e)}