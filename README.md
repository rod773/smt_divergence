# EzTrades NY Strategy - Pine Script Indicator

Indicador basado en la estrategia del canal **EzTrades** para operar la sesión de Nueva York con un 76% de win rate mecánico.

## Referencia

- **Video**: [How I Get A 76% Win-Rate Trading NY Session (90% Mechanical)](https://youtu.be/6nVq3RVGQFw)
- **Canal**: EzTrades

---

## Componentes del Indicador

### 1. SMT Divergence (Smart Money Technique)

La divergencia SMT ocurre cuando dos activos correlacionados (MNQ y MES/ES) muestran movimientos opuestos en sus swing points.

**Reglas:**
- **Bullish SMT**: ES hace un lower low mientras MNQ hace un higher low → Señal alcista
- **Bearish SMT**: ES hace un higher high mientras MNQ hace un lower high → Señal bajista

**Cómo funciona:**
- Detecta swing highs y lows en ambos mercados
- Compara la dirección de los últimos swings
- Marca con triángulo cuando hay divergencia

### 2. Fair Value Gaps (FVG)

Los FVG son zonas de desequilibrio donde el precio dejó un "gap" entre velas.

**Timeframes soportados:**
| TF | Uso |
|----|-----|
| 15min | Entry zone,delivery primario |
| 1h | Contexto de sesión |
| 1h+ | Dirección mayor |

**Tipos:**
- **Bullish FVG**: Vela alcista grande que deja gap entre candle[2] high y candle[0] low
- **Bearish FVG**: Vela bajista grande que deja gap entre candle[0] high y candle[2] low

### 3. Inverse Fair Value Gap (IFVG) - Modelo de Entrada

El IFVG es el trigger de entrada. Ocurre cuando el precio "invierte" un FVG existente.

**Reglas:**
- **Bullish IFVG**: Precio cierra por encima de un bearish FVG que fue barrido
- **Bearish IFVG**: Precio cierra por debajo de un bullish FVG que fue barrido

**Confirmación:** V-shape reversal con cierre fuerte sobre/bajo el FVG

### 4. Draws on Liquidity (DOL)

Niveles que el precio quiere alcanzar.

**Detecta automáticamente:**
- Equal highs/lows (máximas/mínimas iguales)
- Liquidity de sesiones anteriores (Asia, London)

### 5. Sessions

| Sesión | Horario (UTC) | Color |
|--------|---------------|-------|
| Asia | 20:00 - 00:00 | Naranja |
| London | 07:00 - 10:00 | Azul |
| NY | 13:30 - 20:00 | Amarillo |

---

## Checklist de la Estrategia (del video)

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

---

## Configuración en TradingView

### Paso 1: Preparar el chart
1. Abre TradingView
2. Busca `CME_MINI:MNQ1!` (Nasdaq futures)
3. Selecciona timeframe de 1min o 3min para entries

### Paso 2: Agregar el indicador
1. Ve a **Pine Editor** (parte inferior)
2. Haz clic en **Open** → **New indicator**
3. Copia el contenido de `EzTrades_NY_Strategy.pine`
4. Haz clic en **Add to chart**

### Paso 3: Configurar
- Activa **SMT** para ver divergencias con ES
- Activa **15m** y **1h FVG** para contexto
- Configura **IFVG** en timeframe de entrada (1min)
- Activa alerts para notificaciones

### Paso 4: Alerts
1. Haz clic en el indicador en el chart
2. Ve a **Alerts** → **Add Alert**
3. Selecciona las condiciones:
   - `SMT Bullish` / `SMT Bearish`
   - `IFVG Bullish` / `IFVG Bearish`

---

## Ejemplo de Setup A+

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

---

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `EzTrades_NY_Strategy.pine` | Indicador principal (copia para TradingView) |
| `How I Get A 76 Mechanical...txt` | Subtítulos del video de referencia |

---

## Notas Importantes

- **Ticker**: El indicador usa `CME_MINI:ES1!` como proxy de MES para el SMT. Si necesitas otro ticker, edita las líneas de `request.security`
- **Timeframes**: Puedes ajustar los TF de FVG en los inputs
- **No es señal automática**: Es una herramienta de análisis. Siempre confirma la estructura del mercado
- **Gestión de riesgo**: El video recomienda BE rápido y targets conservadores (base hits, no 1:5)

---

## Créditos

- **Estrategia original**: EzTrades
- **Indicador**: Generado con asistencia de IA
