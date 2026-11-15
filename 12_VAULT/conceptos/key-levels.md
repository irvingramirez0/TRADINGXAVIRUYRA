---
tipo: "concepto"
titulo: "Key Levels"
title: "Key Levels"
confianza: "explícito"
estado: "vigente"
video: "J7Dh-aj9-e0"
timestamp: "00:03"
categoria: "CORE"
uso: ""
sinonimos: ["key level", "key levels", "zona de conflicto", "nivel clave"]
id: 88
---

# Key Levels

> **Confianza:** explícito · **Estado:** vigente · **Categoría:** CORE
- **Clase del bootcamp:** [[../bootcamp/dia-15|Día 15 — Key Levels]]

## Definición

Zonas de conflicto donde se espera que el precio se frene o se dé la vuelta. Se identifican solo con FVG de 15m, 1H y 4H (nunca 5m) más liquidez: altos y bajos dentro del FVG. Incluye NDOG, NWOG y altos/bajos de 1H y 4H.

## Interpretación de Xavi

Es la zona donde el precio decide si gira o continúa. No hace falta nada más que FVG y liquidez para identificarla; el equilibrium y el SMT ayudan a precisar. Un FVG de 15m solo se usa como key level cuando el movimiento está esponsoreado por un gap de 1H o 4H; si no, suele usarse como condición.

## Cómo identificarlo

Marcar FVG de 15m, 1H y 4H. En los de 1H/4H, exigir altos o bajos dentro del gap. Si el precio toca el FVG de 1H, bajar a 15m/30m/5m para comprobar la liquidez interna que se está quitando. Alinear los puntos de liquidez a favor (equal highs/lows, LRL, NWOG/NDOG).

## Cuándo se usa

Antes de buscar la entrada: define dónde puede girar el precio y dónde no tiene sentido entrar.

## Condiciones

FVG de 15m/1H/4H, nunca de 5m; el de 1H/4H necesita liquidez dentro; el de 15m necesita estar esponsoreado por 1H/4H. Cuanta más liquidez alineada a favor y menos en contra, mejor.

## Temporalidades

15m, 1H y 4H para marcar; 15m/30m/5m para comprobar la liquidez interna.

## Aplicación

Esperar a que el precio toque el key level; comprobar la reacción; si hay buena reacción, buscar distribución sin exigir que revisite el bajo; si consolida junto al low, esperar el sweep y la vuelta. Entrar con IFVG de 30s–5m.

## Errores comunes

Usar FVG de 5m como key level; usar un FVG de 15m sin el respaldo de 1H/4H; no exigir liquidez dentro del FVG de 1H/4H; entrar antes de tocar la zona; ignorar la liquidez en contra.

## Excepciones

El FVG de 15m puede funcionar como condición más que como key level. Un key level puede fallar: no es una garantía.

## Notas

Bootcamp Día 15. Definición 00:03–01:05; FVG válidos 02:09; liquidez dentro 02:40–04:46.

## Requiere / se combina con

- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[equilibrium-premium-descuento|Equilibrium (premium/descuento)]]
- [[smt-smart-money-technique|SMT (Smart Money Technique)]]
- [[nwog-new-week-opening-gap|NWOG (New Week Opening Gap)]]
- [[ndog-new-day-opening-gap|NDOG (New Day Opening Gap)]]
- [[equal-highs-equal-lows|Equal Highs / Equal Lows]]
- [[low-resistance-liquidity-lrl|Low Resistance Liquidity (LRL)]]

## Evidencia

- «Los key levels son zonas donde nosotros estamos buscando que el precio se dé la vuelta o que se frene... una zona de conflicto.» — `J7Dh-aj9-e0` @ 00:03 (explícito)
- «A mí como key level me sirven FVGs de 15 minutos, de una hora y de 4 horas... nunca voy a usar un FVG de 5 minutos como key level.» — `J7Dh-aj9-e0` @ 02:09 (explícito)
- «Estos FVGs de una hora y de 4 horas yo necesito que tengan algún tipo de liquidez... necesito altos y bajos que estén dentro de FVGs.» — `J7Dh-aj9-e0` @ 04:46 (explícito)
- «Ejemplos de key levels: new day opening gap, new week opening gap y altos y bajos de una hora y 4 horas.» — `J7Dh-aj9-e0` @ 05:49 (explícito)

