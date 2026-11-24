"""Ders 1: Dokümanları yüklemek.

RAG'ın ilk adımı: diskteki dosyaları okuyup her birini
"metin + metadata" şeklinde ortak bir yapıya çevirmek.
"""
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader


@dataclass
class Document:
    """Sistemin her yerinde dolaşacak temel birim.

    text:     dokümanın metni
    metadata: metnin NEREDEN geldiği (dosya adı, başlık, sayfa...).
              Citation (kaynak gösterme) bu bilgi sayesinde mümkün olacak.
    """
    text: str
    metadata: dict = field(default_factory=dict)


def load_markdown(path: Path) -> list[Document]:
    """Markdown/metin dosyası: tüm dosya tek bir Document olur."""
    text = path.read_text(encoding="utf-8")
    # Dosyadaki ilk "# Başlık" satırını belgenin başlığı olarak al
    title = next(
        (line[2:].strip() for line in text.splitlines() if line.startswith("# ")),
        path.stem,  # başlık yoksa dosya adını kullan
    )
    return [Document(text=text, metadata={"source": path.name, "title": title})]


def load_pdf(path: Path) -> list[Document]:
    """PDF: her SAYFA ayrı bir Document olur, böylece sayfa numarasını kaybetmeyiz."""
    docs = []
    for page_no, page in enumerate(PdfReader(path).pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:  # boş sayfaları (ör. sadece resim olanlar) atla
            docs.append(Document(text=text, metadata={"source": path.name, "page": page_no}))
    return docs


# Dosya uzantısı -> hangi fonksiyonla okunacağı.
# Yeni bir format eklemek = bu sözlüğe bir satır eklemek.
LOADERS = {
    ".md": load_markdown,
    ".txt": load_markdown,
    ".pdf": load_pdf,
}


def load(folder: str | Path) -> list[Document]:
    """Klasördeki (ve alt klasörlerdeki) desteklenen tüm dosyaları yükler."""
    docs: list[Document] = []
    for path in sorted(Path(folder).rglob("*")):
        if not path.is_file():
            continue
        loader = LOADERS.get(path.suffix.lower())
        if loader is None:
            print(f"  atlandı (desteklenmeyen format): {path.name}")
            continue
        docs.extend(loader(path))
    return docs
