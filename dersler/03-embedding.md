# Ders 3 — Embedding (anlam vektörü)

**Kod:** `rag/embedder.py` · **Çalıştır:** `.venv\Scripts\python.exe ders03_embedding.py`

## Embedding nedir?
Bir metni **sabit uzunlukta bir sayı listesine** (vektöre) çeviren işlem. Bizim modelimiz her
metni 384 sayıya çevirir. Tek tek sayıların bir anlamı yoktur; önemli olan iki vektörün
birbirine ne kadar **yakın** olduğudur. Anlamca yakın metinlerin vektörleri de yakındır.

Benzetme: Bir haritada her şehrin 2 koordinatı (enlem, boylam) vardır; yakın şehirlerin
koordinatları da yakındır. Embedding aynı fikir, ama 2 yerine 384 boyutlu bir "anlam haritası".

## Benzerlik nasıl ölçülür?
**Kosinüs benzerliği:** İki vektörün aynı yöne ne kadar baktığı. 1 = aynı yön (aynı anlam),
0 = dik (ilgisiz). Vektörleri önceden normalize ettiğimiz (uzunluğunu 1 yaptığımız) için
hesap basit bir çarpıma iner: `np.dot(a, b)`.

## Bu derste gördüklerimiz
- Soru ile "Yemek kartı" parçası **0.63** benzerlikle 70 parçanın en üstüne çıktı. Model,
  "günde ne kadar para yükleniyor" ile "her iş günü için 450 TL yüklenir"in aynı şeyi
  anlattığını kelimeler birebir aynı olmasa da anladı. Anahtar kelime aramasından farkı bu.
- Aynı bilgi, temiz bir parçada **0.63**, karışık (diş + yemek) bir parçada **0.47** skor aldı.
  Ders 2'deki "karışık parçanın anlam adresi bulanıklaşır" iddiası artık bir sayı.
- **Tek kelimeler gürültülüdür:** Tabloda "parola"nın "tatil"e (0.58), "şifre"den (0.51) daha
  yakın çıktığı oldu. Küçük modeller, bağlamı olmayan tek kelimelerde şaşırabilir; cümleler ve
  paragraflarda çok daha güvenilirdir. Embedding mükemmel değildir; bu yüzden Ders 4'te
  anahtar kelime aramasıyla birleştireceğiz (hybrid search).

## Kendini test et
<details><summary>1. Neden LLM yerine ayrı, küçük bir embedding modeli kullanıyoruz?</summary>
Embedding modeli sadece "anlam adresi" üretir, cevap yazmaz. Küçük, hızlı ve bizim için ücretsizdir;
70 (ya da 70.000) parçayı tek seferde işleyebilir.
</details>

<details><summary>2. Soruyu ve parçaları aynı modelle mi embed etmek zorundayız?</summary>
Evet. Farklı modellerin "haritaları" farklıdır; birinin koordinatı diğerinde anlamsızdır.
</details>

<details><summary>3. Parçaları her soruda yeniden embed etmek mantıklı mı?</summary>
Hayır, israftır. Parçalar değişmedikçe vektörleri bir kez hesaplanıp saklanır. Bu Ders 4'ün
konusu: index (vector DB).
</details>

## Alıştırma
`ders03_embedding.py` içindeki `soru` değişkenini değiştir ve hangi parçanın üste çıktığına bak:
- "Evden çalışırken internet parası veriliyor mu?"
- "Bilgisayarımı kaybettim, ne yapmalıyım?"
- "Şirketin CEO'su kim?"  ← bu üçünde de doğru parça ilk sırada mı?
