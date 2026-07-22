# RİSK ANAYASASI — DEĞİŞMEZ KURALLAR

## Pozisyon boyutlandırma
- Tekil işlem riski: P1 max 25.000 TL, P2 max 25.000 TL
- Tek hisse max ağırlık: P1 %20, P2 %25
- Pozisyon boyutu ≤ hissenin günlük ortalama cirosunun %3'ü (likidite kuralı)
- Kaldıraç yok, VİOP yok, kredili işlem yok

## Devre kesiciler
- P1 aylık drawdown -%8 → tüm riskli pozisyonlar kapanır, PPF'e park
- P2 aylık drawdown -%12 → aynı
- Stop seviyeleri KAPANIŞ bazlıdır, gün içi fitil sayılmaz

## Giriş disiplini
- Kademeli giriş: ilk kademe %40-50, kalan teyit/katalizör sonrası
- Aşırı alım bölgesinden (RSI > 75) yeni pozisyon AÇILMAZ — kovalama yasak
- Yan tahta / düşük float hisselerde Fintables takas teyidi ZORUNLU
- Yakın İzleme Pazarı ve PÖİP: kategorik yasak
- Endeks kritik desteğin altındayken (şu an 13.900/13.800) yeni alım yok

## Çıkış disiplini
- Her pozisyonun girişte yazılı stopu ve 2 kademeli kâr hedefi olur
- Zaman stopu konulmuşsa fiyat güzel olsa bile uygulanır
- Tez bozulduğunda maliyet fiyatı karar kriteri DEĞİLDİR

## Portföy ayrımı
- Aynı hisse iki portföyde birden tutulmaz
- P2 evreni: XU100 = False olan hisseler (CSV'deki XU100 kolonu)

## Analiz metodolojisi
- MFI-RSI ıraksaması (MFI eksi RSI): +20 üstü = sessiz para girişi izi
- Hacim ivmesi: 10 günlük ort. hacim / 30 günlük ort. hacim
- Wyckoff faz konumu: SMA50/SMA200'e göre fiyat konumu
- Kantitatif skor tek başına yeterli değil — haber/KAP ve takas teyidi şart
  (PRKME dersi: skor 2. sıradaydı, şirket zararda ve dağıtım fazındaydı)
