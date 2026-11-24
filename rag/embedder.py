"""Ders 3: Embedding — metni "anlam vektörüne" çevirmek.

Embedding modeli bir metni alır, sabit uzunlukta bir sayı listesi (vektör) döndürür.
Anlamca yakın metinlerin vektörleri de birbirine yakın olur.

Model bilgisayarında çalışır (API yok, ücret yok). İlk çalıştırmada internetten
bir kez indirilir (~470 MB), sonra diskten okunur.
"""
import numpy as np
from sentence_transformers import SentenceTransformer

# Türkçe dahil 50+ dili anlayan, küçük ve hızlı bir model. Her metni 384 sayıya çevirir.
MODEL_ADI = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_model = None  # model büyük; ilk ihtiyaç duyulduğunda bir kez yükleyip saklıyoruz


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_ADI)
    return _model


def embed(metinler: list[str]) -> np.ndarray:
    """Metin listesini vektörlere çevirir.

    Dönüş: (metin sayısı × 384) boyutunda bir tablo (numpy dizisi).
    normalize_embeddings=True → her vektörün uzunluğu 1 olur. Böylece iki vektörün
    benzerliğini basit bir çarpımla (dot product) hesaplayabiliriz.
    """
    return _get_model().encode(metinler, normalize_embeddings=True)


def benzerlik(a: np.ndarray, b: np.ndarray) -> float:
    """İki (normalize edilmiş) vektörün kosinüs benzerliği: 1 = aynı anlam, 0 = ilgisiz."""
    return float(np.dot(a, b))
