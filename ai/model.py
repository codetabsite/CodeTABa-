import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai

SYSTEM_PROMPT = """Sen CodeTab AI'sın. Teknofest projesi için geliştirilmiş bir yapay zeka asistanısın.
Yalnızca şu konularda yardım ediyorsun ancak yinede farklı konulara cevap ver:
- Linux komutları ve terminal kullanımı
- Matematik (asal sayı, EBOB, EKOK, denklemler, algoritmalar)
- Programlama Dilleri
- Ders Konuları( Turkce, Almanca, Sosyal Bilgiler, Fen, Kimya, Din, Felesefe, Geometri vb)

Cevaplarını Türkçe ver. Kısa, net ve örnekli açıklamalar yap.
Konu dışı sorulara 'Farklı bir konuya gecebilirsin' de.Ancak hafif basit bir cevap ver"""


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
        self.history = []

    def ask(self, question: str, max_tokens: int = 512) -> str:
        self.history.append({"role": "user", "parts": [question]})
        recent = self.history[-10:]

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
        return answer

    def gecmisi_temizle(self):
        self.history = []
