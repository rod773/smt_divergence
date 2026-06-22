from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.platypus.flowables import HRFlowable
import os

path = r"D:\Descargas\smt_divergence\ManipulationX_V6_Tutorial.pdf"
doc = SimpleDocTemplate(path, pagesize=letter,
    rightMargin=0.75*inch, leftMargin=0.75*inch,
    topMargin=0.75*inch, bottomMargin=0.75*inch)

styles = getSampleStyleSheet()

sTitle = ParagraphStyle("Title2", parent=styles["Title"], fontSize=26, spaceAfter=6, textColor=HexColor("#1a237e"))
sSub = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=14, spaceAfter=20, textColor=HexColor("#546e7a"), alignment=TA_CENTER)
sH1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18, spaceBefore=18, spaceAfter=10, textColor=HexColor("#1a237e"))
sH2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, spaceBefore=14, spaceAfter=8, textColor=HexColor("#283593"))
sBody = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, spaceAfter=8, leading=14)
sBullet = ParagraphStyle("Bullet", parent=sBody, leftIndent=20, spaceAfter=4)
sCode = ParagraphStyle("Code", parent=styles["Code"], fontSize=8, spaceAfter=6, leftIndent=10, backColor=HexColor("#f5f5f5"))
sNote = ParagraphStyle("Note", parent=sBody, leftIndent=15, rightIndent=15, spaceAfter=10, spaceBefore=10,
    backColor=HexColor("#e8eaf6"), borderPadding=8, borderRadius=3)

elements = []

# ── Cover ──
elements.append(Spacer(1, 1.5*inch))
elements.append(Paragraph("ManipulationX V.6", sTitle))
elements.append(Paragraph("TradingView Indicator Tutorial", sSub))
elements.append(HRFlowable(width="60%", thickness=1, color=HexColor("#1a237e"), spaceAfter=20))
elements.append(Spacer(1, 0.3*inch))
elements.append(Paragraph("SMT Divergence &bull; Fair Value Gaps &bull; Inverse FVGs", ParagraphStyle("sub2", parent=sBody, fontSize=12, alignment=TA_CENTER, textColor=HexColor("#37474f"))))
elements.append(Paragraph("Draws on Liquidity &bull; Killzones &bull; Entry Signals", ParagraphStyle("sub3", parent=sBody, fontSize=12, alignment=TA_CENTER, textColor=HexColor("#37474f"))))
elements.append(Spacer(1, 0.5*inch))
elements.append(Paragraph("Based on the NY Session trading strategy", ParagraphStyle("credit", parent=sBody, fontSize=10, alignment=TA_CENTER, textColor=HexColor("#78909c"))))
elements.append(PageBreak())

# ── TOC ──
elements.append(Paragraph("Table of Contents", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))
toc_items = [
    "1.  Overview",
    "2.  Installation",
    "3.  Settings Reference",
    "4.  Fair Value Gaps (FVG)",
    "5.  Inverse Fair Value Gaps (IFVG)",
    "6.  SMT Divergence",
    "7.  Draws on Liquidity (DOL)",
    "8.  Killzones",
    "9.  Reversals &amp; Continuations",
    "10. Strategy Checklist",
    "11. Alerts",
    "12. Trading the Strategy",
]
for item in toc_items:
    elements.append(Paragraph(item, sBody))
elements.append(PageBreak())

# ── 1. Overview ──
elements.append(Paragraph("1. Overview", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))
elements.append(Paragraph(
    "ManipulationX V.6 is a comprehensive TradingView indicator that automates the NY Session trading strategy "
    "popularized by EzTrades. It encodes the entire decision framework into visual chart elements: "
    "Fair Value Gaps for delivery context, Inverse FVGs for entry timing, SMT Divergence between NQ and ES for "
    "additional confluence, Draws on Liquidity for target levels, and Killzones for session awareness.",
    sBody))
elements.append(Spacer(1, 0.1*inch))

elements.append(Paragraph("Core Strategy (3-Step Checklist)", sH2))
steps = [
    "<b>1. NY Session (9:30am ET):</b> Only trade during the New York session open. Mark the session on your chart.",
    "<b>2. Mark out DOLs/FVGs:</b> Identify Draws on Liquidity (equal highs/lows, trendline liquidity) and "
    "Higher Time Frame Fair Value Gaps (15m, 1h) that provide delivery context.",
    "<b>3. Entry Model (iFVG):</b> Wait for the initial manipulation move, then look for an Inverse Fair Value Gap "
    "as your entry trigger. Add SMT divergence for A+ setups.",
]
for s in steps:
    elements.append(Paragraph(s, sBullet))

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph(
    "The indicator shows all three checklist items directly on your chart so you never lose sight of the plan.",
    sNote))
elements.append(PageBreak())

# ── 2. Installation ──
elements.append(Paragraph("2. Installation", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

steps_install = [
    ("Step 1", "Open TradingView and go to the Pine Editor tab at the bottom."),
    ("Step 2", "Delete any existing code and paste the entire ManipulationX_V6.pine script."),
    ("Step 3", 'Click "Save As" and name it "ManipulationX V.6".'),
    ("Step 4", 'Apply the indicator to your chart: Indicators &rarr; My Scripts &rarr; ManipulationX V.6.'),
    ("Step 5", "Use on NQ1! (Nasdaq 100 E-mini Futures) for best results. The SMT comparison defaults to ES1!."),
]
for i, (step, desc) in enumerate(steps_install):
    elements.append(Paragraph(f"<b>{step}:</b> {desc}", sBody))

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph(
    "<b>Recommended Chart Setup:</b> 2-minute or 3-minute timeframe for the main chart. "
    "Keep the 15-minute and 1-hour timeframes in mind for FVG context. Use during the NY session (9:30am - 4:00pm ET).",
    sNote))
elements.append(PageBreak())

# ── 3. Settings Reference ──
elements.append(Paragraph("3. Settings Reference", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))
elements.append(Paragraph("The indicator has the following settings groups:", sBody))
elements.append(Spacer(1, 0.1*inch))

settings_data = [
    ["Group", "Setting", "Default", "Description"],
    ["IFVG", "Show iFVGs", "On", "Show/hide Inverse FVG entry labels"],
    ["IFVG", "IFVG Line Style", "Solid", "Line style for IFVG zones (Solid/Dashed/Dotted)"],
    ["IFVG", "IFVG Line Width", "2", "Width of IFVG lines"],
    ["IFVG", "Minimum Size", "0.0", "Minimum IFVG body size to filter noise"],
    ["IFVG", "Size Filter", "On", "Enable/disable the minimum size filter"],
    ["HTF FVG", "Show 15m FVG", "On", "15-minute Fair Value Gap boxes"],
    ["HTF FVG", "Show 1h FVG", "On", "1-hour Fair Value Gap boxes"],
    ["HTF FVG", "Show 4h FVG", "Off", "4-hour Fair Value Gap boxes"],
    ["HTF FVG", "Mitigation Method", "100%", "How FVGs are considered mitigated"],
    ["HTF FVG", "Show Internal", "On", "Show internal FVGs"],
    ["HTF FVG", "Show Text", "On", "Show timeframe label on FVG boxes"],
    ["HTF FVG", "Extend FVG", "On", "Extend FVG lines to the right"],
    ["Liquidity", "Show Draws on Liquidity", "On", "Show/hide DOL markers"],
    ["Liquidity", "Liquidity Lookback", "50", "Bars to scan for equal highs/lows"],
    ["SMT", "Show SMT Divergence", "On", "Show/hide SMT divergence labels"],
    ["SMT", "SMT Symbol", "ES1!", "Symbol to compare for divergence"],
    ["Killzones", "Use Killzones", "On", "Enable session background zones"],
    ["Killzones", "New York KZ", "On", "NY session background (09:30-16:00 ET)"],
    ["Killzones", "London KZ", "Off", "London session background"],
    ["Reversals", "Show Reversals", "On", "Show V-shape reversal tags"],
    ["Continuations", "Show Continuations", "Off", "Show continuation tags"],
]

t = Table(settings_data, colWidths=[1*inch, 1.3*inch, 0.7*inch, 2.8*inch])
t.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("BACKGROUND", (0,0), (-1,0), HexColor("#1a237e")),
    ("TEXTCOLOR", (0,0), (-1,0), white),
    ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("GRID", (0,0), (-1,-1), 0.5, HexColor("#c5cae9")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, HexColor("#f5f5f5")]),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
]))
elements.append(t)
elements.append(PageBreak())

# ── 4. FVG ──
elements.append(Paragraph("4. Fair Value Gaps (FVG)", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("What is a Fair Value Gap?", sH2))
elements.append(Paragraph(
    "A Fair Value Gap (FVG) occurs when a candle opens and closes outside the range of the previous candle, "
    "creating an imbalance zone. These zones act as magnets for price - price tends to revisit them before continuing "
    "the trend. This is also known as an imbalance or delivery gap.",
    sBody))

elements.append(Paragraph("How the Indicator Shows FVGs", sH2))
elements.append(Paragraph(
    "The indicator draws colored boxes for FVGs on three timeframes:",
    sBody))
bullets_fvg = [
    "<b>Green boxes</b> = Bullish FVG (price is expected to deliver higher from this zone)",
    "<b>Red boxes</b> = Bearish FVG (price is expected to deliver lower from this zone)",
    "Each box is labeled with the timeframe (15m, 1h, 4h)",
    "Lines extend to the right so you can see active FVGs ahead of price",
    "FVGs are higher timeframe context - they show you <b>where</b> price wants to go",
]
for b in bullets_fvg:
    elements.append(Paragraph(b, sBullet))

elements.append(Paragraph("How to Use FVGs in Trading", sH2))
elements.append(Paragraph(
    "Higher timeframe FVGs (15m, 1h) define your bias:<br/>"
    "&bull; If price is inside a bullish FVG zone, prefer long positions<br/>"
    "&bull; If price is inside a bearish FVG zone, prefer short positions<br/>"
    "&bull; Never short into a bullish FVG or long into a bearish FVG<br/>"
    "&bull; The best trades come when price sweeps liquidity and taps into a higher timeframe FVG simultaneously",
    sBody))

elements.append(Spacer(1, 0.1*inch))
elements.append(Paragraph(
    '"Ideally, for an A+ setup, I\'m looking for a sweep of external liquidity into an untapped 1-hour fair value gap." '
    "&mdash; EzTrades",
    sNote))
elements.append(PageBreak())

# ── 5. IFVG ──
elements.append(Paragraph("5. Inverse Fair Value Gaps (IFVG)", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("What is an Inverse FVG?", sH2))
elements.append(Paragraph(
    "An Inverse Fair Value Gap (IFVG) is the <b>entry model</b> of this strategy. It forms when:",
    sBody))
bullets_ifvg = [
    "<b>Bullish IFVG:</b> A bearish 1-minute candle closes below the previous candle's low (manipulation), "
    "then the next candle closes back above that bearish candle's high (inversion). This traps sellers "
    "and signals a reversal up.",
    "<b>Bearish IFVG:</b> A bullish 1-minute candle closes above the previous candle's high (manipulation), "
    "then the next candle closes back below that bullish candle's low (inversion). This traps buyers "
    "and signals a reversal down.",
    "In simpler terms: price makes a false breakout, reverses, and closes back through the breakout range.",
]
for b in bullets_ifvg:
    elements.append(Paragraph(b, sBullet))

elements.append(Paragraph("The V-Shape Inversion", sH2))
elements.append(Paragraph(
    "The most powerful IFVG setups come in the form of a <b>V-shape inversion</b> - a sharp move down "
    "followed by an immediate, aggressive reversal up (or vice versa for shorts). The indicator will "
    "mark these with a 'REV' label when detected alongside the IFVG.<br/><br/>"
    "Key rules for IFVG entries:<br/>"
    "&bull; Wait for the first 5 minutes after NY open to let manipulation play out<br/>"
    "&bull; The IFVG should appear on the 1-minute timeframe<br/>"
    "&bull; Best when combined with SMT divergence and higher timeframe FVG delivery<br/>"
    "&bull; Set stop loss below the IFVG candle low (longs) or above the high (shorts)",
    sBody))

elements.append(Spacer(1, 0.1*inch))
elements.append(Paragraph(
    "The indicator filters small IFVGs using the Minimum Size and Size Filter settings to reduce noise.",
    sNote))
elements.append(PageBreak())

# ── 6. SMT ──
elements.append(Paragraph("6. SMT Divergence", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("What is SMT Divergence?", sH2))
elements.append(Paragraph(
    "SMT (Smart Money Technique) Divergence compares two correlated assets - typically NQ (Nasdaq) and "
    "ES (S&amp;P 500) - and looks for discrepancies between their swing points. When one asset makes a "
    "lower low while the other makes a higher low, this divergence signals an impending reversal.",
    sBody))

elements.append(Paragraph("Types of SMT Divergence", sH2))
bullets_smt = [
    "<b>Bullish SMT (Blue Label):</b> NQ makes a higher low while ES makes a lower low at the same "
    "swing point. This means ES is 'confirming' the low while NQ is 'rejecting' it - a bullish signal.",
    "<b>Bearish SMT (Orange Label):</b> NQ makes a lower high while ES makes a higher high. NQ is "
    "weaker than ES at this swing high - a bearish signal.",
    "The indicator uses a 3-bar swing detection to identify valid swing points, reducing false signals.",
]
for b in bullets_smt:
    elements.append(Paragraph(b, sBullet))

elements.append(Paragraph("Why SMT Divergence Works", sH2))
elements.append(Paragraph(
    "Nasdaq and S&amp;P 500 are highly correlated but not perfectly synchronized. Algorithms and smart money "
    "often use one to confirm moves in the other. When they diverge at key swing points, it reveals "
    "manipulation - one asset is being used as 'liquidity' for the other's reversal.<br/><br/>"
    "In the video, EzTrades shows how a bullish SMT divergence at the NY open, combined with a higher "
    "timeframe FVG and IFVG entry, creates a 76%+ win-rate setup.",
    sBody))

elements.append(Spacer(1, 0.1*inch))
elements.append(Paragraph(
    '<b>Pro Tip:</b> Change the "SMT Symbol" setting to compare NQ with any correlated asset. '
    "The classic pair is NQ1! / ES1!.",
    sNote))
elements.append(PageBreak())

# ── 7. DOL ──
elements.append(Paragraph("7. Draws on Liquidity (DOL)", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("What are Draws on Liquidity?", sH2))
elements.append(Paragraph(
    "Draws on Liquidity (DOL) are price levels where stop losses and orders cluster. These are targets "
    "that price is 'drawn to' because hitting them unlocks liquidity. The two main types are:",
    sBody))

bullets_dol = [
    "<b>Equal Highs (EQH):</b> Two or more swing highs at the same price level. When price approaches "
    "this level, traders place stops above, creating a liquidity pool for smart money to target.",
    "<b>Equal Lows (EQL):</b> Two or more swing lows at the same level. Stops below create a liquidity pool.",
    "<b>Trendline Liquidity:</b> Consecutive higher highs or lower lows along a trendline. "
    "Breaking the trendline releases this liquidity.",
    "<b>Swing DOL:</b> The most recent significant swing high or low marked with a 'DOL' label.",
]
for b in bullets_dol:
    elements.append(Paragraph(b, sBullet))

elements.append(Paragraph("How to Use DOLs", sH2))
elements.append(Paragraph(
    "1. Identify DOL levels <b>before</b> NY open (marked in purple)<br/>"
    "2. These are your <b>target levels</b> (take profit zones)<br/>"
    "3. Price often sweeps external lows (manipulation) then reverses toward highs (distribution)<br/>"
    "4. The classic setup: price manipulates below a DOL low, then reverses to target DOL highs above",
    sBody))
elements.append(PageBreak())

# ── 8. Killzones ──
elements.append(Paragraph("8. Killzones", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "Killzones mark specific trading sessions on your chart with background colors:",
    sBody))
bullets_kz = [
    "<b>NY Session (09:30 - 16:00 ET):</b> The primary trading session. Most volume, most moves. "
    "The strategy is designed specifically for the NY open.",
    "<b>London Session (03:00 - 12:00 ET):</b> Optional secondary session. Lower volume, "
    "but can provide pre-NY context.",
    "The session label appears at the start of each killzone.",
    "Enable/disable each session independently in settings.",
]
for b in bullets_kz:
    elements.append(Paragraph(b, sBullet))

elements.append(Paragraph("Why Killzones Matter", sH2))
elements.append(Paragraph(
    "The NY session open (9:30am EST) is when the highest volume enters the market. The first 10-20 minutes "
    "typically feature a manipulation move (often a sweep of external lows), followed by a reversal. "
    "This predictable behavior is the foundation of the entire strategy.<br/><br/>"
    "The indicator's checklist reminds you: trade only ONE session (NY), at market open.",
    sBody))
elements.append(PageBreak())

# ── 9. Reversals & Continuations ──
elements.append(Paragraph("9. Reversals &amp; Continuations", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "The indicator can optionally mark two additional entry/exit patterns:",
    sBody))

elements.append(Paragraph("Reversals (REV)", sH2))
elements.append(Paragraph(
    "A V-shape reversal occurs when price makes an aggressive move in one direction and immediately reverses "
    "with equal force. The indicator detects these when a sharp move down is followed by a close above the "
    "midpoint of the prior range, coinciding with an IFVG signal. These are the highest-probability entries.",
    sBody))

elements.append(Paragraph("Continuations (CONT)", sH2))
elements.append(Paragraph(
    "Continuation patterns occur when price moves consistently in one direction without significant pullback. "
    "These are lower-probability but can be used for adding to existing positions. Disabled by default.",
    sBody))
elements.append(PageBreak())

# ── 10. Checklist ──
elements.append(Paragraph("10. Strategy Checklist", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "The indicator displays a permanent checklist overlay on your chart showing the three core steps:",
    sBody))

steps_final = [
    ("1. NY session (9:30am est)", "Only trade during NY session. Mark the session on your chart."),
    ("2. Mark out DOLs/FVGs", "Identify Draws on Liquidity targets and higher timeframe FVGs for delivery context."),
    ("3. Entry model (iFVG)", "Wait for manipulation, then enter on the IFVG with SMT divergence for confluence."),
]
for title, desc in steps_final:
    elements.append(Paragraph(f"<b>{title}</b> &mdash; {desc}", sBody))
    elements.append(Spacer(1, 0.05*inch))

elements.append(Paragraph("A+ Setup Requirements", sH2))
elements.append(Paragraph(
    "The video identifies the ideal A+ setup as:<br/>"
    "1. NY session open at 9:30am ET<br/>"
    "2. Initial manipulation move (first 5-15 minutes)<br/>"
    "3. Higher timeframe FVG providing delivery context<br/>"
    "4. SMT divergence between NQ and ES<br/>"
    "5. IFVG entry signal (V-shape preferred)<br/>"
    "6. Clear DOL target for take profit",
    sBody))
elements.append(PageBreak())

# ── 11. Alerts ──
elements.append(Paragraph("11. Alerts", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "The indicator includes four alert conditions that can be used for real-time notifications:",
    sBody))

alerts_data = [
    ["Alert Name", "Condition", "Use"],
    ["Bullish SMT", "Bullish SMT divergence detected", "Get notified when NQ/ES diverge at swing lows"],
    ["Bearish SMT", "Bearish SMT divergence detected", "Get notified when NQ/ES diverge at swing highs"],
    ["Bullish IFVG", "Bullish IFVG entry signal", "Get notified of long entry opportunities"],
    ["Bearish IFVG", "Bearish IFVG entry signal", "Get notified of short entry opportunities"],
]
t2 = Table(alerts_data, colWidths=[1.3*inch, 2*inch, 2.5*inch])
t2.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("BACKGROUND", (0,0), (-1,0), HexColor("#1a237e")),
    ("TEXTCOLOR", (0,0), (-1,0), white),
    ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("GRID", (0,0), (-1,-1), 0.5, HexColor("#c5cae9")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, HexColor("#f5f5f5")]),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
]))
elements.append(t2)

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph(
    "To set up an alert: Right-click the indicator &rarr; Add Alert &rarr; Select condition &rarr; Choose action.",
    sBody))
elements.append(PageBreak())

# ── 12. Trading the Strategy ──
elements.append(Paragraph("12. Trading the Strategy", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("Complete Trade Walkthrough", sH2))
elements.append(Paragraph(
    "Here is how a complete trade works using the indicator, based on the strategy in the video:",
    sBody))

walkthrough = [
    ("<b>Pre-Market (Before 9:30am):</b>", 
     "Mark out DOLs - look for equal highs/lows and trendline liquidity. Note active higher timeframe FVGs "
     "(15m, 1h) that give delivery context. You don't know direction yet."),
    ("<b>NY Open (9:30am):</b>",
     "Watch the first 5-15 minutes for the manipulation move. Price often sweeps a recent low or high "
     "(taking out stops) before reversing."),
    ("<b>Look for SMT Divergence:</b>",
     "As price makes its manipulation low, check if ES is making a lower low while NQ holds a higher low. "
     "A bull SMT label at the low is a powerful bullish confluence."),
    ("<b>Wait for IFVG:</b>",
     "After the manipulation, wait for an IFVG to form on the 1-minute chart. The ideal entry is a "
     "V-shape inversion where price immediately reverses and closes through the manipulation range."),
    ("<b>Enter the Trade:</b>",
     "Enter on the IFVG candle close. Stop loss below the IFVG candle low (for longs) or above the high "
     "(for shorts). Break even at the most internal structure high/low."),
    ("<b>Take Profit:</b>",
     "Target the external DOL (equal high/low) for full TP. Take partial profits at key structure levels. "
     "Typical RR is around 1.5:1 with a 70%+ win rate."),
]
for title, desc in walkthrough:
    elements.append(Paragraph(title, sBody))
    elements.append(Paragraph(desc, sBullet))
    elements.append(Spacer(1, 0.05*inch))

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph(
    '"I mainly go for base hit trades, but I have a 70% plus win rate because I\'m waiting for '
    "all of these confluences to line up.\" &mdash; EzTrades",
    sNote))

# ── Risk Disclaimer ──
elements.append(Spacer(1, 0.5*inch))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#e0e0e0"), spaceAfter=10))
elements.append(Paragraph(
    "<b>Disclaimer:</b> This indicator is for educational purposes only. Trading futures involves substantial risk. "
    "Past performance does not guarantee future results. Always use proper risk management.",
    ParagraphStyle("disc", parent=sBody, fontSize=8, textColor=HexColor("#999999"))))

doc.build(elements)
print(f"PDF created: {path}")
print(f"Size: {os.path.getsize(path) / 1024:.0f} KB")
