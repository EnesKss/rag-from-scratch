"""search.py testleri: Türkçe tokenizer, BM25, RRF birleştirme ve (yavaş) gerçek vektör index'i."""
import pytest

import rag.search as search
from rag.loader import Document
from rag.search import KelimeIndex, hybrid_ara, kelimelere_ayir


def parca(src, i, text, section="S"):
    return Document(text, {"source": src, "chunk_index": i, "section": section})


# ---------------------------------------------------------------- tokenizer
def test_turkce_buyuk_harf_dogru_kucultulur():
    assert kelimelere_ayir("İZİN IŞIK") == ["izin", "ışık"]


def test_ekler_ilk_5_harfle_eslesir():
    assert len(set(kelimelere_ayir("kartı kartına kartından"))) == 1


def test_noktalama_atilir():
    assert kelimelere_ayir("MFA, SMS!") == ["mfa", "sms"]


# ---------------------------------------------------------------- BM25
def test_kelime_araması_nadir_terimi_bulur():
    ps = [parca("a", 0, "Yemek kartı her gün yüklenir."),
          parca("b", 0, "MFA zorunludur, SMS kabul edilmez."),
          parca("c", 0, "Yıllık izin 18 gündür.")]
    sonuc = KelimeIndex(ps).ara("SMS ile MFA olur mu?", k=1)
    assert sonuc[0][1].metadata["source"] == "b"


def test_kelime_araması_k_kadar_dondurur():
    ps = [parca("a", i, f"metin {i}") for i in range(10)]
    assert len(KelimeIndex(ps).ara("metin", k=3)) == 3


# ---------------------------------------------------------------- RRF (vektör araması taklit edilir)
def test_hybrid_iki_listede_de_ustte_olani_one_cikarir(monkeypatch):
    a, b, c = parca("a", 0, "x"), parca("b", 0, "y"), parca("c", 0, "z")

    class SahteKelime:
        def ara(self, soru, k):
            return [(9.0, b), (5.0, a), (1.0, c)]

    monkeypatch.setattr(search, "vektor_ara", lambda soru, k: [(0.9, a), (0.8, b), (0.1, c)])
    sonuc = hybrid_ara("soru", SahteKelime(), k=3)
    # a: 1/61 + 1/62, b: 1/62 + 1/61 → eşit; c her iki listede 3. → en son
    assert [p.metadata["source"] for _, p in sonuc][2] == "c"
    assert {p.metadata["source"] for _, p in sonuc[:2]} == {"a", "b"}


def test_hybrid_tek_listede_olan_parcayi_da_getirir(monkeypatch):
    a, b = parca("a", 0, "x"), parca("b", 0, "y")

    class SahteKelime:
        def ara(self, soru, k):
            return [(3.0, b)]

    monkeypatch.setattr(search, "vektor_ara", lambda soru, k: [(0.9, a)])
    kaynaklar = {p.metadata["source"] for _, p in hybrid_ara("soru", SahteKelime(), k=5)}
    assert kaynaklar == {"a", "b"}


def test_hybrid_ayni_parcayi_iki_kez_dondurmez(monkeypatch):
    a = parca("a", 0, "x")

    class SahteKelime:
        def ara(self, soru, k):
            return [(3.0, a)]

    monkeypatch.setattr(search, "vektor_ara", lambda soru, k: [(0.9, a)])
    assert len(hybrid_ara("soru", SahteKelime(), k=5)) == 1


# ---------------------------------------------------------------- gerçek index (embedding modeli yükler)
@pytest.mark.slow
def test_gercek_vektor_index_kur_ve_ara(tmp_path, monkeypatch):
    monkeypatch.setattr(search, "INDEX_KLASORU", tmp_path / "index")
    ps = [parca("yan.md", 0, "Yemek kartına her iş günü 450 TL yüklenir.", "Yemek kartı"),
          parca("guv.md", 0, "Şifreler en az 14 karakter olmalıdır.", "Şifreler"),
          parca("izin.md", 0, "Yıllık izin 18 gündür.", "Yıllık izin")]
    search.index_olustur(ps)
    search.index_olustur(ps)          # ikinci kez kurmak hata vermemeli (eski index silinir)
    sonuc = search.vektor_ara("Öğle yemeği için günlük ne kadar para veriliyor?", k=3)
    assert len(sonuc) == 3
    assert sonuc[0][1].metadata["section"] == "Yemek kartı"
    assert sonuc[0][0] >= sonuc[1][0] >= sonuc[2][0]      # benzerliğe göre sıralı
