# -*- coding: utf-8 -*-
"""
BIST Akilli Para Takip Sistemi
- Tum BIST hisseleri + XU100 uyeligi
- Uc zaman diliminde hacim rejimi ve momentum
- Gunluk arsiv (data/history.csv) -> birikim yasi, ATR sikismasi,
  yon bazli hacim analizi
- Sektor bazli normalizasyon
- Makro veriler (ayri sorgu)
"""
import sys, os, datetime, traceback
import pandas as pd
import numpy as np
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
]

RENAME = {
    'name': 'Sembol', 'description': 'Aciklama', 'close': 'Fiyat',
    'change': 'Gunluk %',
    'market_cap_basic': 'Piyasa degeri',
    'float_shares_percent_current': 'Halka aciklik %',
    'volume': 'Hacim 1g',
    'average_volume_10d_calc': 'Hacim ort 10g',
    'average_volume_30d_calc': 'Hacim ort 30g',
    'average_volume_60d_calc': 'Hacim ort 60g',
    'average_volume_90d_calc': 'Hacim ort 90g',
    'relative_volume_10d_calc': 'Bagil hacim',
    'Perf.W': 'Haftalik %', 'Perf.1M': 'Aylik %',
    'Perf.3M': '3 Aylik %', 'Perf.6M': '6 Aylik %',
    'Perf.YTD': 'YTD %',
    'RSI': 'RSI', 'MoneyFlow': 'MFI', 'ADX': 'ADX',
    'MACD.macd': 'MACD', 'MACD.signal': 'MACD Signal',
    'SMA20': 'SMA20', 'SMA50': 'SMA50', 'SMA200': 'SMA200',
    'High.1M': 'Yuksek 1A', 'High.3M': 'Yuksek 3A',
    'High.6M': 'Yuksek 6A', 'price_52_week_high': 'Yuksek 52H',
    'High.All': 'Yuksek ATH',
    'Low.1M': 'Dusuk 1A', 'Low.3M': 'Dusuk 3A',
    'ATRP': 'ATR %', 'Volatility.W': 'Volatilite 1H',
    'Volatility.M': 'Volatilite 1A',
    'BB.upper': 'BB Ust', 'BB.lower': 'BB Alt',
    'sector.tr': 'Sektor',
    'price_earnings_ttm': 'F/K', 'price_book_fq': 'PD/DD',
}

MACRO = {
    'BIST:XU100': 'BIST 100',
    'FX_IDC:USDTRY': 'USD/TRY',
    'FX_IDC:EURTRY': 'EUR/TRY',
    'TVC:UKOIL': 'Brent',
    'TVC:GOLD': 'Ons Altin',
}

HIST_PATH = 'data/history.csv'
HIST_KEEP_DAYS = 120


def pull_market():
    q = (Query().set_markets('turkey').select(*COLUMNS).limit(800))
    q.query['ignore_unknown_fields'] = True
    total, df = q.get_scanner_data()
    print(f"Piyasa cekildi: {len(df)} satir")
    return df


def pull_xu100():
    q = Query().set_markets('turkey').select('name').limit(150)
    q.query['symbols'] = {'symbolset': ['SYML:BIST;XU100']}
    q.query['ignore_unknown_fields'] = True
    try:
        _, df = q.get_scanner_data()
        s = set(df['name'].astype(str))
        print(f"XU100: {len(s)} sembol")
        return s
    except Exception:
        print("UYARI: XU100 cekilemedi")
        return set()


def pull_macro():
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
                rows.append({'Gosterge': isim, 'Deger': v[0],
                             'Gunluk %': v[1], 'Haftalik %': v[2],
                             'Aylik %': v[3]})
                print(f"  {isim}: {v[0]}")
            else:
                print(f"  UYARI: {isim} bos")
        except Exception as e:
            print(f"  UYARI: {isim} hata: {e}")
    print(f"Makro: {len(rows)} gosterge")
    return pd.DataFrame(rows)


def num(s):
    return pd.to_numeric(s, errors='coerce')


def compute_signals(df):
    """Uc zaman diliminde hacim rejimi + momentum + cakisma."""
    v1, v10 = num(df['Hacim 1g']), num(df['Hacim ort 10g'])
    v30, v60 = num(df['Hacim ort 30g']), num(df['Hacim ort 60g'])
    v90 = num(df['Hacim ort 90g'])
    v_long = v90.fillna(v60)          # 90g yoksa 60g
    px = num(df['Fiyat'])

    # Sabah calistirmada 'Hacim 1g' henuz olusmamis olabilir; o durumda
    # TradingView'in kendi bagil hacim kolonunu kullan (onceki kapanis bazli)
    rejim_g = (v1 / v10)
    bagil = num(df['Bagil hacim'])
    df['Rejim G'] = np.where(rejim_g < 0.4, bagil, rejim_g).round(2)
    df['Rejim H'] = (v10 / v30).round(2)
    df['Rejim A'] = (v30 / v_long).round(2)
    df['Ciro M TL'] = (v10 * px / 1e6).round(1)

    sg = (df['Rejim G'] > 1.3) & (num(df['Gunluk %']) > 0)
    sh = (df['Rejim H'] > 1.15) & (num(df['Haftalik %']) > 0)
    sa = (df['Rejim A'] > 1.10) & (num(df['Aylik %']) > 0)
    df['Sinyal G'] = sg.astype(int)
    df['Sinyal H'] = sh.astype(int)
    df['Sinyal A'] = sa.astype(int)
    df['Cakisma'] = df['Sinyal G'] + df['Sinyal H'] + df['Sinyal A']
    df['Cakisma tipi'] = (
        np.where(sg, 'G', '') + np.where(sh, 'H', '') + np.where(sa, 'A', ''))

    # Dagitim: hacim genis ama fiyat asagi
    dg = (df['Rejim G'] > 1.3) & (num(df['Gunluk %']) < 0)
    dh = (df['Rejim H'] > 1.15) & (num(df['Haftalik %']) < 0)
    da = (df['Rejim A'] > 1.10) & (num(df['Aylik %']) < 0)
    df['Dagitim'] = (dg.astype(int) + dh.astype(int) + da.astype(int))

    # Sektor goreliligi: hissenin aylik rejimi / sektor medyani
    med = df.groupby('Sektor')['Rejim A'].transform('median')
    df['Sektor gorelilik'] = (df['Rejim A'] / med).round(2)

    # 3 aylik bant konumu: 0 = dipte, 100 = zirvede
    h3, l3 = num(df['Yuksek 3A']), num(df['Dusuk 3A'])
    df['Bant konum'] = ((px - l3) / (h3 - l3) * 100).round(0)

    # SIKISMA: hacim genisliyor ama fiyat yatay (yay kuruluyor)
    hacim_genis = (df['Rejim A'] > 1.15) | (df['Rejim H'] > 1.20)
    fiyat_yatay = num(df['Aylik %']).between(-8, 12) & num(df['Haftalik %']).between(-6, 6)
    saglikli = (df['Bant konum'] > 40) & (num(df['MFI']) > 55)
    df['Sikisma'] = (hacim_genis & fiyat_yatay & saglikli).astype(int)
    rej_max = df[['Rejim A', 'Rejim H']].max(axis=1)
    hareket = num(df['Aylik %']).abs() + num(df['Haftalik %']).abs() + 2
    df['Sikisma skoru'] = np.where(df['Sikisma'] == 1,
                                   ((rej_max - 1) * 100 / hareket).round(1), np.nan)
    # Bandin dibinde hacimli yataylik = dagitim sonrasi tutunma, birikim degil
    df['Yanlis birikim'] = (hacim_genis & fiyat_yatay & (df['Bant konum'] <= 25)).astype(int)

    # SMA konumu
    p, s20, s50, s200 = px, num(df['SMA20']), num(df['SMA50']), num(df['SMA200'])
    df['SMA konum'] = (
        np.where(p > s20, '20+', '20-') + '/' +
        np.where(p > s50, '50+', '50-') + '/' +
        np.where(p > s200, '200+', '200-'))
    df['Zirveye mesafe %'] = ((p / num(df['Yuksek 3A']) - 1) * 100).round(1)
    return df


def load_history():
    if os.path.exists(HIST_PATH):
        try:
            h = pd.read_csv(HIST_PATH)
            print(f"Arsiv yuklendi: {len(h)} satir")
            return h
        except Exception:
            print("UYARI: arsiv okunamadi, sifirdan baslaniyor")
    else:
        print("Arsiv yok, ilk kayit olusturuluyor")
    return pd.DataFrame(columns=['Tarih', 'Sembol', 'Fiyat', 'Gunluk %',
                                 'Hacim 1g', 'Rejim G', 'Rejim H', 'Rejim A',
                                 'Cakisma', 'ATR %'])


def enrich_with_history(df, hist, today):
    """Arsivden turetilen metrikler: birikim yasi, ATR sikismasi,
    yon bazli hacim orani, rejim trendi."""
    if hist.empty:
        df['Birikim yasi'] = np.nan
        df['ATR degisim %'] = np.nan
        df['Yukselen/dusen hacim'] = np.nan
        df['Rejim A trend'] = np.nan
        df['Yeni giris'] = ''
        return df

    h = hist[hist['Tarih'] != today].copy()
    if h.empty:
        df['Birikim yasi'] = np.nan
        df['ATR degisim %'] = np.nan
        df['Yukselen/dusen hacim'] = np.nan
        df['Rejim A trend'] = np.nan
        df['Yeni giris'] = ''
        return df

    h = h.sort_values('Tarih')
    out = {}

    for sym, g in h.groupby('Sembol'):
        g = g.tail(60)
        # 1) Birikim yasi: kac gundur ust uste Cakisma >= 2
        yas = 0
        for c in reversed(g['Cakisma'].tolist()):
            if c >= 2:
                yas += 1
            else:
                break
        # 2) ATR degisimi (20 gun once vs bugun arsivdeki son)
        atr_ser = pd.to_numeric(g['ATR %'], errors='coerce').dropna()
        atr_chg = np.nan
        if len(atr_ser) >= 20:
            eski = atr_ser.iloc[-20]
            if eski and eski > 0:
                atr_chg = round((atr_ser.iloc[-1] / eski - 1) * 100, 1)
        # 3) Yon bazli hacim: yukselen gunlerin ort hacmi / dusen gunlerin
        gg = g.tail(20).copy()
        gg['chg'] = pd.to_numeric(gg['Gunluk %'], errors='coerce')
        gg['vol'] = pd.to_numeric(gg['Hacim 1g'], errors='coerce')
        up = gg.loc[gg['chg'] > 0, 'vol'].mean()
        dn = gg.loc[gg['chg'] < 0, 'vol'].mean()
        ud = round(up / dn, 2) if (dn and dn > 0 and not np.isnan(up)) else np.nan
        # 4) Rejim A trendi: son deger - 10 gun onceki
        ra = pd.to_numeric(g['Rejim A'], errors='coerce').dropna()
        ra_trend = round(ra.iloc[-1] - ra.iloc[-10], 2) if len(ra) >= 10 else np.nan
        # 5) Dun cakisma
        dun = g['Cakisma'].iloc[-1] if len(g) else np.nan
        out[sym] = (yas, atr_chg, ud, ra_trend, dun)

    df['Birikim yasi'] = df['Sembol'].map(lambda s: out.get(s, (np.nan,)*5)[0])
    df['ATR degisim %'] = df['Sembol'].map(lambda s: out.get(s, (np.nan,)*5)[1])
    df['Yukselen/dusen hacim'] = df['Sembol'].map(lambda s: out.get(s, (np.nan,)*5)[2])
    df['Rejim A trend'] = df['Sembol'].map(lambda s: out.get(s, (np.nan,)*5)[3])
    dun = df['Sembol'].map(lambda s: out.get(s, (np.nan,)*5)[4])
    df['Yeni giris'] = np.where((df['Cakisma'] >= 2) & (dun < 2), 'YENI', '')
    return df


def classify(df):
    """Asama siniflandirmasi."""
    def f(r):
        if r['Dagitim'] >= 2:
            return 'DAGITIM'
        if r['Yanlis birikim'] == 1:
            return 'YANLIS BIRIKIM'
        if r['Sikisma'] == 1:
            return 'SIKISMA'
        if r['Cakisma'] == 3:
            return 'TETIKLENME'
        if r['Sinyal H'] == 1 and r['Sinyal A'] == 1:
            return 'UYANIS'
        if r['Sinyal A'] == 1 and r['Cakisma'] == 1:
            return 'SESSIZ BIRIKIM'
        if r['Cakisma'] == 2:
            return 'UYANIS'
        return ''
    df['Asama'] = df.apply(f, axis=1)
    return df


def append_history(df, hist, today):
    yeni = df[['Sembol', 'Fiyat', 'Gunluk %', 'Hacim 1g', 'Rejim G',
               'Rejim H', 'Rejim A', 'Cakisma', 'ATR %']].copy()
    yeni.insert(0, 'Tarih', today)
    hist = hist[hist['Tarih'] != today] if not hist.empty else hist
    merged = pd.concat([hist, yeni], ignore_index=True)
    # eski kayitlari buda
    tarihler = sorted(merged['Tarih'].unique())
    if len(tarihler) > HIST_KEEP_DAYS:
        tut = set(tarihler[-HIST_KEEP_DAYS:])
        merged = merged[merged['Tarih'].isin(tut)]
    merged.to_csv(HIST_PATH, index=False, encoding='utf-8-sig')
    print(f"Arsiv guncellendi: {len(merged)} satir, {len(tarihler)} gun")


def main():
    today = datetime.date.today().isoformat()
    os.makedirs('data', exist_ok=True)

    df = pull_market()
    if len(df) < 300:
        print(f"HATA: {len(df)} satir, cikiliyor")
        sys.exit(1)

    xu = pull_xu100()
    df = df.rename(columns=RENAME)
    if 'ticker' in df.columns:
        df = df.drop(columns=['ticker'])
    df['XU100'] = df['Sembol'].astype(str).isin(xu)

    df = compute_signals(df)
    hist = load_history()
    df = enrich_with_history(df, hist, today)
    df = classify(df)
    df.insert(0, 'Tarih', today)

    df.to_csv('data/latest.csv', index=False, encoding='utf-8-sig')
    print(f"Kaydedildi: data/latest.csv ({len(df)} satir, {len(df.columns)} kolon)")
    append_history(df, hist, today)

    macro = pull_macro()
    if len(macro):
        macro.insert(0, 'Tarih', today)
        macro.to_csv('data/macro.csv', index=False, encoding='utf-8-sig')

    # ozet log
    print("\n--- OZET ---")
    print(f"3/3 cakisma: {(df['Cakisma']==3).sum()}")
    print(f"2/3 cakisma: {(df['Cakisma']==2).sum()}")
    print(f"Dagitim (>=2): {(df['Dagitim']>=2).sum()}")
    print(f"Sikisma: {(df['Sikisma']==1).sum()} | Yanlis birikim: {(df['Yanlis birikim']==1).sum()}")
    print(df['Asama'].value_counts().to_string())


if __name__ == '__main__':
    main()
