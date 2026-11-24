# Ders 7 — Cevap kalitesini ölçmek ve deney yapmak

**Kod:** `rag/evaluate.py` · **Çalıştır:** `.venv\Scripts\python.exe ders07_olcum.py` (hızlı: `--hizli`)
**Ayrıntılı sonuçlar:** `sonuclar/baslik.json`, `sonuclar/sabit.json`

## Metrikler
| Metrik | Ne ölçer? | Nasıl? |
|---|---|---|
| Doğruluk (hakem) | Cevap altın cevapla aynı bilgiyi veriyor mu? | Hakem LLM |
| Doğruluk (anahtar) | Anahtar ifadeler cevapta geçiyor mu? | Metin kontrolü |
| Sadakat (faithfulness) | Cevaptaki her bilgi kaynaklarda var mı? | Hakem LLM (Ragas'taki fikir) |
| Kaynak gösterme | Cevapta [n] atfı var mı? | Metin kontrolü |
| 'Bilgi yok' doğru deme | Cevapsız sorularda uydurmadı mı? | Sabit cümle kontrolü |

## Deney: Başlığa göre vs sabit chunking (40 soru, aynı test seti)

| Metrik | Başlığa göre | Sabit (500/50) |
|---|---|---|
| Doğruluk (hakem) | **92%** | 90% |
| Doğruluk (anahtar) | **95%** | 88% |
| Sadakat (faithfulness) | 100% | 100% |
| Kaynak gösterme | **97%** | 88% |
| 'Bilgi yok' doğru deme | 100% | 100% |
| Basit soru doğruluğu | **100%** | 96% |
| Birleştirme doğruluğu | 71% | **86%** |
| Hileli soru doğruluğu | **75%** | 50% |

## Yorum
1. **Genel kazanan: başlığa göre chunking**, ama fark küçük (92% vs 90%). İki ölçüm (hakem ve
   anahtar) aynı yönü gösteriyor; bu yüzden sonuca güvenebiliriz.
2. **Birleştirme sorularında sabit chunking daha iyi** (86% vs 71%). Komşu bölümler aynı parçaya
   düşebildiği için iki bilgi tek parçada geliyor. Başlığa göre yöntemin kaçırdığı #24 ve #27,
   Ders 6'da recall'ı 50% çıkan soruların aynısı → hata **retrieval**'dan geliyor.
3. **Sadakat iki yöntemde de 100%:** Model hiçbir cevapta kaynakta olmayan bilgi uydurmadı.
4. **#31 iki yöntemde de yanlış** ("25 gün, değil mi?" → "Bu bilgi dokümanlarda yok."). Doğru
   parça bulunuyor ama model yanlış varsayımı düzeltmek yerine "bilgi yok" diyor → hata **LLM/prompt**'tan.

## Sonraki iyileştirme fikirleri (her biri ölçülerek denenmeli)
- Prompt'a kural: "Soru yanlış bir varsayım içeriyorsa, kaynaklara göre düzelt." (#31 için)
- k=5 yerine k=8 parça: birleştirme sorularında ikinci bölümün de gelme ihtimali artar.
- Her parçanın başına doküman başlığını eklemek (contextual chunking).

## Sınırlamalar (README'de dürüstçe yazılmalı)
- Hakem, cevabı yazan modelle aynı model (gemini-3.5-flash-lite); kendi cevabını kayırabilir.
- 40 soru küçük bir set; %2'lik fark tek bir soru demek.
- Dokümanlar kurgusal ve temiz; gerçek PDF'ler daha dağınık olur.
