import streamlit as st
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ACE Wide State Scanner",
    page_icon="♠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

* { font-family: 'Syne', sans-serif; }
.stApp { background-color: #0a0a0f; }
#MainMenu, footer, header { visibility: hidden; }

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
.ace-subtitle { color: #a0c8e8; font-size: 0.75rem; letter-spacing: 0.4em; text-transform: uppercase; margin-top: 0.3rem; }
.ace-tagline  { color: #2a4060; font-size: 0.65rem; letter-spacing: 0.3em; text-transform: uppercase; margin-top: 0.2rem; }

.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.4em;
    text-transform: uppercase;
    padding: 0.6rem 1rem;
    border: 1px solid #0099ff;
    margin-bottom: 1.5rem;
    color: #00ccff;
    background: rgba(0,153,255,0.05);
    text-align: center;
    border-radius: 4px;
}

.score-10 { background: #FFD700; color: #000; padding: 2px 10px; border-radius: 3px; font-weight: 700; font-family: 'Space Mono', monospace; font-size: 0.9rem; }
.score-9  { background: #FFA500; color: #000; padding: 2px 10px; border-radius: 3px; font-weight: 700; font-family: 'Space Mono', monospace; font-size: 0.9rem; }
.score-8  { background: #00d4aa; color: #000; padding: 2px 10px; border-radius: 3px; font-weight: 700; font-family: 'Space Mono', monospace; font-size: 0.9rem; }
.score-7  { background: #4FC3F7; color: #000; padding: 2px 10px; border-radius: 3px; font-weight: 700; font-family: 'Space Mono', monospace; font-size: 0.9rem; }
.score-low { background: #1a2a3a; color: #4a6080; padding: 2px 10px; border-radius: 3px; font-family: 'Space Mono', monospace; font-size: 0.9rem; }

.elephant-card {
    background: #0d1520;
    border: 1px solid #FFD700;
    border-radius: 8px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 0 25px rgba(255,215,0,0.12);
}
.regular-card {
    background: #0d1520;
    border: 1px solid #1a2a3a;
    border-radius: 8px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
}
.regular-card:hover { border-color: #0099ff33; }

.coin-name { font-size: 1.2rem; font-weight: 700; color: #fff; font-family: 'Space Mono', monospace; }
.metric-label { font-size: 0.58rem; letter-spacing: 0.2em; text-transform: uppercase; color: #6a90b0; margin-bottom: 2px; }
.metric-value { font-size: 0.88rem; font-family: 'Space Mono', monospace; color: #b0d0f0; }
.metric-green { color: #00d4aa; }
.metric-gold  { color: #FFD700; }

.stat-box {
    background: #0d1520;
    border: 1px solid #1a2a3a;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}
.stat-number { font-size: 2rem; font-weight: 700; font-family: 'Space Mono', monospace; }
.stat-label  { font-size: 0.6rem; letter-spacing: 0.3em; text-transform: uppercase; color: #8ab0d0; margin-top: 0.2rem; }

.no-results {
    text-align: center;
    padding: 3rem;
    color: #8ab0d0;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.15em;
    border: 1px dashed #1a2a3a;
    border-radius: 8px;
    line-height: 2;
}
.timestamp { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #6a90b0; text-align: center; margin-bottom: 1.2rem; }
.elephant-label { color: #FFD700; font-size: 0.78rem; font-family: 'Space Mono', monospace; font-size: 0.7rem; letter-spacing: 0.3em; margin-bottom: 1rem; }
.regular-label  { color: #00ccff; font-family: 'Space Mono', monospace; font-size: 0.7rem; letter-spacing: 0.3em; margin-bottom: 1rem; margin-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ace-header">
    <div class="ace-logo">♠ACE</div>
    <div class="ace-subtitle">Accumulation Computation Engine</div>
</div>
""", unsafe_allow_html=True)

# ── TSX Scanner Functions ──────────────────────────────────────────────────────
def get_tsx_symbols():
    try:
        url = "https://www.tsx.com/json/company-directory/search/tsx/^*"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        data = r.json()
        excluded = ["etf","cdr","trust","fund","index","ishares","vanguard",
                    "horizons","debenture","warrant","bond","preferred","reit"]
        symbols = []
        for c in data.get("results", []):
            sym  = c.get("symbol","").strip()
            name = c.get("name","").lower()
            if not sym or "." in sym: continue
            if any(k in name for k in excluded): continue
            symbols.append(f"{sym}.TO")
        return symbols
    except:
        return ["SHOP.TO","BB.TO","LSPD.TO","NFI.TO","MRE.TO","TLRY.TO",
                "ATZ.TO","GIL.TO","DOL.TO","MRU.TO","WSP.TO","CAE.TO"]

def fetch_tsx_stock(symbol):
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist   = ticker.history(period="60d")
        if hist.empty or len(hist) < 22: return None

        today  = hist.iloc[-1]
        prev   = hist.iloc[-11:-1]
        close  = float(today["Close"])

        if close < 5: return None

        high_10   = float(prev["High"].max())
        low_10    = float(prev["Low"].min())
        range_pct = (high_10 - low_10) / high_10 if high_10 > 0 else 1

        if range_pct > 0.10 or close <= high_10: return None

        try:
            info     = ticker.info
            sector   = (info.get("sector","") or "").lower()
            industry = (info.get("industry","") or "").lower()
            excl_s   = ["basic materials","energy","utilities","real estate"]
            excl_i   = ["gold","silver","copper","mining","oil","gas","coal","uranium","etf","trust"]
            if any(s in sector   for s in excl_s): return None
            if any(s in industry for s in excl_i): return None
        except: pass

        t_open    = float(today["Open"])
        t_high    = float(today["High"])
        t_low     = float(today["Low"])
        brkout    = (close - high_10) / high_10 * 100
        day_range = t_high - t_low
        close_pos = (close - t_low) / day_range * 100 if day_range > 0 else 0

        ma20       = float(hist["Close"].iloc[-21:-1].mean())
        ma20_5ago  = float(hist["Close"].iloc[-26:-6].mean())
        ma20_slope = (ma20 - ma20_5ago) / ma20_5ago * 100

        # Only keep stocks where MA20 is declining (slope < 0%)
        # Wide Down state only — flat/rising MA20 filtered out
        if ma20_slope >= 0:
            return None

        price_to_ma20 = abs(float(hist["Close"].iloc[-2]) - ma20) / ma20 * 100

        last_20_bodies = []
        for i in range(2, 22):
            try:
                bar_open  = float(hist["Open"].iloc[-i])
                bar_close = float(hist["Close"].iloc[-i])
                last_20_bodies.append(abs(bar_close - bar_open))
            except: pass

        if len(last_20_bodies) < 10: return None

        today_body = abs(close - t_open)
        last_20_sorted = sorted(last_20_bodies)
        percentile_70  = last_20_sorted[int(len(last_20_sorted) * 0.70)]

        is_elephant = (today_body > percentile_70 and close_pos >= 75.0)

        bars_beaten     = sum(1 for b in last_20_bodies if today_body > b)
        eb_pct          = round(bars_beaten / len(last_20_bodies) * 100, 1)

        body_pct = abs(close - t_open) / close * 100

        n = 5 if range_pct<0.02 else 4 if range_pct<0.03 else 3 if range_pct<0.05 else 2 if range_pct<0.06 else 1

        if eb_pct >= 95:   e = 3
        elif eb_pct >= 85: e = 2
        elif eb_pct >= 70: e = 1
        else:              e = 0

        b = 2 if brkout >= 3 else 1 if brkout >= 1 else 0

        p = 2 if close_pos >= 90 else 1 if close_pos >= 75 else 0

        total = n + e + b + p

        return {
            "symbol":         symbol.replace(".TO",""),
            "score":          total,
            "n": n, "e": e, "b": b, "p": p,
            "elephant":       is_elephant,
            "eb_pct":         eb_pct,
            "close":          round(close, 2),
            "volume":         int(today["Volume"]),
            "body_pct":       round(body_pct, 1),
            "close_pos":      round(close_pos, 1),
            "range_pct":      round(range_pct*100, 2),
            "breakout_pct":   round(brkout, 2),
            "high_10d":       round(high_10, 2),
            "low_10d":        round(low_10, 2),
            "ma20":           round(ma20, 2),
            "ma20_slope":     round(ma20_slope, 2),
            "price_to_ma20":  round(price_to_ma20, 2),
        }
    except: return None

def run_tsx_scan():
    progress = st.progress(0, text="Fetching TSX symbol list from TMX...")
    symbols  = get_tsx_symbols()
    total    = len(symbols)
    progress.progress(10, text=f"Scanning {total} TSX stocks — this takes 3-5 minutes...")
    results  = []
    done     = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(fetch_tsx_stock, s): s for s in symbols}
        for f in as_completed(futures):
            done += 1
            if done % 60 == 0:
                pct = 10 + int(done/total*85)
                progress.progress(pct, text=f"Progress: {done}/{total} | Breakouts found: {len(results)}")
            try:
                r = f.result()
                if r: results.append(r)
            except: pass
    results.sort(key=lambda x: (-x["score"], -x["eb_pct"]))
    progress.progress(100, text="Scan complete!")
    time.sleep(0.5)
    progress.empty()
    return results

def score_badge(score):
    cls = ("score-10" if score==10 else "score-9" if score==9 else
           "score-8"  if score>=8  else "score-7"  if score>=7 else "score-low")
    return f'<span class="{cls}">{score}</span>'

def display_results(results):
    elephants = [r for r in results if r["elephant"]]
    regular   = [r for r in results if not r["elephant"]]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-number metric-gold">{len(elephants)}</div><div class="stat-label">🐘 Elephant Bars</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#0099ff">{len(regular)}</div><div class="stat-label">Regular Breakouts</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#fff">{len(results)}</div><div class="stat-label">Total Breakouts</div></div>', unsafe_allow_html=True)
    with c4:
        top = results[0]["score"] if results else 0
        st.markdown(f'<div class="stat-box"><div class="stat-number metric-gold">{top}</div><div class="stat-label">Top Score Today</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if elephants:
        st.markdown('<div class="elephant-label">🐘 ELEPHANT BARS — A+ SETUPS — CHECK LOCATION BEFORE TRADING</div>', unsafe_allow_html=True)
        for r in elephants:
            st.markdown(f"""
            <div class="elephant-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem">
                    <span class="coin-name">🐘 {r['symbol']}</span>
                    {score_badge(r['score'])}
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.8rem;margin-bottom:0.8rem">
                    <div><div class="metric-label">Price CAD</div><div class="metric-value">${r['close']:,.2f}</div></div>
                    <div><div class="metric-label">EB Strength</div><div class="metric-value metric-gold">{int(r['eb_pct'])}%</div></div>
                    <div><div class="metric-label">Close Pos</div><div class="metric-value">{r['close_pos']}%</div></div>
                    <div><div class="metric-label">Breakout</div><div class="metric-value metric-green">+{r['breakout_pct']}%</div></div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.8rem">
                    <div><div class="metric-label">MA20</div><div class="metric-value">${r['ma20']}</div></div>
                    <div><div class="metric-label">MA20 Slope</div><div class="metric-value metric-gold">{r['ma20_slope']}%</div></div>
                    <div><div class="metric-label">Volume</div><div class="metric-value">{r['volume']:,}</div></div>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#4a7a4a;font-family:Space Mono,monospace;font-size:0.75rem;text-align:center;padding:1.5rem;border:1px dashed #2a4a2a;border-radius:8px;margin-bottom:1rem">🐘 No Elephant Bars today — waiting for the A+ setup</div>', unsafe_allow_html=True)

    if regular:
        st.markdown('<div class="regular-label">◈ REGULAR BREAKOUTS — WATCH LIST ONLY</div>', unsafe_allow_html=True)
        for r in regular:
            st.markdown(f"""
            <div class="regular-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem">
                    <span class="coin-name">{r['symbol']}</span>
                    {score_badge(r['score'])}
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.8rem;margin-bottom:0.8rem">
                    <div><div class="metric-label">Price CAD</div><div class="metric-value">${r['close']:,.2f}</div></div>
                    <div><div class="metric-label">EB Strength</div><div class="metric-value">{int(r['eb_pct'])}%</div></div>
                    <div><div class="metric-label">Close Pos</div><div class="metric-value">{r['close_pos']}%</div></div>
                    <div><div class="metric-label">Breakout</div><div class="metric-value">+{r['breakout_pct']}%</div></div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.8rem">
                    <div><div class="metric-label">MA20</div><div class="metric-value">${r['ma20']}</div></div>
                    <div><div class="metric-label">MA20 Slope</div><div class="metric-value">{r['ma20_slope']}%</div></div>
                    <div><div class="metric-label">Volume</div><div class="metric-value">{r['volume']:,}</div></div>
                </div>
            </div>""", unsafe_allow_html=True)

    if not elephants and not regular:
        st.markdown("""
        <div class="no-results">
            NO BREAKOUTS FOUND TODAY<br><br>
            TSX is consolidating or no elephant bars fired<br>
            The scanner is telling you to stay on the sidelines<br><br>
            Best run after 4:00pm EST on trading days
        </div>""", unsafe_allow_html=True)

# ── Main Layout ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">TSX - WIDE STATE SCANNER - DAILY TIMEFRAME</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run = st.button("▶  RUN D1 TSX SCAN", type="primary", use_container_width=True)

if run:
    with st.spinner(""):
        results = run_tsx_scan()
        st.session_state["tsx_results"] = results
        st.session_state["tsx_time"]    = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

if "tsx_results" in st.session_state:
    st.markdown(f'<div class="timestamp">Last scan: {st.session_state["tsx_time"]}</div>', unsafe_allow_html=True)
    display_results(st.session_state["tsx_results"])
else:
    st.markdown("""
    <div class="no-results">
        CLICK RUN TSX SCAN TO START<br><br>
        Elephant Bar: body larger than 70% of last 20 bars<br>
        Best run after 4:00pm EST on trading days
    </div>""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:3rem;padding-top:1rem;border-top:1px solid #1a2a3a">
    <span style="font-family:Space Mono,monospace;font-size:0.6rem;letter-spacing:0.4em;color:#1a2a3a">
        ♠ ACE 2 RCB · RANDOM CONSOLIDATION BREAKOUT · TSX · D1 · NOT FINANCIAL ADVICE
    </span>
</div>
""", unsafe_allow_html=True)
