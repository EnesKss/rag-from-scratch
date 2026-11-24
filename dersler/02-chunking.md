# Ders 2 — Chunking (parçalama)

**Kodu sen yazıyorsun:** `rag/chunker.py`
**Kontrol:** `.venv\Scripts\python.exe -m pytest -v`
**Sonra çalıştır:** `.venv\Scripts\python.exe ders02_parcala.py`

## Neden parçalıyoruz?

1. **Arama isabeti:** Bir paragrafın embedding'i (anlam adresi) o paragrafın konusunu net
   gösterir. Bütün bir dokümanın embedding'i ise 10 konunun ortalaması olur ve bulanıklaşır.
   "Yemek kartı" sorusu, içinde sigorta, spor ve emeklilik de geçen dev bir metinle zayıf eşleşir.
2. **Maliyet ve odak:** LLM'e her soruda tüm dokümanları değil, sadece ilgili 3–5 parçayı
   göndeririz. Daha az metin daha ucuz ve daha hızlıdır; model de dikkatini doğru yere verir.
3. **Kesin kaynak:** "Yan Haklar › Yemek kartı" demek, sadece "Yan Haklar" demekten çok daha yararlı.

## İki yöntem

| | Sabit boyut (Görev 1) | Başlığa göre (Görev 2) |
|---|---|---|
| Nasıl? | Her N karakterde makasla kes | Belgenin kendi yapısına (## başlıklar, paragraflar) göre böl |
| Artısı | Çok basit, her metinde çalışır | Parçalar anlamlı bütünler; bölüm adı kaynağa eklenir |
| Eksisi | Cümleyi, tabloyu, kelimeyi ortadan bölebilir | Belgenin düzgün başlıkları olmasına dayanır |

**Overlap (örtüşme) neden var?** Sabit kesmede bir cümle iki parçanın arasında kalabilir.
Ardışık parçaların son/ilk 50 karakteri ortak olursa, sınırda kalan bilgi en az bir parçada
bütün olarak bulunur.

Rehberdeki uyarıyı hatırla: *"Metni her 1000 karakterde böldüm"* = YANLIŞ örnek.
*"Paragraf sınırlarında böldüm ve etkisini ölçtüm"* = DOĞRU örnek. Görev 1'i bilerek
yapıyoruz ki farkı kendi gözünle gör. Ders 7'de (ölçüm) ikisini sayılarla karşılaştıracağız.

## Kendini test et
<details><summary>1. Parçalar çok KÜÇÜK olursa (ör. 50 karakter) ne olur?</summary>
Her parça bağlamını kaybeder: "450 TL" bulunur ama neyin 450 TL olduğu başka parçada kalır.
</details>

<details><summary>2. Parçalar çok BÜYÜK olursa (ör. bütün doküman) ne olur?</summary>
Embedding bulanıklaşır, arama isabeti düşer, LLM'e gereksiz ve pahalı metin gider.
</details>

<details><summary>3. Metadata'yı neden kopyalıyoruz ({**doc.metadata, ...})?</summary>
Python'da sözlükler referansla taşınır. Kopyalamazsan tüm parçalar AYNI sözlüğü paylaşır;
birine "chunk_index" yazınca hepsi (ve orijinal doküman) değişir.
</details>
