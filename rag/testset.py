"""Ders 6: Test seti — sistemi ölçmek için sorular ve doğru cevaplar.

Her satır (data/testset.jsonl) bir soru:
  tur       : basit | birlestirme (2 bölüm gerekir) | hileli (yanlış varsayım) | yok (cevap dokümanlarda yok)
  soru      : kullanıcının soracağı soru
  beklenen  : doğru cevap (insanın yazdığı "altın cevap")
  anahtar   : doğru cevapta MUTLAKA geçmesi gereken kısa ifadeler (hızlı otomatik kontrol için)
  bolumler  : cevabın geçtiği [dosya, bölüm] listesi (retrieval'ı ölçmek için)
"""
import json
import re
from dataclasses import dataclass

from rag.loader import Document


@dataclass
class TestSorusu:
    __test__ = False   # adı "Test" ile başlıyor; pytest bunu test sınıfı sanmasın
    id: int
    tur: str
    soru: str
    beklenen: str
    anahtar: list[str]
    bolumler: list[tuple[str, str]]


def yukle(yol: str = "data/testset.jsonl") -> list[TestSorusu]:
    sorular = []
    with open(yol, encoding="utf-8") as f:
        for satir in f:
            if satir.strip():
                d = json.loads(satir)
                d["bolumler"] = [tuple(b) for b in d["bolumler"]]
                sorular.append(TestSorusu(**d))
    return sorular


def normalize(metin: str) -> str:
    """Karşılaştırma için: küçük harf (Türkçe I/İ dahil) + sayılardaki binlik noktasını sil (7.500 → 7500)."""
    metin = metin.replace("I", "ı").replace("İ", "i").lower()
    return re.sub(r"(?<=\d)\.(?=\d)", "", metin)


def anahtarlar_var_mi(metin: str, anahtarlar: list[str]) -> bool:
    return all(normalize(a) in normalize(metin) for a in anahtarlar)


def dogrula(sorular: list[TestSorusu], parcalar: list[Document]) -> list[str]:
    """Test setinin kendisini test eder. Hata listesi döndürür (boş = sorun yok).

    Test setinde hata varsa, sistemi yanlış puanlarız. O yüzden önce test setini kontrol ederiz:
      - Her soruda adı geçen bölüm gerçekten var mı? (yazım hatası?)
      - Anahtar ifadeler o bölümlerin metninde gerçekten geçiyor mu? (yanlış cevap yazılmış mı?)
    """
    bolum_metni: dict[tuple[str, str], str] = {}
    for p in parcalar:
        anahtar = (p.metadata["source"], p.metadata["section"])
        bolum_metni[anahtar] = bolum_metni.get(anahtar, "") + "\n" + p.text

    hatalar = []
    idler = [s.id for s in sorular]
    if len(idler) != len(set(idler)):
        hatalar.append("Tekrarlanan id var")
    for s in sorular:
        if s.tur not in {"basit", "birlestirme", "hileli", "yok"}:
            hatalar.append(f"#{s.id}: bilinmeyen tür '{s.tur}'")
        if s.tur == "yok":
            if s.bolumler:
                hatalar.append(f"#{s.id}: 'yok' sorusunun bölümü olmamalı")
            continue
        if not s.bolumler:
            hatalar.append(f"#{s.id}: bölüm yazılmamış")
        metin = ""
        for b in s.bolumler:
            if b not in bolum_metni:
                hatalar.append(f"#{s.id}: bölüm bulunamadı → {b[0]} › {b[1]}")
            metin += bolum_metni.get(b, "")
        for a in s.anahtar:
            if not anahtarlar_var_mi(metin, [a]):
                hatalar.append(f"#{s.id}: anahtar '{a}' belirtilen bölümlerde geçmiyor")
    return hatalar
