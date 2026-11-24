"""Ders 1 çalıştırma dosyası: dokümanları yükle ve ne yüklediğimize bak.

Çalıştır:  .venv\\Scripts\\python.exe ders01_yukle.py
"""
from rag.loader import load

docs = load("data/raw")

print(f"\nYüklenen doküman sayısı: {len(docs)}\n")
print(f"{'Dosya':<32} {'Başlık':<42} {'Kelime':>7}")
print("-" * 83)
total_words = 0
for doc in docs:
    words = len(doc.text.split())
    total_words += words
    print(f"{doc.metadata['source']:<32} {doc.metadata.get('title', '-'):<42} {words:>7}")

print("-" * 83)
print(f"Toplam: {total_words} kelime  (~{total_words // 300} sayfa, sayfa başı ~300 kelime)\n")

# Bir dokümanın içine bakalım: Document nesnesi neye benziyor?
ornek = docs[1]
print("Örnek Document:")
print(f"  metadata = {ornek.metadata}")
print(f"  text     = {ornek.text[:200]!r}...")
