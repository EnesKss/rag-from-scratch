"""loader.py testleri: Markdown, TXT ve (şimdiye kadar hiç denenmemiş) PDF yükleme."""
from rag.loader import Document, load, load_markdown, load_pdf


def mini_pdf(sayfalar: list[str]) -> bytes:
    """Test için, kütüphane kullanmadan, her sayfasında bir satır yazı olan küçük bir PDF üretir."""
    n = len(sayfalar)
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(n))
    objs = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {n} >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    for i, metin in enumerate(sayfalar):
        akis = f"BT /F1 12 Tf 72 720 Td ({metin}) Tj ET" if metin else "BT ET"
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    f"/Resources << /Font << /F1 3 0 R >> >> /Contents {5 + 2 * i} 0 R >>")
        objs.append(f"<< /Length {len(akis)} >>\nstream\n{akis}\nendstream")
    cikti, ofsetler = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, start=1):
        ofsetler.append(len(cikti))
        cikti += f"{i} 0 obj\n{o}\nendobj\n".encode("latin-1")
    xref = len(cikti)
    cikti += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    cikti += b"".join(f"{o:010d} 00000 n \n".encode() for o in ofsetler)
    cikti += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return cikti


def test_markdown_baslik_ve_kaynak(tmp_path):
    f = tmp_path / "not.md"
    f.write_text("Giriş satırı\n# Asıl Başlık\n\nMetin.", encoding="utf-8")
    [doc] = load_markdown(f)
    assert doc.metadata == {"source": "not.md", "title": "Asıl Başlık"}
    assert "Metin." in doc.text


def test_markdown_basliksiz_dosya_adini_kullanir(tmp_path):
    f = tmp_path / "basliksiz.txt"
    f.write_text("Sadece düz metin.", encoding="utf-8")
    [doc] = load_markdown(f)
    assert doc.metadata["title"] == "basliksiz"


def test_pdf_her_sayfa_ayri_document_ve_sayfa_numarasi(tmp_path):
    f = tmp_path / "rapor.pdf"
    f.write_bytes(mini_pdf(["Birinci sayfa", "Ikinci sayfa"]))
    docs = load_pdf(f)
    assert [d.metadata for d in docs] == [
        {"source": "rapor.pdf", "page": 1},
        {"source": "rapor.pdf", "page": 2},
    ]
    assert "Birinci" in docs[0].text and "Ikinci" in docs[1].text


def test_pdf_bos_sayfa_atlanir_ama_numaralar_kaymaz(tmp_path):
    f = tmp_path / "bosluklu.pdf"
    f.write_bytes(mini_pdf(["Bir", "", "Uc"]))
    assert [d.metadata["page"] for d in load_pdf(f)] == [1, 3]


def test_load_klasoru_tarar_desteklenmeyeni_atlar(tmp_path, capsys):
    (tmp_path / "alt").mkdir()
    (tmp_path / "a.md").write_text("# A\n\nmetin", encoding="utf-8")
    (tmp_path / "alt" / "b.txt").write_text("b metni", encoding="utf-8")
    (tmp_path / "c.pdf").write_bytes(mini_pdf(["C sayfasi"]))
    (tmp_path / "resim.png").write_bytes(b"\x89PNG")
    docs = load(tmp_path)
    assert sorted(d.metadata["source"] for d in docs) == ["a.md", "b.txt", "c.pdf"]
    assert "resim.png" in capsys.readouterr().out


def test_load_bos_klasor(tmp_path):
    assert load(tmp_path) == []


def test_gercek_veri_seti():
    docs = load("data/raw")
    assert len(docs) == 8
    assert all(isinstance(d, Document) and d.text for d in docs)
