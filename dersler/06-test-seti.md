# Ders 6 — Test seti ve retrieval ölçümü

**Veri:** `data/testset.jsonl` · **Kod:** `rag/testset.py` · **Çalıştır:** `.venv\Scripts\python.exe ders06_testset.py`

## Test seti nedir?
Sistemi puanlamak için hazırladığımız sınav kâğıdı: sorular ve **doğru cevaplar**
("altın cevaplar"). Cevap anahtarı olmayan bir sınavı puanlayamazsın.

40 soru, 4 tür:
| Tür | Sayı | Ne ölçer? |
|---|---|---|
| basit | 23 | Tek bir bölümde cevabı olan sorular |
| birlestirme | 7 | Cevabı iki farklı bölümde/dokümanda olan sorular |
| hileli | 4 | Yanlış bir varsayımla sorulan sorular ("25 gün, değil mi?") |
| yok | 6 | Cevabı dokümanlarda olmayan sorular ("bilmiyorum" demeli) |

Her soruda: `beklenen` (altın cevap), `anahtar` (cevapta mutlaka geçmesi gereken ifadeler),
`bolumler` (cevabın geçtiği dosya › bölüm).

## Önce test setini test et
Test setinde hata varsa sistemi yanlış puanlarız. `dogrula()` her bölümün gerçekten var
olduğunu ve anahtar ifadelerin o bölümlerde gerçekten geçtiğini kontrol eder.
İlk çalıştırmada **gerçekten bir hata yakaladı**: #28'de "1 hafta" yazmıştım ama doküman
"sırasıyla 1, 2 ve 3 hafta" diyor. İnsanlar test seti yazarken de hata yapar.

## Retrieval'ı LLM'siz ölçmek: recall@5
"Doğru bölüm(ler), ilk 5 sonucun içinde mi?" Birleştirme sorularında 2 bölüm gerekir;
biri bulunursa recall %50 olur. LLM çağırmadığı için **ücretsiz ve saniyeler sürer**.

| Yöntem | basit | birleştirme | hileli | TOPLAM |
|---|---|---|---|---|
| Vektör | 91% | 86% | 100% | 91% |
| Kelime | 100% | 93% | 100% | **99%** |
| Hybrid | 100% | 86% | 100% | 97% |

## Çıkarımlar
1. **Birleştirme soruları en zoru.** Hybrid'in kaçırdığı iki soru da bu türden (#24, #27):
   ikinci bölümü ilk 5'e sokamadı.
2. **Hybrid otomatik olarak en iyi değil.** Bu sette kelime araması bir tık önde. RRF, zayıf
   olan vektör listesini de hesaba katınca bazen doğru parçayı aşağı itebiliyor.
3. **Ders 4'teki 6 soruluk sonuç yanıltıcıydı:** Orada vektör araması 6 sorunun 4'ünde
   kaçırıyor gibi görünüyordu; 34 soruda recall'ı %91. Az soruyla karar vermek bu yüzden tehlikeli.

## Kendini test et
<details><summary>1. Neden "yok" sorularını retrieval ölçümüne katmadık?</summary>
Bulunması gereken bir bölüm yok. Onlar Ders 7'de cevap kalitesiyle ölçülecek: model
"Bu bilgi dokümanlarda yok." dedi mi?
</details>

<details><summary>2. Recall %100 ise sistem mükemmel midir?</summary>
Hayır. Doğru parça LLM'e gitmiş olabilir ama LLM yine yanlış cevap yazabilir. Retrieval ile
generation ayrı ayrı ölçülür. Ders 7 generation'ı ölçecek.
</details>

## Alıştırma
`data/testset.jsonl` dosyasına kendi yazdığın 5 soru ekle (en az biri "birlestirme", biri "yok"
olsun) ve `ders06_testset.py` dosyasını çalıştır. Doğrulayıcı hata verirse düzelt.
