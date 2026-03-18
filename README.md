# 🌤️ WeatherWise: AI Destekli Hava Durumu Asistanı

Sıkıcı hava durumu verilerini (nem, rüzgar hızı, basınç vb.) okumak yerine, yapay zekanın durumu analiz edip doğrudan "Bugün mont giy" veya "Şemsiyesiz çıkma" gibi pratik tavsiyeler vermesini istedim. 

Bu projeyi, modern web teknolojilerini (FastAPI) ve yeni nesil büyük dil modellerini (Google Gemini 2.5 Flash) birleştirerek, veriyi insan diline çeviren uçtan uca, hızlı bir çözüm geliştirmek amacıyla kodladım.

## ✨ Özellikler
- **Gerçek Zamanlı Veri:** Open-Meteo API ile anlık saatlik konum verisi.
- **Kural Motoru:** Gelen veriyi (sıcaklık, rüzgar, UV vb.) analiz eden özel mantık katmanı.
- **Yapay Zeka (Gemini AI):** Robotik verileri, sosyal medyada paylaşılacak kıvamda doğal ve akıcı bir hikayeye (Story) dönüştürme.
- **Dinamik Arayüz:** Havanın durumuna (güneşli, yağmurlu, soğuk) göre anında renk ve ikon değiştiren Tailwind CSS tabanlı tasarım.

## 🛠️ Teknolojiler
- **Backend:** Python, FastAPI, Pandas, Requests
- **Yapay Zeka:** Google Gemini 2.5 Flash API
- **Frontend:** HTML5, Tailwind CSS, JavaScript (Fetch API)
- **Performans:** `lru_cache` ile optimize edilmiş, gereksiz API isteklerini engelleyen önbellek mimarisi.

## 🚀 Nasıl Çalıştırılır?
1. Repoyu indirin ve proje klasörüne gidin.
2. Gerekli kütüphaneleri kurun: `pip install -r requirements.txt`
3. Kök dizinde bir `.env` dosyası oluşturup içine Google Gemini API anahtarınızı ekleyin: `GEMINI_API_KEY=sizin_anahtariniz`
4. Backend sunucusunu başlatın: `uvicorn main:app --reload`
5. Tarayıcıda doğrudan `index.html` dosyasını açın.
