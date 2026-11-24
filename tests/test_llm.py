"""llm.py testleri: yeniden deneme (retry) davranışı. Gerçek API çağrılmaz."""
import pytest
from google.genai import errors

import rag.llm as llm


def hata(cls, kod):
    return cls(kod, {"error": {"code": kod, "message": "test", "status": "X"}})


class SahteIstemci:
    def __init__(self, olaylar):
        self.olaylar = list(olaylar)
        self.cagri = 0
        self.models = self

    def generate_content(self, model, contents):
        self.cagri += 1
        olay = self.olaylar.pop(0)
        if isinstance(olay, Exception):
            raise olay
        return type("Yanit", (), {"text": olay})()


@pytest.fixture
def ortam(monkeypatch):
    beklemeler = []
    monkeypatch.setattr(llm.time, "sleep", beklemeler.append)

    def kur(olaylar):
        istemci = SahteIstemci(olaylar)
        monkeypatch.setattr(llm, "_get_client", lambda: istemci)
        return istemci, beklemeler

    return kur


def test_basarili_cagri(ortam):
    istemci, beklemeler = ortam(["merhaba"])
    assert llm.generate("p") == "merhaba"
    assert istemci.cagri == 1 and beklemeler == []


def test_gecici_hatada_artan_beklemeyle_tekrar_dener(ortam):
    istemci, beklemeler = ortam([hata(errors.ServerError, 503), hata(errors.ClientError, 429), "tamam"])
    assert llm.generate("p") == "tamam"
    assert istemci.cagri == 3 and beklemeler == [2, 4]


def test_kalici_hatada_hemen_vazgecer(ortam):
    istemci, beklemeler = ortam([hata(errors.ClientError, 400), "kullanılmamalı"])
    with pytest.raises(errors.ClientError):
        llm.generate("p")
    assert istemci.cagri == 1 and beklemeler == []


def test_anahtar_yoksa_anlasilir_hata(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(llm, "_client", None)
    with pytest.raises(RuntimeError, match=".env"):
        llm.generate("p")


def test_deneme_hakki_bitince_hatayi_iletir(ortam):
    istemci, _ = ortam([hata(errors.ServerError, 503)] * 3)
    with pytest.raises(errors.ServerError):
        llm.generate("p", deneme=3)
    assert istemci.cagri == 3
