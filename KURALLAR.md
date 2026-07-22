# RİSK ANAYASASI — TEK PORTFÖY, MOMENTUM + PRICE ACTION
Güncelleme: 22 Temmuz 2026

## PORTFÖY YAPISI
- Tek portföy, endeks kısıtı yok (XU100 içi/dışı fark etmez)
- Hedef dağılım: %60-80 hisse (momentum pozisyonları), %20-40 PPF (kuru barut)
- Eş zamanlı maksimum 5 açık pozisyon
- Fonlama kaynağı: TERA pozisyonu satışı

## POZİSYON BOYUTLANDIRMA (yüzde bazlı — NAV'dan hesaplanır)
- Tekil işlem riski: NAV'ın %2,5'i → 1R = NAV × 0,025
- Lot hesabı: (NAV × 0,025 × kademe katsayısı) / (Giriş − Stop) = Lot
- Tek hisse max ağırlık: NAV'ın %25'i
- Pozisyon ≤ hissenin günlük ortalama cirosunun %3'ü (çıkış kısıtı)
- Toplam açık risk (tüm pozisyonların stop mesafeleri toplamı) ≤ NAV'ın %10'u
- Kaldıraç yok, VİOP yok, kredili işlem yok

## DEVRE KESİCİLER
- Aylık drawdown -%10 → tüm pozisyonlar kapanır, ay sonuna kadar PPF'te bekle
- Üst üste 3 stop yeme → 2 gün işlem yasağı, kurulum kalitesi gözden geçirilir
- Stoplar KAPANIŞ bazlı; gün içi fitil sayılmaz

## GİRİŞ KURALLARI — PRICE ACTION
Bir kurulumun geçerli olması için ÜÇÜ birden gerekir:

1. YAPI: Fiyat tanımlı bir yapısal seviyeyi kırmış olmalı
   - 20 günlük yatay konsolidasyonun üst bandı, VEYA
   - 3 aylık zirve, VEYA
   - Düşen trendin tepe noktalarını birleştiren çizgi, VEYA
   - Son 20 günün en yükseği (dönüş kurulumlarında)
   Kırılım GÜNLÜK KAPANIŞLA teyit edilir, gün içi dokunuş sayılmaz

2. HACİM: Kademeye göre eşik değişir (aşağıdaki tabloya bak)
   Hacimsiz kırılım = tuzak. Beklenir, alınmaz

3. TREND KADEMESİ: Boyut, fiyatın ortalamalara göre konumuyla belirlenir

   | Kademe | Konum | Hacim şartı | Ek şart | Boyut |
   |---|---|---|---|---|
   | A — Tam trend | Fiyat > SMA20 ve > SMA50, ADX > 20 | relvol > 1,5 | — | 1R |
   | B — Dönüş | Fiyat > SMA20, < SMA50 | relvol > 2,0 | SMA20 yukarı dönmüş (fiyat > SMA20 > 5 gün önceki SMA20) | 0,5R |
   | C — Derin dönüş | Fiyat < SMA20 ve < SMA50 | relvol > 2,5 | Son 20 günün en yükseğini kırmış + ADX > 20 + stop kırılım seviyesinin %2 altı | 0,25R |

   SMA200 altındaki TÜM kurulumlarda boyut ayrıca yarıya iner.
   Örnek: B kademesi + SMA200 altı = 0,25R.

   UYARI: B ve C kademeleri en çok yanlış sinyal üreten bölgedir.
   "Düşen bıçak yakalama" yasağıyla arasındaki fark, hacim eşiği ve
   20 günün zirvesini kırma şartıdır. Bu iki şart yoksa o bir dönüş
   değil, düşüş içinde tepkidir. Zaman stopu burada sıkı uygulanır.

## GİRİŞ ZAMANLAMASI
İki meşru giriş noktası var:
- (a) KIRILIM GÜNÜ: kapanışa yakın, teyit gerçekleşmişse
- (b) GERİ TEST: kırılan seviyeye dönüş + tutunma göstergesi
     (uzun alt fitil, hacim azalması, yeşil kapanış)
Kırılımdan %8'den fazla uzaklaşmış fiyata girilmez — kovalama yasağı

## YASAKLAR
- RSI > 78 iken yeni pozisyon açılmaz
- Düşen bıçak: SMA altında olup 20 günün zirvesini kırmamış ve hacim
  eşiğini geçmemiş hisseye alım yok
- Yakın İzleme Pazarı ve PÖİP yasak (işlem kısıtları)
- Endeks 13.900 altındayken yeni pozisyon açılmaz; açıklar stopuyla yönetilir
- Temel kontrol zorunlu: zararı büyüyen, kayyum/TMSF geçmişi olan, parabolik
  koşup çökmüş hisselere girilmez (PRKME dersi)

## ÇIKIŞ KURALLARI
- Stop: kırılım seviyesinin %2-3 altı VEYA son swing dip; hangisi yakınsa
  (C kademesinde %2 sabit)
- 1R'de pozisyonun 1/3'ü satılır, stop girişe çekilir (risksiz pozisyon)
- 2R'de bir 1/3 daha satılır
- Kalan 1/3 trailing: SMA20 kapanış altı VEYA son 3 günün en düşüğü kırılırsa
- ZAMAN STOPU: 10 işlem gününde 1R'ye ulaşmayan pozisyon kapatılır
- Tez bozulduğunda maliyet fiyatı karar kriteri DEĞİLDİR

## GÜNLÜK TARAMA KRİTERLERİ
KIRILIM (A): relvol > 1,5 · günlük değişim > +%3 VEYA 3A zirveye mesafe < %2
· fiyat > SMA20 ve SMA50 · ADX > 20 · ciro > 50M TL · RSI 50-78

GERİ TEST: son 10 günde 3A zirve kırmış · kırılan seviyenin %0-5 üstünde
· relvol < 1,0

DÖNÜŞ (B/C): relvol > 2,0 · son 20 günün en yükseğini kırmış · ADX > 20
· ciro > 50M TL · RSI 45-78 · kademe konuma göre belirlenir
