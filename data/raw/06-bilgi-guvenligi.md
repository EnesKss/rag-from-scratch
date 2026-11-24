# Bilgi Güvenliği Politikası

Mavikod'un ürünleri 18.000'den fazla işletmenin muhasebe ve müşteri verisini tutar. Bu verinin güvenliği şirketin varlık sebebidir. Bu politika tüm çalışanlar, stajyerler ve dış danışmanlar için zorunludur.

## Şifreler ve kimlik doğrulama

- Tüm şirket hesaplarında şifreler en az **14 karakter** olmalıdır.
- Şifreler yalnızca **kurumsal şifre yöneticisinde** saklanır. Şifreleri not defterine, tarayıcıya ya da e-postaya yazmak yasaktır.
- Aynı şifre iki farklı hesapta kullanılamaz.
- Tüm şirket hesaplarında **çok faktörlü kimlik doğrulama (MFA)** zorunludur. SMS ile doğrulama kabul edilmez; doğrulayıcı uygulama ya da donanım anahtarı kullanılır.
- Şifreler düzenli aralıklarla değiştirilmez; yalnızca sızıntı şüphesi olduğunda değiştirilir.

## Cihaz güvenliği

- Şirket bilgisayarlarında **disk şifreleme** açık olmalıdır. IT ekibi bunu kurulumda açar; kapatılması yasaktır.
- Ekran, **5 dakika** işlem yapılmadığında otomatik olarak kilitlenir. Bilgisayarın başından kalkarken ekranı elle kilitlemen beklenir.
- İşletim sistemi güncellemeleri yayımlandıktan sonra en geç **7 gün** içinde kurulmalıdır.
- **USB bellek** ve harici disk kullanımı yasaktır. Dosya paylaşımı şirketin bulut depolama alanı üzerinden yapılır.
- Kişisel cihazlardan yalnızca Slack ve e-postaya erişilebilir; bu cihazlarda da ekran kilidi ve MFA zorunludur.

## VPN

Ofis dışından iç sistemlere (yönetim paneli, iç wiki, veritabanları) yalnızca şirket **VPN**'i üzerinden bağlanılır. Halka açık Wi-Fi ağlarında (kafe, havalimanı, otel) VPN, iç sistemlere bağlanılmasa bile açık tutulmalıdır.

## Veri sınıflandırması

Mavikod'daki tüm bilgiler dört sınıftan birine girer:

| Sınıf | Örnekler | Kurallar |
|-------|----------|----------|
| Herkese Açık | Web sitesi, blog yazıları, basın bültenleri | Serbestçe paylaşılabilir |
| İç | Ekip dokümanları, toplantı notları, iç wiki | Sadece çalışanlarla paylaşılır |
| Gizli | Maaş bilgileri, sözleşmeler, finansal raporlar | Sadece ihtiyacı olan kişilerle paylaşılır |
| Çok Gizli | Müşteri verileri, üretim veritabanları, şifreleme anahtarları | Sadece yetkili ekipler erişebilir, tüm erişim kayıt altındadır |

**Çok Gizli** veriler hiçbir koşulda kişisel cihaza indirilemez, e-postayla gönderilemez ve yapay zeka sohbet araçlarına yapıştırılamaz.

## Erişim yönetimi

- Üretim sistemlerine erişim yalnızca bu erişime ihtiyacı olan ekiplere verilir ve **bilgi güvenliği eğitimini tamamlamış** olmak ön koşuldur.
- Erişim talepleri `#yardim-it` kanalından değil, Mavinet'teki "Erişim Talebi" formundan yapılır ve yöneticinin onayını gerektirir.
- Tüm erişim yetkileri **90 günde bir** gözden geçirilir. Kullanılmayan yetkiler otomatik olarak kaldırılır.
- İşten ayrılan çalışanların tüm erişimleri son iş günü saat 18:00'de kapatılır.

## Oltalama (phishing) e-postaları

Şüpheli bir e-posta aldığında linke tıklama ve ekini açma. E-posta istemcisindeki **"Şüpheli e-posta bildir"** butonunu kullan. Bilgi güvenliği ekibi yılda dört kez habersiz oltalama tatbikatı yapar; tatbikat e-postasındaki linke tıklayanlar 15 dakikalık kısa bir eğitimi tekrar alır.

## Güvenlik olayı bildirimi

Bir güvenlik olayından şüphelendiğinde (bilgisayarını kaybettin, şüpheli bir linke tıkladın, yanlış kişiye gizli bir dosya gönderdin) **en geç 1 saat içinde** bildir:

1. Slack'te `#guvenlik-olay` kanalına yaz, ya da
2. **guvenlik@mavikod.example** adresine e-posta gönder, ya da
3. Mesai dışında nöbetçi güvenlik telefonunu ara (numara iç wiki'de).

Hata yapan çalışan, olayı hızla bildirdiği sürece cezalandırılmaz. Olayı saklamak ise disiplin sürecine yol açar.

## Eğitimler

- **Bilgi güvenliği eğitimi:** İşe başlarken ilk 5 iş günü içinde ve sonrasında **her yıl** tekrarlanır.
- **KVKK eğitimi:** İşe başlarken ilk 30 gün içinde ve sonrasında her yıl tekrarlanır.
