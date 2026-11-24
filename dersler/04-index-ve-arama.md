# Ders 4 — Index (vector DB) ve hybrid search

**Kod:** `rag/search.py` · **Çalıştır:** `.venv\Scripts\python.exe ders04_arama.py`

## 1. Index: vektörleri neden saklıyoruz?
Ders 3'te her çalıştırmada 70 parçayı yeniden embed ettik. 70 parça için sorun değil ama
70.000 parçada her soruda dakikalarca beklerdik. **Vector DB** (biz Chroma kullanıyoruz)
vektörleri bir kez hesaplayıp diske (`index/` klasörü) yazar ve en yakınları hızlıca bulur.

- `index_olustur(parcalar)`: embed et + diske yaz (belge değişince tekrar çalıştırılır)
- `vektor_ara(soru, k)`: sadece soruyu embed et, en yakın k parçayı diskten getir

## 2. Kelime araması (BM25)
Ctrl+F'in akıllı hâli. Soru ile parçada **ortak geçen kelimelere** puan verir:
- Nadir kelime daha değerlidir: "MFA" sadece 1 parçada geçer, çok puan getirir. "için" her
  yerde geçer, neredeyse hiç puan getirmez.
- Türkçe sorunu: "kartı", "kartına", "kartından" farklı kelime sayılır. Çözümümüz kaba ama
  etkili: her kelimenin **ilk 5 harfini** almak ("kartı", "kartı", "kartı").

## 3. Hybrid search (RRF)
İki listenin sıralarını birleştiririz: her parça her listede `1 / (60 + sıra)` puan toplar.
Skorları değil sıraları kullanırız, çünkü iki yöntemin skorları farklı ölçeklerdedir
(kosinüs 0–1 arası, BM25 0–20 arası); elma ile armudu toplamamak için.

## Sonuçlar (6 soru, doğru parçanın sırası)

| Soru | Vektör | Kelime | Hybrid |
|---|---|---|---|
| İnternet parası | – | 2 | 2 |
| Bilgisayarımı kaybettim | – | 1 | 1 |
| CEO kim | 2 | 1 | 2 |
| MFA için SMS | 3 | 1 | 1 |
| M4 unvanı | 1 | 1 | 1 |
| Yemek kartı | 1 | 1 | 1 |

**Dürüst yorum:** Bu küçük sette kelime araması, küçük çok dilli embedding modelimizden daha iyi
çıktı. Hybrid hiçbir soruda doğru parçayı kaçırmadı. Ama 6 soru bir karar vermek için az;
Ders 7'de 30–50 soruluk test setiyle gerçekten ölçeceğiz. Her zaman "hangisi iyi?" sorusunun
cevabı veriye bağlıdır ve ancak ölçerek bilinir.

## Kendini test et
<details><summary>1. Embedding modelini değiştirirsek index'e ne olur?</summary>
Index tamamen yeniden kurulmalı. Eski vektörler eski modelin "haritasında"; yeni modelin
soru vektörüyle karşılaştırılamaz.
</details>

<details><summary>2. Hybrid'de neden skorları toplamıyoruz da sıraları kullanıyoruz?</summary>
Ölçekler farklı: BM25 skoru 12, kosinüs skoru 0.6 olabilir. Toplasak BM25 her zaman baskın
çıkar. Sıra (1., 2., 3.) iki yöntemde de aynı anlamı taşır.
</details>

<details><summary>3. Kelime araması hangi sorularda zorlanır?</summary>
Soru ile belge farklı kelimeler kullandığında (eş anlamlılar): "tatil" vs "yıllık izin",
"parola" vs "şifre". Vektör araması tam bu durumlar için var.
</details>
