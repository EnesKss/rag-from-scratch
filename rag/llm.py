"""LLM katmanı: projenin geri kalanı sadece `generate()` fonksiyonunu bilir.

Neden ayrı bir dosya? İleride Gemini yerine Claude ya da OpenAI kullanmak
istersen sadece bu dosyayı değiştirirsin; RAG kodunun geri kalanı aynı kalır.
"""
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()  # .env dosyasındaki değişkenleri ortama yükler

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
_client = None


def _get_client() -> genai.Client:
    """İstemciyi ilk ihtiyaçta oluşturur.

    Dosya import edilir edilmez oluşturmuyoruz: öyle yapsaydık API anahtarı olmayan bir
    bilgisayarda (ör. repoyu yeni indiren biri) LLM'i hiç kullanmayan kodlar bile çökerdi.
    """
    global _client
    if _client is None:
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError(
                "GEMINI_API_KEY bulunamadı. .env.example dosyasını .env adıyla kopyala ve "
                "https://aistudio.google.com/apikey adresinden aldığın anahtarı içine yaz."
            )
        _client = genai.Client()  # GEMINI_API_KEY'i ortamdan kendisi okur
    return _client


def generate(prompt: str, deneme: int = 6) -> str:
    """Prompt'u modele gönderir, metin cevabı döndürür.

    API'ler bazen geçici hata verir: 503 (sunucu yoğun) ya da 429 (çok hızlı istek).
    Bu durumda hemen pes etmek yerine bekleyip tekrar deneriz; her denemede bekleme
    süresi ikiye katlanır (2, 4, 8, 16, 32 sn). Buna "exponential backoff" denir.
    """
    for i in range(deneme):
        try:
            response = _get_client().models.generate_content(model=MODEL, contents=prompt)
            return response.text
        except (errors.ServerError, errors.ClientError) as hata:
            gecici = getattr(hata, "code", None) in (429, 500, 503)
            if not gecici or i == deneme - 1:
                raise                         # kalıcı hata ya da son deneme: vazgeç
            bekle = 2 ** (i + 1)
            print(f"  [llm] geçici hata ({hata.code}), {bekle} sn sonra tekrar deneniyor...")
            time.sleep(bekle)
