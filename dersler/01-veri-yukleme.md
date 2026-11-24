# Ders 1 — Veriyi seçmek ve yüklemek

**Kod:** `rag/loader.py` · **Çalıştır:** `.venv\Scripts\python.exe ders01_yukle.py`

## Bu derste ne yaptık?

RAG hattının (pipeline) ilk halkasını kurduk:

```
[Dokümanlar] → Yükle → Chunk → Embed → Index → Search → LLM + kaynak
     ▲ buradayız
```

## Ana fikirler

### 1. Veriyi iyi bil
Asistanın verdiği yanlış cevabı ancak doğru cevabı biliyorsan yakalayabilirsin. Bu yüzden
kurgusal bir şirketin (Mavikod) 8 dokümanını kullanıyoruz: her rakamı biz yazdık ve LLM bunları
ezbere bilemez. Doğru cevap geliyorsa bu retrieval sayesindedir.

### 2. Her şey `Document` olur
Farklı formatlar (Markdown, PDF, TXT) tek bir ortak yapıya çevrilir:

```python
Document(text="...", metadata={"source": "02-izin-politikasi.md", "title": "İzin Politikası"})
```

Sistemin geri kalanı dosya formatını hiç bilmez; sadece `Document` görür. Yeni bir format
eklemek, `LOADERS` sözlüğüne bir satır eklemek demektir.

### 3. Metadata = gelecekteki citation
RAG'ın en önemli vaadi "cevabı kaynağıyla vermek". Bunun için metnin nereden geldiğini **en
baştan** taşımamız gerekir. Metadata'yı yükleme aşamasında kaybedersen sonradan geri getiremezsin.

- Markdown → `source` + `title`
- PDF → `source` + `page` (her sayfa ayrı Document; "kaçıncı sayfada?" sorusunun cevabı)

## Sonuç
8 doküman, ~3.600 kelime (~11 sayfa). Rehber 20–50 sayfa öneriyor; ileride doküman ekleyerek
büyüteceğiz. Az veriyle başlamak hataları görmeyi kolaylaştırır.

## Kendini test et
<details><summary>1. PDF'te neden her sayfayı ayrı Document yapıyoruz?</summary>
Sayfa numarası metadata'da kalsın diye. Tek Document yapsaydık "bu bilgi 7. sayfada" diyemezdik.
</details>

<details><summary>2. Metadata'yı neden chunk'larken değil, yüklerken ekliyoruz?</summary>
Yükleme, dosya adının ve sayfanın bilindiği tek andır. Sonraki adımlar sadece metni görür.
</details>

<details><summary>3. Neden kurgusal bir şirketin dokümanlarını kullanıyoruz?</summary>
LLM bu bilgileri eğitimde görmedi. Doğru cevap ancak bizim dokümanlarımızdan gelebilir; böylece
retrieval'ın gerçekten çalıştığını ölçebiliriz.
</details>

## Alıştırma
`data/raw/` içine kendin bir `09-sss.md` dosyası yaz: Mavikod çalışanlarının sık sorduğu 5 soru
ve cevapları (kendi uydurduğun kurallarla). Sonra `ders01_yukle.py` dosyasını tekrar çalıştır ve
tabloda göründüğünü kontrol et. Bu dosya, ileride "test setindeki sorular" için de işimize yarayacak.
