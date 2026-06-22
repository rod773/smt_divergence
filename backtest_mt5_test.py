"""
MetaTrader 5 Backtest — ManipulationX V.6 + MACD Divergences
Uses tick data from MT5 for realistic backtesting.

Requirements:
  - MetaTrader 5 terminal running
  - MetaTrader5 Python package installed
  - Symbol available in MT5 (AUDUSD, EURUSD, etc.)

Usage:
  python backtest_mt5.py
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
from pytz import timezone as tzfunc
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION — Edit these as needed
# ═══════════════════════════════════════════════════════════════════
SYMBOL        = "AUDUSD"
TIMEFRAMES    = ["M1", "M15", "H1"]        # Base, FVG, trend
BACKTEST_DAYS = 60                          # Days of history to fetch
USE_TICKS     = False                        # True=tick-level (slow), False=M1 bars (fast)

# Strategy params (matching MQ5 EA)
LOT_SIZE      = 0.1
TP_SL_RATIO   = 2
SL_POINTS     = 200
SWEEP_LOOKBACK = 12     # bars on current TF
FVG_MIN_PTS   = 30      # minimum FVG gap in points
DOL_MIN_PTS   = 50      # minimum DOL swing in points
MAGIC         = 202406
USE_NY_FILTER = True    # Only enter during NY session

# Session times (Madrid timezone - matching Pine script)
NY_START      = 15       # NY session start hour (15:00 Madrid)
NY_END        = 22       # NY session end hour (22:00 Madrid)
LON_START     = 9        # London session start hour
LON_END       = 17       # London session end hour

# MACD params
MACD_FAST     = 12
MACD_SLOW     = 26
MACD_SIG      = 9

# ═══════════════════════════════════════════════════════════════════
# MT5 Connection & Data
# ═══════════════════════════════════════════════════════════════════
def mt5_connect():
    if not mt5.initialize():
        raise RuntimeError(f"MT5 init failed: {mt5.last_error()}")
    print(f"MT5 version: {mt5.version()}")

def get_tick_data(symbol, days):
    """Download tick data for the specified period."""
    now = datetime.now()
    from_date = now - timedelta(days=days)
    # Get ticks in chunks (MT5 max ~2M per call)
    all_ticks = []
    chunk_start = from_date
    while chunk_start < now:
        chunk_end = min(chunk_start + timedelta(days=7), now)
        ticks = mt5.copy_ticks_range(symbol, chunk_start, chunk_end,
                                      mt5.COPY_TICKS_ALL)
        if ticks is None or len(ticks) == 0:
            chunk_start = chunk_end
            continue
        df = pd.DataFrame(ticks)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        all_ticks.append(df)
        chunk_start = chunk_end
        print(f"  Downloaded {len(df):,} ticks {chunk_start.date()}..{chunk_end.date()}")
    if not all_ticks:
        raise ValueError(f"No tick data for {symbol}")
    ticks_df = pd.concat(all_ticks).sort_values("time").reset_index(drop=True)
    print(f"  Total ticks: {len(ticks_df):,}")
    return ticks_df

def get_rates(symbol, tf, days):
    """Download OHLC rates for a timeframe."""
    now = datetime.now()
    from_date = now - timedelta(days=days)
    rates = mt5.copy_rates_range(symbol, tf_map[tf], from_date, now)
    if rates is None or len(rates) == 0:
        raise ValueError(f"No {tf} data for {symbol}")
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

def ticks_to_m1(ticks_df):
    """Aggregate tick data into M1 OHLCV bars."""
    ticks = ticks_df.copy()
    ticks["time"] = ticks["time"].dt.floor("min")
    agg_ops = {
        "Open": ("bid", "first"),
        "High": ("bid", "max"),
        "Low": ("bid", "min"),
        "Close": ("bid", "last"),
        "TickVolume": ("bid", "count")
    }
    if "spread" in ticks.columns:
        agg_ops["Spread"] = ("spread", "mean")
    agg = ticks.groupby("time").agg(**agg_ops).reset_index()
    return agg

tf_map = {
    "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15, "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1
}

# ═══════════════════════════════════════════════════════════════════
# Strategy Logic
# ═══════════════════════════════════════════════════════════════════
POINT = None  # set after getting first bar

def detect_fvg(h, l, min_gap):
    """3-bar FVG detection (same as Pine Script / MQ5)."""
    bull = pd.Series(index=h.index, dtype=float)
    bull[:] = np.nan
    bear = pd.Series(index=h.index, dtype=float)
    bear[:] = np.nan
    lo = l.values; hi = h.values
    for i in range(2, len(lo)):
        gapB = lo[i] - hi[i-2]
        gapR = lo[i-2] - hi[i]
        if gapB >= min_gap:
            bull.iloc[i] = lo[i]; bear.iloc[i] = hi[i-2]
        elif gapR >= min_gap:
            bear.iloc[i] = lo[i-2]; bull.iloc[i] = hi[i]
    return bull, bear

def osc_pivots(osc, lbL=5, lbR=5):
    """Find oscillator pivots (MACD)."""
    pl = pd.Series(index=osc.index, dtype=float); pl[:] = np.nan
    ph = pd.Series(index=osc.index, dtype=float); ph[:] = np.nan
    v = osc.values
    for i in range(lbL + lbR, len(v) - lbR):
        if all(v[i] < v[i-j] for j in range(1, lbL+1)) and all(v[i] < v[i+j] for j in range(1, lbR+1)):
            pl.iloc[i] = v[i]
        if all(v[i] > v[i-j] for j in range(1, lbL+1)) and all(v[i] > v[i+j] for j in range(1, lbR+1)):
            ph.iloc[i] = v[i]
    return pl, ph

def find_swing_pivots(h, l, left=2, right=2):
    """Swing high/low detection (same as MQ5 FindPivotHigh/Low)."""
    ph = pd.Series(index=h.index, dtype=float); ph[:] = np.nan
    pl = pd.Series(index=l.index, dtype=float); pl[:] = np.nan
    hi = h.values; lo = l.values
    for i in range(left, len(hi) - right):
        if all(hi[i] > hi[i+j] for j in range(-left, right+1) if j != 0):
            ph.iloc[i] = hi[i]
        if all(lo[i] < lo[i+j] for j in range(-left, right+1) if j != 0):
            pl.iloc[i] = lo[i]
    return ph, pl

def detect_sweeps(df, high_col="High", low_col="Low", close_col="Close", lb=10):
    """Liquidity sweep detection (same as MQ5 CheckSweep)."""
    sb = pd.Series(index=df.index, dtype=bool); sb[:] = False
    sr = pd.Series(index=df.index, dtype=bool); sr[:] = False
    for i in range(lb+1, len(df)):
        w = df.iloc[i-lb:i]
        hh = w[high_col].max()
        ll = w[low_col].min()
        # Bearish: high > range high, close < range high
        if df[high_col].iloc[i] > hh and df[close_col].iloc[i] < hh:
            sr.iloc[i] = True
        # Bullish: low < range low, close > range low
        if df[low_col].iloc[i] < ll and df[close_col].iloc[i] > ll:
            sb.iloc[i] = True
    return sb, sr

def compute_macd_divergence(df, fast=12, slow=26, sig=9):
    """Compute MACD and detect regular divergences."""
    df["emaF"] = df["Close"].ewm(span=fast).mean()
    df["emaS"] = df["Close"].ewm(span=slow).mean()
    df["macd"] = df["emaF"] - df["emaS"]
    df["macdSig"] = df["macd"].ewm(span=sig).mean()
    df["macdHist"] = df["macd"] - df["macdSig"]

    df["macdPl"], df["macdPh"] = osc_pivots(df["macd"])
    df["macdBull"] = False; df["macdBear"] = False

    lbR = 5
    for i in range(lbR, len(df)):
        if not np.isnan(df["macdPl"].iloc[i]):
            prev_idx = None
            for j in range(i-1, max(0, i-60), -1):
                if not np.isnan(df["macdPl"].iloc[j]):
                    prev_idx = j; break
            if prev_idx is not None and 1 <= (i - prev_idx) <= 60:
                if (df["Low"].iloc[i] < df["Low"].iloc[prev_idx] and
                    df["macd"].iloc[i] > df["macd"].iloc[prev_idx] and
                    df["macd"].iloc[i] < 0):
                    df.loc[df.index[i], "macdBull"] = True

        if not np.isnan(df["macdPh"].iloc[i]):
            prev_idx = None
            for j in range(i-1, max(0, i-60), -1):
                if not np.isnan(df["macdPh"].iloc[j]):
                    prev_idx = j; break
            if prev_idx is not None and 1 <= (i - prev_idx) <= 60:
                if (df["High"].iloc[i] > df["High"].iloc[prev_idx] and
                    df["macd"].iloc[i] < df["macd"].iloc[prev_idx] and
                    df["macd"].iloc[i] > 0):
                    df.loc[df.index[i], "macdBear"] = True

    return df

def trend_from_macd(df):
    """Persistent trend bias from MACD divergence (matches MQ5 CheckMACDTrend)."""
    trend = pd.Series(index=df.index, dtype=int)
    trend[:] = 0
    last = 0
    for i in range(len(df)):
        if df["macdBull"].iloc[i]:
            last = 1
        elif df["macdBear"].iloc[i]:
            last = -1
        trend.iloc[i] = last
    return trend

# ═══════════════════════════════════════════════════════════════════
# Backtest Engine
# ═══════════════════════════════════════════════════════════════════
def in_ny_session(t, tz='Europe/Madrid'):
    """Check if time is within NY session (configured hours)."""
    tz_obj = tzfunc(tz)
    local_t = t.tz_localize('UTC').tz_convert(tz_obj)
    return NY_START <= local_t.hour < NY_END

def detect_ifvg(df):
    """iFVG detection: (prev bar bearish close below prev low, current closes above prev high = bullish)."""
    bull = pd.Series(index=df.index, dtype=bool); bull[:] = False
    bear = pd.Series(index=df.index, dtype=bool); bear[:] = False
    for i in range(2, len(df)):
        m_op = df["Open"].iloc[i-1]
        m_cl = df["Close"].iloc[i-1]
        m_hi1 = df["High"].iloc[i-2]
        m_lo1 = df["Low"].iloc[i-2]
        if m_cl < m_op and m_cl < m_lo1 and df["Close"].iloc[i] > m_hi1:
            bull.iloc[i] = True
        if m_cl > m_op and m_cl > m_hi1 and df["Close"].iloc[i] < m_lo1:
            bear.iloc[i] = True
    return bull, bear

def detect_dol_levels(df, min_gap, left=4, right=4):
    """DOL swing high/low detection with minimum gap filter."""
    ph = pd.Series(index=df.index, dtype=float); ph[:] = np.nan
    pl = pd.Series(index=df.index, dtype=float); pl[:] = np.nan
    hi = df["High"].values; lo = df["Low"].values
    last_hi = None
    last_lo = None
    for i in range(left, len(hi) - right):
        if all(hi[i] > hi[i+j] for j in range(-left, right+1) if j != 0):
            if last_lo is None or hi[i] - last_lo >= min_gap:
                ph.iloc[i] = hi[i]
                last_hi = hi[i]
        if all(lo[i] < lo[i+j] for j in range(-left, right+1) if j != 0):
            if last_hi is None or last_hi - lo[i] >= min_gap:
                pl.iloc[i] = lo[i]
                last_lo = lo[i]
    return ph, pl

def run_backtest(df_m1, df_m15, df_h1, point_size, tick_data=None):
    """
    Run the ManipulationX V.6 backtest.
    Uses M1 as base timeframe for entries, M15 for sweeps, H1 for MACD trend.
    """
    global POINT
    POINT = point_size

    min_gap = FVG_MIN_PTS * POINT
    sl_pts = SL_POINTS * POINT
    tp_pts = sl_pts * TP_SL_RATIO

    # --- Compute indicators ---
    # M15: FVG, sweeps
    df_m15 = df_m15.copy()
    df_m15["fvgTop"], df_m15["fvgBot"] = detect_fvg(df_m15["High"], df_m15["Low"], min_gap)
    df_m15["fvgBull"] = df_m15["fvgTop"].notna() & (df_m15["fvgTop"] > df_m15["fvgBot"])
    df_m15["fvgBear"] = df_m15["fvgTop"].notna() & (df_m15["fvgTop"] < df_m15["fvgBot"])
    df_m15["sBul"], df_m15["sBer"] = detect_sweeps(df_m15, lb=SWEEP_LOOKBACK)

    # H1: MACD divergence trend
    df_h1 = df_h1.copy()
    df_h1 = compute_macd_divergence(df_h1, MACD_FAST, MACD_SLOW, MACD_SIG)
    h1_trend = trend_from_macd(df_h1)

    def get_h1_trend(t):
        """Get H1 trend at a given time."""
        idx = h1_trend.index.searchsorted(t)
        if idx >= len(h1_trend):
            idx = len(h1_trend) - 1
        if idx > 0:
            idx -= 1  # use previous completed bar
        return h1_trend.iloc[idx]

    def nearest_prev(df, t, col):
        """Get value from last completed bar before time t."""
        idx = df.index.searchsorted(t)
        if idx >= len(df):
            idx = len(df) - 1
        if idx > 0:
            idx -= 1
        return df[col].iloc[idx]

    fvg_lookback = pd.Timedelta(minutes=15 * 10)  # last 10 M15 bars

    # Detect iFVG on M1 for entry triggers
    df_m1["ifvgBull"], df_m1["ifvgBear"] = detect_ifvg(df_m1)

    # Detect DOL on M15 for levels
    dol_min = DOL_MIN_PTS * POINT if DOL_MIN_PTS else min_gap * 2
    df_m15["dolHi"], df_m15["dolLo"] = detect_dol_levels(df_m15, dol_min)

    # --- Main loop on M1 ---
    trades = []
    in_trade = 0    # 1=long, -1=short, 0=none
    entry_price = 0.0
    entry_time = None
    entry_dir = ""
    equity = [10000.0]

    for i in range(2, len(df_m1)):
        t = df_m1.index[i]
        o = df_m1["Open"].iloc[i]
        hi = df_m1["High"].iloc[i]
        lo = df_m1["Low"].iloc[i]
        cl = df_m1["Close"].iloc[i]
        ifvg_bull = df_m1["ifvgBull"].iloc[i]
        ifvg_bear = df_m1["ifvgBear"].iloc[i]
        ny_session = in_ny_session(t)

        if in_trade == 0:
            sweep_b = nearest_prev(df_m15, t, "sBul")
            sweep_r = nearest_prev(df_m15, t, "sBer")
            # trend_bias removed (no MACD)

            m15_idx = df_m15.index.searchsorted(t)
            fvg_near_b = False
            fvg_near_r = False
            for j in range(max(0, m15_idx-10), max(0, m15_idx)):
                if df_m15["fvgBull"].iloc[j]:
                    fvg_near_b = True
                if df_m15["fvgBear"].iloc[j]:
                    fvg_near_r = True

            # Entry: iFVG triggered within NY session after sweep+FVG setup
            if ifvg_bull and ny_session and fvg_near_b :
                in_trade = 1
                entry_price = cl
                entry_time = t
                entry_dir = "long"
            elif ifvg_bear and ny_session and fvg_near_r :
                in_trade = -1
                entry_price = cl
                entry_time = t
                entry_dir = "short"
        else:
            # Manage position: TP / SL / timeout
            sl = entry_price - sl_pts if in_trade == 1 else entry_price + sl_pts
            tp = entry_price + tp_pts if in_trade == 1 else entry_price - tp_pts
            reason = None
            exit_price = 0.0

            if in_trade == 1:
                if hi >= tp:
                    reason = "TP"; exit_price = tp
                elif lo <= sl:
                    reason = "SL"; exit_price = sl
            else:
                if lo <= tp:
                    reason = "TP"; exit_price = tp
                elif hi >= sl:
                    reason = "SL"; exit_price = sl

            if reason is None and (t - entry_time) >= timedelta(hours=4):
                reason = "timeout"; exit_price = cl

            if reason:
                ret = (exit_price / entry_price - 1) * (1 if in_trade == 1 else -1) * 100
                trades.append({
                    "entry_date": entry_time,
                    "exit_date": t,
                    "dir": entry_dir,
                    "entry": entry_price,
                    "exit": exit_price,
                    "ret": ret,
                    "reason": reason
                })
                equity.append(equity[-1] * (1 + ret / 100))
                in_trade = 0

    # Handle still-open position at end
    if in_trade != 0:
        sl = entry_price - sl_pts if in_trade == 1 else entry_price + sl_pts
        ret = (sl / entry_price - 1) * (1 if in_trade == 1 else -1) * 100
        trades.append({
            "entry_date": entry_time,
            "exit_date": df_m1.index[-1],
            "dir": entry_dir,
            "entry": entry_price,
            "exit": sl,
            "ret": ret,
            "reason": "end"
        })
        equity.append(equity[-1] * (1 + ret / 100))

    return trades, equity, df_m1, df_m15, df_h1


# ═══════════════════════════════════════════════════════════════════
# Results & Plotting
# ═══════════════════════════════════════════════════════════════════
def print_results(trades, equity):
    win = [t for t in trades if t["ret"] > 0]
    los = [t for t in trades if t["ret"] <= 0]
    print(f"\n{'='*50}")
    print(f"   Backtest Results — {SYMBOL}")
    print(f"{'='*50}")
    print(f"  Trades:       {len(trades)}")
    print(f"  Win rate:     {len(win)/len(trades)*100:.1f}%" if trades else "  Win rate:     N/A")
    if win:
        print(f"  Avg win:      {np.mean([t['ret'] for t in win]):.2f}%")
    if los:
        print(f"  Avg loss:     {np.mean([t['ret'] for t in los]):.2f}%")
    if trades:
        total_ret = (equity[-1] / equity[0] - 1) * 100
        peak = np.maximum.accumulate(equity)
        dd = (equity - peak) / peak * 100
        print(f"  Total return: {total_ret:.1f}%")
        print(f"  Final equity: ${equity[-1]:.0f}")
        print(f"  Max DD:       {dd.min():.1f}%")
        print(f"  Sharpe (est): {np.mean([t['ret'] for t in trades]) / np.std([t['ret'] for t in trades]) * np.sqrt(365):.2f}")
    print(f"{'='*50}\n")

def plot_results(trades, equity, df_m1, df_m15, df_h1, save_path=None):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12),
        gridspec_kw={"height_ratios": [3, 0.8, 1]})
    fig.suptitle(f"ManipulationX V.6 — {SYMBOL} MT5 Backtest (Tick Data)", fontsize=14, fontweight="bold")

    # Price
    ax1.plot(df_m1.index, df_m1["Close"], color="#1a1a2e", lw=0.5, label=SYMBOL, zorder=2)

    # Session boxes (NY: 15:00-22:00, London: 09:00-17:00 Madrid)
    tz_obj = tzfunc('Europe/Madrid')
    dates = df_m1.index.normalize().unique()
    for d in dates:
        for start_h, end_h, color, alpha in [
            (NY_START, NY_END, '#9C27B0', 0.04),
            (LON_START, LON_END, '#2196F3', 0.03)
        ]:
            start_t = d + timedelta(hours=start_h)
            end_t = d + timedelta(hours=end_h)
            ax1.axvspan(start_t, end_t, alpha=alpha, color=color, zorder=0)

    # FVG bands on M15
    for i in range(len(df_m15)):
        if df_m15["fvgBull"].iloc[i]:
            ax1.axhspan(df_m15["fvgBot"].iloc[i], df_m15["fvgTop"].iloc[i],
                alpha=0.1, color="#00ff88", zorder=1)
        elif df_m15["fvgBear"].iloc[i]:
            ax1.axhspan(df_m15["fvgBot"].iloc[i], df_m15["fvgTop"].iloc[i],
                alpha=0.1, color="#ff4444", zorder=1)

    # Trades
    for t in trades:
        c = "#00E676" if t["ret"] > 0 else "#FF1744"
        mk = "^" if t["dir"] == "long" else "v"
        ax1.scatter(t["entry_date"], t["entry"], marker=mk, s=70, color=c, ec="white", lw=0.8, zorder=10)
        ax1.scatter(t["exit_date"], t["exit"], marker="x", s=50, color=c, lw=0.8, zorder=10)
        ax1.plot([t["entry_date"], t["exit_date"]], [t["entry"], t["exit"]],
                 color=c, lw=0.5, ls="--", zorder=9)

    ax1.set_ylabel("Price"); ax1.legend(loc="upper left", fontsize=7); ax1.grid(alpha=0.2)

    # MACD (from H1)
    ax2.axhline(0, color="#666", lw=0.5)
    ax2.plot(df_h1.index, df_h1["macd"], color="#2962FF", lw=1, label="MACD")
    ax2.plot(df_h1.index, df_h1["macdSig"], color="#FF6D00", lw=0.7, label="Signal")
    ax2.bar(df_h1.index, df_h1["macdHist"], width=1,
            color=np.where(df_h1["macdHist"]>=0, "#26A69A", "#FF5252"), alpha=0.6)
    bull_idx = df_h1.index[df_h1["macdBull"]]
    bear_idx = df_h1.index[df_h1["macdBear"]]
    ax2.scatter(bull_idx, df_h1.loc[bull_idx, "macd"], marker="^", s=60,
                color="#00E676", ec="white", zorder=5, label="Bull div")
    ax2.scatter(bear_idx, df_h1.loc[bear_idx, "macd"], marker="v", s=60,
                color="#FF5252", ec="white", zorder=5, label="Bear div")
    ax2.set_ylabel("MACD (H1)"); ax2.legend(loc="upper left", fontsize=7); ax2.grid(alpha=0.2)

    # Equity curve
    eq = pd.Series(index=range(len(equity)), data=equity)
    ax3.plot(eq.index, eq.values, color="#1a237e", lw=1)
    ax3.fill_between(eq.index, equity[0], eq.values, alpha=0.1, color="#1a237e")
    ax3.axhline(equity[0], color="#666", lw=0.5, ls="--")
    ax3.set_ylabel("Equity ($)"); ax3.set_xlabel("Trade #"); ax3.grid(alpha=0.2)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Chart saved: {save_path}")
    plt.show()


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"Connecting to MT5...")
    mt5_connect()

    print(f"\nDownloading {SYMBOL} data ({BACKTEST_DAYS} days)...")

    if USE_TICKS:
        print("  Mode: Tick-level (aggregated to M1)")
        ticks = get_tick_data(SYMBOL, BACKTEST_DAYS)
        df_m1 = ticks_to_m1(ticks)
    else:
        print("  Mode: M1 bars (from MT5)")
        df_m1 = get_rates(SYMBOL, "M1", BACKTEST_DAYS)

    # Get point size
    symbol_info = mt5.symbol_info(SYMBOL)
    point_size = symbol_info.point if symbol_info else 0.00001

    print(f"  Point size: {point_size}")
    print(f"  M1 bars: {len(df_m1)}")

    # Get M15 and H1 data
    print(f"\nDownloading M15 & H1 data...")
    df_m15 = get_rates(SYMBOL, "M15", BACKTEST_DAYS)
    df_h1  = get_rates(SYMBOL, "H1", BACKTEST_DAYS)
    print(f"  M15 bars: {len(df_m15)}")
    print(f"  H1 bars:  {len(df_h1)}")

    # Set time index
    # Standardize column names to uppercase (matching backtest.py convention)
    col_map = {"open": "Open", "high": "High", "low": "Low", "close": "Close",
               "tick_volume": "TickVolume", "real_volume": "RealVolume"}
    for df in [df_m1, df_m15, df_h1]:
        df.set_index("time", inplace=True)
        df.rename(columns=col_map, inplace=True)

    # Align start to M1
    start = max(df_m1.index.min(), df_m15.index.min(), df_h1.index.min())
    end = min(df_m1.index.max(), df_m15.index.max(), df_h1.index.max())
    for df in [df_m1, df_m15, df_h1]:
        df.drop(df.index[df.index < start], inplace=True)
        df.drop(df.index[df.index > end], inplace=True)
    print(f"\nAligned range: {start.date()} to {end.date()}")

    # Run backtest
    print(f"\nRunning backtest...")
    trades, equity, df_m1, df_m15, df_h1 = run_backtest(df_m1, df_m15, df_h1, point_size)

    # Results
    print_results(trades, equity)

    # Plot
    save_path = "D:\\VIBE_CODE\\smt_divergence\\backtest_mt5_chart.png"
    plot_results(trades, equity, df_m1, df_m15, df_h1, save_path=save_path)

    # Shutdown MT5
    mt5.shutdown()
    print("\nDone.")
