# BIST Otomatik Veri Hattı — Kurulum Rehberi

## Mimari (bilgisayar gerektirmez)

```
GitHub Actions (bulut, hafta içi 18:22)
  └─ bist_screener.py → TradingView scanner API (şifresiz)
       └─ data/latest.csv  (repo'ya otomatik commit)
            └─ Cowork zamanlanmış görevi (18:35) URL'den okur
                 └─ Günlük rapor önüne düşer
```

## Kurulum adımları (bir kere, ~10 dk)

1. **GitHub hesabı** yoksa aç (github.com — ücretsiz).
2. **Yeni repo oluştur:** adı `bist-agent`, **Public** seç
   (içinde kişisel veri yok, sadece halka açık borsa verisi;
   Public repo = Actions tamamen ücretsiz + raw URL şifresiz okunur).
3. Bu klasördeki 3 dosyayı repoya yükle (web arayüzünden
   "Add file → Upload files" ile sürükle-bırak yeterli):
   - `bist_screener.py`
   - `.github/workflows/screener.yml`  (klasör yapısını koru!)
   - `README_KURULUM.md` (opsiyonel)
4. Repo → **Actions** sekmesi → "BIST Gunluk Tarama" → **Run workflow**
   ile elle bir test çalıştır. 1-2 dk içinde yeşil ✓ ve
   `data/latest.csv` dosyası oluşmalı.
5. CSV'nin ham adresini not et:
   `https://raw.githubusercontent.com/KULLANICI_ADIN/bist-agent/main/data/latest.csv`

## Cowork görevlerine eklenecek satır

Günlük ve haftalık görev prompt'larının başına şunu ekle:

> Önce şu adresten güncel tarama verisini indir ve DataFrame olarak
> yükle: https://raw.githubusercontent.com/KULLANICI_ADIN/bist-agent/main/data/latest.csv
> 'Tarih' kolonunun bugünün tarihi olduğunu doğrula; eski tarihliyse
> raporun başına "VERİ GÜNCEL DEĞİL" uyarısı koy.
> XU100 kolonu True = BIST 100 üyesi (Portföy 2 evreni = XU100 False).

Artık haftalık raporda CSV yüklemene gerek yok — tam tarama her gün
otomatik veriyle yapılabilir.

## Olası sorunlar

- **İlk testte kolon hatası:** TradingView bazı alan adlarını
  değiştirebiliyor. Actions log'undaki hata mesajını Claude'a yapıştır,
  script'i güncellesin.
- **TradingView, GitHub IP'lerini engellerse** (nadir): aynı script'i
  evdeki bir bilgisayarda Görev Zamanlayıcı ile çalıştırıp
  `git push` ile aynı repoya gönderirsin — mimarinin geri kalanı
  hiç değişmez. "Kafasız bilgisayar" planın B planı olarak hazır.
- **Hafta sonu/tatil:** Cron sadece hafta içi çalışır; resmi tatillerde
  son işlem gününün verisi kalır (Tarih kolonu bunu gösterir).

## Değişmeyen kural

Bu hat SADECE veri toplar ve rapor üretir. Midas'ta emir girişi
manueldir ve öyle kalacaktır — güvenlik ve hesap sözleşmesi gereği.
