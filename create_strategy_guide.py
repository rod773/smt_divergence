from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
import os

path = r"D:\Descargas\smt_divergence\Strategy_Guide.pdf"
doc = SimpleDocTemplate(path, pagesize=letter,
    rightMargin=0.75*inch, leftMargin=0.75*inch,
    topMargin=0.75*inch, bottomMargin=0.75*inch)

styles = getSampleStyleSheet()

sT = ParagraphStyle("T", parent=styles["Title"], fontSize=26, spaceAfter=4, textColor=HexColor("#1a237e"))
sST = ParagraphStyle("ST", parent=styles["Normal"], fontSize=14, spaceAfter=20, textColor=HexColor("#546e7a"), alignment=TA_CENTER)
sH1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18, spaceBefore=16, spaceAfter=8, textColor=HexColor("#1a237e"))
sH2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceBefore=12, spaceAfter=6, textColor=HexColor("#283593"))
sH3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, spaceBefore=8, spaceAfter=4, textColor=HexColor("#37474f"))
sB = ParagraphStyle("B", parent=styles["Normal"], fontSize=10, spaceAfter=6, leading=14, alignment=TA_JUSTIFY)
sBL = ParagraphStyle("BL", parent=sB, leftIndent=20, spaceAfter=3)
sNOTE = ParagraphStyle("NOTE", parent=sB, leftIndent=15, rightIndent=15, spaceAfter=10, spaceBefore=10,
    backColor=HexColor("#e8eaf6"), borderPadding=8)
sQ = ParagraphStyle("Q", parent=sB, leftIndent=25, rightIndent=25, spaceAfter=10, spaceBefore=10,
    textColor=HexColor("#37474f"), fontSize=9, fontName="Helvetica-Oblique",
    backColor=HexColor("#f5f5f5"), borderPadding=8)

elements = []

# ── Cover ──
elements.append(Spacer(1, 1.5*inch))
elements.append(Paragraph("NY Session Trading Strategy", sT))
elements.append(Paragraph("Complete Guide to the Concepts Behind ManipulationX V.6", sST))
elements.append(HRFlowable(width="60%", thickness=1, color=HexColor("#1a237e"), spaceAfter=24))
elements.append(Spacer(1, 0.3*inch))
concepts_list = [
    "SMT Divergence \u2022 Fair Value Gaps \u2022 Inverse FVGs",
    "Draws on Liquidity \u2022 Manipulation \u2022 Killzones",
    "V-Shape Reversals \u2022 The 3-Step Checklist",
]
for c in concepts_list:
    elements.append(Paragraph(c, ParagraphStyle("cl", parent=sB, fontSize=12, alignment=TA_CENTER, textColor=HexColor("#37474f"))))
elements.append(Spacer(1, 1*inch))
elements.append(Paragraph("Based on the strategy by EzTrades", ParagraphStyle("cr", parent=sB, fontSize=10, alignment=TA_CENTER, textColor=HexColor("#78909c"))))
elements.append(PageBreak())

# ── TOC ──
elements.append(Paragraph("Contents", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))
toc = [
    "1.  The Core Idea",
    "2.  Smart Money Concepts Overview",
    "3.  Fair Value Gaps (FVG)",
    "4.  Inverse Fair Value Gaps (IFVG)",
    "5.  SMT Divergence",
    "6.  Draws on Liquidity (DOL)",
    "7.  Manipulation & The NY Open",
    "8.  Killzones",
    "9.  V-Shape Reversals",
    "10. The 3-Step Checklist in Practice",
    "11. Putting It All Together: A+ Setup",
    "12. Risk Management",
]
for t in toc:
    elements.append(Paragraph(t, sB))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 1. THE CORE IDEA
# ════════════════════════════════════════════════════════
elements.append(Paragraph("1. The Core Idea", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "This strategy exploits predictable institutional order flow during the New York session open. "
    "The core insight is that every trading day, market makers and algorithms follow a script:",
    sB))

elements.append(Paragraph(
    "<b>1.</b> Before NY open, price has accumulated at levels where liquidity is clustered "
    "(equal highs, equal lows, trendlines).<br/><br/>"
    "<b>2.</b> At 9:30am EST, the market opens and makes an initial move in one direction. "
    "This is the <b>manipulation leg</b> \u2014 designed to trigger retail stop losses and build positions "
    "for the real move.<br/><br/>"
    "<b>3.</b> After the manipulation, price reverses sharply into a <b>V-shape inversion</b> "
    "and runs toward the opposite liquidity pool.<br/><br/>"
    "<b>4.</b> The reversal typically occurs when price taps into a higher timeframe "
    "<b>Fair Value Gap</b> \u2014 creating a confluence zone where smart money enters.",
    sB))

elements.append(Paragraph(
    "The entire strategy can be summarized as: <b>wait for the manipulation, identify the delivery context "
    "(FVG), confirm with SMT divergence, and enter on the IFVG.</b>",
    sNOTE))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 2. SMART MONEY CONCEPTS
# ════════════════════════════════════════════════════════
elements.append(Paragraph("2. Smart Money Concepts Overview", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "This strategy is built on Smart Money Concepts (SMC) \u2014 the idea that central banks, institutions, "
    "and algorithms drive price movements, and retail traders are the liquidity they harvest. "
    "Understanding these concepts is essential:",
    sB))

elements.append(Paragraph("Liquidity", sH2))
elements.append(Paragraph(
    "Liquidity refers to clustered stop-loss orders resting below swing lows or above swing highs. "
    "Price is algorithmically driven to grab this liquidity before reversing. Retail traders place "
    "stops at obvious levels, and smart money targets these exact levels to fill large orders.",
    sB))

elements.append(Paragraph("Displacement & Mitigation", sH2))
elements.append(Paragraph(
    "When price moves aggressively through a level with high momentum, it creates a displacement. "
    "These displaced moves often leave behind Fair Value Gaps (imbalances) that price will later "
    "return to 'mitigate' before continuing. This is the foundation of the FVG concept.",
    sB))

elements.append(Paragraph("Order Flow", sH2))
elements.append(Paragraph(
    "The sequence of candles tells a story:<br/>"
    "&bull; <b>Manipulation candle:</b> A wide-range candle that sweeps a low/high (grabbing liquidity)<br/>"
    "&bull; <b>Reversal candle:</b> Immediately closes back in the opposite direction<br/>"
    "&bull; <b>Continuation candles:</b> Follow-through in the reversal direction<br/><br/>"
    "Reading this flow is more important than any single indicator. The ManipulationX tools simply "
    "make this flow visible at a glance.",
    sB))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 3. FAIR VALUE GAPS
# ════════════════════════════════════════════════════════
elements.append(Paragraph("3. Fair Value Gaps (FVG)", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("Definition", sH2))
elements.append(Paragraph(
    "A Fair Value Gap (FVG) is a price imbalance created when a candle opens and closes outside the range "
    "of the previous candle, leaving a gap where price moved too quickly. These gaps represent "
    "inefficient price delivery \u2014 the market moved so fast that not all orders were filled. "
    "Price is naturally drawn back to these zones to 'fill the gap' (mitigation) before continuing.",
    sB))

elements.append(Paragraph("How FVGs Form", sH2))
elements.append(Paragraph(
    "<b>Bullish FVG:</b> Three-candle sequence: bearish, strong bullish, bullish. "
    "The middle bullish candle opens below the first candle's close and closes above its high, "
    "creating a gap between the first candle's high and the second candle's low.<br/><br/>"
    "<b>Bearish FVG:</b> Three-candle sequence: bullish, strong bearish, bearish. "
    "The middle bearish candle opens above the first candle's close and closes below its low, "
    "creating a gap between the second candle's high and the first candle's low.",
    sB))

elements.append(Paragraph("The Importance of Timeframe", sH2))
elements.append(Paragraph(
    "Higher timeframe FVGs (15-minute, 1-hour) act as <b>delivery magnets</b>. "
    "A 15-minute bullish FVG tells you that price wants to go up \u2014 it will likely sweep a low "
    "into that gap, then reverse and push higher. Trading against the HTF FVG direction is "
    "low-probability.<br/><br/>"
    "Key rule from the video: <b>Never short into a bullish FVG or long into a bearish FVG.</b> "
    "The FVG tells you where the market wants to go. Your trade should align with it.",
    sB))

elements.append(Paragraph(
    '\u201cThe 15-minute and 1-hour FVGs give me my delivery context. I want to see price delivering '
    'from a higher timeframe FVG.\u201d \u2014 EzTrades',
    sQ))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 4. INVERSE FAIR VALUE GAPS
# ════════════════════════════════════════════════════════
elements.append(Paragraph("4. Inverse Fair Value Gaps (IFVG)", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("Definition", sH2))
elements.append(Paragraph(
    "An Inverse Fair Value Gap (IFVG) is the <b>entry trigger</b> for this strategy. It represents the "
    "moment when manipulation ends and the real move begins. It is the transition from "
    "liquidity grab to directional delivery.",
    sB))

elements.append(Paragraph("Bullish IFVG Formation", sH2))
elements.append(Paragraph(
    "1. A bearish 1-minute candle closes below the previous candle's low<br/>"
    "   <i>(This sweeps liquidity \u2014 it triggers stops below the prior low)</i><br/>"
    "2. The next candle immediately closes back <b>above</b> the bearish candle's high<br/>"
    "   <i>(This is the inversion \u2014 trapped sellers are now underwater)</i><br/><br/>"
    "The zone between the bearish candle's high and low becomes the IFVG. The break above the high "
    "confirms the reversal and is your entry signal.",
    sB))

elements.append(Paragraph("Bearish IFVG Formation", sH2))
elements.append(Paragraph(
    "1. A bullish 1-minute candle closes above the previous candle's high<br/>"
    "2. The next candle immediately closes back <b>below</b> the bullish candle's low<br/><br/>"
    "Same concept in reverse. Trapped buyers fuel the move down.",
    sB))

elements.append(Paragraph("Why IFVGs Work", sH2))
elements.append(Paragraph(
    "The IFVG captures the exact moment when smart money has finished accumulating their position "
    "during the manipulation leg and begins the distribution leg. The initial false breakout "
    "triggered retail stops; the immediate reversal traps those who chased the breakout, "
    "creating fuel for the reversal.<br/><br/>"
    "This is why the IFVG must happen <b>immediately</b> \u2014 a V-shape. If price lingers "
    "at the manipulated level, the trap didn't work.",
    sB))

elements.append(Paragraph(
    '\u201cWe waited for price to tap into this 15-minute gap and create a bullish SMT with ES. '
    'This is our manipulation leg. We take out all the retail, we immediately reverse on them, '
    'gives us our inverse fair value gap.\u201d \u2014 EzTrades',
    sQ))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 5. SMT DIVERGENCE
# ════════════════════════════════════════════════════════
elements.append(Paragraph("5. SMT Divergence", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("What is SMT?", sH2))
elements.append(Paragraph(
    "SMT stands for Smart Money Technique. It is a form of <b>inter-instrument divergence</b> that "
    "compares two correlated assets to detect concealed institutional activity. The core idea: "
    "if two assets that normally move together suddenly diverge at a key swing point, "
    "one of them is revealing the true direction.",
    sB))

elements.append(Paragraph("The NQ / ES Relationship", sH2))
elements.append(Paragraph(
    "Nasdaq (NQ) and S&P 500 (ES) are the two most liquid index futures. They are highly correlated "
    "(typically >95%) but not identical. NQ is more volatile and tech-heavy; ES is broader. "
    "This slight difference creates opportunities for SMT analysis:<br/><br/>"
    "&bull; When both make higher lows together \u2014 neutral, trend is up<br/>"
    "&bull; When both make lower lows together \u2014 neutral, trend is down<br/>"
    "&bull; When NQ makes a higher low but ES makes a lower low \u2014 <b>Bullish SMT divergence</b><br/>"
    "&bull; When NQ makes a lower high but ES makes a higher high \u2014 <b>Bearish SMT divergence</b>",
    sB))

elements.append(Paragraph("Bullish SMT Divergence", sH2))
elements.append(Paragraph(
    "At a swing low point:<br/>"
    "&bull; <b>NQ</b> creates a <b>higher low</b> (did not break the previous low)<br/>"
    "&bull; <b>ES</b> creates a <b>lower low</b> (broke below the previous low)<br/><br/>"
    "Interpretation: ES swept liquidity (grabbed stops below the old low), but NQ held firm. "
    "This tells you that ES was used to manipulate the market down while NQ reveals the true "
    "bullish intent. Price is about to reverse up.<br/><br/>"
    "This is a powerful buy signal with high probability.",
    sB))

elements.append(Paragraph("Bearish SMT Divergence", sH2))
elements.append(Paragraph(
    "At a swing high point:<br/>"
    "&bull; <b>NQ</b> creates a <b>lower high</b> (failed to break the previous high)<br/>"
    "&bull; <b>ES</b> creates a <b>higher high</b> (broke above the previous high)<br/><br/>"
    "Interpretation: ES swept liquidity (grabbed stops above the old high) while NQ showed weakness. "
    "ES was used to manipulate the market up while NQ reveals bearish intent. "
    "Price is about to reverse down.",
    sB))

elements.append(Paragraph(
    '\u201cSMT divergence is one of the most powerful confluences you can have when you are day trading Nasdaq. '
    'Whenever I have this formation where price is delivering from a 15-minute FVG, we have draws on '
    'liquidity higher, and we have an SMT divergence, this is a textbook trade.\u201d \u2014 EzTrades',
    sQ))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 6. DRAWS ON LIQUIDITY
# ════════════════════════════════════════════════════════
elements.append(Paragraph("6. Draws on Liquidity (DOL)", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("Concept", sH2))
elements.append(Paragraph(
    "A Draw on Liquidity (DOL) is a price level where a significant number of stop-loss orders are "
    "clustered. These levels act as 'magnets' \u2014 price is algorithmically driven to grab this "
    "liquidity before reversing. Identifying DOLs before the session opens is the second step "
    "of the strategy checklist.",
    sB))

elements.append(Paragraph("Types of DOLs", sH2))

dol_data = [
    ["Type", "Description", "How to Spot"],
    ["Equal Highs\n(EQH)", "Two or more swing highs at the same price level. Stops accumulate above.", "Swing highs that align horizontally within a few ticks"],
    ["Equal Lows\n(EQL)", "Two or more swing lows at the same price level. Stops accumulate below.", "Swing lows that align horizontally within a few ticks"],
    ["Trendline\nLiquidity", "A series of higher highs or lower lows along a trendline. Breaking it releases all that liquidity.", "Draw a trendline connecting swing points"],
    ["External\nLiquidity", "A swing high or low that is clearly beyond the current visible range. A target far away.", "Look at higher timeframe for obvious extremes"],
    ["Internal\nLiquidity", "The most recent swing high or low within the current range.", "Nearest obvious swing point"],
]
t = Table(dol_data, colWidths=[0.9*inch, 2.5*inch, 2.4*inch])
t.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("BACKGROUND", (0,0), (-1,0), HexColor("#1a237e")),
    ("TEXTCOLOR", (0,0), (-1,0), white),
    ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("GRID", (0,0), (-1,-1), 0.5, HexColor("#c5cae9")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, HexColor("#f5f5f5")]),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
]))
elements.append(t)
elements.append(Spacer(1, 0.1*inch))

elements.append(Paragraph("How DOLs Drive the Strategy", sH2))
elements.append(Paragraph(
    "The strategy works because the market is predictable in its pursuit of liquidity:<br/><br/>"
    "1. Before 9:30am, mark all DOLs on your chart (both above and below current price)<br/>"
    "2. At 9:30am, watch which DOL gets swept first (manipulation)<br/>"
    "3. If price sweeps a low DOL and reverses, the high DOLs become your targets<br/>"
    "4. If price sweeps a high DOL and reverses, the low DOLs become your targets<br/><br/>"
    "The strategy typically targets the <b>external</b> DOL for full take profit "
    "and uses <b>internal</b> DOLs for break-even or partial profit levels.",
    sB))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 7. MANIPULATION & THE NY OPEN
# ════════════════════════════════════════════════════════
elements.append(Paragraph("7. Manipulation & the NY Open", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("The 9:30am Script", sH2))
elements.append(Paragraph(
    "The New York session open at 9:30am EST is the most predictable 30 minutes of the trading day. "
    "Here is what typically happens:",
    sB))

steps_ny = [
    "<b>T-5 to T+0 (9:25-9:30):</b> Price often sets up at a level near a DOL. Algorithms position "
    "themselves for the open.",
    "<b>T+0 to T+5 (9:30-9:35):</b> The first candle prints. This is usually a manipulation candle "
    "that sweeps the nearest liquidity pool. This is designed to trigger retail traders.",
    "<b>T+5 to T+15 (9:35-9:45):</b> Price either continues the manipulation or reverses sharply. "
    "This is the decision window. The IFVG will form here.",
    "<b>T+15 to T+30 (9:45-10:00):</b> If the reversal is real, price now runs toward the opposite "
    "DOL. The move often accelerates into the 10:00am macro window.",
]
for s in steps_ny:
    elements.append(Paragraph(s, sBL))

elements.append(Paragraph("Why This Happens", sH2))
elements.append(Paragraph(
    "The NY open represents the convergence of global traders. London is still active, Asia is done, "
    "and US institutional traders are entering. This concentration of order flow creates "
    "predictable patterns:<br/><br/>"
    "&bull; Algorithms need liquidity to execute large orders, so they intentionally trigger stops<br/>"
    "&bull; The manipulation sweeps are how they build their positions<br/>"
    "&bull; Once positioned, they reverse the price and distribute to latecomers<br/>"
    "&bull; The entire process takes 15-30 minutes, after which the trend is established",
    sB))

elements.append(Paragraph(
    '\u201cI do not trade the first 5 minutes of market open. I need to let that initial manipulation '
    'move play out.\u201d \u2014 EzTrades',
    sQ))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 8. KILLZONES
# ════════════════════════════════════════════════════════
elements.append(Paragraph("8. Killzones", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "Killzones are pre-defined trading sessions where volume and volatility are highest. "
    "The strategy focuses almost exclusively on the <b>New York Killzone</b>:",
    sB))

elements.append(Paragraph("New York Killzone (09:30 - 16:00 ET)", sH2))
elements.append(Paragraph(
    "This is the primary session. The first 30 minutes (09:30-10:00) contain the highest-probability "
    "setup. Over 70% of the strategy's trades occur within this window. The rest of the NY session "
    "can produce additional setups, but the quality declines after 11:00am.",
    sB))

elements.append(Paragraph("London Killzone (03:00 - 12:00 ET)", sH2))
elements.append(Paragraph(
    "Optional. The London open can provide context for the NY session (pre-NY highs/lows often act as "
    "DOLs). Some traders trade London exclusively, but this strategy is designed for NY.",
    sB))

elements.append(Paragraph("The Macro Windows", sH2))
elements.append(Paragraph(
    "Beyond the standard killzones, pay attention to these macro windows:<br/>"
    "&bull; <b>09:30am:</b> NY open \u2014 highest volume spike<br/>"
    "&bull; <b>10:00am:</b> Economic data releases, institutional rebalancing<br/>"
    "&bull; <b>11:30am:</b> Lunch hour begins \u2014 volume drops<br/>"
    "&bull; <b>02:00pm:</b> Afternoon session<br/>"
    "&bull; <b>03:30-04:00pm:</b> Close \u2014 position squaring<br/><br/>"
    "The 10:00am window is particularly important. Reversals at 10:00am have high volume "
    "confirmation and often lead to powerful moves.",
    sB))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 9. V-SHAPE REVERSALS
# ════════════════════════════════════════════════════════
elements.append(Paragraph("9. V-Shape Reversals", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("What is a V-Shape Reversal?", sH2))
elements.append(Paragraph(
    "A V-shape reversal is an immediate, aggressive turn in price with no consolidation or "
    "rounding. It looks like the letter 'V' on the chart (or an upside-down 'V' for shorts). "
    "This is the highest-probability entry pattern because it reveals urgent institutional buying "
    "or selling.",
    sB))

elements.append(Paragraph("Characteristics of a V-Shape", sH2))
elements.append(Paragraph(
    "&bull; A sharp, one-sided move (often a single large candle)<br/>"
    "&bull; Immediate reversal on the next candle with equal force<br/>"
    "&bull; The reversal candle closes through the entire range of the manipulation candle<br/>"
    "&bull; High volume, visible as wide-range candles<br/>"
    "&bull; No hesitation \u2014 price doesn't consolidate, it just flips",
    sB))

elements.append(Paragraph("V-Shape vs. Rounded Reversal", sH2))
elements.append(Paragraph(
    "A rounded reversal (taking several candles to turn) is weaker. It suggests indecision. "
    "The V-shape reveals that smart money has finished accumulating and is now aggressively "
    "pushing price in the intended direction. This is why the strategy demands a V-shape: "
    "it's the signature of institutional order flow.<br/><br/>"
    "In the video, every A+ trade example shows a sharp V-shape reversal at the IFVG. "
    "If the reversal is slow or choppy, the trade quality is lower.",
    sB))

elements.append(Paragraph(
    '\u201cBoom, instant V-shape reversal. Very small 1-minute candle, very obvious V-shape inversion. '
    'Stop loss below this displacement candle low, break even at this equal high.\u201d \u2014 EzTrades',
    sQ))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 10. THE 3-STEP CHECKLIST
# ════════════════════════════════════════════════════════
elements.append(Paragraph("10. The 3-Step Checklist in Practice", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "The indicator displays a permanent checklist. Here is how to execute each step in real time:",
    sB))

elements.append(Paragraph("Step 1: NY Session (9:30am est)", sH2))
elements.append(Paragraph(
    "Before 9:30am, have your chart open and ready. Mark the NY session on your chart (the indicator "
    "does this automatically with the killzone background). <b>Do not trade outside NY session.</b> "
    "This rule alone eliminates low-probability trading.",
    sB))

elements.append(Paragraph("Step 2: Mark out DOLs / FVGs", sH2))
elements.append(Paragraph(
    "Before 9:30am, identify:<br/>"
    "&bull; <b>DOLs:</b> Look for equal highs above and equal lows below current price. "
    "Also note any clear external swing highs/lows.<br/>"
    "&bull; <b>FVGs:</b> Check the 15-minute and 1-hour charts for active FVGs. "
    "These determine your bias. If a bullish FVG is below price, expect a sweep into it "
    "followed by a rally. If a bearish FVG is above, expect a rejection.<br/><br/>"
    "The indicator draws these automatically. Your job is to be aware of them.",
    sB))

elements.append(Paragraph("Step 3: Entry Model (iFVG)", sH2))
elements.append(Paragraph(
    "During the first 5-15 minutes after open, watch for:<br/>"
    "&bull; Price sweeps a DOL (manipulation)<br/>"
    "&bull; Price taps into a HTF FVG (delivery context)<br/>"
    "&bull; A bullish or bearish SMT divergence forms (confluence)<br/>"
    "&bull; An IFVG appears (entry signal)<br/>"
    "&bull; The reversal is V-shaped (high quality)<br/><br/>"
    "If all these align, enter immediately on the IFVG close. If some are missing, "
    "it's a lower-probability trade \u2014 consider skipping.",
    sB))

elements.append(Paragraph(
    '\u201cThis is my entire strategy given to you for free. Most of you guys are like 90% there. '
    'You\'re just missing that last 10%.\u201d \u2014 EzTrades',
    sQ))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 11. PUTTING IT ALL TOGETHER
# ════════════════════════════════════════════════════════
elements.append(Paragraph("11. Putting It All Together: A+ Setup", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("The A+ Setup Checklist", sH2))
elements.append(Paragraph(
    "From the video, here is the exact sequence of events that produces a 76%+ win-rate trade:",
    sB))

aplus = [
    "<b>Time:</b> NY session, 9:30-10:00am EST window",
    "<b>Context:</b> Price is delivering from a 15-minute or 1-hour Fair Value Gap",
    "<b>DOLs:</b> Clear external liquidity above (for longs) or below (for shorts)",
    "<b>Manipulation:</b> Initial move (first 5-15 min) sweeps internal liquidity",
    "<b>SMT:</b> Bullish SMT divergence at the sweep low (or bearish at the sweep high)",
    "<b>Entry:</b> V-shape inversion creates an IFVG on the 1-minute chart",
    "<b>Stop:</b> Below the IFVG candle body (longs) or above it (shorts)",
    "<b>Break Even:</b> At the most internal structure high/low",
    "<b>Target:</b> External DOL for full take profit (typically 1.5:1 RR)",
]
for a in aplus:
    elements.append(Paragraph(a, sBL))

elements.append(Spacer(1, 0.15*inch))
elements.append(Paragraph("Example: Long Setup", sH2))
elements.append(Paragraph(
    "Price opens at 9:30am and immediately drops (manipulation). It sweeps below an internal low, "
    "tapping into a 15-minute bullish FVG that was identified pre-market. At the same time, ES makes "
    "a lower low while NQ holds a higher low \u2014 bullish SMT divergence. Within minutes, price V-shapes "
    "back up, creating an IFVG on the 1-minute chart. Entry is at the IFVG close, stop below the "
    "IFVG low, break even at the internal equal high, and target is the external equal high above.<br/><br/>"
    "Result: The trade triggers, hits break even, and then runs to full TP within minutes. "
    "The entire process takes 15-30 minutes.",
    sB))

elements.append(Paragraph("Example: Short Setup", sH2))
elements.append(Paragraph(
    "Same structure but inverted. Price opens and rallies above internal resistance (manipulation), "
    "tapping into a bearish FVG. NQ makes a lower high while ES makes a higher high "
    "(bearish SMT). Price reverses down with an IFVG. Entry on the IFVG, stop above, "
    "target the external low below.",
    sB))

elements.append(Paragraph(
    '\u201cWe have New York session open, price manipulates lower. We waited for price to tap into '
    'this 15-minute gap and create a bullish SMT with ES. This is our manipulation leg. '
    'We take out all the retail, we immediately reverse.\u201d \u2014 EzTrades',
    sQ))
elements.append(PageBreak())

# ════════════════════════════════════════════════════════
# 12. RISK MANAGEMENT
# ════════════════════════════════════════════════════════
elements.append(Paragraph("12. Risk Management", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "The strategy's high win rate (70%+) comes from strict adherence to the setup criteria. "
    "But even the best setups can fail. Here is the risk framework:",
    sB))

elements.append(Paragraph("Position Sizing", sH2))
elements.append(Paragraph(
    "&bull; Risk 1-2% of account per trade<br/>"
    "&bull; The stop is tight (typically 5-10 points on NQ), so position size should be adjusted "
    "accordingly<br/>"
    "&bull; For prop firm evaluations, reduce risk to 0.25-0.5% per trade",
    sB))

elements.append(Paragraph("Stop Loss Placement", sH2))
elements.append(Paragraph(
    "&bull; Primary: Below the IFVG displacement candle low (longs) or above its high (shorts)<br/>"
    "&bull; Secondary: Below the manipulation low (longs) if you want more room<br/>"
    "&bull; Never move your stop loss wider after entry. Only tighten it.",
    sB))

elements.append(Paragraph("Take Profit Strategy", sH2))
elements.append(Paragraph(
    "&bull; <b>Partial (50%):</b> Take partial profits at the first internal structure (break even level)<br/>"
    "&bull; <b>Break Even:</b> Once partial is taken, move stop to break even on remaining position<br/>"
    "&bull; <b>Full TP:</b> External DOL (equal high/low, trendline, or obvious swing point)<br/>"
    "&bull; Typical RR: 1.5:1 to 2:1",
    sB))

elements.append(Paragraph("When to Skip", sH2))
elements.append(Paragraph(
    "The strategy is 'mechanical' for a reason. Skip trades when:<br/>"
    "&bull; No clear DOL is visible before the open<br/>"
    "&bull; No higher timeframe FVG is providing delivery context<br/>"
    "&bull; No SMT divergence forms at the manipulation point<br/>"
    "&bull; The reversal is not V-shaped (slow, choppy turn)<br/>"
    "&bull; It's Friday (the video mentions they didn't trade Friday)<br/>"
    "&bull; Major news events are within 30 minutes",
    sB))

elements.append(Paragraph(
    '"My risk reward is not the highest. I\'m not claiming I hit 1:5, 1:10 risk reward trades. '
    'I mainly go for base hit trades, but I have a 70% plus win rate because I\'m waiting for '
    'all of these confluences to line up." \u2014 EzTrades',
    sQ))

# ── Final Disclaimer ──
elements.append(Spacer(1, 0.5*inch))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#e0e0e0"), spaceAfter=10))
elements.append(Paragraph(
    "<b>Disclaimer:</b> This guide is for educational purposes only. Trading futures, forex, and "
    "equities involves substantial risk of loss. Past performance does not guarantee future results. "
    "The strategies and concepts described are based on publicly available educational content. "
    "Always consult with a qualified financial advisor before trading.",
    ParagraphStyle("disc", parent=sB, fontSize=8, textColor=HexColor("#999999"))))

doc.build(elements)
print(f"PDF created: {path}")
print(f"Size: {os.path.getsize(path) / 1024:.0f} KB")
