"""evaluate.py testleri: hakem cevabını okuma, puanlama dalları ve özet. LLM taklit edilir."""
import rag.evaluate as evaluate
from rag.evaluate import Sonuc, degerlendir, ozet
from rag.loader import Document
from rag.pipeline import BILGI_YOK, Cevap
from rag.testset import TestSorusu

P = [Document("Yıllık izin 18 gündür.", {"source": "izin.md", "section": "Yıllık izin"})]


def soru(tur="basit", anahtar=("18",), id=1):
    return TestSorusu(id=id, tur=tur, soru="İzin kaç gün?", beklenen="18 gün",
                      anahtar=list(anahtar), bolumler=[] if tur == "yok" else [("izin.md", "Yıllık izin")])


class SahteRAG:
    def __init__(self, metin, kullanilan=(1,)):
        self.metin, self.kullanilan = metin, list(kullanilan)

    def sor(self, s):
        return Cevap(soru=s, metin=self.metin, parcalar=P, kullanilan=self.kullanilan)


def hakem_yaniti(monkeypatch, yanit):
    cagri = {"n": 0}

    def sahte(prompt):
        cagri["n"] += 1
        return yanit

    monkeypatch.setattr(evaluate, "generate", sahte)
    return cagri


# ---------------------------------------------------------------- hakem cevabını okumak
def test_hakem_json_metin_icinde_olsa_da_okunur(monkeypatch):
    hakem_yaniti(monkeypatch, 'İşte sonuç:\n```json\n{"dogru": true, "sadik": false, "gerekce": "x"}\n```')
    c = SahteRAG("18 gün [1]").sor("q")
    assert evaluate._hakem(soru(), c) == (True, False, "x")


def test_hakem_bozuk_cevap_none_dondurur(monkeypatch):
    hakem_yaniti(monkeypatch, "bilemedim")
    dogru, sadik, gerekce = evaluate._hakem(soru(), SahteRAG("18").sor("q"))
    assert dogru is None and sadik is None and "okunamadı" in gerekce


# ---------------------------------------------------------------- puanlama dalları
def test_yok_sorusunda_bilgi_yok_demek_dogrudur_ve_hakem_cagrilmaz(monkeypatch):
    cagri = hakem_yaniti(monkeypatch, "kullanılmamalı")
    [s] = degerlendir(SahteRAG(BILGI_YOK, []), [soru("yok", ())], bekleme=0)
    assert s.dogru and s.sadik and s.kaynak_var is None
    assert cagri["n"] == 0


def test_yok_sorusunda_cevap_uydurmak_yanlistir(monkeypatch):
    hakem_yaniti(monkeypatch, "kullanılmamalı")
    [s] = degerlendir(SahteRAG("Ciro 5 milyon TL [1]"), [soru("yok", ())], bekleme=0)
    assert s.dogru is False


def test_cevap_varken_bilgi_yok_demek_yanlis_ama_sadik(monkeypatch):
    cagri = hakem_yaniti(monkeypatch, "kullanılmamalı")
    [s] = degerlendir(SahteRAG(BILGI_YOK, []), [soru()], bekleme=0)
    assert s.dogru is False and s.sadik is True and cagri["n"] == 0


def test_normal_soru_hakeme_gider_ve_anahtar_kontrol_edilir(monkeypatch):
    cagri = hakem_yaniti(monkeypatch, '{"dogru": true, "sadik": true, "gerekce": "ok"}')
    [s] = degerlendir(SahteRAG("Yıllık izin 18 gündür [1]."), [soru()], bekleme=0)
    assert s.dogru and s.sadik and s.anahtar_ok and s.kaynak_var
    assert cagri["n"] == 1


def test_atifsiz_cevap_kaynak_yok_sayilir(monkeypatch):
    hakem_yaniti(monkeypatch, '{"dogru": true, "sadik": true}')
    [s] = degerlendir(SahteRAG("18 gün", []), [soru()], bekleme=0)
    assert s.kaynak_var is False


# ---------------------------------------------------------------- özet
def test_ozet_oranlari_ve_none_degerleri():
    sonuclar = [
        Sonuc(1, "basit", "q", "a", True, True, True, True),
        Sonuc(2, "basit", "q", "a", False, False, True, False),
        Sonuc(3, "basit", "q", "a", False, None, None, True),      # hakem okunamadı → paydaya girmez
        Sonuc(4, "yok", "q", "a", True, True, True, None),
    ]
    o = ozet(sonuclar)
    assert o["Doğruluk (hakem)"] == 2 / 3
    assert o["Kaynak gösterme"] == 2 / 3
    assert o["'Bilgi yok' doğru deme"] == 1.0
    assert o["Birleştirme doğruluğu"] is None
