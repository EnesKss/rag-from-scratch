"""Ders 6 çalıştırma dosyası: test setini doğrula ve RETRIEVAL'ı ölç (LLM yok, ücretsiz).

Çalıştır:  .venv\\Scripts\\python.exe ders06_testset.py
"""
from collections import Counter, defaultdict

from rag.chunker import chunk_by_section
from rag.loader import load
from rag.search import KelimeIndex, hybrid_ara, index_olustur, vektor_ara
from rag.testset import dogrula, yukle

K = 5
parcalar = [c for d in load("data/raw") for c in chunk_by_section(d)]
sorular = yukle()

# ---------------------------------------------------------------- 1. Test setini doğrula
print(f"\n1) Test seti: {len(sorular)} soru  {dict(Counter(s.tur for s in sorular))}")
hatalar = dogrula(sorular, parcalar)
if hatalar:
    print("   ❌ Test setinde hatalar var, önce bunları düzelt:")
    for h in hatalar:
        print("     -", h)
    raise SystemExit(1)
print("   ✅ Tüm bölümler mevcut, tüm anahtar ifadeler doğru bölümlerde geçiyor.")

# ---------------------------------------------------------------- 2. Retrieval'ı ölç
index_olustur(parcalar)
kelime_index = KelimeIndex(parcalar)
yontemler = {
    "Vektör": lambda q: vektor_ara(q, k=K),
    "Kelime": lambda q: kelime_index.ara(q, k=K),
    "Hybrid": lambda q: hybrid_ara(q, kelime_index, k=K),
}


def recall(soru, sonuclar) -> float:
    """Gereken bölümlerin kaçta kaçı ilk K sonuç içinde? (1.0 = hepsi bulundu)"""
    bulunan = {(p.metadata["source"], p.metadata["section"]) for _, p in sonuclar}
    return sum(b in bulunan for b in soru.bolumler) / len(soru.bolumler)


olculecek = [s for s in sorular if s.tur != "yok"]   # 'yok' sorularında bulunacak bölüm yok
skor = defaultdict(lambda: defaultdict(list))         # skor[yöntem][tür] = [recall, ...]
kacirilan = defaultdict(list)
for s in olculecek:
    for ad, ara in yontemler.items():
        r = recall(s, ara(s.soru))
        skor[ad][s.tur].append(r)
        skor[ad]["TOPLAM"].append(r)
        if ad == "Hybrid" and r < 1:
            kacirilan[ad].append((s, r))

turler = ["basit", "birlestirme", "hileli", "TOPLAM"]
print(f"\n2) Retrieval recall@{K}  (doğru bölümlerin ilk {K} sonuçta bulunma oranı)\n")
print(f"{'Yöntem':<8}" + "".join(f"{t:>14}" for t in turler))
print("-" * (8 + 14 * len(turler)))
for ad in yontemler:
    print(f"{ad:<8}" + "".join(f"{sum(skor[ad][t]) / len(skor[ad][t]):>14.0%}" for t in turler))

print(f"\n3) Hybrid'in kaçırdığı sorular (hata analizi için):")
for s, r in kacirilan["Hybrid"] or []:
    print(f"   #{s.id:<3} recall={r:.0%}  {s.soru}")
if not kacirilan["Hybrid"]:
    print("   yok 🎉")
