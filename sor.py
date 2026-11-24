"""Dokümanlara soru sor.

Tek soru:      .venv\\Scripts\\python.exe sor.py "Yıllık izin kaç gün?"
Sohbet modu:   .venv\\Scripts\\python.exe sor.py          (çıkmak için boş satır)
"""
import sys

from rag.pipeline import RAG


def yazdir(cevap) -> None:
    print(f"\n{cevap.metin}")
    if cevap.kullanilan:
        print("\nKaynaklar:")
        for n in cevap.kullanilan:
            p = cevap.parcalar[n - 1]
            yer = p.metadata.get("section") or f"sayfa {p.metadata.get('page', '?')}"
            print(f"  [{n}] {p.metadata['source']} › {yer}")
    print()


if __name__ == "__main__":
    print("Index hazırlanıyor...")
    rag = RAG()
    if len(sys.argv) > 1:
        yazdir(rag.sor(" ".join(sys.argv[1:])))
    else:
        while soru := input("Soru: ").strip():
            yazdir(rag.sor(soru))
