# ⚡ CodeTab AI — Teknofest (Groq API Sürümü)

Raspberry Pi 3B dahil tüm cihazlarda 1-2 saniyede yanıt verir.

## 🚀 Kurulum

```bash
# 1. Bağımlılıkları kur
pip3 install -r requirements.txt

# 2. Groq API key al → groq.com (ücretsiz)

# 3. Başlat (key otomatik sorulur)
./baslat.sh
```
Yada APPIMAGE Yükleyin 

## 🔑 Groq API Key Alma
1. groq.com → Sign Up (ücretsiz)
2. API Keys → Create API Key
3. Kopyala → baslat.sh'e yapıştır

## 📁 Yapı
```
codetab-groq/
├── main.py
├── baslat.sh       ← Bunu çalıştır!
├── requirements.txt
├── ai/model.py     ← Groq API
└── ui/mainwindow.py ← PyQt5 arayüz
```

*Teknofest 2026 — CodeTab AI* 
