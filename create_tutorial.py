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
elements.append(Paragraph("Session Levels &bull; Liquidity Sweeps &bull; Entry Signals", ParagraphStyle("sub3", parent=sBody, fontSize=12, alignment=TA_CENTER, textColor=HexColor("#37474f"))))
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
    "7.  Session Levels & Liquidity Sweeps",
    "8.  Draws on Liquidity (DOL)",
    "9.  Support / Resistance Levels",
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
    "Fair Value Gaps for delivery context, Inverse FVGs for entry timing, SMT Divergence between MNQ and MES for "
    "additional confluence, Draws on Liquidity for target levels, Session levels with liquidity sweep detection, "
    "and Killzones for session awareness.",
    sBody))
elements.append(Spacer(1, 0.1*inch))

elements.append(Paragraph("Core Strategy (4-Step Checklist)", sH2))
steps = [
    "<b>1. NY Session (9:30am ET):</b> Only trade during the New York session open. Mark the session on your chart.",
    "<b>2. Mark out DOLs/FVGs:</b> Identify Draws on Liquidity (swing highs/lows) and "
    "Higher Time Frame Fair Value Gaps (15m, 1h) that provide delivery context.",
    "<b>3. Entry Model (iFVG):</b> Wait for the initial manipulation move, then look for an Inverse Fair Value Gap "
    "as your entry trigger.",
    "<b>4. SMT Divergence:</b> Add SMT divergence between MNQ and MES for A+ setup confluence.",
]
for s in steps:
    elements.append(Paragraph(s, sBullet))

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph(
    "The indicator shows all four checklist items directly on your chart so you never lose sight of the plan.",
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
    ("Step 5", "Use on MNQ1! (Micro Nasdaq 100 Futures) for best results. SMT comparison defaults to MES1!."),
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
    ["HTF FVG", "Show 15m FVG", "On", "15-minute Fair Value Gap boxes"],
    ["HTF FVG", "Show 1h FVG", "On", "1-hour Fair Value Gap boxes"],
    ["HTF FVG", "Show 4h FVG", "Off", "4-hour Fair Value Gap boxes"],
    ["HTF FVG", "Min FVG Gap (ticks)", "8", "Minimum gap size to draw a box (filters noise)"],
    ["HTF FVG", "FVG only during NY session", "On", "Only show FVG boxes within NY session hours"],
    ["IFVG", "Show iFVGs", "On", "Show/hide Inverse FVG entry labels on 1m"],
    ["SMT", "Show SMT Divergence", "On", "Show/hide SMT divergence labels and pivot lines"],
    ["SMT", "SMT Symbol", "MES1!", "Symbol to compare for divergence (MES, ES, etc.)"],
    ["Sweep", "Show Liquidity Sweeps", "On", "Show/hide sweep labels and session level lines"],
    ["Sweep", "Sweep Threshold (ticks)", "2", "Minimum wick past level to count as sweep"],
    ["DOL", "Show DOL Levels", "On", "Show/hide Draw on Liquidity labels"],
    ["DOL", "Min DOL Swing (ticks)", "16", "Minimum swing size to draw a DOL label"],
    ["DOL", "DOL only during NY session", "On", "Only show DOL within NY session"],
    ["S/R", "Show S/R Levels", "On", "Show/hide Support/Resistance boxes"],
    ["S/R", "Min S/R Swing (ticks)", "12", "Minimum swing size to draw S/R box"],
    ["S/R", "S/R only during NY session", "On", "Only show S/R within NY session"],
    ["Killzones", "Use Killzones", "On", "Enable session background zones"],
    ["Killzones", "New York KZ", "On", "NY session background (09:30-16:00 ET)"],
    ["Killzones", "London KZ", "Off", "London session background"],
]

t = Table(settings_data, colWidths=[1*inch, 1.5*inch, 0.7*inch, 2.6*inch])
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
    "A Fair Value Gap (FVG) occurs when a candle opens and closes outside the range of two candles prior, "
    "creating a three-candle imbalance zone. These zones act as magnets for price - price tends to revisit "
    "them before continuing the trend. Also known as an imbalance or delivery gap.",
    sBody))

elements.append(Paragraph("How the Indicator Shows FVGs", sH2))
elements.append(Paragraph(
    "The indicator draws colored boxes for FVGs on three timeframes:",
    sBody))
bullets_fvg = [
    "<b>Green boxes</b> = Bullish FVG (price expected to deliver higher from this zone)",
    "<b>Red boxes</b> = Bearish FVG (price expected to deliver lower from this zone)",
    "Each box is labeled with the timeframe (15M, 1H, 4H)",
    "Boxes only draw if the gap exceeds the Min FVG Gap setting (default 8 ticks)",
    "Optional NY-session-only mode reduces clutter outside trading hours",
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
    "<b>Bullish IFVG:</b> A bearish 1m candle closes below the prior low (manipulation), "
    "then the next candle closes back above that bearish candle's high (inversion). Traps sellers, signals reversal up.",
    "<b>Bearish IFVG:</b> A bullish 1m candle closes above the prior high (manipulation), "
    "then the next candle closes back below that bullish candle's low (inversion). Traps buyers, signals reversal down.",
    "In simpler terms: price makes a false breakout, reverses, and closes back through the breakout range.",
]
for b in bullets_ifvg:
    elements.append(Paragraph(b, sBullet))

elements.append(Paragraph("Key Rules for IFVG Entries", sH2))
elements.append(Paragraph(
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
    "SMT (Smart Money Technique) Divergence compares two correlated assets - typically MNQ (Micro Nasdaq) and "
    "MES (Micro S&amp;P 500) - and looks for discrepancies between their swing points. When one asset makes a "
    "lower low while the other makes a higher low, this divergence signals an impending reversal.",
    sBody))

elements.append(Paragraph("How the Indicator Shows It", sH2))
elements.append(Paragraph(
    "When divergence is detected, the indicator draws <b>two angled lines</b> connecting the pivots:",
    sBody))
bullets_smt = [
    "<b>Bullish SMT (Blue):</b> Green line between NQ pivot lows (higher lows) + orange line between "
    "ES/MES pivot lows (lower lows). The split lines visually show the divergence.",
    "<b>Bearish SMT (Orange):</b> Orange line between NQ pivot highs (lower highs) + green line between "
    "ES/MES pivot highs (higher highs).",
    "Each detection also shows a blue/orange SMT label at the swing point.",
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
    "The classic pair is MNQ1! / MES1!.",
    sNote))
elements.append(PageBreak())

# ── 7. Session Levels & Sweeps ──
elements.append(Paragraph("7. Session Levels &amp; Liquidity Sweeps", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("Session Levels", sH2))
elements.append(Paragraph(
    "The indicator tracks two trading sessions and draws horizontal lines at their highs and lows when each session ends:",
    sBody))
bullets_sess = [
    "<b>Asia Session (19:00-03:00 ET):</b> High and low drawn at 3:00am ET",
    "<b>London Session (03:00-12:00 ET):</b> High and low drawn at 12:00pm ET",
    "These levels act as support/resistance for the remainder of the trading day.",
]
for b in bullets_sess:
    elements.append(Paragraph(b, sBullet))

elements.append(Paragraph("Liquidity Sweep Detection", sH2))
elements.append(Paragraph(
    "A liquidity sweep occurs when price breaks beyond a key level (session high/low) briefly to trigger stop losses, "
    "then reverses. The indicator detects sweeps of completed session levels:",
    sBody))
bullets_sweep = [
    "<b>Bearish Sweep (Red label):</b> Price crosses above the session high by the threshold ticks, but the candle "
    "closes back below the high. Smart money swept buy stops above the level.",
    "<b>Bullish Sweep (Green label):</b> Price crosses below the session low by the threshold ticks, but the candle "
    "closes back above the low. Smart money swept sell stops below the level.",
    "Each level can only trigger ONE sweep label per session (avoid re-labeling).",
    "Threshold configurable via the Sweep Threshold setting (default 2 ticks).",
]
for b in bullets_sweep:
    elements.append(Paragraph(b, sBullet))
elements.append(PageBreak())

# ── 8. DOL ──
elements.append(Paragraph("8. Draws on Liquidity (DOL)", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph("What are Draws on Liquidity?", sH2))
elements.append(Paragraph(
    "Draws on Liquidity (DOL) are price levels where stop losses and orders cluster. These are targets "
    "that price is 'drawn to' because hitting them unlocks liquidity. The indicator marks them with 'DOL' labels.",
    sBody))

bullets_dol = [
    "<b>Swing High DOL:</b> A significant swing high where buy stops accumulate above.",
    "<b>Swing Low DOL:</b> A significant swing low where sell stops accumulate below.",
    "DOL labels alternate (high, low, high, low...) to avoid cluttering consecutive same-direction pivots.",
    "Filtered by minimum swing size (default 16 ticks) and NY-only mode.",
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

# ── 9. S/R ──
elements.append(Paragraph("9. Support / Resistance Levels", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "The indicator draws thin horizontal boxes at significant swing highs and lows to highlight support and resistance levels:",
    sBody))
bullets_sr = [
    "<b>Resistance (yellow):</b> Thin box at swing high pivots, marking potential resistance zones.",
    "<b>Support (yellow):</b> Thin box at swing low pivots, marking potential support zones.",
    "Filtered by minimum swing size (default 12 ticks) to show only significant levels.",
    "Optional NY-session-only mode reduces non-session levels.",
]
for b in bullets_sr:
    elements.append(Paragraph(b, sBullet))

elements.append(Paragraph(
    "S/R levels are drawn as 2-tick-tall boxes extending 40 bars to the right, giving a clear visual of key price levels.",
    sBody))
elements.append(PageBreak())

# ── 10. Checklist ──
elements.append(Paragraph("10. Strategy Checklist", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "The indicator displays a permanent checklist overlay on your chart showing the four core steps:",
    sBody))

steps_final = [
    ("1. NY session (9:30am est)", "Only trade during NY session."),
    ("2. Mark out DOLs/FVGs", "Identify liquidity targets and FVG delivery context."),
    ("3. Entry model (iFVG)", "Wait for manipulation, enter on IFVG."),
    ("4. SMT divergence", "Add SMT divergence for A+ confluence."),
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
    "4. SMT divergence between MNQ and MES<br/>"
    "5. IFVG entry signal (bullish or bearish)<br/>"
    "6. Clear DOL target for take profit",
    sBody))
elements.append(PageBreak())

# ── 11. Alerts ──
elements.append(Paragraph("11. Alerts", sH1))
elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#c5cae9"), spaceAfter=10))

elements.append(Paragraph(
    "The indicator includes six alert conditions for real-time notifications:",
    sBody))

alerts_data = [
    ["Alert Name", "Condition", "Use"],
    ["Bullish SMT", "Bullish SMT divergence detected at swing low", "Get notified of bullish divergence"],
    ["Bearish SMT", "Bearish SMT divergence detected at swing high", "Get notified of bearish divergence"],
    ["Bullish IFVG", "Bullish IFVG entry signal on 1m", "Get notified of long entry opportunities"],
    ["Bearish IFVG", "Bearish IFVG entry signal on 1m", "Get notified of short entry opportunities"],
    ["Bearish Sweep", "Price swept above session high and closed below", "Get notified of bearish liquidity grab"],
    ["Bullish Sweep", "Price swept below session low and closed above", "Get notified of bullish liquidity grab"],
]
t2 = Table(alerts_data, colWidths=[1.3*inch, 2.2*inch, 2.3*inch])
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
    "Here is how a complete trade works using the indicator:",
    sBody))

walkthrough = [
    ("<b>Pre-Market (Before 9:30am):</b>",
     "Mark out DOLs - look for significant swing highs/lows. Note active higher timeframe FVGs "
     "(15m, 1h) that give delivery context. Check Asia session levels for potential sweep targets."),
    ("<b>NY Open (9:30am):</b>",
     "Watch the first 5-15 minutes for the manipulation move. Price often sweeps a recent low or high "
     "(taking out stops) before reversing. Look for sweeps of Asia/London session levels."),
    ("<b>Look for SMT Divergence:</b>",
     "As price makes its manipulation low, check if MES is making a lower low while MNQ holds a higher low. "
     "A bull SMT label with pivot connection lines at the low is powerful bullish confluence."),
    ("<b>Wait for IFVG:</b>",
     "After the manipulation, wait for an IFVG to form on the 1-minute chart. The ideal entry is an "
     "inversion where price reverses and closes through the manipulation range."),
    ("<b>Enter the Trade:</b>",
     "Enter on the IFVG candle close. Stop loss below the IFVG candle low (longs) or above the high "
     "(shorts). Break even at the most internal structure high/low."),
    ("<b>Take Profit:</b>",
     "Target the external DOL (high/low) for full TP. Take partial profits at key structure levels. "
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
