"""Ders 3 çalıştırma dosyası: embedding'leri kendi gözünle gör.

Çalıştır:  .venv\\Scripts\\python.exe ders03_embedding.py
"""
from rag.chunker import chunk_by_section, chunk_fixed
from rag.embedder import benzerlik, embed
from rag.loader import load

# ---------------------------------------------------------------- 1. Bir vektör neye benzer?
v = embed(["yıllık izin"])[0]
print("\n1) 'yıllık izin' metninin embedding'i")
print(f"   uzunluk: {len(v)} sayı")
print(f"   ilk 8 sayı: {[round(float(x), 3) for x in v[:8]]} ...")

# ---------------------------------------------------------------- 2. Hangi kelimeler yakın?
kelimeler = ["yıllık izin", "tatil", "şifre", "parola", "yemek kartı", "öğle yemeği"]
vektorler = embed(kelimeler)

print("\n2) Benzerlik tablosu (1.00 = aynı anlam, 0 civarı = ilgisiz)\n")
print(" " * 14 + "".join(f"{k:>13}" for k in kelimeler))
for k1, v1 in zip(kelimeler, vektorler):
    print(f"{k1:>14}" + "".join(f"{benzerlik(v1, v2):>13.2f}" for v2 in vektorler))

# ---------------------------------------------------------------- 3. Gerçek parçalarda arama
docs = load("data/raw")
parcalar = [c for d in docs for c in chunk_by_section(d)]
parca_vektorleri = embed([p.text for p in parcalar])

soru = "Evden çalışırken internet parası veriliyor mu?"
soru_vektoru = embed([soru])[0]

skorlar = [(benzerlik(soru_vektoru, pv), p) for pv, p in zip(parca_vektorleri, parcalar)]
skorlar.sort(key=lambda x: x[0], reverse=True)

print(f"\n3) Soru: '{soru}'")
print(f"   {len(parcalar)} parçanın içinden en benzer 3 tanesi:\n")
for skor, p in skorlar[:3]:
    print(f"   {skor:.2f}  {p.metadata['source']} › {p.metadata['section']}")

# ---------------------------------------------------------------- 4. Ders 2'nin kanıtı
temiz = next(p for p in parcalar if p.metadata["section"] == "Yemek kartı")
karisik = next(c for d in docs for c in chunk_fixed(d) if "450 TL" in c.text)
print("\n4) Aynı bilgiyi içeren iki parçanın soruya benzerliği:")
print(f"   başlığa göre parça (sadece yemek kartı):   {benzerlik(soru_vektoru, embed([temiz.text])[0]):.2f}")
print(f"   sabit parça (diş sigortası + yemek kartı): {benzerlik(soru_vektoru, embed([karisik.text])[0]):.2f}")
