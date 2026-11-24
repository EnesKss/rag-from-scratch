"""Ders 4 çalıştırma dosyası: index'i kur, üç arama yöntemini karşılaştır.

Çalıştır:  .venv\\Scripts\\python.exe ders04_arama.py
"""
from rag.chunker import chunk_by_section
from rag.loader import load
from rag.search import KelimeIndex, hybrid_ara, index_olustur, vektor_ara

parcalar = [c for d in load("data/raw") for c in chunk_by_section(d)]

print("\nIndex kuruluyor (parçalar embed edilip index/ klasörüne yazılıyor)...")
index_olustur(parcalar)
kelime_index = KelimeIndex(parcalar)
print(f"Tamam: {len(parcalar)} parça index'te.\n")

# Her soru için DOĞRU parçanın bölüm adını biliyoruz (dokümanları biz yazdık).
sorular = {
    "Evden çalışırken internet parası veriliyor mu?": "Ev ofis desteği",
    "Bilgisayarımı kaybettim, ne yapmalıyım?": "Güvenlik olayı bildirimi",
    "Şirketin CEO'su kim?": "Kısaca Mavikod",
    "MFA için SMS kullanabilir miyim?": "Şifreler ve kimlik doğrulama",
    "M4 seviyesinin unvanı ne?": "Kariyer seviyeleri (mühendislik)",
    "Yemek kartına günde ne kadar para yükleniyor?": "Yemek kartı",
}


def sira_bul(sonuclar, dogru):
    """Doğru parça listede kaçıncı sırada? Yoksa '-'."""
    for sira, (_, p) in enumerate(sonuclar, start=1):
        if p.metadata["section"] == dogru:
            return str(sira)
    return "-"


print(f"{'Soru':<50} {'Vektör':>7} {'Kelime':>7} {'Hybrid':>7}")
print("-" * 74)
for soru, dogru in sorular.items():
    v = sira_bul(vektor_ara(soru, k=5), dogru)
    b = sira_bul(kelime_index.ara(soru, k=5), dogru)
    h = sira_bul(hybrid_ara(soru, kelime_index, k=5), dogru)
    print(f"{soru:<50} {v:>7} {b:>7} {h:>7}")
print("-" * 74)
print("Tablodaki sayı: doğru parçanın ilk 5 sonuç içindeki sırası ('-' = ilk 5'te yok)")
