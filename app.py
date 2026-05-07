import streamlit as st
import urllib.request
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ACE Trading System",
    page_icon="♠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

* { font-family: 'Syne', sans-serif; }
code, .mono { font-family: 'Space Mono', monospace; }

/* Dark background */
.stApp { background-color: #0a0a0f; }
section[data-testid="stSidebar"] { background-color: #0d0d14; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Hero header */
.ace-header {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1a2e 50%, #0a0a0f 100%);
    border-bottom: 1px solid #1a2a4a;
    padding: 2rem 0 1.5rem 0;
    text-align: center;
    margin-bottom: 2rem;
}
.ace-logo {
    font-family: 'Space Mono', monospace;
    font-size: 3.5rem;
    font-weight: 700;
    letter-spacing: 0.3em;
    background: linear-gradient(135deg, #00d4aa, #0099ff, #00d4aa);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s infinite;
}
@keyframes shimmer {
    0% { background-position: 0% }
    100% { background-position: 200% }
}
.ace-subtitle {
    color: #4a6080;
    font-size: 0.75rem;
    letter-spacing: 0.4em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}
.ace-tagline {
    color: #2a4060;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}

/* Section headers */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.4em;
    text-transform: uppercase;
    padding: 0.4rem 1rem;
    border-left: 3px solid;
    margin-bottom: 1.5rem;
}
.crypto-header { color: #00d4aa; border-color: #00d4aa; background: rgba(0,212,170,0.05); }
.tsx-header { color: #0099ff; border-color: #0099ff; background: rgba(0,153,255,0.05); }

/* Score badges */
.score-10 { background: #FFD700; color: #000; padding: 2px 8px; border-radius: 3px; font-weight: 700; font-family: 'Space Mono', monospace; }
.score-9  { background: #FFA500; color: #000; padding: 2px 8px; border-radius: 3px; font-weight: 700; font-family: 'Space Mono', monospace; }
.score-8  { background: #00d4aa; color: #000; padding: 2px 8px; border-radius: 3px; font-weight: 700; font-family: 'Space Mono', monospace; }
.score-7  { background: #4FC3F7; color: #000; padding: 2px 8px; border-radius: 3px; font-weight: 700; font-family: 'Space Mono', monospace; }
.score-low { background: #1a2a3a; color: #4a6080; padding: 2px 8px; border-radius: 3px; font-family: 'Space Mono', monospace; }

/* Cards */
.coin-card {
    background: #0d1520;
    border: 1px solid #1a2a3a;
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
}
.coin-card:hover { border-color: #00d4aa33; }
.coin-card-elephant {
    background: #0d1520;
    border: 1px solid #FFD700;
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 0 20px rgba(255,215,0,0.1);
}
.coin-name { font-size: 1.1rem; font-weight: 700; color: #fff; font-family: 'Space Mono', monospace; }
.coin-price { font-size: 0.85rem; color: #4a6080; font-family: 'Space Mono', monospace; }
.metric-label { font-size: 0.6rem; letter-spacing: 0.2em; text-transform: uppercase; color: #2a4060; }
.metric-value { font-size: 0.85rem; font-family: 'Space Mono', monospace; color: #8ab0d0; }
.metric-neg { color: #00d4aa; }
.metric-pos { color: #ff6b6b; }
.no-results {
    text-align: center;
    padding: 3rem;
    color: #2a4060;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.2em;
    border: 1px dashed #1a2a3a;
    border-radius: 6px;
}
.stat-box {
    background: #0d1520;
    border: 1px solid #1a2a3a;
    border-radius: 6px;
    padding: 1rem;
    text-align: center;
}
.stat-number { font-size: 1.8rem; font-weight: 700; font-family: 'Space Mono', monospace; }
.stat-label { font-size: 0.6rem; letter-spacing: 0.3em; text-transform: uppercase; color: #4a6080; margin-top: 0.2rem; }
.elephant-badge { font-size: 1.2rem; margin-right: 0.3rem; }
.vs-up { color: #00d4aa; font-family: 'Space Mono', monospace; font-size: 0.75rem; }
.vs-down { color: #ff6b6b; font-family: 'Space Mono', monospace; font-size: 0.75rem; }
.vs-new { color: #FFD700; font-family: 'Space Mono', monospace; font-size: 0.75rem; }
.timestamp { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #2a4060; text-align: center; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ace-header">
    <div class="ace-logo">♠ ACE</div>
    <div class="ace-subtitle">Accumulation Computation Engine</div>
    <div class="ace-tagline">Crypto · TSX · Phase 1 Squeeze · Velez Breakout</div>
</div>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
BASE = "https://fapi.binance.com"

# ── Crypto Scanner Functions ───────────────────────────────────────────────────
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def get_oi_change(symbol):
    try:
        url = f"{BASE}/futures/data/openInterestHist?symbol={symbol}&period=1h&limit=5"
        data = fetch(url)
        if len(data) < 2: return None
        oldest = float(data[0]["sumOpenInterest"])
        newest = float(data[-1]["sumOpenInterest"])
        if oldest == 0: return None
        return (newest - oldest) / oldest * 100
    except: return None

def score_crypto(ticker, funding, oi_pct):
    price_chg = abs(float(ticker["priceChangePercent"]))
    p = 4 if price_chg < 1 else 3 if price_chg < 3 else 2 if price_chg < 5 else 1 if price_chg < 8 else 0
    f = 3 if funding < -0.0005 else 2 if funding < -0.0002 else 1 if funding < 0 else 0
    o = 0 if oi_pct is None else 3 if oi_pct > 5 else 2 if oi_pct > 2 else 1 if oi_pct > 0 else 0
    return p + f + o, p, f, o

def run_crypto_scan():
    progress = st.progress(0, text="Fetching 24h tickers...")
    tickers = [d for d in fetch(f"{BASE}/fapi/v1/ticker/24hr") if d["symbol"].endswith("USDT")]
    progress.progress(20, text="Fetching funding rates...")
    fundings = {d["symbol"]: float(d["lastFundingRate"]) for d in fetch(f"{BASE}/fapi/v1/premiumIndex") if d["symbol"].endswith("USDT")}
    symbols = [t["symbol"] for t in tickers]
    progress.progress(30, text=f"Fetching OI history for {len(symbols)} pairs...")
    oi_map = {}
    done = 0
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(get_oi_change, s): s for s in symbols}
        for f in as_completed(futures):
            s = futures[f]
            try: oi_map[s] = f.result()
            except: oi_map[s] = None
            done += 1
            if done % 50 == 0:
                progress.progress(30 + int(done/len(symbols)*60), text=f"OI progress: {done}/{len(symbols)}")
    progress.progress(90, text="Scoring all coins...")
    results = []
    for t in tickers:
        sym = t["symbol"]
        funding = fundings.get(sym, 0.0)
        oi_pct = oi_map.get(sym)
        total, p, f, o = score_crypto(t, funding, oi_pct)
        results.append({
            "symbol": sym.replace("USDT",""),
            "score": total, "p": p, "f": f, "o": o,
            "price_chg": float(t["priceChangePercent"]),
            "funding": funding * 100,
            "oi_chg": oi_pct,
            "price": float(t["lastPrice"]),
            "volume": float(t["quoteVolume"]),
        })
    results.sort(key=lambda x: (-x["score"], -x["volume"]))
    progress.progress(100, text="Done!")
    time.sleep(0.5)
    progress.empty()
    return results

# ── TSX Scanner Functions ──────────────────────────────────────────────────────
def get_tsx_symbols():
    try:
        url = "https://www.tsx.com/json/company-directory/search/tsx/^*"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        excluded_keywords = ["etf","cdr","trust","fund","index","ishares","vanguard","horizons","debenture","warrant","bond","preferred","reit"]
        symbols = []
        for c in data.get("results", []):
            sym = c.get("symbol","").strip()
            name = c.get("name","").lower()
            if not sym or "." in sym: continue
            if any(k in name for k in excluded_keywords): continue
            symbols.append(f"{sym}.TO")
        return symbols
    except:
        return ["SHOP.TO","BB.TO","LSPD.TO","NFI.TO","MRE.TO","TLRY.TO","ATZ.TO","GIL.TO","DOL.TO","MRU.TO"]

def fetch_tsx_stock(symbol):
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="60d")
        if hist.empty or len(hist) < 12: return None
        today = hist.iloc[-1]
        prev = hist.iloc[-11:-1]
        close = float(today["Close"])
        vol_today = float(today["Volume"])
        if close < 5 or vol_today == 0: return None
        avg_vol = float(prev["Volume"].mean())
        vol_ratio = vol_today / avg_vol if avg_vol > 0 else 0
        if vol_today < 100_000 or vol_ratio < 2.0: return None
        high_10 = float(prev["High"].max())
        low_10 = float(prev["Low"].min())
        range_pct = (high_10 - low_10) / high_10 if high_10 > 0 else 1
        if range_pct > 0.10 or close <= high_10: return None
        try:
            info = ticker.info
            sector = (info.get("sector","") or "").lower()
            industry = (info.get("industry","") or "").lower()
            excl_s = ["basic materials","energy","utilities","real estate"]
            excl_i = ["gold","silver","copper","mining","oil","gas","coal","uranium","etf","trust"]
            if any(s in sector for s in excl_s): return None
            if any(s in industry for s in excl_i): return None
        except: pass
        t_open = float(today["Open"])
        t_high = float(today["High"])
        t_low  = float(today["Low"])
        brkout = (close - high_10) / high_10 * 100
        body = abs(close - t_open) / close * 100
        day_range = t_high - t_low
        close_pos = (close - t_low) / day_range * 100 if day_range > 0 else 0
        elephant = vol_ratio >= 3.0 and body >= 3.0 and close_pos >= 75.0
        n = 5 if range_pct<0.02 else 4 if range_pct<0.03 else 3 if range_pct<0.05 else 2 if range_pct<0.06 else 1
        v = 3 if vol_ratio>=5 else 2 if vol_ratio>=3 else 1
        b = 2 if brkout>=3 else 1 if brkout>=1 else 0
        e = 2 if elephant else 0
        return {
            "symbol": symbol.replace(".TO",""),
            "score": n+v+b+e, "n": n, "v": v, "b": b, "e": e,
            "elephant": elephant,
            "close": round(close,2),
            "volume": int(vol_today),
            "vol_ratio": round(vol_ratio,1),
            "body_pct": round(body,1),
            "close_pos": round(close_pos,1),
            "range_pct": round(range_pct*100,2),
            "breakout_pct": round(brkout,2),
        }
    except: return None

def run_tsx_scan():
    progress = st.progress(0, text="Fetching TSX symbol list from TMX...")
    symbols = get_tsx_symbols()
    progress.progress(10, text=f"Scanning {len(symbols)} TSX stocks (3-5 min)...")
    results = []
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(fetch_tsx_stock, s): s for s in symbols}
        for f in as_completed(futures):
            done += 1
            if done % 80 == 0:
                pct = 10 + int(done/len(symbols)*85)
                progress.progress(pct, text=f"Progress: {done}/{len(symbols)} | Found: {len(results)}")
            try:
                r = f.result()
                if r: results.append(r)
            except: pass
    results.sort(key=lambda x: (-x["score"], -x["vol_ratio"]))
    progress.progress(100, text="Done!")
    time.sleep(0.5)
    progress.empty()
    return results

# ── Display Functions ──────────────────────────────────────────────────────────
def score_badge(score):
    cls = "score-10" if score==10 else "score-9" if score==9 else "score-8" if score>=8 else "score-7" if score>=7 else "score-low"
    return f'<span class="{cls}">{score}</span>'

def display_crypto_results(results):
    high = [r for r in results if r["score"] >= 8]
    watch = [r for r in results if r["score"] == 7]
    dist = {}
    for r in results:
        dist[r["score"]] = dist.get(r["score"], 0) + 1

    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#00d4aa">{len(high)}</div><div class="stat-label">High Conviction 8+</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#4FC3F7">{len(watch)}</div><div class="stat-label">Watch List 7</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#fff">{len(results)}</div><div class="stat-label">Total Pairs Scanned</div></div>', unsafe_allow_html=True)
    with c4:
        top = results[0]["score"] if results else 0
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#FFD700">{top}</div><div class="stat-label">Top Score Today</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if high:
        st.markdown('<div style="color:#00d4aa;font-family:Space Mono,monospace;font-size:0.7rem;letter-spacing:0.3em;margin-bottom:1rem">★ HIGH CONVICTION — SCORE 8+</div>', unsafe_allow_html=True)
        for r in high:
            oi_str = f"{r['oi_chg']:+.2f}%" if r['oi_chg'] is not None else "N/A"
            fund_cls = "metric-neg" if r['funding'] < 0 else "metric-pos"
            price_cls = "metric-neg" if r['price_chg'] > 0 else "metric-pos"
            st.markdown(f"""
            <div class="coin-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                    <span class="coin-name">{r['symbol']}</span>
                    {score_badge(r['score'])}
                </div>
                <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.5rem">
                    <div><div class="metric-label">Price</div><div class="metric-value">${r['price']:,.4f}</div></div>
                    <div><div class="metric-label">24h %</div><div class="metric-value {price_cls}">{r['price_chg']:+.2f}%</div></div>
                    <div><div class="metric-label">Funding</div><div class="metric-value {fund_cls}">{r['funding']:+.4f}%</div></div>
                    <div><div class="metric-label">OI Change</div><div class="metric-value">{oi_str}</div></div>
                    <div><div class="metric-label">P·F·O</div><div class="metric-value">{r['p']}·{r['f']}·{r['o']}</div></div>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="no-results">NO HIGH CONVICTION SETUPS TODAY<br><br>Market may be in Wide Down state<br>Scanner is telling you to stay on the sidelines</div>', unsafe_allow_html=True)

    if watch:
        st.markdown('<br><div style="color:#4FC3F7;font-family:Space Mono,monospace;font-size:0.7rem;letter-spacing:0.3em;margin-bottom:1rem">◈ WATCH LIST — SCORE 7</div>', unsafe_allow_html=True)
        for r in watch:
            oi_str = f"{r['oi_chg']:+.2f}%" if r['oi_chg'] is not None else "N/A"
            fund_cls = "metric-neg" if r['funding'] < 0 else "metric-pos"
            st.markdown(f"""
            <div class="coin-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                    <span class="coin-name">{r['symbol']}</span>
                    {score_badge(r['score'])}
                </div>
                <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.5rem">
                    <div><div class="metric-label">Price</div><div class="metric-value">${r['price']:,.4f}</div></div>
                    <div><div class="metric-label">24h %</div><div class="metric-value">{r['price_chg']:+.2f}%</div></div>
                    <div><div class="metric-label">Funding</div><div class="metric-value {fund_cls}">{r['funding']:+.4f}%</div></div>
                    <div><div class="metric-label">OI Change</div><div class="metric-value">{oi_str}</div></div>
                    <div><div class="metric-label">P·F·O</div><div class="metric-value">{r['p']}·{r['f']}·{r['o']}</div></div>
                </div>
            </div>""", unsafe_allow_html=True)

def display_tsx_results(results):
    elephants = [r for r in results if r["elephant"]]
    regular = [r for r in results if not r["elephant"]]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#FFD700">{len(elephants)}</div><div class="stat-label">🐘 Elephant Bars</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#0099ff">{len(regular)}</div><div class="stat-label">Regular Breakouts</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#fff">{len(results)}</div><div class="stat-label">Total Breakouts</div></div>', unsafe_allow_html=True)
    with c4:
        top = results[0]["score"] if results else 0
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#FFD700">{top}</div><div class="stat-label">Top Score Today</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if elephants:
        st.markdown('<div style="color:#FFD700;font-family:Space Mono,monospace;font-size:0.7rem;letter-spacing:0.3em;margin-bottom:1rem">🐘 ELEPHANT BARS — HIGHEST CONVICTION</div>', unsafe_allow_html=True)
        for r in elephants:
            st.markdown(f"""
            <div class="coin-card-elephant">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                    <span class="coin-name">🐘 {r['symbol']}</span>
                    {score_badge(r['score'])}
                </div>
                <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:0.5rem">
                    <div><div class="metric-label">Price</div><div class="metric-value">${r['close']:,.2f}</div></div>
                    <div><div class="metric-label">Volume</div><div class="metric-value">{r['volume']:,}</div></div>
                    <div><div class="metric-label">Vol Surge</div><div class="metric-value metric-neg">{r['vol_ratio']}x</div></div>
                    <div><div class="metric-label">Body %</div><div class="metric-value">{r['body_pct']}%</div></div>
                    <div><div class="metric-label">Close Pos</div><div class="metric-value">{r['close_pos']}%</div></div>
                    <div><div class="metric-label">Breakout</div><div class="metric-value metric-neg">+{r['breakout_pct']}%</div></div>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#2a4060;font-family:Space Mono,monospace;font-size:0.75rem;text-align:center;padding:1rem">🐘 No Elephant Bars today</div>', unsafe_allow_html=True)

    if regular:
        st.markdown('<br><div style="color:#0099ff;font-family:Space Mono,monospace;font-size:0.7rem;letter-spacing:0.3em;margin-bottom:1rem">◈ REGULAR BREAKOUTS</div>', unsafe_allow_html=True)
        for r in regular:
            st.markdown(f"""
            <div class="coin-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                    <span class="coin-name">{r['symbol']}</span>
                    {score_badge(r['score'])}
                </div>
                <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:0.5rem">
                    <div><div class="metric-label">Price</div><div class="metric-value">${r['close']:,.2f}</div></div>
                    <div><div class="metric-label">Volume</div><div class="metric-value">{r['volume']:,}</div></div>
                    <div><div class="metric-label">Vol Surge</div><div class="metric-value">{r['vol_ratio']}x</div></div>
                    <div><div class="metric-label">Body %</div><div class="metric-value">{r['body_pct']}%</div></div>
                    <div><div class="metric-label">Close Pos</div><div class="metric-value">{r['close_pos']}%</div></div>
                    <div><div class="metric-label">Breakout</div><div class="metric-value">+{r['breakout_pct']}%</div></div>
                </div>
            </div>""", unsafe_allow_html=True)
    elif not elephants:
        st.markdown('<div class="no-results">NO BREAKOUTS FOUND TODAY<br><br>TSX is in Narrow or Wide Down state<br>Scanner is telling you to stay on the sidelines</div>', unsafe_allow_html=True)

# ── Main Layout ────────────────────────────────────────────────────────────────
col_crypto, col_tsx = st.columns(2, gap="large")

with col_crypto:
    st.markdown('<div class="section-header crypto-header">⬡ Crypto · Binance Perpetual Futures · Phase 1 Squeeze</div>', unsafe_allow_html=True)

    if st.button("▶ RUN CRYPTO SCAN", type="primary", use_container_width=True, key="crypto_btn"):
        with st.spinner(""):
            results = run_crypto_scan()
            st.session_state["crypto_results"] = results
            st.session_state["crypto_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    if "crypto_results" in st.session_state:
        st.markdown(f'<div class="timestamp">Last scan: {st.session_state["crypto_time"]}</div>', unsafe_allow_html=True)
        display_crypto_results(st.session_state["crypto_results"])
    else:
        st.markdown('<div class="no-results">CLICK RUN CRYPTO SCAN<br><br>Scans all 559 Binance USDT<br>Perpetual Futures pairs</div>', unsafe_allow_html=True)

with col_tsx:
    st.markdown('<div class="section-header tsx-header">◈ TSX · Toronto Stock Exchange · Velez Breakout</div>', unsafe_allow_html=True)

    if st.button("▶ RUN TSX SCAN", type="primary", use_container_width=True, key="tsx_btn"):
        with st.spinner(""):
            results = run_tsx_scan()
            st.session_state["tsx_results"] = results
            st.session_state["tsx_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    if "tsx_results" in st.session_state:
        st.markdown(f'<div class="timestamp">Last scan: {st.session_state["tsx_time"]}</div>', unsafe_allow_html=True)
        display_tsx_results(st.session_state["tsx_results"])
    else:
        st.markdown('<div class="no-results">CLICK RUN TSX SCAN<br><br>Scans 640+ TSX listed stocks<br>Elephant Bar detection enabled 🐘<br>Best run after 4pm EST</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:3rem;padding-top:1rem;border-top:1px solid #1a2a3a">
    <span style="font-family:Space Mono,monospace;font-size:0.6rem;letter-spacing:0.4em;color:#1a2a3a">
        ♠ ACE TRADING SYSTEM · ACCUMULATION COMPUTATION ENGINE · NOT FINANCIAL ADVICE
    </span>
</div>
""", unsafe_allow_html=True)
