"""
Backtest ManipulationX V.6 strategy on AUDUSD (daily data).
Simulates: FVG zones, swing pivots (DOL/SR), liquidity sweeps, and entry signals.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from datetime import datetime, timedelta

# ── Fetch AUDUSD data ──────────────────────────────────────────────────────────
print("Downloading AUDUSD data...")
raw = yf.download("AUDUSD=X", period="2y", interval="1d")
df = raw.copy()
df.columns = [c[0] for c in df.columns]  # flatten MultiIndex
df = df.dropna()
print(f"  {len(df)} daily bars ({df.index[0].date()} to {df.index[-1].date()})")

# ─── Helper: detect 3-bar FVG ─────────────────────────────────────────────────
def detect_fvg(h, l):
    bull = pd.Series(index=h.index, dtype=float)
    bear = pd.Series(index=h.index, dtype=float)
    bull[:] = np.nan; bear[:] = np.nan
    lo = l.values; hi = h.values
    for i in range(2, len(lo)):
        if lo[i] > hi[i-2]:
            bull.iloc[i] = lo[i]       # top of gap
            bear.iloc[i] = hi[i-2]     # bottom of gap  (reusing bear series for bottom)
        elif hi[i] < lo[i-2]:
            bear.iloc[i] = lo[i-2]     # top of gap
            bull.iloc[i] = hi[i]       # bottom of gap  (reusing bull series for bottom)
    return bull, bear

df["fvgTop"], df["fvgBot"] = detect_fvg(df["High"], df["Low"])
df["fvgBull"] = df["fvgTop"].notna() & (df["fvgTop"] > df["fvgBot"])
df["fvgBear"] = df["fvgTop"].notna() & (df["fvgTop"] < df["fvgBot"])

# ─── Pivot detection (2 left + 2 right) ───────────────────────────────────────
def find_pivots(h, l):
    ph = pd.Series(index=h.index, dtype=float); ph[:] = np.nan
    pl = pd.Series(index=l.index, dtype=float); pl[:] = np.nan
    hi = h.values; lo = l.values
    for i in range(2, len(hi) - 2):
        if hi[i] > hi[i-1] and hi[i] > hi[i-2] and hi[i] > hi[i+1] and hi[i] > hi[i+2]:
            ph.iloc[i] = hi[i]
        if lo[i] < lo[i-1] and lo[i] < lo[i-2] and lo[i] < lo[i+1] and lo[i] < lo[i+2]:
            pl.iloc[i] = lo[i]
    return ph, pl

df["ph"], df["pl"] = find_pivots(df["High"], df["Low"])

# ─── DOL (alternating pivots with min swing) ──────────────────────────────────
dol_min = 0.001   # ~10 pips on AUDUSD
last_hi = None; last_lo = None; dol_last = ""
df["dolHi"] = np.nan; df["dolLo"] = np.nan

for i in range(len(df)):
    ph = df["ph"].iloc[i]; pl = df["pl"].iloc[i]
    if not np.isnan(ph) and (dol_last == "" or dol_last == "low") and (last_lo is None or ph - last_lo >= dol_min):
        df.loc[df.index[i], "dolHi"] = ph
        last_hi = ph; dol_last = "high"
    if not np.isnan(pl) and (dol_last == "" or dol_last == "high") and (last_hi is None or last_hi - pl >= dol_min):
        df.loc[df.index[i], "dolLo"] = pl
        last_lo = pl; dol_last = "low"

# ─── S/R pivots (3,3) ─────────────────────────────────────────────────────────
def sr_pivots(h, l):
    sr_h = pd.Series(index=h.index, dtype=float); sr_h[:] = np.nan
    sr_l = pd.Series(index=l.index, dtype=float); sr_l[:] = np.nan
    hi = h.values; lo = l.values
    for i in range(3, len(hi) - 3):
        if all(hi[i] > hi[i-j] for j in range(1,4)) and all(hi[i] > hi[i+j] for j in range(1,4)):
            sr_h.iloc[i] = hi[i]
        if all(lo[i] < lo[i-j] for j in range(1,4)) and all(lo[i] < lo[i+j] for j in range(1,4)):
            sr_l.iloc[i] = lo[i]
    return sr_h, sr_l

df["srHi"], df["srLo"] = sr_pivots(df["High"], df["Low"])

# ─── Sweep detection ──────────────────────────────────────────────────────────
def detect_sweeps(df, lookback=10):
    sweep_bull = pd.Series(index=df.index, dtype=bool); sweep_bull[:] = False
    sweep_bear = pd.Series(index=df.index, dtype=bool); sweep_bear[:] = False
    for i in range(lookback + 1, len(df)):
        window = df.iloc[i - lookback : i]
        hi_level = window["High"].max()
        lo_level = window["Low"].min()
        close = df["Close"].iloc[i]
        high = df["High"].iloc[i]
        low = df["Low"].iloc[i]
        # Bearish sweep: breaks above recent high, closes below
        if high > hi_level and close < hi_level:
            sweep_bear.iloc[i] = True
        # Bullish sweep: breaks below recent low, closes above
        if low < lo_level and close > lo_level:
            sweep_bull.iloc[i] = True
    return sweep_bull, sweep_bear

df["sweepBul"], df["sweepBer"] = detect_sweeps(df, lookback=10)

# ─── Entry signals ────────────────────────────────────────────────────────────
# Bullish: bullish sweep + near a bullish FVG (within 10 periods)
# Bearish: bearish sweep + near a bearish FVG (within 10 periods)
df["entryLong"] = False; df["entryShort"] = False
fvg_lookback = 10

for i in range(1, len(df)):
    start = max(0, i - fvg_lookback)
    near_bull_fvg = df["fvgBull"].iloc[start:i+1].any()
    near_bear_fvg = df["fvgBear"].iloc[start:i+1].any()
    if df["sweepBul"].iloc[i] and near_bull_fvg:
        df.loc[df.index[i], "entryLong"] = True
    if df["sweepBer"].iloc[i] and near_bear_fvg:
        df.loc[df.index[i], "entryShort"] = True

# ─── Backtest ─────────────────────────────────────────────────────────────────
trades = []
in_trade = 0
entry_price = 0; entry_idx = 0; entry_dir = ""
tp_pts = 0.006  # ~60 pips
sl_pts = 0.003  # ~30 pips
equity = [10000]
bars = df.index

for i in range(1, len(df)):
    if in_trade == 0:
        if df["entryLong"].iloc[i]:
            in_trade = 1
            entry_price = df["Close"].iloc[i]
            entry_idx = i
            entry_dir = "long"
        elif df["entryShort"].iloc[i]:
            in_trade = -1
            entry_price = df["Close"].iloc[i]
            entry_idx = i
            entry_dir = "short"
    else:
        high = df["High"].iloc[i]
        low = df["Low"].iloc[i]
        close = df["Close"].iloc[i]
        hit_tp = False; hit_sl = False
        if in_trade == 1:   # long
            tp = entry_price + tp_pts
            sl = entry_price - sl_pts
            if high >= tp: hit_tp = True
            if low <= sl: hit_sl = True
        else:               # short
            tp = entry_price - tp_pts
            sl = entry_price + sl_pts
            if low <= tp: hit_tp = True
            if high >= sl: hit_sl = True

        exit_reason = None
        if hit_tp:
            exit_price = tp
            exit_reason = "TP"
        elif hit_sl:
            exit_price = sl
            exit_reason = "SL"
        elif i - entry_idx >= 20:   # max 20 bars
            exit_price = close
            exit_reason = "timeout"

        if exit_reason:
            ret = (exit_price / entry_price - 1) * (1 if in_trade == 1 else -1) * 100
            trades.append({
                "entry_date": bars[entry_idx], "exit_date": bars[i],
                "dir": entry_dir, "entry": entry_price, "exit": exit_price,
                "ret": ret, "reason": exit_reason
            })
            equity.append(equity[-1] * (1 + ret / 100))
            in_trade = 0
            entry_price = 0

# ─── Print results ────────────────────────────────────────────────────────────
win = [t for t in trades if t["ret"] > 0]
loss = [t for t in trades if t["ret"] <= 0]
print(f"\n--- Backtest Results ---")
print(f"Trades: {len(trades)}")
print(f"Win rate: {len(win)/len(trades)*100:.1f}%" if trades else "N/A")
if win:
    print(f"Avg win: {np.mean([t['ret'] for t in win]):.2f}%")
if loss:
    print(f"Avg loss: {np.mean([t['ret'] for t in loss]):.2f}%")
if trades:
    print(f"Total return: {(equity[-1]/equity[0]-1)*100:.1f}%")
    print(f"Final equity: ${equity[-1]:.0f}")

# ─── Plot ──────────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={"height_ratios": [3, 1]})
fig.suptitle("ManipulationX V.6 — AUDUSD Backtest", fontsize=15, fontweight="bold")

# Price + indicator elements
ax1.plot(df.index, df["Close"], color="#1a1a2e", linewidth=0.8, label="AUDUSD", zorder=2)

# FVG zones
for i in range(len(df)):
    if df["fvgBull"].iloc[i]:
        ax1.axhspan(df["fvgBot"].iloc[i], df["fvgTop"].iloc[i],
                     xmin=i/len(df), xmax=(i+5)/len(df),
                     alpha=0.15, color="#00ff88", zorder=1)
    elif df["fvgBear"].iloc[i]:
        ax1.axhspan(df["fvgBot"].iloc[i], df["fvgTop"].iloc[i],
                     xmin=i/len(df), xmax=(i+5)/len(df),
                     alpha=0.15, color="#ff4444", zorder=1)

# Pivot markers (DOL)
dol_idx = df.index[df["dolHi"].notna()]
ax1.scatter(dol_idx, df.loc[dol_idx, "dolHi"], marker="v", s=40,
            color="#9C27B0", edgecolors="white", linewidths=0.5, zorder=5, label="DOL High")
dol_idx = df.index[df["dolLo"].notna()]
ax1.scatter(dol_idx, df.loc[dol_idx, "dolLo"], marker="^", s=40,
            color="#9C27B0", edgecolors="white", linewidths=0.5, zorder=5, label="DOL Low")

# S/R lines
for i in range(len(df)):
    if not np.isnan(df["srHi"].iloc[i]):
        ax1.axhline(y=df["srHi"].iloc[i], color="#FFD600", alpha=0.15, linewidth=0.8)
    if not np.isnan(df["srLo"].iloc[i]):
        ax1.axhline(y=df["srLo"].iloc[i], color="#FFD600", alpha=0.15, linewidth=0.8)

# Sweep labels
swp_b = df.index[df["sweepBul"]]
swp_s = df.index[df["sweepBer"]]
ax1.scatter(swp_b, df.loc[swp_b, "Low"] - 0.001, marker=6, s=30, color="#69F0AE", zorder=6)
ax1.scatter(swp_s, df.loc[swp_s, "High"] + 0.001, marker=7, s=30, color="#FF5252", zorder=6)
for idx in swp_b[:5]:
    ax1.annotate(" SWEEP", (idx, df.loc[idx, "Low"] - 0.001), fontsize=6, color="#69F0AE")
for idx in swp_s[:5]:
    ax1.annotate(" SWEEP", (idx, df.loc[idx, "High"] + 0.002), fontsize=6, color="#FF5252")

# Trade markers
for t in trades:
    color = "#00E676" if t["ret"] > 0 else "#FF1744"
    marker = "^" if t["dir"] == "long" else "v"
    ax1.scatter(t["entry_date"], t["entry"], marker=marker, s=80,
                color=color, edgecolors="white", linewidths=1, zorder=10)
    ax1.scatter(t["exit_date"], t["exit"], marker="x", s=60,
                color=color, linewidths=1, zorder=10)
    ax1.plot([t["entry_date"], t["exit_date"]], [t["entry"], t["exit"]],
             color=color, linewidth=0.6, linestyle="--", zorder=9)

ax1.set_ylabel("Price")
ax1.legend(loc="upper left", fontsize=7, ncol=2)
ax1.grid(alpha=0.2)

# Equity curve
dates = df.index
eq_series = pd.Series(index=dates[:len(equity)], data=equity)
ax2.plot(eq_series.index, eq_series.values, color="#1a237e", linewidth=1)
ax2.fill_between(eq_series.index, 10000, eq_series.values, alpha=0.1, color="#1a237e")
ax2.set_ylabel("Equity ($)")
ax2.set_xlabel("Date")
ax2.grid(alpha=0.2)

plt.tight_layout()
plt.savefig("D:\\Descargas\\smt_divergence\\backtest_chart.png", dpi=150)
print(f"\nChart saved: backtest_chart.png")
# plt.show()  # uncomment to display interactively
print("Done.")
