---
tipo: "operacion"
titulo: "Operación #18 — NQ (Nasdaq 100); referencia SP500/SPX — 2026-05-20"
title: "Operación #18 — NQ (Nasdaq 100); referencia SP500/SPX — 2026-05-20"
confianza: "observado"
estado: "vigente"
video: "UtarQMiPE0U"
timestamp: ""
fecha: "2026-05-20"
clasificacion: "Error de ejecución"
id: 18
---

> **Aviso:** P&L autodeclarado, no auditado. Las cifras provienen de lo que Xavi dice en el vídeo y no se han verificado con extractos de cuenta.

> **Clasificación:** Error de ejecución · **Confianza:** observado

## Contexto

El título dice +2.000 $, pero la cifra no se dice en el audio. Operó solo en una eval de 25K (que pasó y fondeó) y en una fondeada de 25K de Lucid; no usó Alpha ni Topstep porque había FOMC y el price action estaba horrible/rangeando. Bias compras, aunque el high timeframe no estaba bonito y había rango; los highs de arriba no le parecían relevantes; la buy side 'más tocha' era un high prominente y ese era el objetivo. Al open los activos estaban poco correlacionados: Nasdaq alcista, SP500 bajando; normalmente espera a que se alineen. Buscaba compras por key levels: quitó el internal low dentro de un FVG de 1H pequeño; el SPX ya había tocado un FVG más grande/en descuento y había quitado equal lows. Esperó; a las 9:40 el SPX quitó el FVG y el low y giró; marcó el FVG de 2m y esperó su inversión. Entró y TP 1:1,39.

## Razonamiento

High timeframe mandaba; SPX había tocado su FVG en descuento y girado; estructura y velas de 1m bonitas; confianza en el high. Pero el FVG de 2m no estaba realmente invertido: el requisito no se cumplió.

## Setup

FVG de 2m invertido (en teoría) tras el giro del SPX y la toma de equal lows; entrada long con TP en la buy side liquidity marcada; 1:1,39.

## Entrada

no consta (inverse FVG de 2 min, sin confirmación real)

## Stop

no consta

## Objetivo

1:1,39 en la buy side liquidity

## Resultado

TP +2.000 $ (título). Operó en eval de 25K y fondeada de 25K Lucid.

## Gestión

BE en un nivel que no es importante en NQ 5m/15m, pero el SP500 sí estaba en un FVG de 15m; tras el TP hubo rechazo en esa zona, por lo que lo considera buen BE. No consta parciales.

## Análisis posterior

Esperar el close/confirmación de la inversión del FVG; si hay que hacer zoom, es mala señal.; El DOL es más importante que el sistema de entrada, pero el requisito de entrada debe cumplirse igualmente.; En FOMC/rango, proteger capital: usar cuentas pequeñas o secundarias y no las fondeadas principales.; El BE puede justificarse por el activo correlacionado (SP500 en FVG de 15m) aunque el NQ no tenga zona allí.; Un TP no valida una entrada que no cumplía el plan.

## Notas

Fuente: recap del vídeo. Entró sin que el FVG de 2m estuviera realmente invertido; no hizo zoom y el requisito no se cumplió: 'El trade se invalida por el simple hecho de que no ha cumplido el requisito'.; En FOMC y con price action ranging, el setup no estaba claro; él mismo dice que no estaba 'clarísimo' y que debió esperar el close de la vela de 2m.; Si tienes que hacer zoom para ver la inversión, es mala señal.; No operó las cuentas 'tochas' ese día; no queda claro si fue intencional (protección de capital) o inconsistencia.. Citas: [34.67s] hemos entrado a partir de este inverse de dos, TP en la byside liquidity que teníamos marcada. | [34.67s] porque hay FOMC y se puede ver que el el price action está siendo horrible, o sea, estamos rangeando un montón. | [192.68s] Me han dicho en el Discord que no se ha inversado el gap. Y si haces zoom, no se ha inversado | [224.0s] El trade se invalida por el simple hecho de que no ha cumplido el requisito

## Conceptos presentes

- [[key-levels|Key Levels]]
- [[liquidez-bsl-ssl|Liquidez (BSL/SSL)]]
- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[draw-on-liquidity-dol|Draw on Liquidity (DOL)]]

## Reglas relacionadas (detección automática)

- [[secuencia-del-analisis-key-levels-fvg-1h-4h-reversion-o-continuacion-fvg|Secuencia del análisis: key levels → FVG 1H/4H → reversión o continuación → FVG en equilibrium → IFVG → BSL/SSL]]
- [[ifvg-obligatorio-nunca-entrar-sin-ifvg|IFVG obligatorio: nunca entrar sin IFVG]]
- [[afirmaciones-htf-condiciones-5m-15m-ejecucion-con-ifvg-30s5m|Afirmaciones HTF, condiciones 5m/15m, ejecución con IFVG 30s–5m]]
- [[hacer-backtesting-con-nq-y-es-abiertos-y-en-sesion-de-nueva-york|Hacer backtesting con NQ y ES abiertos y en sesión de Nueva York]]

