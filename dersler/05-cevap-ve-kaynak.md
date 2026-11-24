# Ders 5 — Cevap üretme ve kaynak gösterme (citation)

**Kod:** `rag/pipeline.py` · **Çalıştır:** `.venv\Scripts\python.exe ders05_cevap.py`

## RAG'ın üç harfi, üç satır kod
```python
parcalar = hybrid_ara(soru, ...)                          # R — Retrieval: bul
prompt   = PROMPT_SABLONU.format(kaynaklar=..., soru=...)  # A — Augmentation: prompt'a ekle
metin    = generate(prompt)                                # G — Generation: cevap yazdır
```

## Prompt'taki 4 kural ve nedenleri
| Kural | Neden? |
|---|---|
| Sadece KAYNAKLAR'ı kullan | Modelin ezberinden (ör. İş Kanunu'ndaki 14 gün) cevap vermesini engeller |
| Her bilgiye [n] ile atıf yap | Kullanıcı cevabı kontrol edebilir; biz de hangi parçanın kullanıldığını görürüz |
| Yoksa "Bu bilgi dokümanlarda yok." yaz | Halüsinasyonun panzehiri. **Sabit bir cümle** istedik ki kodla yakalayabilelim |
| Kısa, net, Türkçe | Tutarlı çıktı |

Parçaları LLM'e **numaralı** veriyoruz: `[1] (02-izin-politikasi.md › Yıllık ücretli izin) ...`.
Model `[1]` yazınca, koddaki regex (`\[(\d+)\]`) bu numarayı yakalar ve parçanın metadata'sından
dosya ve bölüm adını buluruz. Ders 1'deki "metadata = gelecekteki citation" sözü burada gerçek oldu.

## Gördüklerimiz
- **RAG olmadan:** Gemini dürüst davrandı ("resmi veri yok") ama yine de İş Kanunu'nun
  **14 gün**ünü verdi. Mavikod için bu yanlış: doğru cevap 18 gün. Model kendi bildiği en
  yakın şeyi söyledi.
- **RAG ile:** 18 / 24 / 30 gün, kıdeme göre ve kaynağıyla. Kaynak doğru bölüm.
- **Dokümanlarda olmayan sorular** (ciro, köpek): ikisinde de "Bu bilgi dokümanlarda yok."
- Bir 503 hatası geldi ve `generate()` 2 sn bekleyip yeniden denedi: Ders 5 öncesi
  eklediğimiz retry işe yaradı.

## Kendini test et
<details><summary>1. Neden "bilmiyorum" yerine sabit bir cümle istiyoruz?</summary>
Kod bu cümleyi `if BILGI_YOK in metin` ile yakalayabilir. Ders 7'de "model bilmediğini
kaç kez doğru söyledi?" diye ölçerken bu işimize yarayacak.
</details>

<details><summary>2. Cevap yanlışsa, hatanın retrieval'dan mı LLM'den mi geldiğini nasıl anlarsın?</summary>
LLM'e verilen parçalara (`cevap.parcalar`) bak. Doğru parça yoksa → retrieval hatası.
Doğru parça varsa ama cevap yanlışsa → LLM (ya da prompt) hatası. Rehberdeki "Neye odaklan?"
sorusu buydu.
</details>

<details><summary>3. k=5 yerine k=50 parça versek daha iyi olmaz mı?</summary>
Hem pahalı (her parça token = para) hem de model alakasız metinde kaybolabilir. Az ama
isabetli parça genelde daha iyidir. Bunu da Ders 7'de ölçebiliriz.
</details>

## Alıştırma
`ders05_cevap.py` içine kendi sorularını ekle. Özellikle şunları dene:
- İki dokümanı birleştirmeyi gerektiren bir soru: "Uzaktan çalışırken eğitim bütçemle kulaklık alabilir miyim?"
- Hileli bir soru: "Yıllık izin 25 gün, değil mi?"
