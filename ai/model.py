import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq import Groq

SYSTEM_PROMPT = """Sen CodeTab AI'sın. Teknofest projesi için geliştirilmiş bir yapay zeka asistanısın.
Yalnızca şu konularda yardım ediyorsun:
- Linux komutları ve terminal kullanımı
- Matematik (asal sayı, EBOB, EKOK, denklemler, algoritmalar)
- Python programlama
- C++ programlama

Cevaplarını Türkçe ver. Kısa, net ve örnekli açıklamalar yap.
Konu dışı sorulara 'Bu konuda yardımcı olamam, Linux, Matematik veya Kodlama soruları sorabilirsin.' de."""


class CodeTabModel:
    def __init__(self):
        from ui.api_key_dialog import load_api_key
        api_key = load_api_key()
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY bulunamadı!\n"
                "Uygulamayı yeniden başlatın ve API key girin."
            )
        self.client = Groq(api_key=api_key)
        self.model = "llama3-70b-8192"
        self.history = []

    def ask(self, question: str, max_tokens: int = 512) -> str:
        self.history.append({"role": "user", "content": question})
        recent = self.history[-10:]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *recent
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )

        answer = response.choices[0].message.content.strip()
        self.history.append({"role": "assistant", "content": answer})
        return answer

    def gecmisi_temizle(self):
        self.history = []
