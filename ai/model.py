import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai

SYSTEM_PROMPT = """Sen CodeTab AI'sın. Teknofest projesi için geliştirilmiş bir yapay zeka asistanısın.
Her konuda yardım edebilirsin:
- Linux komutları ve terminal kullanımı
- Matematik (asal sayı, EBOB, EKOK, denklemler, algoritmalar)
- Programlama Dilleri
- Ders Konuları (Türkçe, Almanca, Sosyal Bilgiler, Fen, Kimya, Din, Felsefe, Geometri vb)
- Genel sohbet ve günlük sorular

Cevaplarını Türkçe ver. Kısa, net ve örnekli açıklamalar yap."""

HISTORY_FILE = Path.home() / ".config" / "codetab" / "history.json"


def load_history() -> list:
    try:
        if HISTORY_FILE.exists():
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


def save_history(history: list) -> None:
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        # Sadece son 50 mesajı sakla
        HISTORY_FILE.write_text(
            json.dumps(history[-50:], ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception:
        pass


class CodeTabModel:
    def __init__(self):
        from ui.api_key_dialog import load_api_key
        api_key = load_api_key()
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY bulunamadı!\n"
                "Uygulamayı yeniden başlatın ve API key girin."
            )
        genai.configure(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        # Hafızayı dosyadan yükle
        self.history = load_history()

    def ask(self, question: str, max_tokens: int = 1024) -> str:
        self.history.append({"role": "user", "parts": [question]})
        recent = self.history[-20:]

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=SYSTEM_PROMPT,
        )

        response = model.generate_content(
            recent,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,
            ),
        )

        answer = response.text.strip()
        self.history.append({"role": "model", "parts": [answer]})
        # Her cevaptan sonra diske kaydet
        save_history(self.history)
        return answer

    def gecmisi_temizle(self):
        self.history = []
        save_history([])
