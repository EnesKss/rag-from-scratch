"""testset.py testleri: test setinin kendisi geçerli mi, doğrulayıcı hataları yakalıyor mu?"""
from rag.chunker import chunk_by_section
from rag.loader import Document, load
from rag.testset import TestSorusu, anahtarlar_var_mi, dogrula, normalize, yukle

PARCALAR = [Document("## Yemek kartı\n\nGünde 7.500 TL yüklenir.",
                     {"source": "yan.md", "section": "Yemek kartı", "chunk_index": 0})]


def soru(**degisiklik):
    temel = dict(id=1, tur="basit", soru="q", beklenen="b", anahtar=["7500"],
                 bolumler=[("yan.md", "Yemek kartı")])
    return TestSorusu(**{**temel, **degisiklik})


def test_normalize_turkce_ve_binlik_ayirac():
    assert normalize("İZİN 7.500 TL, 1.000.000") == "izin 7500 tl, 1000000"
    assert normalize("16:00") == "16:00"


def test_anahtarlar_buyuk_kucuk_harf_ve_nokta_duyarsiz():
    assert anahtarlar_var_mi("Yemek kartına 7500 tl yüklenir", ["7.500 TL", "YEMEK"])
    assert not anahtarlar_var_mi("Yemek kartı", ["7.500"])


def test_gecerli_soru_hata_vermez():
    assert dogrula([soru()], PARCALAR) == []


def test_yanlis_bolum_adi_yakalanir():
    hatalar = dogrula([soru(bolumler=[("yan.md", "Yemek Karti")])], PARCALAR)
    assert any("bölüm bulunamadı" in h for h in hatalar)


def test_yanlis_anahtar_yakalanir():
    assert any("anahtar" in h for h in dogrula([soru(anahtar=["450"])], PARCALAR))


def test_yok_sorusunda_bolum_olmamali():
    assert dogrula([soru(tur="yok", bolumler=[("yan.md", "Yemek kartı")])], PARCALAR)


def test_tekrarlanan_id_ve_bilinmeyen_tur():
    hatalar = dogrula([soru(), soru(tur="garip")], PARCALAR)
    assert "Tekrarlanan id var" in hatalar
    assert any("bilinmeyen tür" in h for h in hatalar)


def test_gercek_test_seti_gecerli():
    sorular = yukle()
    parcalar = [c for d in load("data/raw") for c in chunk_by_section(d)]
    assert len(sorular) == 40
    assert dogrula(sorular, parcalar) == []
