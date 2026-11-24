"""Ders 2 testleri. Bu dosyayı DEĞİŞTİRME; kodun doğruysa hepsi geçer.

Çalıştır:  .venv\\Scripts\\python.exe -m pytest -v
"""
import pytest

from rag.chunker import chunk_by_section, chunk_fixed
from rag.loader import Document, load


# ---------------------------------------------------------------- Görev 1
def _doc(text):
    return Document(text=text, metadata={"source": "test.md", "title": "Test"})


def test_fixed_ornekteki_gibi_boler():
    text = "".join(str(i % 10) for i in range(1000))  # 1000 karakter
    chunks = chunk_fixed(_doc(text), size=400, overlap=100)
    assert [c.text for c in chunks] == [text[0:400], text[300:700], text[600:1000]]


def test_fixed_parcalar_overlap_kadar_ortusur():
    text = "abcdefghij" * 50
    chunks = chunk_fixed(_doc(text), size=120, overlap=20)
    for a, b in zip(chunks, chunks[1:]):
        assert a.text[-20:] == b.text[:20]


def test_fixed_metnin_sonu_kaybolmaz():
    text = "x" * 1234 + "SON"
    chunks = chunk_fixed(_doc(text), size=500, overlap=50)
    assert chunks[0].text.startswith("x")
    assert chunks[-1].text.endswith("SON")
    assert all(len(c.text) <= 500 for c in chunks)


def test_fixed_metadata_kopyalanir_ve_index_eklenir():
    doc = _doc("a" * 300)
    chunks = chunk_fixed(doc, size=100, overlap=0)
    assert [c.metadata["chunk_index"] for c in chunks] == [0, 1, 2]
    assert all(c.metadata["source"] == "test.md" for c in chunks)
    chunks[0].metadata["source"] = "değişti"
    assert doc.metadata["source"] == "test.md", "orijinal metadata değişmemeli (kopyala!)"


def test_fixed_hatali_overlap_hata_verir():
    with pytest.raises(ValueError):
        chunk_fixed(_doc("abc"), size=10, overlap=10)


# ---------------------------------------------------------------- Görev 2
ORNEK = """# Başlık

Giriş paragrafı.

## Bölüm A

A metni.

### Alt

Alt metni.

## Bölüm B

B metni."""


def test_section_basliklardan_boler():
    chunks = chunk_by_section(Document(ORNEK, {"source": "test.md", "title": "Başlık"}))
    assert [c.metadata["section"] for c in chunks] == ["Başlık", "Bölüm A", "Bölüm B"]


def test_section_alt_baslik_ayni_bolumde_kalir():
    chunks = chunk_by_section(Document(ORNEK, {"source": "test.md", "title": "Başlık"}))
    assert "### Alt" in chunks[1].text and "Alt metni." in chunks[1].text
    assert chunks[1].text.startswith("## Bölüm A")


def test_section_metadata():
    doc = Document(ORNEK, {"source": "test.md", "title": "Başlık"})
    chunks = chunk_by_section(doc)
    assert [c.metadata["chunk_index"] for c in chunks] == [0, 1, 2]
    assert all(c.metadata["source"] == "test.md" for c in chunks)
    assert "section" not in doc.metadata, "orijinal metadata değişmemeli (kopyala!)"


def test_section_uzun_bolum_paragraflara_bolunur():
    p1, p2, p3 = "a" * 300, "b" * 300, "c" * 300
    text = f"# T\n\n## Uzun\n\n{p1}\n\n{p2}\n\n{p3}"
    chunks = chunk_by_section(Document(text, {"source": "t.md", "title": "T"}), max_chars=700)
    uzun = [c for c in chunks if c.metadata["section"] == "Uzun"]
    assert len(uzun) == 2
    assert all(len(c.text) <= 700 for c in uzun)
    birlesik = "\n\n".join(c.text for c in uzun)
    for p in (p1, p2, p3):
        assert p in birlesik, "hiçbir paragraf kaybolmamalı"


def test_section_gercek_dokumanlarda_calisir():
    for doc in load("data/raw"):
        chunks = chunk_by_section(doc)
        assert chunks, f"{doc.metadata['source']} için hiç parça çıkmadı"
        for c in chunks:
            assert c.text.strip() == c.text and c.text, "boş ya da boşluklu parça var"
            assert c.metadata["section"]
            assert c.metadata["source"] == doc.metadata["source"]
