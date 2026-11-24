"""Ders 2 çalıştırma dosyası: iki parçalama yöntemini yan yana karşılaştır.

Testlerin hepsi geçtikten sonra çalıştır:  .venv\\Scripts\\python.exe ders02_parcala.py
"""
from rag.chunker import chunk_by_section, chunk_fixed
from rag.loader import load

docs = load("data/raw")
fixed = [c for d in docs for c in chunk_fixed(d, size=500, overlap=50)]
section = [c for d in docs for c in chunk_by_section(d, max_chars=800)]


def ozet(ad, chunks):
    uzunluklar = [len(c.text) for c in chunks]
    print(f"{ad:<22} parça: {len(chunks):>3}   ort. uzunluk: {sum(uzunluklar) // len(chunks):>4}   "
          f"en kısa: {min(uzunluklar):>4}   en uzun: {max(uzunluklar):>4}")


print()
ozet("Sabit (500/50)", fixed)
ozet("Başlığa göre (800)", section)

# Aynı bilgiyi iki yöntemde arayalım: "Yemek kartına günde ne kadar yükleniyor?"
aranan = "450 TL"
print(f"\n'{aranan}' geçen parça — SABİT yöntem:")
print("-" * 70)
print(next(c for c in fixed if aranan in c.text).text)
print("-" * 70)

print(f"\n'{aranan}' geçen parça — BAŞLIĞA GÖRE yöntem:")
c = next(c for c in section if aranan in c.text)
print(f"[kaynak: {c.metadata['source']} › {c.metadata['section']}]")
print("-" * 70)
print(c.text)
print("-" * 70)
print("\nSoru: Hangi parçayı LLM'e verirsen daha iyi cevap alırsın? Neden?")
