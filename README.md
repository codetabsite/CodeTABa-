# ⚡ CodeTab AI — Teknofest 

Raspberry Pi 3B dahil tüm cihazlarda hızlı yanıt verir.  
**Model:** Gemini 2.5 Flash-Lite — günde 1000 ücretsiz istek.

## 🚀 Kurulum

```bash
# 1. Bağımlılıkları kur
pip3 install -r requirements.txt

# 2. Gemini API key al → aistudio.google.com (ücretsiz, kredi kartı gerekmez)

# 3. Başlat (key otomatik sorulur)
./baslat.sh
```
Yada APPIMAGE Yükleyin (API GEREKLI)
APP IMAGE CALISMAZ ISE .DEB DOSYASINI YUKLEYİN(DEBIAN LAZIM)

## 🔑 Gemini API Key Alma
1. [aistudio.google.com](https://aistudio.google.com) → Sign In (Google hesabı)
2. **Get API Key** → Create API Key
3. Kopyala → uygulamayı başlatınca yapıştır

## 📁 Yapı
```
CodeTABai/
├── main.py
├── baslat.sh        ← Bunu çalıştır!
├── requirements.txt
├── ai/model.py      ← Gemini API
└── ui/mainwindow.py 

## 📊 Ücretsiz Limitler
| Model | Günlük | Dakika |
|-------|--------|--------|
| Gemini 2.5 Flash | 250 istek | 10 istek |

*Teknofest 2026 — CodeTab AI*

