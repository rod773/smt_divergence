# ManipulationX V.6 — SMT Divergence & FVG Indicator

TradingView Pine Script indicator replicating the "ManipulationX V.6" strategy from the video.

## Features

- **Fair Value Gaps** — 15m, 1h, 4h with colored boxes (green bullish, red bearish)
- **Inverse FVGs** — 1m IFVG entry signals with size filtering
- **SMT Divergence** — Compares NQ vs ES for bullish/bearish divergences
- **Draws on Liquidity** — EQH/EQL and swing DOL markers
- **Killzones** — NY session (9:30-16:00 ET) and London session backgrounds
- **Reversals & Continuations** — V-shape reversal and continuation tags
- **Checklist Overlay** — Strategy steps on chart
- **Alerts** — For SMT divergence and IFVG signals

## Usage

1. Open TradingView → Pine Editor
2. Paste `ManipulationX_V6.pine` contents
3. Save as "ManipulationX V.6"
4. Apply to NQ1! chart
5. SMT defaults to ES1! — configurable in settings
