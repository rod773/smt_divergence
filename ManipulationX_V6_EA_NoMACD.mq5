//+------------------------------------------------------------------+
//|                                ManipulationX_V6_EA_NoMACD.mq5    |
//|                         Pure replication of Pine Script logic    |
//+------------------------------------------------------------------+
#property copyright "ManipulationX V.6"
#property version   "1.00"
#property description "Pure EA from ManipulationX V.6 Pine Script (no MACD)"
#property description "FVG zones, iFVG triggers, SMT divergence, sweeps, DOL/SR"

#include <Trade\Trade.mqh>
CTrade trade;

//+------------------------------------------------------------------+
//| Inputs                                                           |
//+------------------------------------------------------------------+
input string   InpCorrSymbol   = "NZDUSD";        // SMT correlation pair
input double   InpLotSize      = 0.1;              // Lot size
input int      InpTPSL_Ratio   = 2;                // TP/SL ratio
input int      InpSL_Points    = 200;              // Stop Loss in points
input int      InpFvgMinPts    = 30;               // Min FVG gap (points)
input int      InpSweepPts     = 20;               // Sweep threshold (points)
input int      InpMagicNumber  = 202406;           // Magic number

//+------------------------------------------------------------------+
//| Structures                                                       |
//+------------------------------------------------------------------+
struct FvgZone {
   double   hi;
   double   lo;
   int      dir;       // 1 bull, -1 bear
   datetime formedAt;
};
FvgZone fvgList[100];
int fvgCount = 0;

//+------------------------------------------------------------------+
//| Globals                                                          |
//+------------------------------------------------------------------+
datetime lastBarTime = 0;
double   lastNqLo = 0, lastEsLo = 0;
double   lastNqHi = 0, lastEsHi = 0;
int      lastNqLoBar = 0, lastEsLoBar = 0;
int      lastNqHiBar = 0, lastEsHiBar = 0;
int      smtBias = 0;     // 1 bull, -1 bear, 0 none

// DOL tracking
double   lastDolHi = 0, lastDolLo = 0;
string   dolLast = "";

// Session level tracking (Asia 19:00-03:00 ET, London 03:00-12:00 ET)
int      asiaDate = 0, lonDate = 0;
double   asiaHi = 0, asiaLo = 0;
double   lonHi  = 0, lonLo  = 0;
bool     asiaHiHit = false, asiaLoHit = false;
bool     lonHiHit  = false, lonLoHit  = false;
bool     asiaLevelSet = false, lonLevelSet = false;

//+------------------------------------------------------------------+
//| Helper: read rates                                               |
//+------------------------------------------------------------------+
bool GetRates(string symbol, ENUM_TIMEFRAMES tf, MqlRates &r[], int count) {
   ArraySetAsSeries(r, true);
   return CopyRates(symbol, tf, 0, count, r) >= count;
}

//+------------------------------------------------------------------+
//| 3-bar FVG: store new FVG zones                                   |
//+------------------------------------------------------------------+
void ScanFVG(string symbol, ENUM_TIMEFRAMES tf, int scanBars) {
   MqlRates r[];
   int need = scanBars + 2;
   ArrayResize(r, need);
   if (!GetRates(symbol, tf, r, need)) return;
   for (int i = 1; i <= scanBars - 2; i++) {
      if (i + 2 >= ArraySize(r)) break;
      double gapBull = r[i].low - r[i+2].high;
      double gapBear = r[i+2].low - r[i].high;
      int dir = 0;
      if (gapBull >= InpFvgMinPts * _Point) dir = 1;
      else if (gapBear >= InpFvgMinPts * _Point) dir = -1;
      if (dir != 0) {
         // Avoid duplicates: same level already stored recently
         bool dup = false;
         for (int j = 0; j < fvgCount && !dup; j++) {
            if (MathAbs(fvgList[j].hi - r[i].high) < 10 * _Point &&
                MathAbs(fvgList[j].lo - r[i].low) < 10 * _Point)
               dup = true;
         }
         if (!dup && fvgCount < 100) {
            fvgList[fvgCount].hi = (dir == 1) ? r[i].low : r[i].high;
            fvgList[fvgCount].lo = (dir == 1) ? r[i+2].high : r[i+2].low;
            fvgList[fvgCount].dir = dir;
            fvgList[fvgCount].formedAt = TimeCurrent();
            fvgCount++;
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Check if price is near an active FVG zone                        |
//+------------------------------------------------------------------+
int NearFVG(double price) {
   int res = 0;
   for (int i = 0; i < fvgCount; i++) {
      double zoneHi = fvgList[i].hi;
      double zoneLo = fvgList[i].lo;
      double dist = 5 * _Point; // within 5 pips
      if (price >= zoneLo - dist && price <= zoneHi + dist) {
         if (fvgList[i].dir == 1) res = 1;   // near bullish FVG
         else res = -1;
      }
   }
   return res;
}

//+------------------------------------------------------------------+
//| iFVG: check last N 1m bars for trap signals                      |
//+------------------------------------------------------------------+
int CheckIFVG() {
   MqlRates r[3];
   if (!GetRates(_Symbol, PERIOD_M1, r, 3)) return 0;
   // bIFVG: 1m close < 1m open AND 1m close < prev 1m low AND current close > prev 1m high
   bool bIFVG = (r[0].close < r[0].open) && (r[0].close < r[1].low) && (r[0].close > r[1].high);
   // Actually the Pine says: close > mHi1 (current chart close > prev 1m high)
   // r[0] is the last completed 1m bar, r[2] is 2 bars ago
   // Let me re-check: bIFVG = mCl < mOp and mCl < mLo1 and close > mHi1
   // mCl = close of "1" timeframe bar, mOp = open, mLo1 = low[1], mHi1 = high[1]
   bIFVG = (r[0].close < r[0].open) && (r[0].close < r[1].low) && (r[0].close > r[1].high);
   bool sIFVG = (r[0].close > r[0].open) && (r[0].close > r[1].high) && (r[0].close < r[1].low);
   if (bIFVG) return 1;
   if (sIFVG) return -1;
   return 0;
}

//+------------------------------------------------------------------+
//| SMT Divergence                                                   |
//+------------------------------------------------------------------+
int CheckSMT() {
   MqlRates r1[10], r2[10];
   if (!GetRates(_Symbol, PERIOD_CURRENT, r1, 10)) return 0;
   if (!GetRates(InpCorrSymbol, PERIOD_CURRENT, r2, 10)) return 0;
   double nqLo = 0, nqHi = 0, esLo = 0, esHi = 0;
   for (int i = 2; i <= 6; i++) {
      if (r1[i].low  <= r1[i-1].low && r1[i].low  <= r1[i-2].low && r1[i].low  <= r1[i+1].low  && r1[i].low  <= r1[i+2].low) nqLo = r1[i].low;
      if (r1[i].high >= r1[i-1].high && r1[i].high >= r1[i-2].high && r1[i].high >= r1[i+1].high && r1[i].high >= r1[i+2].high) nqHi = r1[i].high;
      if (r2[i].low  <= r2[i-1].low && r2[i].low  <= r2[i-2].low && r2[i].low  <= r2[i+1].low  && r2[i].low  <= r2[i+2].low) esLo = r2[i].low;
      if (r2[i].high >= r2[i-1].high && r2[i].high >= r2[i-2].high && r2[i].high >= r2[i+1].high && r2[i].high >= r2[i+2].high) esHi = r2[i].high;
   }
   int sig = 0;
   if (nqLo != 0 && lastNqLo != 0 && esLo != 0 && lastEsLo != 0) {
      if (nqLo > lastNqLo && esLo < lastEsLo) sig = 1;
   }
   if (nqHi != 0 && lastNqHi != 0 && esHi != 0 && lastEsHi != 0) {
      if (nqHi < lastNqHi && esHi > lastEsHi) sig = -1;
   }
   if (nqLo != 0) { lastNqLo = nqLo; lastEsLo = (esLo != 0) ? esLo : lastEsLo; }
   if (nqHi != 0) { lastNqHi = nqHi; lastEsHi = (esHi != 0) ? esHi : lastEsHi; }
   return sig;
}

//+------------------------------------------------------------------+
//| Session update                                                   |
//+------------------------------------------------------------------+
void UpdateSessions() {
   MqlDateTime dt;
   TimeCurrent(dt);
   int todayNum = dt.year * 10000 + dt.mon * 100 + dt.day;
   // Asia: 19:00-03:00 ET ≈ 00:00-08:00 UTC
   int utcHour = dt.hour;
   bool inAsia = (utcHour >= 0 && utcHour < 8);
   bool inLon  = (utcHour >= 8 && utcHour < 17);

   if (inAsia && asiaDate != todayNum) {
      asiaDate = todayNum;
      asiaHi = 0; asiaLo = 99999;
      asiaHiHit = false; asiaLoHit = false;
      asiaLevelSet = false;
      MqlRates r[1];
      if (GetRates(_Symbol, PERIOD_CURRENT, r, 1)) {
         asiaHi = r[0].high; asiaLo = r[0].low;
      }
   }
   if (inAsia && asiaHi != 0) {
      MqlRates r[1];
      if (GetRates(_Symbol, PERIOD_CURRENT, r, 1)) {
         if (r[0].high > asiaHi) asiaHi = r[0].high;
         if (r[0].low  < asiaLo) asiaLo = r[0].low;
      }
   }
   if (!inAsia && asiaHi != 0 && !asiaLevelSet) {
      asiaLevelSet = true; // level finalized when session ends
   }

   if (inLon && lonDate != todayNum) {
      lonDate = todayNum;
      lonHi = 0; lonLo = 99999;
      lonHiHit = false; lonLoHit = false;
      lonLevelSet = false;
      MqlRates r[1];
      if (GetRates(_Symbol, PERIOD_CURRENT, r, 1)) {
         lonHi = r[0].high; lonLo = r[0].low;
      }
   }
   if (inLon && lonHi != 0) {
      MqlRates r[1];
      if (GetRates(_Symbol, PERIOD_CURRENT, r, 1)) {
         if (r[0].high > lonHi) lonHi = r[0].high;
         if (r[0].low  < lonLo) lonLo = r[0].low;
      }
   }
   if (!inLon && lonHi != 0 && !lonLevelSet) {
      lonLevelSet = true;
   }
}

//+------------------------------------------------------------------+
//| Sweep detection on session levels                                |
//+------------------------------------------------------------------+
int CheckSessionSweep() {
   MqlRates r[1];
   if (!GetRates(_Symbol, PERIOD_CURRENT, r, 1)) return 0;
   double swp = InpSweepPts * _Point;
   // Asia sweeps
   if (asiaLevelSet && asiaHi != 0 && !asiaHiHit && r[0].high > asiaHi + swp && r[0].close < asiaHi) {
      asiaHiHit = true; return -1;
   }
   if (asiaLevelSet && asiaLo != 0 && !asiaLoHit && r[0].low < asiaLo - swp && r[0].close > asiaLo) {
      asiaLoHit = true; return 1;
   }
   // London sweeps
   if (lonLevelSet && lonHi != 0 && !lonHiHit && r[0].high > lonHi + swp && r[0].close < lonHi) {
      lonHiHit = true; return -1;
   }
   if (lonLevelSet && lonLo != 0 && !lonLoHit && r[0].low < lonLo - swp && r[0].close > lonLo) {
      lonLoHit = true; return 1;
   }
   return 0;
}

//+------------------------------------------------------------------+
//| DOL update                                                       |
//+------------------------------------------------------------------+
void UpdateDOL() {
   MqlRates r[10];
   if (!GetRates(_Symbol, PERIOD_CURRENT, r, 10)) return;
   double ph = 0, pl = 0;
   for (int i = 4; i <= 6; i++) {
      if (r[i].high >= r[i-1].high && r[i].high >= r[i-2].high && r[i].high >= r[i-3].high && r[i].high >= r[i-4].high &&
          r[i].high >= r[i+1].high && r[i].high >= r[i+2].high && r[i].high >= r[i+3].high && r[i].high >= r[i+4].high)
         ph = r[i].high;
      if (r[i].low  <= r[i-1].low  && r[i].low  <= r[i-2].low  && r[i].low  <= r[i-3].low  && r[i].low  <= r[i-4].low  &&
          r[i].low  <= r[i+1].low  && r[i].low  <= r[i+2].low  && r[i].low  <= r[i+3].low  && r[i].low  <= r[i+4].low)
         pl = r[i].low;
   }
   if (ph != 0 && (dolLast == "" || dolLast == "low") &&
       (lastDolLo == 0 || ph - lastDolLo >= 16 * _Point)) {
      lastDolHi = ph; dolLast = "high";
   }
   if (pl != 0 && (dolLast == "" || dolLast == "high") &&
       (lastDolHi == 0 || lastDolHi - pl >= 16 * _Point)) {
      lastDolLo = pl; dolLast = "low";
   }
}

//+------------------------------------------------------------------+
//| Main entry logic                                                 |
//| Entry: sweep near FVG zone, or IFVG near FVG zone                |
//+------------------------------------------------------------------+
int GetEntrySignal() {
   // 1. Scan for new FVG zones (on each call, keep list fresh)
   ScanFVG(_Symbol, PERIOD_M15, 10);
   ScanFVG(_Symbol, PERIOD_H1, 12);
   ScanFVG(_Symbol, PERIOD_H4, 8);
   // Prune old zones (>24h)
   int kept = 0;
   for (int i = 0; i < fvgCount; i++) {
      if (TimeCurrent() - fvgList[i].formedAt < 86400) // 24h
         fvgList[kept++] = fvgList[i];
   }
   fvgCount = kept;

   // 2. SMT bias
   int smt = CheckSMT();
   if (smt != 0) smtBias = smt;

   // 3. Check IFVG
   int ifvg = CheckIFVG();
   if (ifvg != 0) {
      MqlRates r[1];
      GetRates(_Symbol, PERIOD_CURRENT, r, 1);
      double price = r[0].close;
      int nearFvg = NearFVG(price);
      // IFVG + FVG zone confluence
      if (ifvg == 1 && nearFvg != -1) {
         if (smtBias == -1) return 1; // long but careful with bearish SMT
         return 2; // strong long
      }
      if (ifvg == -1 && nearFvg != 1) {
         if (smtBias == 1) return -1;
         return -2;
      }
   }

   // 4. Check session sweep
   int sweep = CheckSessionSweep();
   if (sweep != 0) {
      MqlRates r[1];
      GetRates(_Symbol, PERIOD_CURRENT, r, 1);
      int nearFvg = NearFVG(r[0].close);
      if (sweep == 1 && nearFvg != -1) return 3;  // sweep long
      if (sweep == -1 && nearFvg != 1) return -3; // sweep short
   }

   return 0;
}

//+------------------------------------------------------------------+
//| Position check                                                   |
//+------------------------------------------------------------------+
bool HasPosition() {
   for (int i = PositionsTotal() - 1; i >= 0; i--) {
      if (PositionSelectByTicket(PositionGetTicket(i))) {
         if (PositionGetInteger(POSITION_MAGIC) == InpMagicNumber) return true;
      }
   }
   return false;
}

//+------------------------------------------------------------------+
//| OnInit                                                           |
//+------------------------------------------------------------------+
int OnInit() {
   trade.SetExpertMagicNumber(InpMagicNumber);
   Print("ManipulationX V6 NoMACD EA on ", _Symbol, " ", EnumToString(Period()));
   Print("Correlation pair: ", InpCorrSymbol);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int) {}

//+------------------------------------------------------------------+
//| OnTick                                                           |
//+------------------------------------------------------------------+
void OnTick() {
   datetime curBar = iTime(_Symbol, PERIOD_M15, 0);
   if (curBar == lastBarTime) return;
   lastBarTime = curBar;

   UpdateSessions();
   UpdateDOL();

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
         Print("LONG signal=", signal, " smt=", smtBias);
   } else {
      sl = ask + InpSL_Points * _Point;
      tp = bid - InpSL_Points * InpTPSL_Ratio * _Point;
      if (trade.Sell(InpLotSize, _Symbol, bid, sl, tp, "MX V6"))
         Print("SHORT signal=", signal, " smt=", smtBias);
   }
}
//+------------------------------------------------------------------+
