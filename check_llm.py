"""Kurulum testi: Gemini'ye bağlanabiliyor muyuz?

Çalıştır:  python check_llm.py
"""
from rag.llm import MODEL, generate

print(f"Model: {MODEL}")
print(generate("Tek cümleyle: RAG nedir?"))
