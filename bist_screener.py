# -*- coding: utf-8 -*-
"""
BIST Otomatik Tarama Verisi Cekici
- Tum BIST hisseleri + XU100 uyeligi
- Makro veriler (BIST100 endeks, USDTRY, Brent, ons altin)
- Akilli Para Skoru bilesenleri (hacim rejimi + fiyat-hacim uyumu)
"""
import sys, os, datetime, traceback
import pandas as pd
from tradingview_screener import Query

COLUMNS = [
    'name', 'description', 'close', 'change',
    'market_cap_basic', 'float_shares_percent_current',
    'volume', 'average_volume_10d_calc', 'average_volume_30d_calc',
    'average_volume_60d_calc', 'average_volume_90d_calc',
    'relative_volume_10d_calc',
    'Perf.W', 'Perf.1M', 'Perf.3M', 'Perf.6M', 'Perf.YTD',
    'RSI', 'MoneyFlow', 'ADX',
    'MACD.macd', 'MACD.signal',
    'SMA20', 'SMA50', 'SMA200',
    'High.1M', 'High.3M', 'High.6M', 'price_52_week_high', 'High.All',
    'Low.1M', 'Low.3M',
    'ATRP', 'Volatility.W', 'Volatility.M',
    'BB.upper', 'BB.lower',
    'sector.tr', 'price_earnings_ttm', 'price_book_fq',
    'change_from_open', 'gap',
]

RENAME = {
    'name': 'Sembol', 'description': 'Açıklama', 'close': 'Fiyat',
    'change': 'Fiyat değişimi %, 1 gün',
    'market_cap_basic': 'Piyasa değeri',
    'float_shares_percent_current': 'Halka açıklık %',
    'volume': 'Hacim, 1 gün',
    'average_volume_10d_calc': 'Ortalama hacim, 10 gün',
    'average_volume_30d_calc': 'Ortalama hacim, 30 gün',
    'average_volume_60d_calc': 'Ortalama hacim, 60 gün',
    'average_volume_90d_calc': 'Ortalama hacim, 90 gün',
    'relative_volume_10d_calc': 'Bağıl hacim, 1 gün',
    'Perf.W': 'Performans %, 1 hafta', 'Perf.1M': 'Performans %, 1 ay',
    'Perf.3M': 'Performans %, 3 ay', 'Perf.6M': 'Performans %, 6 ay',
    'Perf.YTD': 'Performans %, Güncel yıl',
    'RSI': 'RSI', 'MoneyFlow': 'MFI', 'ADX': 'ADX',
    'MACD.macd': 'MACD Level', 'MACD.signal': 'MACD Signal',
    'SMA20': 'SMA20', 'SMA50': 'SMA50', 'SMA200': 'SMA200',
    'High.1M': 'Yüksek, 1 ay', 'High.3M': 'Yüksek, 3 ay',
    'High.6M': 'Yüksek, 6 ay', 'price_52_week_high': 'Yüksek, 52 hafta',
    'High.All': 'Yüksek, Tüm Zamanlar',
    'Low.1M': 'Düşük, 1 ay', 'Low.3M': 'Düşük, 3 ay',
    'ATRP': 'ATR %', 'Volatility.W': 'Volatilite, 1 hafta',
    'Volatility.M': 'Volatilite, 1 ay',
    'BB.upper': 'BB Upper', 'BB.lower': 'BB Lower',
    'sector.tr': 'Sektör',
    'price_earnings_ttm': 'F/K', 'price_book_fq': 'PD/DD',
    'change_from_open': 'Açılıştan değişim %', 'gap': 'Gap %',
}

MACRO = {
    'BIST:XU100': 'BIST 100',
    'FX_IDC:USDTRY': 'USD/TRY',
    'FX_IDC:EURTRY': 'EUR/TRY',
    'TVC:UKOIL': 'Brent',
    'TVC:GOLD': 'Ons Altın',
    'TVC:TR10Y': 'TR 10Y Tahvil',
}


def pull_market():
    q = (Query().set_markets('turkey').select(*COLUMNS).limit(800))
    q.query['ignore_unknown_fields'] = True
    total, df = q.get_scanner_data()
    print(f"Piyasa cekildi: {len(df)} satir (toplam {total})")
    return df


def pull_xu100_symbols():
    q = Query().set_markets('turkey').select('name').limit(150)
    q.query['symbols'] = {'symbolset': ['SYML:BIST;XU100']}
    q.query['ignore_unknown_fields'] = True
    try:
        _, df = q.get_scanner_data()
        syms = set(df['name'].astype(str))
        print(f"XU100 uyeleri: {len(syms)} sembol")
        return syms
    except Exception:
        print("UYARI: XU100 listesi cekilemedi")
        traceback.print_exc()
        return set()


def pull_macro():
    """Endeks, kur, emtia verilerini cek (her biri ayri sorgu)."""
    import requests
    rows = []
    url = 'https://scanner.tradingview.com/global/scan'
    headers = {'User-Agent': 'Mozilla/5.0'}
    for tk, isim in MACRO.items():
        try:
            payload = {
                'symbols': {'tickers': [tk], 'query': {'types': []}},
                'columns': ['close', 'change', 'Perf.W', 'Perf.1M'],
            }
            r = requests.post(url, json=payload, headers=headers, timeout=20)
            r.raise_for_status()
            d = r.json().get('data', [])
            if d and d[0].get('d'):
                v = d[0]['d']
                rows.append({
                    'Gosterge': isim, 'Ticker': tk,
                    'Deger': v[0], 'Degisim %': v[1],
                    'Hafta %': v[2], 'Ay %': v[3],
                })
                print(f"  {isim}: {v[0]}")
            else:
                print(f"  UYARI: {isim} ({tk}) bos dondu")
        except Exception as e:
            print(f"  UYARI: {isim} ({tk}) cekilemedi: {e}")
    print(f"Makro veriler cekildi: {len(rows)} gosterge")
    return pd.DataFrame(rows)


def add_smart_money(df):
    """Akilli Para Skoru bilesenleri.

    (a) Fiyat-hacim uyumu: hacim genislerken fiyat yonu
    (b) Hacim rejimi degisimi: gunluk / haftalik / aylik pencereler
    """
    v1 = pd.to_numeric(df['Hacim, 1 gün'], errors='coerce')
    v10 = pd.to_numeric(df['Ortalama hacim, 10 gün'], errors='coerce')
    v30 = pd.to_numeric(df['Ortalama hacim, 30 gün'], errors='coerce')
    v60 = pd.to_numeric(df['Ortalama hacim, 60 gün'], errors='coerce')
    v90 = pd.to_numeric(df['Ortalama hacim, 90 gün'], errors='coerce')
    px = pd.to_numeric(df['Fiyat'], errors='coerce')
    ch1 = pd.to_numeric(df['Fiyat değişimi %, 1 gün'], errors='coerce')
    chw = pd.to_numeric(df['Performans %, 1 hafta'], errors='coerce')
    chm = pd.to_numeric(df['Performans %, 1 ay'], errors='coerce')

    # (b) Hacim rejimi — uc pencere
    df['Hacim rejimi, gunluk'] = (v1 / v10).round(2)      # bugun vs son 2 hafta
    df['Hacim rejimi, haftalik'] = (v10 / v30).round(2)   # son 2 hafta vs 6 hafta
    df['Hacim rejimi, aylik'] = (v30 / v90).round(2)      # son 6 hafta vs 4.5 ay
    df['Ciro, 10g (M TL)'] = (v10 * px / 1e6).round(1)

    # (a) Fiyat-hacim uyumu: her pencerede hacim genisledi mi VE fiyat yukari mi
    def concord(vol_ratio, perf, vol_esik):
        s = pd.Series(0.0, index=df.index)
        genis = vol_ratio > vol_esik
        s[genis & (perf > 0)] = 1.0        # hacim genis + fiyat yukari = birikim
        s[genis & (perf < 0)] = -1.0       # hacim genis + fiyat asagi = dagitim
        return s

    c_d = concord(df['Hacim rejimi, gunluk'], ch1, 1.3)
    c_w = concord(df['Hacim rejimi, haftalik'], chw, 1.15)
    c_m = concord(df['Hacim rejimi, aylik'], chm, 1.10)
    df['Fiyat-hacim uyumu'] = (c_d + c_w + c_m).round(1)  # -3 ile +3 arasi

    # Akilli Para Skoru (0-100)
    rej = ((df['Hacim rejimi, gunluk'].clip(0, 3) / 3) * 15 +
           ((df['Hacim rejimi, haftalik'] - 0.8).clip(0, 1.2) / 1.2) * 20 +
           ((df['Hacim rejimi, aylik'] - 0.8).clip(0, 1.2) / 1.2) * 20)
    uyum = ((df['Fiyat-hacim uyumu'] + 3) / 6) * 30
    mfi = pd.to_numeric(df['MFI'], errors='coerce')
    rsi = pd.to_numeric(df['RSI'], errors='coerce')
    irak = ((mfi - rsi).clip(-10, 40) / 40) * 15
    df['Akilli Para Skoru'] = (rej + uyum + irak).round(1)
    return df


def main():
    today = datetime.date.today().isoformat()
    os.makedirs('data', exist_ok=True)

    df = pull_market()
    if len(df) < 300:
        print(f"HATA: {len(df)} satir, cok az. Cikiliyor.")
        sys.exit(1)

    xu100 = pull_xu100_symbols()
    df = df.rename(columns=RENAME)
    if 'ticker' in df.columns:
        df = df.drop(columns=['ticker'])
    df['XU100'] = df['Sembol'].astype(str).isin(xu100)
    df = add_smart_money(df)
    df.insert(0, 'Tarih', today)

    df.to_csv('data/latest.csv', index=False, encoding='utf-8-sig')
    df.to_csv(f'data/bist_{today}.csv', index=False, encoding='utf-8-sig')
    print(f"Kaydedildi: data/latest.csv ({len(df)} satir, {len(df.columns)} kolon)")

    macro = pull_macro()
    if len(macro):
        macro.insert(0, 'Tarih', today)
        macro.to_csv('data/macro.csv', index=False, encoding='utf-8-sig')
        print("Kaydedildi: data/macro.csv")


if __name__ == '__main__':
    main()
