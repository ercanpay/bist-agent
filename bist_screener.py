# -*- coding: utf-8 -*-
"""
BIST Otomatik Tarama Verisi Çekici
TradingView scanner API'sinden (tradingview-screener paketi) tüm BIST
hisselerini ve XU100 üyelik bilgisini çeker, CSV olarak kaydeder.
Günlük GitHub Actions ile çalışır. Giriş/şifre GEREKTİRMEZ.
"""
import sys, os, datetime, traceback
import pandas as pd
from tradingview_screener import Query

# Claude'un tarama sisteminin kullandığı tüm kolonlar (TradingView ham adları)
COLUMNS = [
    'name', 'description', 'close', 'change',
    'market_cap_basic', 'float_shares_percent_current',
    'volume', 'average_volume_10d_calc', 'average_volume_30d_calc',
    'average_volume_60d_calc', 'relative_volume_10d_calc',
    'Perf.W', 'Perf.1M', 'Perf.3M', 'Perf.6M', 'Perf.YTD',
    'RSI', 'MoneyFlow', 'ADX',
    'MACD.macd', 'MACD.signal',
    'SMA20', 'SMA50', 'SMA200',
    'High.1M', 'High.3M', 'High.6M', 'price_52_week_high', 'High.All',
    'Low.1M', 'Low.3M',
    'ATRP', 'Volatility.W', 'Volatility.M',
    'BB.upper', 'BB.lower',
    'sector.tr', 'price_earnings_ttm', 'price_book_fq',
]

# Rapor tarafındaki Türkçe kolon adları (Claude'un beklediği şema)
RENAME = {
    'name': 'Sembol', 'description': 'Açıklama', 'close': 'Fiyat',
    'change': 'Fiyat değişimi %, 1 gün',
    'market_cap_basic': 'Piyasa değeri',
    'float_shares_percent_current': 'Halka açıklık %',
    'volume': 'Hacim, 1 gün',
    'average_volume_10d_calc': 'Ortalama hacim, 10 gün',
    'average_volume_30d_calc': 'Ortalama hacim, 30 gün',
    'average_volume_60d_calc': 'Ortalama hacim, 60 gün',
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
}


def pull_market():
    """Tüm BIST hisselerini çek."""
    q = (Query()
         .set_markets('turkey')
         .select(*COLUMNS)
         .limit(800))
    q.query['ignore_unknown_fields'] = True
    q.query.pop('preset', None)
    q.query['options'] = {'lang': 'tr'}
    total, df = q.get_scanner_data()
    print(f"Piyasa çekildi: {len(df)} satır (toplam {total})")
    return df


def pull_xu100_symbols():
    """XU100 (BIST 100) üyelerinin sembol listesini çek."""
    q = Query().set_markets('turkey').select('name').limit(150)
    q.query['symbols'] = {'symbolset': ['SYML:BIST;XU100']}
    q.query['ignore_unknown_fields'] = True
    try:
        _, df = q.get_scanner_data()
        syms = set(df['name'].astype(str))
        print(f"XU100 üyeleri çekildi: {len(syms)} sembol")
        return syms
    except Exception:
        print("UYARI: XU100 listesi çekilemedi, kolon boş bırakılıyor")
        traceback.print_exc()
        return set()


def main():
    today = datetime.date.today().isoformat()
    os.makedirs('data', exist_ok=True)
    df = pull_market()
    if len(df) < 300:
        print(f"HATA: {len(df)} satır — beklenenden az, veri şüpheli. Çıkılıyor.")
        sys.exit(1)

    xu100 = pull_xu100_symbols()
    df = df.rename(columns=RENAME)
    # ticker kolonu 'BIST:XXXX' formatında gelir; sembolü temizle
    if 'ticker' in df.columns:
        df = df.drop(columns=['ticker'])
    df['XU100'] = df['Sembol'].astype(str).isin(xu100)
    df.insert(0, 'Tarih', today)

    df.to_csv('data/latest.csv', index=False, encoding='utf-8-sig')
    df.to_csv(f'data/bist_{today}.csv', index=False, encoding='utf-8-sig')
    print(f"Kaydedildi: data/latest.csv ve data/bist_{today}.csv ({len(df)} satır)")


if __name__ == '__main__':
    main()
