"""pipeline.py testleri: prompt'a giden kaynaklar ve atıf ayıklama. LLM taklit edilir (API çağrısı yok)."""
import rag.pipeline as pipeline
from rag.loader import Document
from rag.pipeline import BILGI_YOK, RAG, Cevap, kaynaklari_yaz


def parca(src, section, text):
    return Document(text, {"source": src, "section": section, "chunk_index": 0})


PARCALAR = [parca("izin.md", "Yıllık izin", "18 gün."), parca("yan.md", "Yemek kartı", "450 TL.")]


def sahte_rag(monkeypatch, llm_cevabi):
    """Index kurmadan (embedding modeli yüklemeden) bir RAG nesnesi hazırlar."""
    rag = RAG.__new__(RAG)
    rag.kelime_index = None
    gorulen = {}
    monkeypatch.setattr(pipeline, "hybrid_ara", lambda soru, ki, k: [(1.0, p) for p in PARCALAR])

    def sahte_generate(prompt):
        gorulen["prompt"] = prompt
        return llm_cevabi

    monkeypatch.setattr(pipeline, "generate", sahte_generate)
    return rag, gorulen


def test_kaynaklar_numarali_ve_basliklı():
    metin = kaynaklari_yaz(PARCALAR)
    assert metin.startswith("[1] (izin.md › Yıllık izin)\n18 gün.")
    assert "[2] (yan.md › Yemek kartı)\n450 TL." in metin


def test_prompt_soruyu_ve_kaynaklari_icerir(monkeypatch):
    rag, gorulen = sahte_rag(monkeypatch, "18 gün [1].")
    rag.sor("İzin kaç gün?")
    assert "SORU: İzin kaç gün?" in gorulen["prompt"]
    assert "[2] (yan.md › Yemek kartı)" in gorulen["prompt"]


def test_atiflar_ayiklanir_tekrarlar_birlesir(monkeypatch):
    rag, _ = sahte_rag(monkeypatch, "18 gün [1]. Ayrıca 450 TL [2]. Yine [1].")
    cevap = rag.sor("soru")
    assert cevap.kullanilan == [1, 2]
    assert not cevap.bilgi_yok


def test_olmayan_kaynak_numarasi_yok_sayilir(monkeypatch):
    rag, _ = sahte_rag(monkeypatch, "Bir şey [7] ve [0].")
    assert rag.sor("soru").kullanilan == []


def test_bilgi_yok_algilanir(monkeypatch):
    rag, _ = sahte_rag(monkeypatch, f"  {BILGI_YOK}  ")
    cevap = rag.sor("Ciro ne kadar?")
    assert cevap.bilgi_yok and cevap.metin == BILGI_YOK


def test_cevap_nesnesi_parcalari_tasir(monkeypatch):
    rag, _ = sahte_rag(monkeypatch, "x [2]")
    cevap = rag.sor("soru")
    assert isinstance(cevap, Cevap)
    assert cevap.parcalar[cevap.kullanilan[0] - 1].metadata["section"] == "Yemek kartı"
