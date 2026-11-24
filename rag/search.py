"""Ders 4: Index (vector DB) + anahtar kelime araması + hybrid search.

Üç arama yöntemi:
  1. Vektör araması   — anlamca yakın parçaları bulur ("para" ≈ "450 TL")
  2. Kelime araması   — aynı kelimeleri içeren parçaları bulur ("MFA", "SMS", "M4")
  3. Hybrid           — ikisinin sıralamasını birleştirir (RRF)
"""
import re
from pathlib import Path

import chromadb
from rank_bm25 import BM25Okapi

from rag.embedder import embed
from rag.loader import Document

INDEX_KLASORU = Path("index")   # vector DB burada, diskte saklanır (.gitignore'da)
KOLEKSIYON = "mavikod"


# =========================================================== 1. Vektör araması (Chroma)
def index_olustur(parcalar: list[Document]) -> None:
    """Parçaları embed edip vector DB'ye yazar. Eski index varsa silip baştan kurar."""
    client = chromadb.PersistentClient(path=str(INDEX_KLASORU))
    if KOLEKSIYON in [c.name for c in client.list_collections()]:
        client.delete_collection(KOLEKSIYON)
    koleksiyon = client.create_collection(KOLEKSIYON, metadata={"hnsw:space": "cosine"})
    koleksiyon.add(
        ids=[f"{p.metadata['source']}#{p.metadata['chunk_index']}" for p in parcalar],
        documents=[p.text for p in parcalar],
        embeddings=embed([p.text for p in parcalar]).tolist(),
        metadatas=[p.metadata for p in parcalar],
    )


def vektor_ara(soru: str, k: int = 5) -> list[tuple[float, Document]]:
    """Diskteki index'te soruya anlamca en yakın k parçayı bulur."""
    koleksiyon = chromadb.PersistentClient(path=str(INDEX_KLASORU)).get_collection(KOLEKSIYON)
    sonuc = koleksiyon.query(query_embeddings=embed([soru]).tolist(), n_results=k)
    return [
        (1 - mesafe, Document(text=metin, metadata=meta))   # Chroma "mesafe" verir: benzerlik = 1 - mesafe
        for metin, meta, mesafe in zip(
            sonuc["documents"][0], sonuc["metadatas"][0], sonuc["distances"][0]
        )
    ]


# =========================================================== 2. Kelime araması (BM25)
def kelimelere_ayir(metin: str) -> list[str]:
    """Türkçe için basit tokenizer: küçük harf + kelimelere böl + ilk 5 harf.

    Neden ilk 5 harf? Türkçe eklemeli bir dil: "kartı", "kartına", "kartından" aynı kelime
    ama BM25 bunları farklı sayar. İlk 5 harfi almak kaba ama etkili bir "kök bulma" yöntemi.
    """
    metin = metin.replace("I", "ı").replace("İ", "i").lower()   # Türkçe I/İ düzeltmesi
    return [kelime[:5] for kelime in re.findall(r"\w+", metin)]


class KelimeIndex:
    """Parçalar üzerinde BM25 araması. Bellekte tutulur; 70 parça için anında kurulur."""

    def __init__(self, parcalar: list[Document]):
        self.parcalar = parcalar
        self.bm25 = BM25Okapi([kelimelere_ayir(p.text) for p in parcalar])

    def ara(self, soru: str, k: int = 5) -> list[tuple[float, Document]]:
        skorlar = self.bm25.get_scores(kelimelere_ayir(soru))
        sirali = sorted(zip(skorlar, self.parcalar), key=lambda x: x[0], reverse=True)
        return [(float(s), p) for s, p in sirali[:k]]


# =========================================================== 3. Hybrid (RRF)
def _kimlik(p: Document) -> str:
    return f"{p.metadata['source']}#{p.metadata['chunk_index']}"


def hybrid_ara(soru: str, kelime_index: KelimeIndex, k: int = 5) -> list[tuple[float, Document]]:
    """Reciprocal Rank Fusion: iki listenin SKORLARINI değil SIRALARINI birleştirir.

    Her parça, her listede aldığı sıraya göre 1 / (60 + sıra) puan toplar.
    İki listede de üst sıralarda olan parça en çok puanı alır.
    """
    puan: dict[str, float] = {}
    parca: dict[str, Document] = {}
    for liste in (vektor_ara(soru, k=20), kelime_index.ara(soru, k=20)):
        for sira, (_, p) in enumerate(liste, start=1):
            puan[_kimlik(p)] = puan.get(_kimlik(p), 0) + 1 / (60 + sira)
            parca[_kimlik(p)] = p
    en_iyiler = sorted(puan, key=puan.get, reverse=True)[:k]
    return [(puan[i], parca[i]) for i in en_iyiler]
