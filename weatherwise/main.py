from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import pandas as pd
from datetime import datetime
from functools import lru_cache

# ---------------------------------------------------------
# BURAYA KENDİ GEMINI API ANAHTARINIZI YAZIN:
GEMINI_API_KEY = "AIzaSyBW3LZ4jq1wpkqXZ27ekAaQ6-hMDQo0jIY"
# ---------------------------------------------------------

app = FastAPI(title="WeatherWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# FAZ 2.1: Karar Motoru
def generate_weather_tags(current_temp, feels_like, wind_speed, precip_prob, humidity, uv_index, cloud_cover, evening_temp):
    tags = []
    if precip_prob > 50:
        if wind_speed > 30: tags.append("Şemsiye ters dönebilir, kapüşonlu yağmurluk şart.")
        else: tags.append("Yağmur ihtimali yüksek, şemsiyeni yanına al.")
    if current_temp > 25 and uv_index > 6 and cloud_cover < 30:
        tags.append("Güneş çok dik, şapka tak ve güneş kremini unutma.")
    if current_temp > 28 and humidity > 70:
        tags.append("Hava yapış yapış ve nemli. Terletmeyen pamuklu giysiler seç.")
    if cloud_cover < 20 and wind_speed > 25 and current_temp < 15:
        tags.append("Güneşe aldanma, rüzgar üşütür. İnce bir rüzgarlık hayat kurtarır.")
    if (current_temp - evening_temp) > 8:
        tags.append("Gündüz tişörtle gezilir ama akşam çok soğuyacak, yanına kesinlikle ceket al.")
    if feels_like < 10 and not any("üşütür" in t or "soğuyacak" in t for t in tags):
        tags.append("Hava oldukça soğuk, kalın giyin (mont vakti).")
    elif feels_like > 25 and not any("pamuklu" in t or "güneş" in t for t in tags):
        tags.append("Hava sıcak, ince ve rahat giysiler tercih et.")
    if len(tags) == 0:
        tags.append("Hava tam kararında. Normal günlük kıyafetlerinle çıkabilirsin.")
    return " ".join(tags)

# FAZ 2.2: REST API (Curl) ile Gemini Bağlantısı
# FAZ 2.2: REST API (Curl) ile Gemini Bağlantısı
@lru_cache(maxsize=32)
def rewrite_with_ai(raw_tags):
    # Eski modeller silindiği için en güncel 'gemini-2.5-flash' modeline geçiş yaptık!
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"Sen WEATHERWISE adında, genç ve enerjik bir hava durumu asistanısın. Sana verilen hava durumu tavsiyelerini, sosyal medyada paylaşılacak 1 veya 2 cümlelik, akıcı, arkadaşça bir 'Story' metnine dönüştür. Tırnak işareti kullanma. Ham tavsiyeler: {raw_tags}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() 
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        
    except Exception as e:
        return f"DEDEKTİF MODU: {str(e)}"

@app.get("/api/story")
def generate_story(lat: float = 40.18, lon: float = 29.06): 
    # Open-Meteo'dan veri çekme
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon, "forecast_days": 1,
        "hourly": ["temperature_2m", "apparent_temperature", "precipitation_probability",
                   "windspeed_10m", "relative_humidity_2m", "cloudcover", "uv_index"],
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    df = pd.DataFrame({
        'tarih_saat': pd.to_datetime(data['hourly']['time']),
        'sicaklik': data['hourly']['temperature_2m'],
        'hissedilen': data['hourly']['apparent_temperature'],
        'yagis': data['hourly']['precipitation_probability'],
        'ruzgar': data['hourly']['windspeed_10m'],
        'nem': data['hourly']['relative_humidity_2m'],
        'bulut': data['hourly']['cloudcover'],
        'uv': data['hourly']['uv_index']
    })
    
   # df.iloc[0] yerine bilgisayarın şu anki saatini bulup o indeksi çekiyoruz!
    su_anki_saat = datetime.now().hour
    current_data = df.iloc[su_anki_saat]
    
    aksam_verisi = df[df['tarih_saat'].dt.hour == 20]
    evening_temp = aksam_verisi['sicaklik'].values[0] if not aksam_verisi.empty else current_data['sicaklik']
    
    raw_advice = generate_weather_tags(
        current_data['sicaklik'], current_data['hissedilen'], current_data['ruzgar'],
        current_data['yagis'], current_data['nem'], current_data['uv'],
        current_data['bulut'], evening_temp
    )
    
    humanized_story = rewrite_with_ai(raw_advice)
    
   # ... (önceki kodlar aynı kalıyor)

    # Hava durumuna göre bir 'mood' (mod) belirliyoruz
    weather_mood = "clear" # varsayılan
    if current_data['yagis'] > 50:
        weather_mood = "rainy"
    elif current_data['sicaklik'] < 5:
        weather_mood = "cold"
    elif current_data['uv'] > 6:
        weather_mood = "sunny"
    elif current_data['bulut'] > 60:
        weather_mood = "cloudy"

    return {
        "location": "Bursa",
        "current_temp": int(current_data['sicaklik']),
        "wind_kmh": int(current_data['ruzgar']),
        "precip_prob": int(current_data['yagis']),
        "story_text": str(humanized_story),
        "mood": weather_mood  # YENİ: Arayüz bu bilgiye göre renk değiştirecek
    }
    
