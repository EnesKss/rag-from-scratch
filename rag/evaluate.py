"""Ders 7: Cevap kalitesini ölçmek (LLM-as-a-judge).

Her test sorusu için:
  1. RAG sistemine sor, cevabı al.
  2. Cevabı puanla:
     - anahtar_ok : Anahtar ifadeler cevapta geçiyor mu? (ucuz, kural tabanlı)
     - dogru      : Hakem LLM'e göre cevap, altın cevapla aynı bilgiyi veriyor mu?
     - sadik      : Hakem LLM'e göre cevaptaki her bilgi kaynaklarda var mı? (faithfulness)
     - kaynak_var : Cevapta en az bir [n] atfı var mı?

Ragas kütüphanesi de faithfulness'ı aynı fikirle (bir LLM'e kontrol ettirerek) ölçer.
Biz burada aynı fikri birkaç satırla kendimiz yazıyoruz ki içini görelim.
"""
import json
import re
import time
from dataclasses import dataclass

from rag.llm import generate
from rag.pipeline import RAG, kaynaklari_yaz
from rag.testset import TestSorusu, anahtarlar_var_mi

HAKEM_PROMPT = """Bir soru-cevap sistemini değerlendiren tarafsız ve titiz bir hakemsin.

KAYNAKLAR (sisteme verilen belge parçaları):
{kaynaklar}

SORU: {soru}
DOĞRU CEVAP (insan tarafından yazıldı): {beklenen}
SİSTEMİN CEVABI: {cevap}

İki şeyi değerlendir:
1. dogru: Sistemin cevabı, DOĞRU CEVAP ile aynı bilgiyi veriyor mu? Farklı kelimelerle anlatması
   sorun değil. Önemli bir bilgi eksikse ya da DOĞRU CEVAP ile çelişiyorsa false.
2. sadik: Sistemin cevabındaki HER bilgi KAYNAKLAR'da geçiyor mu? Kaynaklarda olmayan tek bir
   bilgi bile varsa false.

SADECE şu formatta JSON döndür, başka hiçbir şey yazma:
{{"dogru": true, "sadik": true, "gerekce": "tek cümle"}}"""


@dataclass
class Sonuc:
    id: int
    tur: str
    soru: str
    cevap: str
    anahtar_ok: bool
    dogru: bool | None      # None = hakem cevabı okunamadı
    sadik: bool | None
    kaynak_var: bool | None  # 'yok' sorularında anlamsız → None
    gerekce: str = ""


def _hakem(soru: TestSorusu, cevap) -> tuple[bool | None, bool | None, str]:
    prompt = HAKEM_PROMPT.format(
        kaynaklar=kaynaklari_yaz(cevap.parcalar), soru=soru.soru,
        beklenen=soru.beklenen, cevap=cevap.metin,
    )
    yanit = generate(prompt)
    eslesme = re.search(r"\{.*\}", yanit, re.DOTALL)   # LLM bazen JSON'un etrafına metin ekler
    try:
        d = json.loads(eslesme.group(0))
        return bool(d["dogru"]), bool(d["sadik"]), str(d.get("gerekce", ""))
    except (AttributeError, ValueError, KeyError):
        return None, None, f"hakem cevabı okunamadı: {yanit[:80]}"


def degerlendir(rag: RAG, sorular: list[TestSorusu], bekleme: float = 4.0) -> list[Sonuc]:
    """bekleme: ücretsiz API'nin dakikalık istek sınırına takılmamak için çağrılar arası saniye."""
    sonuclar = []
    for i, s in enumerate(sorular, start=1):
        cevap = rag.sor(s.soru)
        time.sleep(bekleme)

        if s.tur == "yok":
            # Doğru davranış: "Bu bilgi dokümanlarda yok." demek. Hakeme gerek yok.
            ok = cevap.bilgi_yok
            sonuc = Sonuc(s.id, s.tur, s.soru, cevap.metin, ok, ok, True, None,
                          "" if ok else "bilgi yok demesi gerekirdi")
        elif cevap.bilgi_yok:
            # Cevap dokümanlarda VARDI ama sistem 'yok' dedi → yanlış ama uydurma değil (sadık).
            sonuc = Sonuc(s.id, s.tur, s.soru, cevap.metin, False, False, True, False,
                          "cevap varken 'bilgi yok' dedi")
        else:
            dogru, sadik, gerekce = _hakem(s, cevap)
            time.sleep(bekleme)
            sonuc = Sonuc(s.id, s.tur, s.soru, cevap.metin,
                          anahtarlar_var_mi(cevap.metin, s.anahtar), dogru, sadik,
                          bool(cevap.kullanilan), gerekce)

        isaret = "✅" if sonuc.dogru else "❌"
        print(f"  [{i:>2}/{len(sorular)}] {isaret} #{s.id:<3} {s.tur:<12} {s.soru[:55]}", flush=True)
        sonuclar.append(sonuc)
    return sonuclar


def _oran(degerler: list) -> float | None:
    gecerli = [v for v in degerler if v is not None]
    return sum(gecerli) / len(gecerli) if gecerli else None


def ozet(sonuclar: list[Sonuc]) -> dict[str, float | None]:
    cevapli = [s for s in sonuclar if s.tur != "yok"]
    yok = [s for s in sonuclar if s.tur == "yok"]
    return {
        "Doğruluk (hakem)": _oran([s.dogru for s in sonuclar]),
        "Doğruluk (anahtar)": _oran([s.anahtar_ok for s in sonuclar]),
        "Sadakat (faithfulness)": _oran([s.sadik for s in sonuclar]),
        "Kaynak gösterme": _oran([s.kaynak_var for s in cevapli]),
        "'Bilgi yok' doğru deme": _oran([s.dogru for s in yok]),
        "Basit soru doğruluğu": _oran([s.dogru for s in sonuclar if s.tur == "basit"]),
        "Birleştirme doğruluğu": _oran([s.dogru for s in sonuclar if s.tur == "birlestirme"]),
        "Hileli soru doğruluğu": _oran([s.dogru for s in sonuclar if s.tur == "hileli"]),
    }
