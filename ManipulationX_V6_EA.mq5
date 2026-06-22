//+------------------------------------------------------------------+
//|                                       ManipulationX_V6_EA.mq5    |
//|                              SMT Divergence + FVG + MACD Trend   |
//+------------------------------------------------------------------+
#property copyright "ManipulationX V.6"
#property version   "1.00"
#property description "EA that replicates ManipulationX V.6 strategy"
#property description "SMT divergence, FVG zones, liquidity sweeps, MACD trend"

#include <Trade\Trade.mqh>
CTrade trade;

//+------------------------------------------------------------------+
//| Inputs                                                           |
//+------------------------------------------------------------------+
input string   InpCorrSymbol    = "NZDUSD";        // Correlation pair for SMT
input double   InpLotSize       = 0.1;              // Lot size
input int      InpTPSL_Ratio    = 2;                // TP/SL ratio
input int      InpSL_Points     = 200;              // Stop Loss in points
input bool     InpUseMACD       = true;             // Use MACD divergence as trend filter
input int      InpMacdFast      = 12;               // MACD fast
input int      InpMacdSlow      = 26;               // MACD slow
input int      InpMacdSignal    = 9;                // MACD signal
input int      InpSweepLookback = 12;               // Sweep lookback bars (15m)
input int      InpFvgMinPts     = 30;               // Min FVG gap in points
input int      InpMagicNumber   = 202406;           // Magic number

//+------------------------------------------------------------------+
//| Global vars                                                      |
//+------------------------------------------------------------------+
datetime lastBarTime = 0;
int      trendBias   = 0;       // 1=bull, -1=bear, 0=neutral
int      macdHandle1h= INVALID_HANDLE;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
   trade.SetExpertMagicNumber(InpMagicNumber);
   macdHandle1h = iMACD(_Symbol, PERIOD_H1, InpMacdFast, InpMacdSlow, InpMacdSignal, PRICE_CLOSE);
   if (macdHandle1h == INVALID_HANDLE) {
      Print("MACD handle error"); return INIT_FAILED;
   }
   Print("ManipulationX V6 EA started on ", _Symbol, " ", EnumToString(Period()));
   Print("Correlation pair: ", InpCorrSymbol);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
   IndicatorRelease(macdHandle1h);
}

//+------------------------------------------------------------------+
//| Helper: read price array                                         |
//+------------------------------------------------------------------+
bool GetRates(string symbol, ENUM_TIMEFRAMES tf, MqlRates &r[], int count) {
   ArraySetAsSeries(r, true);
   return CopyRates(symbol, tf, 0, count, r) >= count;
}

//+------------------------------------------------------------------+
//| 3-bar FVG detection: scan completed bars on a timeframe          |
//| Returns 1 if bullish FVG found in last N bars, -1 if bearish     |
//+------------------------------------------------------------------+
int CheckFVG(string symbol, ENUM_TIMEFRAMES tf, int scanBars=15) {
   MqlRates r[];
   int need = scanBars + 2;
   ArrayResize(r, need);
   if (!GetRates(symbol, tf, r, need)) return 0;
   // Scan from index 1 (latest completed bar) down to scanBars-2
   for (int i = 1; i <= scanBars - 2; i++) {
      if (i + 2 >= ArraySize(r)) break;
      double gapBull = r[i].low - r[i+2].high;
      double gapBear = r[i+2].low - r[i].high;
      if (gapBull >= InpFvgMinPts * _Point) return 1;
      if (gapBear >= InpFvgMinPts * _Point) return -1;
   }
   return 0;
}

//+------------------------------------------------------------------+
//| Swing pivot detection                                            |
//+------------------------------------------------------------------+
double FindPivotHigh(MqlRates &r[], int left, int right) {
   int i = left;
   if (i + right >= ArraySize(r)) return 0;
   for (int j = 1; j <= left;  j++) if (r[i].high <= r[i-j].high) return 0;
   for (int j = 1; j <= right; j++) if (r[i].high <= r[i+j].high) return 0;
   return r[i].high;
}
double FindPivotLow(MqlRates &r[], int left, int right) {
   int i = left;
   if (i + right >= ArraySize(r)) return 0;
   for (int j = 1; j <= left;  j++) if (r[i].low >= r[i-j].low) return 0;
   for (int j = 1; j <= right; j++) if (r[i].low >= r[i+j].low) return 0;
   return r[i].low;
}

//+------------------------------------------------------------------+
//| SMT Divergence between primary and correlated pair               |
//+------------------------------------------------------------------+
int CheckSMT() {
   MqlRates r1[10], r2[10];
   if (!GetRates(_Symbol, PERIOD_CURRENT, r1, 10)) return 0;
   if (!GetRates(InpCorrSymbol, PERIOD_CURRENT, r2, 10)) return 0;
   double ph1 = FindPivotHigh(r1, 2, 2);
   double pl1 = FindPivotLow(r1, 2, 2);
   double ph2 = FindPivotHigh(r2, 2, 2);
   double pl2 = FindPivotLow(r2, 2, 2);
   static double pph1=0, ppl1=0, pph2=0, ppl2=0;
   int sig = 0;
   if (pl1 != 0 && ppl1 != 0 && pl2 != 0 && ppl2 != 0) {
      if (pl1 > ppl1 && pl2 < ppl2) sig = 1;
   }
   if (ph1 != 0 && pph1 != 0 && ph2 != 0 && pph2 != 0) {
      if (ph1 < pph1 && ph2 > pph2) sig = -1;
   }
   if (pl1 != 0) { ppl1 = pl1; ppl2 = (pl2 != 0) ? pl2 : ppl2; }
   if (ph1 != 0) { pph1 = ph1; pph2 = (ph2 != 0) ? ph2 : pph2; }
   return sig;
}

//+------------------------------------------------------------------+
//| MACD divergence on 1h for trend                                  |
//+------------------------------------------------------------------+
int CheckMACDTrend() {
   double macd[10];
   ArraySetAsSeries(macd, true);
   if (CopyBuffer(macdHandle1h, 0, 0, 10, macd) < 10) return 0;
   double mpl=0, mph=0;
   for (int i=3; i<=7; i++) {
      if (macd[i] < macd[i-1] && macd[i] < macd[i-2] && macd[i] < macd[i+1] && macd[i] < macd[i+2]) mpl = macd[i];
      if (macd[i] > macd[i-1] && macd[i] > macd[i-2] && macd[i] > macd[i+1] && macd[i] > macd[i+2]) mph = macd[i];
   }
   static double pmpl=0, pmph=0, pmplPr=0, pmphPr=0;
   int result = 0;
   MqlRates r[10];
   GetRates(_Symbol, PERIOD_H1, r, 10);
   if (mpl != 0 && pmpl != 0) {
      if (r[3].low < pmplPr && mpl > pmpl && mpl < 0) result = 1;
      pmplPr = r[3].low;
   }
   if (mph != 0 && pmph != 0) {
      if (r[3].high > pmphPr && mph < pmph && mph > 0) result = -1;
      pmphPr = r[3].high;
   }
   if (mpl != 0) pmpl = mpl;
   if (mph != 0) pmph = mph;
   return result;
}

//+------------------------------------------------------------------+
//| Liquidity sweep on LAST COMPLETED bar                            |
//| Checks if bar[1] swept above recent high or below recent low     |
//+------------------------------------------------------------------+
int CheckSweep() {
   MqlRates r[];
   int total = InpSweepLookback + 2;
   ArrayResize(r, total);
   if (!GetRates(_Symbol, PERIOD_CURRENT, r, total)) return 0;
   // Range for comparison: bars 2..(total-1)
   double hiLevel = r[2].high;
   double loLevel = r[2].low;
   for (int i=3; i<total; i++) {
      if (r[i].high > hiLevel) hiLevel = r[i].high;
      if (r[i].low  < loLevel) loLevel = r[i].low;
   }
   // Check LAST COMPLETED bar (index 1) for sweep
   // Bearish: broke above range high, closed back inside
   if (r[1].high > hiLevel && r[1].close < hiLevel) return -1;
   // Bullish: broke below range low, closed back inside
   if (r[1].low  < loLevel && r[1].close > loLevel) return 1;
   return 0;
}

//+------------------------------------------------------------------+
//| Entry signal logic                                               |
//+------------------------------------------------------------------+
int GetEntrySignal() {
   if (InpUseMACD) {
      int md = CheckMACDTrend();
      if (md != 0) trendBias = md;
   }
   int sweep = CheckSweep();
   if (sweep == 0) return 0;
   // FVG formed in last 15 bars on 1h or last 10 bars on 4h
   bool hasFVG = (CheckFVG(_Symbol, PERIOD_H1, 15) != 0) ||
                 (CheckFVG(_Symbol, PERIOD_H4, 10) != 0);
   int smt = CheckSMT();
   if (sweep == 1 && hasFVG && trendBias != -1) {
      return (smt == 1) ? 2 : 1;
   }
   if (sweep == -1 && hasFVG && trendBias != 1) {
      return (smt == -1) ? -2 : -1;
   }
   // Log near-misses
   if (sweep != 0) {
      PrintFormat("Sweep %d | FVG %d | SMT %d | Trend %d", sweep, hasFVG, smt, trendBias);
   }
   return 0;
}

//+------------------------------------------------------------------+
//| Check for open positions                                         |
//+------------------------------------------------------------------+
bool HasPosition() {
   for (int i=PositionsTotal()-1; i>=0; i--) {
      if (PositionSelectByTicket(PositionGetTicket(i))) {
         if (PositionGetInteger(POSITION_MAGIC) == InpMagicNumber) return true;
      }
   }
   return false;
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
   datetime curBar = iTime(_Symbol, PERIOD_CURRENT, 0);
   if (curBar == lastBarTime) return;
   lastBarTime = curBar;
   if (HasPosition()) return;
   int signal = GetEntrySignal();
   if (signal == 0) return;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double sl, tp;
   if (signal > 0) {
      sl = bid - InpSL_Points * _Point;
      tp = ask + InpSL_Points * InpTPSL_Ratio * _Point;
      if (trade.Buy(InpLotSize, _Symbol, ask, sl, tp, "MX V6"))
         Print("LONG entry signal=", signal);
   } else {
      sl = ask + InpSL_Points * _Point;
      tp = bid - InpSL_Points * InpTPSL_Ratio * _Point;
      if (trade.Sell(InpLotSize, _Symbol, bid, sl, tp, "MX V6"))
         Print("SHORT entry signal=", signal);
   }
}
//+------------------------------------------------------------------+
