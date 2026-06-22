"""
Backtest ManipulationX V.6 + MACD Divergences on AUDUSD.
Signals: swing pivot sweeps + FVG zones + MACD regular divergences.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# ── Fetch AUDUSD data ─────────────────────────────────────────────────────────
print("Downloading AUDUSD data...")
raw = yf.download("AUDUSD=X", period="2y", interval="1d")
df = raw.copy()
df.columns = [c[0] for c in df.columns]
df = df.dropna()
print(f"  {len(df)} daily bars ({df.index[0].date()} to {df.index[-1].date()})")

# ─── MACD ─────────────────────────────────────────────────────────────────────
fast = 12; slow = 26; sig = 9
df["emaF"] = df["Close"].ewm(span=fast).mean()
df["emaS"] = df["Close"].ewm(span=slow).mean()
df["macd"] = df["emaF"] - df["emaS"]
df["macdSig"] = df["macd"].ewm(span=sig).mean()
df["macdHist"] = df["macd"] - df["macdSig"]

# ─── MACD pivot detection (5 left/5 right, same as Pine script) ───────────────
lbL, lbR = 5, 5
def osc_pivots(osc):
    pl = pd.Series(index=osc.index, dtype=float); pl[:] = np.nan
    ph = pd.Series(index=osc.index, dtype=float); ph[:] = np.nan
    v = osc.values
    for i in range(lbL + lbR, len(v) - lbR):
        if all(v[i] < v[i-j] for j in range(1, lbL+1)) and all(v[i] < v[i+j] for j in range(1, lbR+1)):
            pl.iloc[i] = v[i]
        if all(v[i] > v[i-j] for j in range(1, lbL+1)) and all(v[i] > v[i+j] for j in range(1, lbR+1)):
            ph.iloc[i] = v[i]
    return pl, ph

df["macdPl"], df["macdPh"] = osc_pivots(df["macd"])

# ─── MACD Regular Divergences ─────────────────────────────────────────────────
df["macdBull"] = False; df["macdBear"] = False

for i in range(lbR, len(df)):
    # --- Bullish: price lower low, MACD higher low, both < 0 ---
    if not np.isnan(df["macdPl"].iloc[i]):
        prev_idx = None
        for j in range(i-1, max(0, i-60), -1):
            if not np.isnan(df["macdPl"].iloc[j]):
                prev_idx = j; break
        if prev_idx is not None and 1 <= (i - prev_idx) <= 60:
            price_ll = df["Low"].iloc[i] < df["Low"].iloc[prev_idx]
            macd_hl = df["macd"].iloc[i] > df["macd"].iloc[prev_idx]
            below_zero = df["macd"].iloc[i] < 0
            if price_ll and macd_hl and below_zero:
                df.loc[df.index[i], "macdBull"] = True

    # --- Bearish: price higher high, MACD lower high, both > 0 ---
    if not np.isnan(df["macdPh"].iloc[i]):
        prev_idx = None
        for j in range(i-1, max(0, i-60), -1):
            if not np.isnan(df["macdPh"].iloc[j]):
                prev_idx = j; break
        if prev_idx is not None and 1 <= (i - prev_idx) <= 60:
            price_hh = df["High"].iloc[i] > df["High"].iloc[prev_idx]
            macd_lh = df["macd"].iloc[i] < df["macd"].iloc[prev_idx]
            above_zero = df["macd"].iloc[i] > 0
            if price_hh and macd_lh and above_zero:
                df.loc[df.index[i], "macdBear"] = True

print(f"  MACD Bull divs: {df['macdBull'].sum()}, Bear divs: {df['macdBear'].sum()}")

# ─── 3-bar FVG ────────────────────────────────────────────────────────────────
def detect_fvg(h, l):
    bull = pd.Series(index=h.index, dtype=float); bull[:] = np.nan
    bear = pd.Series(index=h.index, dtype=float); bear[:] = np.nan
    lo = l.values; hi = h.values
    for i in range(2, len(lo)):
        if lo[i] > hi[i-2]:
            bull.iloc[i] = lo[i]; bear.iloc[i] = hi[i-2]
        elif hi[i] < lo[i-2]:
            bear.iloc[i] = lo[i-2]; bull.iloc[i] = hi[i]
    return bull, bear

df["fvgTop"], df["fvgBot"] = detect_fvg(df["High"], df["Low"])
df["fvgBull"] = df["fvgTop"].notna() & (df["fvgTop"] > df["fvgBot"])
df["fvgBear"] = df["fvgTop"].notna() & (df["fvgTop"] < df["fvgBot"])

# ─── Pivot & DOL ──────────────────────────────────────────────────────────────
def find_pivots(h, l):
    ph = pd.Series(index=h.index, dtype=float); ph[:] = np.nan
    pl = pd.Series(index=l.index, dtype=float); pl[:] = np.nan
    hi = h.values; lo = l.values
    for i in range(2, len(hi)-2):
        if all(hi[i] > hi[i+j] for j in (-2,-1,1,2)):
            ph.iloc[i] = hi[i]
        if all(lo[i] < lo[i+j] for j in (-2,-1,1,2)):
            pl.iloc[i] = lo[i]
    return ph, pl

df["ph"], df["pl"] = find_pivots(df["High"], df["Low"])

dol_min = 0.001
last_hi=None; last_lo=None; dol_last=""
df["dolHi"]=np.nan; df["dolLo"]=np.nan
for i in range(len(df)):
    ph=df["ph"].iloc[i]; pl=df["pl"].iloc[i]
    if not np.isnan(ph) and (dol_last=="" or dol_last=="low") and (last_lo is None or ph-last_lo>=dol_min):
        df.loc[df.index[i],"dolHi"]=ph; last_hi=ph; dol_last="high"
    if not np.isnan(pl) and (dol_last=="" or dol_last=="high") and (last_hi is None or last_hi-pl>=dol_min):
        df.loc[df.index[i],"dolLo"]=pl; last_lo=pl; dol_last="low"

# ─── Sweep detection ──────────────────────────────────────────────────────────
def detect_sweeps(df, lb=10):
    sb=pd.Series(index=df.index,dtype=bool); sb[:]=False
    sr=pd.Series(index=df.index,dtype=bool); sr[:]=False
    for i in range(lb+1, len(df)):
        w=df.iloc[i-lb:i]; hh=w["High"].max(); ll=w["Low"].min()
        if df["High"].iloc[i]>hh and df["Close"].iloc[i]<hh: sr.iloc[i]=True
        if df["Low"].iloc[i]<ll and df["Close"].iloc[i]>ll: sb.iloc[i]=True
    return sb, sr

df["sBul"], df["sBer"] = detect_sweeps(df)

# ─── Entry signals ────────────────────────────────────────────────────────────
fvg_lb = 10
df["entryLong"]=False; df["entryShort"]=False
df["entryStrongL"]=False; df["entryStrongS"]=False

for i in range(1, len(df)):
    s = max(0, i-fvg_lb)
    nearB = df["fvgBull"].iloc[s:i+1].any()
    nearR = df["fvgBear"].iloc[s:i+1].any()
    if df["sBul"].iloc[i] and nearB:
        df.loc[df.index[i], "entryLong"] = True
        if df["macdBull"].iloc[i]: df.loc[df.index[i], "entryStrongL"] = True
    if df["sBer"].iloc[i] and nearR:
        df.loc[df.index[i], "entryShort"] = True
        if df["macdBear"].iloc[i]: df.loc[df.index[i], "entryStrongS"] = True

# ─── Backtest ─────────────────────────────────────────────────────────────────
trades = []
in_trade=0; entry_p=0; entry_i=0; entry_d=""
tp_pts=0.006; sl_pts=0.003
equity=[10000]; bars=df.index

for i in range(1, len(df)):
    if in_trade==0:
        if df["entryStrongL"].iloc[i] or df["entryLong"].iloc[i]:
            in_trade=1; entry_p=df["Close"].iloc[i]; entry_i=i; entry_d="long"
        elif df["entryStrongS"].iloc[i] or df["entryShort"].iloc[i]:
            in_trade=-1; entry_p=df["Close"].iloc[i]; entry_i=i; entry_d="short"
    else:
        hi=df["High"].iloc[i]; lo=df["Low"].iloc[i]; cl=df["Close"].iloc[i]
        ht=False; hs=False
        if in_trade==1:
            tp=entry_p+tp_pts; sl=entry_p-sl_pts
            if hi>=tp: ht=True
            if lo<=sl: hs=True
        else:
            tp=entry_p-tp_pts; sl=entry_p+sl_pts
            if lo<=tp: ht=True
            if hi>=sl: hs=True
        reason=None; xp=0
        if ht: reason="TP"; xp=tp
        elif hs: reason="SL"; xp=sl
        elif i-entry_i>=20: reason="timeout"; xp=cl
        if reason:
            ret = (xp/entry_p-1)*(1 if in_trade==1 else -1)*100
            trades.append({"entry_date":bars[entry_i],"exit_date":bars[i],
                           "dir":entry_d,"entry":entry_p,"exit":xp,
                           "ret":ret,"reason":reason, "strong":"strong" in entry_d})
            equity.append(equity[-1]*(1+ret/100))
            in_trade=0

# ─── Results ──────────────────────────────────────────────────────────────────
win=[t for t in trades if t["ret"]>0]
los=[t for t in trades if t["ret"]<=0]
strong=[t for t in trades if t.get("strong")]
print(f"\n--- Backtest Results ---")
print(f"Trades: {len(trades)} (strong: {len(strong)})")
print(f"Win rate: {len(win)/len(trades)*100:.1f}%")
if win and los:
    print(f"Avg win: {np.mean([t['ret'] for t in win]):.2f}%")
    print(f"Avg loss: {np.mean([t['ret'] for t in los]):.2f}%")
if strong:
    sw=[t for t in strong if t["ret"]>0]
    print(f"Strong trades: {len(strong)}, win: {len(sw)/len(strong)*100:.1f}%")
if trades:
    print(f"Total return: {(equity[-1]/equity[0]-1)*100:.1f}%")
    print(f"Final equity: ${equity[-1]:.0f}")
    print(f"Max drawdown: {(equity[0]-min(equity))/equity[0]*100:.1f}%")

# ─── Plot ─────────────────────────────────────────────────────────────────────
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12),
    gridspec_kw={"height_ratios": [3, 0.8, 1]})
fig.suptitle("ManipulationX V.6 + MACD Divergences — AUDUSD Backtest", fontsize=14, fontweight="bold")

# Price panel
ax1.plot(df.index, df["Close"], color="#1a1a2e", lw=0.8, label="AUDUSD", zorder=2)
for i in range(len(df)):
    if df["fvgBull"].iloc[i]:
        ax1.axhspan(df["fvgBot"].iloc[i], df["fvgTop"].iloc[i],
            xmin=i/len(df), xmax=(i+5)/len(df), alpha=0.12, color="#00ff88", zorder=1)
    elif df["fvgBear"].iloc[i]:
        ax1.axhspan(df["fvgBot"].iloc[i], df["fvgTop"].iloc[i],
            xmin=i/len(df), xmax=(i+5)/len(df), alpha=0.12, color="#ff4444", zorder=1)

dix=df.index[df["dolHi"].notna()]
ax1.scatter(dix, df.loc[dix,"dolHi"], marker="v", s=35, color="#9C27B0", ec="white", lw=0.3, zorder=5)
dix=df.index[df["dolLo"].notna()]
ax1.scatter(dix, df.loc[dix,"dolLo"], marker="^", s=35, color="#9C27B0", ec="white", lw=0.3, zorder=5)

ax1.scatter(df.index[df["macdBull"]], df.loc[df["macdBull"],"Low"]-0.002,
            marker=6, s=40, color="#00E676", zorder=6)
ax1.scatter(df.index[df["macdBear"]], df.loc[df["macdBear"],"High"]+0.002,
            marker=7, s=40, color="#FF5252", zorder=6)

for t in trades:
    c = "#00E676" if t["ret"]>0 else "#FF1744"
    mk = "^" if t["dir"]=="long" else "v"
    ax1.scatter(t["entry_date"], t["entry"], marker=mk, s=70, color=c, ec="white", lw=0.8, zorder=10)
    ax1.scatter(t["exit_date"], t["exit"], marker="x", s=50, color=c, lw=0.8, zorder=10)
    ax1.plot([t["entry_date"], t["exit_date"]], [t["entry"], t["exit"]],
             color=c, lw=0.5, ls="--", zorder=9)

ax1.set_ylabel("Price"); ax1.legend(loc="upper left", fontsize=7); ax1.grid(alpha=0.2)

# MACD panel
ax2.axhline(0, color="#666", lw=0.5)
ax2.plot(df.index, df["macd"], color="#2962FF", lw=1, label="MACD")
ax2.plot(df.index, df["macdSig"], color="#FF6D00", lw=0.7, label="Signal")
ax2.bar(df.index, df["macdHist"], width=1, color=np.where(df["macdHist"]>=0, "#26A69A", "#FF5252"), alpha=0.6)
ax2.scatter(df.index[df["macdBull"]], df.loc[df["macdBull"],"macd"], marker="^", s=60,
            color="#00E676", ec="white", zorder=5, label="Bull div")
ax2.scatter(df.index[df["macdBear"]], df.loc[df["macdBear"],"macd"], marker="v", s=60,
            color="#FF5252", ec="white", zorder=5, label="Bear div")
ax2.set_ylabel("MACD"); ax2.legend(loc="upper left", fontsize=7); ax2.grid(alpha=0.2)

# Equity
dates=df.index
eq=pd.Series(index=dates[:len(equity)], data=equity)
ax3.plot(eq.index, eq.values, color="#1a237e", lw=1)
ax3.fill_between(eq.index, 10000, eq.values, alpha=0.1, color="#1a237e")
ax3.axhline(10000, color="#666", lw=0.5, ls="--")
ax3.set_ylabel("Equity ($)"); ax3.set_xlabel("Date"); ax3.grid(alpha=0.2)

plt.tight_layout()
plt.savefig("D:\\Descargas\\smt_divergence\\backtest_chart.png", dpi=150)
print(f"\nChart saved: backtest_chart.png")
print("Done.")
