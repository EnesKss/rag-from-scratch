"""Ders 7 çalıştırma dosyası: test setinde cevap kalitesini ölç ve iki chunking yöntemini karşılaştır.

Hızlı deneme (6 soru):   .venv\\Scripts\\python.exe ders07_olcum.py --hizli
Tam ölçüm (40 soru × 2): .venv\\Scripts\\python.exe ders07_olcum.py      (~15 dk; ücretsiz API sınırları yüzünden yavaş)
"""
import json
import sys
from dataclasses import asdict
from pathlib import Path

from rag.chunker import chunk_by_section, chunk_fixed
from rag.evaluate import degerlendir, ozet
from rag.pipeline import RAG
from rag.testset import yukle

hizli = "--hizli" in sys.argv
sorular = yukle()
if hizli:
    sorular = [s for s in sorular if s.id in {1, 23, 24, 31, 35, 36}]   # her türden birkaç soru

deneyler = {
    "Başlığa göre": chunk_by_section,
    "Sabit (500/50)": chunk_fixed,
}
dosya_adi = {"Başlığa göre": "baslik", "Sabit (500/50)": "sabit"}

Path("sonuclar").mkdir(exist_ok=True)
tablolar = {}
for ad, parcalayici in deneyler.items():
    print(f"\n=== Deney: {ad} chunking — {len(sorular)} soru ===")
    rag = RAG(parcalayici=parcalayici)
    sonuclar = degerlendir(rag, sorular)
    tablolar[ad] = ozet(sonuclar)
    dosya = Path("sonuclar") / f"{'hizli_' if hizli else ''}{dosya_adi[ad]}.json"
    dosya.write_text(json.dumps([asdict(s) for s in sonuclar], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ayrıntılar → {dosya}")

# ---------------------------------------------------------------- Karşılaştırma tablosu
print(f"\n{'Metrik':<26}" + "".join(f"{ad:>18}" for ad in deneyler))
print("-" * (26 + 18 * len(deneyler)))
for metrik in next(iter(tablolar.values())):
    hucreler = []
    for ad in deneyler:
        v = tablolar[ad][metrik]
        hucreler.append(f"{'-' if v is None else f'{v:.0%}':>18}")
    print(f"{metrik:<26}" + "".join(hucreler))
