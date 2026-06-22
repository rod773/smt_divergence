//+------------------------------------------------------------------+
//|                                ManipulationX_V6_EA_NoMACD.mq5    |
//|                         Pure replication of Pine Script logic    |
//+------------------------------------------------------------------+
#property copyright "ManipulationX V.6"
#property version   "1.01"
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
struct FvgLevel {
   double hi, lo;
   int    dir;        // 1 bull, -1 bear
   datetime t;
};
FvgLevel fvg[100];
int fvgN = 0;

//+------------------------------------------------------------------+
//| Globals                                                          |
//+------------------------------------------------------------------+
datetime lastBar = 0;
double   lastNqLo=0, lastEsLo=0, lastNqHi=0, lastEsHi=0;
int      smtBias = 0;

// DOL
double   dolHi=0, dolLo=0;
string   dolLast="";

// Sessions
int      asiaDay=0, lonDay=0;
double   asiaHi=0, asiaLo=0, lonHi=0, lonLo=0;
bool     asiaHiHit=false, asiaLoHit=false, lonHiHit=false, lonLoHit=false;
bool     asiaDone=false, lonDone=false;

//+------------------------------------------------------------------+
//| Helpers                                                          |
//+------------------------------------------------------------------+
bool GetR(string s, ENUM_TIMEFRAMES tf, MqlRates &r[], int n) {
   ArraySetAsSeries(r, true);
   return CopyRates(s, tf, 0, n, r) >= n;
}

//+------------------------------------------------------------------+
//| FVG scan: store new zones                                        |
//+------------------------------------------------------------------+
void ScanFVG(string sym, ENUM_TIMEFRAMES tf, int scan) {
   MqlRates r[];
   int need = scan + 2;
   ArrayResize(r, need);
   if (!GetR(sym, tf, r, need)) return;
   for (int i = 1; i <= scan - 2; i++) {
      if (i+2 >= ArraySize(r)) break;
      double gb = r[i].low - r[i+2].high;
      double gs = r[i+2].low - r[i].high;
      int d = 0;
      if (gb >= InpFvgMinPts * _Point) d = 1;
      else if (gs >= InpFvgMinPts * _Point) d = -1;
      if (d == 0) continue;
      bool dup = false;
      for (int j = 0; j < fvgN && !dup; j++)
         if (MathAbs(fvg[j].hi - r[i].high) < 10*_Point && MathAbs(fvg[j].lo - r[i].low) < 10*_Point) dup = true;
      if (!dup && fvgN < 100) {
         fvg[fvgN].hi = (d==1)?r[i].low:r[i].high;
         fvg[fvgN].lo = (d==1)?r[i+2].high:r[i+2].low;
         fvg[fvgN].dir = d;
         fvg[fvgN].t = TimeCurrent();
         fvgN++;
      }
   }
}

int NearFVG(double price) {
   for (int i=0; i<fvgN; i++) {
      double d = 5*_Point;
      if (price >= fvg[i].lo-d && price <= fvg[i].hi+d) return fvg[i].dir;
   }
   return 0;
}

//+------------------------------------------------------------------+
//| iFVG: scan last 15 completed 1m bars vs prev M15 close           |
//+------------------------------------------------------------------+
int CheckIFVG() {
   MqlRates r1[18], r15[3];
   if (!GetR(_Symbol, PERIOD_M1,  r1, 18)) return 0;
   if (!GetR(_Symbol, PERIOD_M15, r15, 3)) return 0;
   // r1[0]=latest completed M1, r15[1]=prev completed M15 bar
   // Scan pairs (i,i+1) within the last ~15 M1 bars
   for (int i = 0; i <= 14; i++) {
      if (i+2 >= ArraySize(r1)) break;
      // bIFVG: M1 bar[i] closed bearish below bar[i+1].low, AND M15 close above bar[i+1].high
      bool b = r1[i].close < r1[i].open && r1[i].close < r1[i+1].low && r15[1].close > r1[i+1].high;
      // sIFVG: M1 bar[i] closed bullish above bar[i+1].high, AND M15 close below bar[i+1].low
      bool s = r1[i].close > r1[i].open && r1[i].close > r1[i+1].high && r15[1].close < r1[i+1].low;
      if (b) return 1;
      if (s) return -1;
   }
   return 0;
}

//+------------------------------------------------------------------+
//| SMT divergence                                                   |
//+------------------------------------------------------------------+
int CheckSMT() {
   MqlRates r1[10], r2[10];
   if (!GetR(_Symbol, PERIOD_CURRENT, r1, 10)) return 0;
   if (!GetR(InpCorrSymbol, PERIOD_CURRENT, r2, 10)) return 0;
   double nqLo=0, nqHi=0, esLo=0, esHi=0;
   for (int i=2; i<=6; i++) {
      bool l1 = r1[i].low<=r1[i-1].low && r1[i].low<=r1[i-2].low && r1[i].low<=r1[i+1].low && r1[i].low<=r1[i+2].low;
      bool h1 = r1[i].high>=r1[i-1].high && r1[i].high>=r1[i-2].high && r1[i].high>=r1[i+1].high && r1[i].high>=r1[i+2].high;
      bool l2 = r2[i].low<=r2[i-1].low && r2[i].low<=r2[i-2].low && r2[i].low<=r2[i+1].low && r2[i].low<=r2[i+2].low;
      bool h2 = r2[i].high>=r2[i-1].high && r2[i].high>=r2[i-2].high && r2[i].high>=r2[i+1].high && r2[i].high>=r2[i+2].high;
      if (l1) nqLo = r1[i].low;  if (h1) nqHi = r1[i].high;
      if (l2) esLo = r2[i].low;  if (h2) esHi = r2[i].high;
   }
   int sig = 0;
   if (nqLo&&lastNqLo&&esLo&&lastEsLo) { if (nqLo>lastNqLo && esLo<lastEsLo) sig=1; }
   if (nqHi&&lastNqHi&&esHi&&lastEsHi) { if (nqHi<lastNqHi && esHi>lastEsHi) sig=-1; }
   if (nqLo) { lastNqLo=nqLo; if(esLo)lastEsLo=esLo; }
   if (nqHi) { lastNqHi=nqHi; if(esHi)lastEsHi=esHi; }
   return sig;
}

//+------------------------------------------------------------------+
//| Sessions + sweeps                                                |
//+------------------------------------------------------------------+
void UpdateSessions() {
   MqlDateTime dt;
   TimeCurrent(dt);
   int today = dt.year*10000 + dt.mon*100 + dt.day;
   bool asia = (dt.hour>=0 && dt.hour<8);
   bool lon  = (dt.hour>=8 && dt.hour<17);

   if (asia && asiaDay!=today) {
      asiaDay = today; asiaDone = false;
      asiaHiHit=false; asiaLoHit=false;
      MqlRates r[1];
      if (GetR(_Symbol, PERIOD_CURRENT, r, 1)) { asiaHi=r[0].high; asiaLo=r[0].low; }
   }
   if (asia && asiaHi!=0) {
      MqlRates r[1];
      if (GetR(_Symbol, PERIOD_CURRENT, r, 1)) {
         if (r[0].high>asiaHi) asiaHi=r[0].high;
         if (r[0].low<asiaLo) asiaLo=r[0].low;
      }
   }
   if (!asia && asiaHi!=0) asiaDone=true;

   if (lon && lonDay!=today) {
      lonDay = today; lonDone = false;
      lonHiHit=false; lonLoHit=false;
      MqlRates r[1];
      if (GetR(_Symbol, PERIOD_CURRENT, r, 1)) { lonHi=r[0].high; lonLo=r[0].low; }
   }
   if (lon && lonHi!=0) {
      MqlRates r[1];
      if (GetR(_Symbol, PERIOD_CURRENT, r, 1)) {
         if (r[0].high>lonHi) lonHi=r[0].high;
         if (r[0].low<lonLo) lonLo=r[0].low;
      }
   }
   if (!lon && lonHi!=0) lonDone=true;
}

int CheckSweep() {
   MqlRates r[2];
   if (!GetR(_Symbol, PERIOD_M15, r, 2)) return 0;
   // Check PREVIOUS completed M15 bar (index 1) for sweep against session levels
   double swp = InpSweepPts * _Point;
   // Asia sweeps
   if (asiaDone && asiaHi!=0 && !asiaHiHit && r[1].high>asiaHi+swp && r[1].close<asiaHi) { asiaHiHit=true; return -1; }
   if (asiaDone && asiaLo!=0 && !asiaLoHit && r[1].low<asiaLo-swp && r[1].close>asiaLo) { asiaLoHit=true; return 1; }
   // London sweeps
   if (lonDone && lonHi!=0 && !lonHiHit && r[1].high>lonHi+swp && r[1].close<lonHi) { lonHiHit=true; return -1; }
   if (lonDone && lonLo!=0 && !lonLoHit && r[1].low<lonLo-swp && r[1].close>lonLo) { lonLoHit=true; return 1; }
   return 0;
}

//+------------------------------------------------------------------+
//| DOL                                                              |
//+------------------------------------------------------------------+
void UpdateDOL() {
   MqlRates r[10];
   if (!GetR(_Symbol, PERIOD_M15, r, 10)) return;
   double ph=0, pl=0;
   for (int i=4; i<=6; i++) {
      if (r[i].high>=r[i-1].high && r[i].high>=r[i-2].high && r[i].high>=r[i-3].high && r[i].high>=r[i-4].high &&
          r[i].high>=r[i+1].high && r[i].high>=r[i+2].high && r[i].high>=r[i+3].high && r[i].high>=r[i+4].high)
         ph = r[i].high;
      if (r[i].low<=r[i-1].low && r[i].low<=r[i-2].low && r[i].low<=r[i-3].low && r[i].low<=r[i-4].low &&
          r[i].low<=r[i+1].low && r[i].low<=r[i+2].low && r[i].low<=r[i+3].low && r[i].low<=r[i+4].low)
         pl = r[i].low;
   }
   double minD = 16 * _Point;
   if (ph && (dolLast==""||dolLast=="low") && (dolLo==0||ph-dolLo>=minD)) { dolHi=ph; dolLast="high"; }
   if (pl && (dolLast==""||dolLast=="high") && (dolHi==0||dolHi-pl>=minD)) { dolLo=pl; dolLast="low"; }
}

//+------------------------------------------------------------------+
//| Entry logic                                                      |
//+------------------------------------------------------------------+
int GetEntrySignal() {
   // Prune old FVG zones (>12h)
   int kept = 0;
   for (int i=0; i<fvgN; i++) {
      if (TimeCurrent()-fvg[i].t < 43200) fvg[kept++]=fvg[i];
   }
   fvgN = kept;

   // Scan fresh FVGs
   ScanFVG(_Symbol, PERIOD_M15, 8);
   ScanFVG(_Symbol, PERIOD_H1,  10);
   ScanFVG(_Symbol, PERIOD_H4,  6);

   // SMT bias
   int smt = CheckSMT();
   if (smt != 0) smtBias = smt;

   MqlRates r[2];
   GetR(_Symbol, PERIOD_M15, r, 2);
   double price = r[1].close;

   // 1) IFVG trigger
   int ifvg = CheckIFVG();
   if (ifvg != 0) {
      int nfvg = NearFVG(price);
      if ((ifvg==1 && nfvg!=-1) || (ifvg==-1 && nfvg!=1)) {
         if (ifvg==1) return (smtBias==-1)?1:2;
         else return (smtBias==1)?-1:-2;
      }
   }

   // 2) Session sweep
   int sweep = CheckSweep();
   if (sweep != 0) {
      int nfvg = NearFVG(price);
      if ((sweep==1 && nfvg!=-1) || (sweep==-1 && nfvg!=1))
         return (sweep==1)?3:-3;
   }

   return 0;
}

//+------------------------------------------------------------------+
//| Boilerplate                                                      |
//+------------------------------------------------------------------+
bool HasPos() {
   for (int i=PositionsTotal()-1; i>=0; i--)
      if (PositionSelectByTicket(PositionGetTicket(i)))
         if (PositionGetInteger(POSITION_MAGIC)==InpMagicNumber) return true;
   return false;
}

int OnInit() {
   trade.SetExpertMagicNumber(InpMagicNumber);
   Print("ManipulationX V6 NoMACD on ", _Symbol, " ", EnumToString(Period()));
   Print("SMT pair: ", InpCorrSymbol);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int) {}

void OnTick() {
   datetime nb = iTime(_Symbol, PERIOD_M15, 0);
   if (nb == lastBar) return;
   lastBar = nb;

   UpdateSessions();
   UpdateDOL();

   if (HasPos()) return;

   int sig = GetEntrySignal();

   // Debug: show near-misses
   int ifvg = CheckIFVG();
   int sweep = CheckSweep();
   MqlRates r[2]; GetR(_Symbol, PERIOD_M15, r, 2);
   int nfvg = NearFVG(r[1].close);
   if (ifvg!=0) PrintFormat("M15[%s] IFVG=%d NFVG=%d SMT=%d", TimeToString(nb), ifvg, nfvg, smtBias);
   if (sweep!=0) PrintFormat("M15[%s] SWP=%d NFVG=%d SMT=%d", TimeToString(nb), sweep, nfvg, smtBias);

   if (sig == 0) return;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double sl, tp;

   if (sig > 0) {
      sl = bid - InpSL_Points * _Point;
      tp = ask + InpSL_Points * InpTPSL_Ratio * _Point;
      if (trade.Buy(InpLotSize, _Symbol, ask, sl, tp, "MX V6"))
         Print(">>> LONG signal=", sig);
   } else {
      sl = ask + InpSL_Points * _Point;
      tp = bid - InpSL_Points * InpTPSL_Ratio * _Point;
      if (trade.Sell(InpLotSize, _Symbol, bid, sl, tp, "MX V6"))
         Print(">>> SHORT signal=", sig);
   }
}
//+------------------------------------------------------------------+
