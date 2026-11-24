"""Ders 5 çalıştırma dosyası: sistemi uçtan uca çalıştır.

Çalıştır:  .venv\\Scripts\\python.exe ders05_cevap.py
"""
from rag.llm import generate
from rag.pipeline import RAG


def goster(cevap):
    print(f"\n❓ {cevap.soru}")
    print(f"💬 {cevap.metin}")
    if cevap.kullanilan:
        print("📎 Kaynaklar:")
        for n in cevap.kullanilan:
            p = cevap.parcalar[n - 1]
            print(f"   [{n}] {p.metadata['source']} › {p.metadata['section']}")
    print("-" * 70)


# ------------------------------------------------ 1. RAG OLMADAN: model ezberinden cevaplasın
soru = "Mavikod Teknoloji şirketinde çalışanlara yıllık kaç gün izin veriliyor?"
print("\n========== 1) RAG OLMADAN (sadece Gemini) ==========")
print(f"\n❓ {soru}")
print(f"💬 {generate(soru).strip()}")
print("-" * 70)

# ------------------------------------------------ 2. RAG İLE
print("\n========== 2) RAG İLE ==========")
rag = RAG()
for s in [
    soru,
    "Yemek kartına günde ne kadar para yükleniyor?",
    "Bilgisayarımı kaybettim, ne yapmalıyım?",
]:
    goster(rag.sor(s))

# ------------------------------------------------ 3. Cevabı dokümanlarda OLMAYAN sorular
print("\n========== 3) DOKÜMANLARDA OLMAYAN SORULAR ==========")
for s in [
    "Mavikod'un geçen yılki cirosu ne kadar?",
    "Ofise köpeğimi getirebilir miyim?",
]:
    goster(rag.sor(s))
