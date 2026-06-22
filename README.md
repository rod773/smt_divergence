# ManipulationX V.6 — SMT Divergence & FVG Indicator

TradingView Pine Script indicator for the NY Session SMT divergence strategy.

## Features

- **Fair Value Gaps** — 15m, 1h, 4h colored boxes with min gap filter, NY-only mode
- **Inverse FVGs** — 1m IFVG entry signals
- **SMT Divergence** — Compares MNQ vs MES with pivot connection lines drawn between diverging pivots
- **Liquidity Sweeps** — Detects sweeps of Asia/London session highs/lows (once per level per session)
- **Session Levels** — Asia (19:00-03:00 ET) & London (03:00-12:00 ET) highs/lows drawn as horizontal rays
- **Draws on Liquidity** — DOL markers at major swing pivots with swing size filter, NY-only mode
- **Support / Resistance** — Thin boxes at pivot swings with size filter, NY-only mode
- **Killzones** — NY session (9:30-16:00 ET) and London session backgrounds
- **Checklist** — Strategy steps overlayed on chart
- **Alerts** — SMT divergence, IFVG, bearish/bullish liquidity sweeps

## Usage

1. Open TradingView → Pine Editor
2. Paste `ManipulationX_V6.pine` contents
3. Save as "ManipulationX V.6"
4. Apply to MNQ1! chart
5. SMT defaults to MES1! — all thresholds configurable in settings
