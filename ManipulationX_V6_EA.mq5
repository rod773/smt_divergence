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
input int      InpSL_Points     = 200;              // Stop Loss in points (1/10 pip)
input bool     InpUseMACD       = true;             // Use MACD divergence as trend filter
input int      InpMacdFast      = 12;               // MACD fast
input int      InpMacdSlow      = 26;               // MACD slow
input int      InpMacdSignal    = 9;                // MACD signal
input int      InpSweepLookback = 20;               // Sweep lookback bars
input int      InpFvgMinPts     = 30;               // Min FVG gap in points
input double   InpDolMinDist    = 0.0010;           // Min DOL swing distance
input int      InpMagicNumber   = 202406;           // Magic number

//+------------------------------------------------------------------+
//| Global vars                                                      |
//+------------------------------------------------------------------+
datetime lastBarTime = 0;
int      trendBias   = 0;       // 1=bull, -1=bear, 0=neutral
int      macdHandle  = INVALID_HANDLE;
int      macdHandle1h= INVALID_HANDLE;
double   macdBuf[];

// DOL tracking
double   lastDolHi = 0;
double   lastDolLo = 0;
string   dolLast   = "";

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
   trade.SetExpertMagicNumber(InpMagicNumber);
   // MACD handles
   macdHandle   = iMACD(_Symbol, PERIOD_CURRENT, InpMacdFast, InpMacdSlow, InpMacdSignal, PRICE_CLOSE);
   macdHandle1h = iMACD(_Symbol, PERIOD_H1, InpMacdFast, InpMacdSlow, InpMacdSignal, PRICE_CLOSE);
   if (macdHandle == INVALID_HANDLE || macdHandle1h == INVALID_HANDLE) {
      Print("MACD handle error");
      return INIT_FAILED;
   }
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                  |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
   IndicatorRelease(macdHandle);
   IndicatorRelease(macdHandle1h);
}

//+------------------------------------------------------------------+
//| Helper: read MACD values                                         |
//+------------------------------------------------------------------+
bool GetMACD(int handle, double &macd[], double &sig[], int count=5) {
   ArraySetAsSeries(macd, true);
   ArraySetAsSeries(sig,  true);
   if (CopyBuffer(handle, 0, 0, count, macd) < count) return false;
   if (CopyBuffer(handle, 1, 0, count, sig)  < count) return false;
   return true;
}

//+------------------------------------------------------------------+
//| Helper: read price array                                         |
//+------------------------------------------------------------------+
bool GetRates(string symbol, ENUM_TIMEFRAMES tf, MqlRates &r[], int count) {
   ArraySetAsSeries(r, true);
   return CopyRates(symbol, tf, 0, count, r) >= count;
}

//+------------------------------------------------------------------+
//| 3-bar FVG detection on a timeframe                               |
//+------------------------------------------------------------------+
int CheckFVG(string symbol, ENUM_TIMEFRAMES tf) {
   MqlRates r[5];
   if (!GetRates(symbol, tf, r, 5)) return 0;
   double gap = (r[0].low > r[2].high) ? (r[0].low - r[2].high) :
                (r[0].high < r[2].low) ? (r[2].low - r[0].high) : 0;
   if (gap == 0 || gap < InpFvgMinPts * _Point) return 0;
   // 1 = bullish FVG, -1 = bearish FVG
   return (r[0].low > r[2].high) ? 1 : -1;
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
//| SMT Divergence between two symbols (on current TF)               |
//+------------------------------------------------------------------+
int CheckSMT() {
   MqlRates r1[10], r2[10];
   if (!GetRates(_Symbol, PERIOD_CURRENT, r1, 10)) return 0;
   if (!GetRates(InpCorrSymbol, PERIOD_CURRENT, r2, 10)) return 0;

   // Pivots on primary
   double ph1 = FindPivotHigh(r1, 2, 2);
   double pl1 = FindPivotLow(r1, 2, 2);
   // Pivots on correlated
   double ph2 = FindPivotHigh(r2, 2, 2);
   double pl2 = FindPivotLow(r2, 2, 2);

   static double prevPh1=0, prevPl1=0, prevPh2=0, prevPl2=0;
   int sig = 0;

   // Bullish SMT: primary higher low, correlated lower low
   if (pl1 != 0 && prevPl1 != 0 && pl2 != 0 && prevPl2 != 0) {
      if (pl1 > prevPl1 && pl2 < prevPl2) sig = 1;
   }
   // Bearish SMT: primary lower high, correlated higher high
   if (ph1 != 0 && prevPh1 != 0 && ph2 != 0 && prevPh2 != 0) {
      if (ph1 < prevPh1 && ph2 > prevPh2) sig = -1;
   }

   if (pl1 != 0) { prevPl1 = pl1; prevPl2 = (pl2 != 0) ? pl2 : prevPl2; }
   if (ph1 != 0) { prevPh1 = ph1; prevPh2 = (ph2 != 0) ? ph2 : prevPh2; }
   return sig;
}

//+------------------------------------------------------------------+
//| MACD divergence on higher timeframe (1h) for trend               |
//+------------------------------------------------------------------+
int CheckMACDTrend() {
   double macd[10], sig[10];
   if (!GetMACD(macdHandle1h, macd, sig, 10)) return 0;
   // Find MACD pivots (3,3)
   double mpl=0, mph=0;
   for (int i=3; i<=7; i++) {
      if (macd[i] < macd[i-1] && macd[i] < macd[i-2] && macd[i] < macd[i+1] && macd[i] < macd[i+2]) mpl = macd[i];
      if (macd[i] > macd[i-1] && macd[i] > macd[i-2] && macd[i] > macd[i+1] && macd[i] > macd[i+2]) mph = macd[i];
   }
   static double prevMpl=0, prevMph=0, prevMplPrice=0, prevMphPrice=0;
   int result = 0;

   MqlRates r[10];
   GetRates(_Symbol, PERIOD_H1, r, 10);

   if (mpl != 0 && prevMpl != 0) {
      // Bullish div: price lower low, MACD higher low, both < 0
      if (r[3].low < prevMplPrice && mpl > prevMpl && mpl < 0) result = 1;
      prevMplPrice = r[3].low;
   }
   if (mph != 0 && prevMph != 0) {
      // Bearish div: price higher high, MACD lower high, both > 0
      if (r[3].high > prevMphPrice && mph < prevMph && mph > 0) result = -1;
      prevMphPrice = r[3].high;
   }
   if (mpl != 0) prevMpl = mpl;
   if (mph != 0) prevMph = mph;
   return result;
}

//+------------------------------------------------------------------+
//| Liquidity sweep detection                                        |
//+------------------------------------------------------------------+
int CheckSweep() {
   MqlRates r[InpSweepLookback+2];
   if (!GetRates(_Symbol, PERIOD_CURRENT, r, InpSweepLookback+2)) return 0;
   double hiLevel = r[1].high, loLevel = r[1].low;
   for (int i=2; i<InpSweepLookback+1; i++) {
      if (r[i].high > hiLevel) hiLevel = r[i].high;
      if (r[i].low  < loLevel) loLevel = r[i].low;
   }
   // Bearish sweep: breaks above recent high, closes below
   if (r[0].high > hiLevel && r[0].close < hiLevel) return -1;
   // Bullish sweep: breaks below recent low, closes above
   if (r[0].low  < loLevel && r[0].close > loLevel) return 1;
   return 0;
}

//+------------------------------------------------------------------+
//| DOL level update                                                 |
//+------------------------------------------------------------------+
void UpdateDOL() {
   MqlRates r[10];
   if (!GetRates(_Symbol, PERIOD_CURRENT, r, 10)) return;
   double ph = FindPivotHigh(r, 4, 4);
   double pl = FindPivotLow(r, 4, 4);
   if (ph != 0 && (dolLast == "" || dolLast == "low") &&
       (lastDolLo == 0 || ph - lastDolLo >= InpDolMinDist)) {
      lastDolHi = ph; dolLast = "high";
   }
   if (pl != 0 && (dolLast == "" || dolLast == "high") &&
       (lastDolHi == 0 || lastDolHi - pl >= InpDolMinDist)) {
      lastDolLo = pl; dolLast = "low";
   }
}

//+------------------------------------------------------------------+
//| Entry signal logic                                               |
//+------------------------------------------------------------------+
int GetEntrySignal() {
   // Trend filter from MACD divergence (1h)
   if (InpUseMACD) {
      int md = CheckMACDTrend();
      if (md != 0) trendBias = md;
   }

   // Sweep detection
   int sweep = CheckSweep();
   if (sweep == 0) return 0;

   // FVG on higher timeframes
   int fvg1h = CheckFVG(_Symbol, PERIOD_H1);
   int fvg4h = CheckFVG(_Symbol, PERIOD_H4);
   bool hasFVG = (fvg1h != 0 || fvg4h != 0);

   // SMT divergence
   int smt = CheckSMT();

   // Entry decision
   // Long: bullish sweep + FVG confluence, not against trend
   if (sweep == 1 && hasFVG && trendBias != -1) {
      if (smt == 1) return 2;  // strong long (with SMT)
      return 1;                 // normal long
   }
   // Short: bearish sweep + FVG confluence, not against trend
   if (sweep == -1 && hasFVG && trendBias != 1) {
      if (smt == -1) return -2; // strong short (with SMT)
      return -1;                 // normal short
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
   // Only act on new bar
   datetime curBar = iTime(_Symbol, PERIOD_CURRENT, 0);
   if (curBar == lastBarTime) return;
   lastBarTime = curBar;

   // Update DOL tracking
   UpdateDOL();

   // Check if already in a trade
   if (HasPosition()) return;

   // Get entry signal
   int signal = GetEntrySignal();
   if (signal == 0) return;

   // Calculate SL/TP
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double sl, tp;

   if (signal > 0) {  // Long
      sl = bid - InpSL_Points * _Point;
      tp = ask + InpSL_Points * InpTPSL_Ratio * _Point;
      if (trade.Buy(InpLotSize, _Symbol, ask, sl, tp, "MX V6")) {
         Print("Long entry. Signal: ", signal, " Trend:", trendBias,
               " Sweep:1 FVG:1 SMT:", (signal==2)?"1":"0");
      }
   } else {  // Short
      sl = ask + InpSL_Points * _Point;
      tp = bid - InpSL_Points * InpTPSL_Ratio * _Point;
      if (trade.Sell(InpLotSize, _Symbol, bid, sl, tp, "MX V6")) {
         Print("Short entry. Signal: ", signal, " Trend:", trendBias,
               " Sweep:-1 FVG:1 SMT:", (signal==-2)?"-1":"0");
      }
   }
}
//+------------------------------------------------------------------+
