# ManipulationX V.6 - Pine Script Indicator

Réplica del indicador **ManipulationX V.6** utilizado por **EzTrades** en su estrategia de trading para la sesión de Nueva York.

## Referencia

- **Video**: [How I Get A 76% Win-Rate Trading NY Session (90% Mechanical)](https://youtu.be/6nVq3RVGQFw)
- **Canal**: EzTrades
- **Indicador original**: ManipulationX V.6 (disponible en la descripción del video)

---

## Archivos del Proyecto

| Archivo | Descripción |
|---------|-------------|
| `ManipulationX_V6.pine` | Indicador principal para TradingView |
| `prompt.txt` | Prompt para recrear el indicador con IA |
| `How I Get A 76 Mechanical...txt` | Subtítulos del video |
| `frames/` | Frames extraídos del video para análisis |

---

## Componentes del Indicador

### 1. HTF Fair Value Gaps (FVG)

Los FVG son zonas de desequilibrio donde el precio dejó un "gap" entre velas. Se muestran como **cajas grises** que se extienden hasta el borde derecho del chart.

| TF | Configuración default | Max FVGs |
|----|----------------------|----------|
| 1 hour | ON | 3 |
| 15 min | ON | 6 |

**Visual:**
- Cajas grises semi-transparentes (`#b0b0b0`)
- Labels "1H FVG" y "15M FVG" al final del box
- Se extienden automáticamente (`extend=extend.right`)

**Detección:**
- **Bullish FVG**: Vela [1] alcista, `low[0] > high[2]`
- **Bearish FVG**: Vela [1] bajista, `high[0] < low[2]`

### 2. Inverse Fair Value Gap (IFVG)

Modelo de entrada principal. Ocurre cuando el precio "invierte" un FVG existente con un V-shape reversal.

**Visual:**
- Línea sólida horizontal (configurable: Solid/Dashed/Dotted)
- Zona gris pequeña marca el IFVG
- Label "IFVG" con color (verde=bull, rojo=bear)

**Detección:**
- **Bullish IFVG**: `close[1] < open[1]` y `close > high[0]` (cierra sobre bearish FVG)
- **Bearish IFVG**: `close[1] > open[1]` y `close < low[0]` (cierra bajo bullish FVG)

**Settings del video:**
- Source: Chart
- Line Style: Solid
- Line Width: 1
- Minimum Size: 1
- Size Filter: ON

### 3. SMT Divergence (Smart Money Technique)

Divergencia entre MNQ y ES (proxy de MES). Uno hace higher high/low mientras el otro hace lower low/high.

**Visual:**
- Label "SMT" pequeño cerca del swing point
- Verde = Bullish SMT
- Rojo = Bearish SMT

**Detección:**
- **Bullish SMT**: ES hace lower low, MNQ hace higher low
- **Bearish SMT**: ES hace higher high, MNQ hace lower high
- Swing lookback configurable (default: 3)

### 4. Entry Markers (Continuation/Reversal)

**Visual:**
- **"C"** (Continuation): Cuadrado negro con texto blanco
- **"R"** (Reversal): Cuadrado verde (bull) o rojo (bear) con texto blanco

**Detección:**
- Continuation: Misma dirección que la tendencia actual
- Reversal: Patrón V-shape (cierra más allá del candle anterior)

### 5. Liquidity (Equal Highs/Lows)

**Visual:**
- Línea horizontal dashed gris
- Label "$$$" al final

**Detección:**
- Equal highs/lows con tolerancia de 0.1%
- Basado en pivot high/low con lookback de 5

### 6. Killzones (Opcional)

| Zona | Horario | Color |
|------|---------|-------|
| New York | 09:30 - 11:00 ET | Amarillo |
| London | 02:30 - 04:00 ET | Azul |
| Custom | 09:30 - 23:00 ET | Púrpura |

---

## Configuración en TradingView

### Paso 1: Preparar el chart
1. Abre TradingView
2. Busca `CME_MINI:MNQ1!` (Nasdaq futures)
3. Selecciona timeframe de 1min, 3min o 5min para entries

### Paso 2: Agregar el indicador
1. Ve a **Pine Editor** (parte inferior)
2. Haz clic en **Open** → **New indicator**
3. Copia el contenido completo de `ManipulationX_V6.pine`
4. Haz clic en **Add to chart**

### Paso 3: Configurar (según el video)
```
Entries:
  ✓ Continuations (C)
  ✓ Reversals (R)

Killzones:
  ☐ Use Killzones (desactivado por defecto)

IFVG:
  ✓ Show IFVGs
  Source: Chart
  Line Style: Solid
  Line Width: 1
  Minimum Size: 1
  ✓ Size Filter

HTF FVG:
  ✓ Show Internal Liquidity (FVG) - 1 hour
  ✓ Show Text
  ☐ Extend FVG
  Max FVGs: 3

  ✓ Show Internal Liquidity (FVG) - 15 min
  ✓ Show Text
  ☐ Extend FVG
  Max FVGs: 6

SMT Divergence:
  ✓ Show SMT
  Swing Lookback: 3

Liquidity:
  ✓ Show Liquidity
```

### Paso 4: Alerts
1. Haz clic en el indicador en el chart
2. Ve a **Alerts** → **Add Alert**
3. Condiciones disponibles:
   - `IFVG Bullish` / `IFVG Bearish`
   - `SMT Bullish` / `SMT Bearish`

---

## Estrategia Completa (del video)

### Checklist de la Estrategia

```
1. □ Esperar apertura NY (9:30 AM ET / 13:30 UTC)
2. □ NO operar primeros 5 minutos (manipulación inicial)
3. □ Marcar Draws on Liquidity (equal highs, trendline liq)
4. □ Marcar FVG de 15min y 1h
5. □ Esperar manipulación (push inicial contra la dirección)
6. □ Buscar SMT divergence (confluencia extra)
7. □ Esperar V-shape reversal con IFVG
8. □ Entrar en IFVG con stop bajo/altar candle anterior
9. □ Break even en structure level
10. □ Target: DOL (equal highs/lows, London H/L)
```

### Ejemplo de Setup A+

```
1. NY abre a 13:30 UTC
2. Precio manipula hacia abajo
3. Toca FVG de 15min bullish
4. ES hace lower low, MNQ hace higher low (SMT Bull)
5. Precio rebota con V-shape
6. Aparece IFVG bullish en 1min
7. ENTRADA: Long en IFVG
8. SL: Bajo candle anterior
9. BE: En internal structure high
10. TP: Equal highs / London high
```

### Macro Window

El video menciona que el **9:50-10:00 AM ET** es una ventana clave para reversal/volumen.

---

## Notas Importantes

- **Ticker**: El indicador usa `CME_MINI:ES1!` como proxy de MES para el SMT
- **No es señal automática**: Es una herramienta de análisis. Siempre confirma la estructura
- **Gestión de riesgo**: El video recomienda BE rápido y targets conservadores (base hits)
- **Timeframes**: Usa 1min/3min para entries, 15min/1h para contexto

---

## Créditos

- **Estrategia original**: EzTrades (ManipulationX V.6)
- **Indicador**: Réplica generada con análisis de video
