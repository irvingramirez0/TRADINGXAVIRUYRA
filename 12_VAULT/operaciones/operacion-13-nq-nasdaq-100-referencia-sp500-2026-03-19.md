---
tipo: "operacion"
titulo: "Operación #13 — NQ (Nasdaq 100); referencia SP500 — 2026-03-19"
title: "Operación #13 — NQ (Nasdaq 100); referencia SP500 — 2026-03-19"
confianza: "observado"
estado: "vigente"
video: "p16KlZS3bn8"
timestamp: ""
fecha: "2026-03-19"
clasificacion: "Bien ejecutado perdedor"
id: 13
---

> **Aviso:** P&L autodeclarado, no auditado. Las cifras provienen de lo que Xavi dice en el vídeo y no se han verificado con extractos de cuenta.

> **Clasificación:** Bien ejecutado perdedor · **Confianza:** observado

## Contexto

Resultado: -453 $; primer stop loss del mes. Bias inicial bajista: la vela de 4H estaba abajo y el Nasdaq podía querer quitar el low de 4H; el SP500 ya lo había quitado, lo que daba SMT. Luego, si el Nasdaq holdeaba el FVG alcista de 4H, esperaba subida porque se había quitado el internal low y había SMT (SP quitó el low, Nasdaq no). No tomó el primer inverse de 5m porque las condiciones no le gustaban y aún no había rechazo suficiente.

## Razonamiento

DOL fuerte + confirmación (inverse de 1m desde wick) + FVG de 15m tapeado e intermediate low quitado. Sin FVG de 2m ni de temporalidad mayor; el BE iba en el FVG de 1m.

## Setup

Quería que se formase un imbalance/FVG de 5m o 15m, se tapease y diese un inverse alcista para confirmar el DOL. El precio chopeó (bueno para AMD), abrió un FVG de 15m, dejó relative equal highs, casi quitó el DOL sin hacerlo, bajó a tocar el FVG de 15m quitando el intermediate low; justo entonces un inverse de 1m desde una wick. Entra largo con stop en la wick y BE en el FVG de 1m.

## Entrada

no consta (inverse FVG de 1 min desde wick)

## Stop

en la wick, protegiéndolo (nivel no consta); 8 contratos; riesgo ~450 $ (él dice '450 dólares'; resultado -453 $)

## Objetivo

no consta (DOL: FVG de 1 h)

## Resultado

SL en 30-40 segundos (<1 minuto). -453 $. Primer stop del mes.

## Gestión

Stop en la wick; BE en el FVG de 1m (no llegó a tocarse). Sin parciales. Lockout inmediato tras el stop para evitar reentrada/sobreoperación.

## Análisis posterior

Un setup válido puede saltar en 30-40 segundos; el stop no siempre implica error.; Paciencia: esperar el high-probability setup y no calentarse.; Con muchas cuentas de fondeo, priorizar setups que realmente gusten.; Lockout instantáneo tras el stop para evitar reentrar/sobreoperar.

## Notas

Fuente: recap del vídeo. No reconoce errores: 'No me he saltado ninguna regla'; está contento y pillaría el trade 100 veces más.; Única pega: el inverse no era el más fuerte/bonito que ha visto; lo atribuye al timing/price action, no al sistema.. Citas: [3.07s] hemos entrado con ocho contratos aquí, con el stop aquí abajo y nos ha dado stop loss y cuando os digo que nos ha dado stop literalmente en 30 segundos, 40 segundos | [218.68s] estoy muy contento con con trade, muy contento. No me he saltado ninguna regla, mi riesgo son normalmente 500 dólares, así que bastante acertado, 450 dólares. | [310.96s] Simplemente creo que no lo he pillado, o sea, no he tenido el timing de pillarlo bien | [341.12s] el lockout me lo hago instantáneamente cuando hago el stop, porque sé que me van a entrar ganas de reentrar, de sobreoperar

## Conceptos presentes

- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[equal-highs-equal-lows|Equal Highs / Equal Lows]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[draw-on-liquidity-dol|Draw on Liquidity (DOL)]]
- [[daily-bias|Daily Bias]]

## Reglas relacionadas (detección automática)

- [[secuencia-del-analisis-key-levels-fvg-1h-4h-reversion-o-continuacion-fvg|Secuencia del análisis: key levels → FVG 1H/4H → reversión o continuación → FVG en equilibrium → IFVG → BSL/SSL]]
- [[el-dol-debe-estar-dentro-de-un-fvg-pd-array|El DOL debe estar dentro de un FVG/PD array]]
- [[judas-swing-acumulacion-manipulacion-distribucion|Judas Swing: acumulación → manipulación → distribución]]
- [[entrada-por-ifvg-cisd-como-alternativa|Entrada por IFVG; CISD como alternativa]]

