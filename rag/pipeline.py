"""Ders 5: Hepsini birleştir — soru → arama → LLM → kaynaklı cevap.

    soru ──► hybrid_ara ──► en iyi k parça ──► PROMPT ──► Gemini ──► cevap + [1][3] kaynaklar
"""
import re
from dataclasses import dataclass

from rag.chunker import chunk_by_section
from rag.llm import generate
from rag.loader import Document, load
from rag.search import KelimeIndex, hybrid_ara, index_olustur

PROMPT_SABLONU = """Sen Mavikod Teknoloji çalışanlarına şirket politikaları hakkında yardım eden bir asistansın.

KURALLAR:
1. SADECE aşağıdaki KAYNAKLAR bölümündeki bilgileri kullan. Kendi genel bilgini kullanma.
2. Cevaptaki her bilginin sonuna, onu hangi kaynaktan aldığını köşeli parantezle yaz: [1], [2] gibi.
3. Cevap kaynaklarda yoksa ya da emin değilsen tam olarak şunu yaz: "Bu bilgi dokümanlarda yok."
   Tahmin etme, bilgi uydurma.
4. Kısa ve net cevap ver. Türkçe yaz.

KAYNAKLAR:
{kaynaklar}

SORU: {soru}

CEVAP:"""

BILGI_YOK = "Bu bilgi dokümanlarda yok."


@dataclass
class Cevap:
    soru: str
    metin: str                 # LLM'in yazdığı cevap
    parcalar: list[Document]   # LLM'e verdiğimiz parçalar (numara sırasıyla)
    kullanilan: list[int]      # cevapta atıf yapılan kaynak numaraları ([1] → 1)

    @property
    def bilgi_yok(self) -> bool:
        return BILGI_YOK in self.metin


def kaynaklari_yaz(parcalar: list[Document]) -> str:
    """Parçaları numaralı bir liste hâline getirir; LLM bu numaralarla atıf yapacak."""
    bloklar = []
    for i, p in enumerate(parcalar, start=1):
        baslik = f"{p.metadata['source']} › {p.metadata.get('section', '')}"
        bloklar.append(f"[{i}] ({baslik})\n{p.text}")
    return "\n\n".join(bloklar)


class RAG:
    def __init__(self, klasor: str = "data/raw", parcalayici=chunk_by_section):
        # parcalayici: hangi chunking yöntemi kullanılsın? (Ders 7'de ikisini karşılaştıracağız)
        self.parcalar = [c for d in load(klasor) for c in parcalayici(d)]
        index_olustur(self.parcalar)                 # vektör index'i (Ders 4)
        self.kelime_index = KelimeIndex(self.parcalar)  # kelime index'i (Ders 4)

    def sor(self, soru: str, k: int = 5) -> Cevap:
        # 1) Retrieval: en alakalı k parçayı bul
        parcalar = [p for _, p in hybrid_ara(soru, self.kelime_index, k=k)]
        # 2) Augmentation: parçaları ve soruyu prompt'a yerleştir
        prompt = PROMPT_SABLONU.format(kaynaklar=kaynaklari_yaz(parcalar), soru=soru)
        # 3) Generation: LLM cevabı yazsın
        metin = generate(prompt).strip()
        # 4) Cevapta hangi kaynak numaraları geçiyor? ([1], [3] → {1, 3})
        kullanilan = sorted({int(n) for n in re.findall(r"\[(\d+)\]", metin) if 1 <= int(n) <= len(parcalar)})
        return Cevap(soru=soru, metin=metin, parcalar=parcalar, kullanilan=kullanilan)
