"""Ders 2: Chunking (parçalama).

Bu dosyayı SEN yazacaksın. Fonksiyonların imzaları ve ne yapmaları gerektiği hazır;
`raise NotImplementedError` satırlarını silip yerine kendi kodunu yaz.

Kontrol etmek için:  .venv\\Scripts\\python.exe -m pytest -v
"""
from rag.loader import Document


# ---------------------------------------------------------------------------
# GÖREV 1 — Sabit boyutlu parçalama (bilerek "saf" yöntem)
# ---------------------------------------------------------------------------
def chunk_fixed(doc: Document, size: int = 500, overlap: int = 50) -> list[Document]:
    """Metni her `size` karakterde bir keser; ardışık parçalar `overlap` karakter paylaşır.

    Kurallar:
    - overlap >= size ise ValueError fırlat (yoksa döngü hiç ilerlemez).
    - Parçalar 0'dan başlar, her seferinde (size - overlap) karakter ilerler.
      Örnek: 1000 karakter, size=400, overlap=100 →
             [0:400], [300:700], [600:1000]   (son parça metnin sonuna ulaşınca dur)
    - Her parça yeni bir Document olur:
        text     = o parçanın metni
        metadata = orijinal metadata'nın KOPYASI + "chunk_index": 0, 1, 2, ...

    İpucu: `range(başlangıç, bitiş, adım)` ve string dilimleme `text[a:b]`.
    İpucu: Metadata kopyalamak için  {**doc.metadata, "chunk_index": i}
    """
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    chunks = []
    text = doc.text
    step = size - overlap
    for i, start in enumerate(range(0, len(text), step)):
        end = min(start + size, len(text))
        chunk_text = text[start:end]
        chunk_metadata = {**doc.metadata, "chunk_index": i}
        chunks.append(Document(text=chunk_text, metadata=chunk_metadata))
        if end == len(text):
            break

    return chunks


# ---------------------------------------------------------------------------
# GÖREV 2 — Başlıklara göre parçalama (akıllı yöntem)
# ---------------------------------------------------------------------------


def _bolumlere_ayir(doc: Document) -> list[tuple[str, str]]:
    """Metni (bölüm_adı, bölüm_metni) çiftlerine ayırır."""
    bolumler = []
    ad = doc.metadata["title"]    # ilk bölüm = ana başlık + giriş
    satirlar = []

    for satir in doc.text.splitlines():
        if satir.startswith("## "):
            bolumler.append((ad, "\n".join(satirlar)))   # eldeki bölümü kaydet
            ad = satir[3:].strip()                         # yeni ad: satırdan "## " kısmını at
            satirlar = [satir]                             # yeni liste: başlık satırı dahil
        else:
            satirlar.append(satir)

    bolumler.append((ad, "\n".join(satirlar)))   # döngü bitti: son bölümü kaydet
    return bolumler


def _uzunsa_bol(metin: str, max_chars: int) -> list[str]:
    """Metin max_chars'tan uzunsa paragrafları gruplayarak parçalara böler."""
    if len(metin) <= max_chars:
        return [metin]                      # zaten kısa: olduğu gibi bırak

    gruplar = []
    eldeki = ""                             # şu an doldurduğumuz grup
    for paragraf in metin.split("\n\n"):
        aday = f"{eldeki}\n\n{paragraf}" if eldeki else paragraf
        if len(aday) <= max_chars or not eldeki:
            eldeki = aday                   # sığıyor (ya da grup boş): ekle
        else:
            gruplar.append(eldeki)          # sığmıyor: eldeki grubu kapat...
            eldeki = paragraf               # ...yeni grubu bu paragrafla başlat
    if eldeki:
        gruplar.append(eldeki)              # son grubu da kaydet
    return gruplar


def chunk_by_section(doc: Document, max_chars: int = 800) -> list[Document]:
    """Markdown metnini "## " ile başlayan başlıklardan böler.

    Kurallar:
    - "## " ile başlayan her satır yeni bir bölüm başlatır. O satır bölümün metnine dahildir.
    - İlk "## " başlığından önceki kısım (ana başlık + giriş) de bir bölümdür;
      onun bölüm adı doc.metadata["title"] olur.
    - "### " alt başlıkları yeni bölüm BAŞLATMAZ; içinde bulundukları "##" bölümünde kalır.
    - Her parçanın metadata'sı: orijinal metadata'nın kopyası
        + "section": bölüm başlığı ("## " olmadan, örn. "Yıllık ücretli izin")
        + "chunk_index": 0, 1, 2, ...  (dokümanın tüm parçaları boyunca artar)
    - Parça metinlerinin baştaki/sondaki boşlukları silinir (.strip()); boş parçalar atılır.
    - Bir bölüm max_chars'tan UZUNSA: paragraflara ("\\n\\n") böl, paragrafları sırayla
      "\\n\\n" ile birleştirerek max_chars'ı aşmayacak şekilde grupla. Her grup ayrı parça
      olur ve hepsi aynı "section" değerini taşır.
      (Tek başına max_chars'tan uzun bir paragraf varsa onu bölme, tek parça olarak bırak.)

    İpucu: Önce bölümleri (başlık, metin) çiftleri olarak bir listede topla,
           sonra uzun olanları ayrı bir yardımcı fonksiyonla paragraflara böl.
    """
    parcalar = []
    for bolum_adi, bolum_metni in _bolumlere_ayir(doc):          # Adım 1
        for parca in _uzunsa_bol(bolum_metni.strip(), max_chars):  # Adım 2
            parca = parca.strip()
            if not parca:
                continue                                         # boş parçayı atla
            metadata = {**doc.metadata, "section": bolum_adi, "chunk_index": len(parcalar)}
            parcalar.append(Document(text=parca, metadata=metadata))
    return parcalar
