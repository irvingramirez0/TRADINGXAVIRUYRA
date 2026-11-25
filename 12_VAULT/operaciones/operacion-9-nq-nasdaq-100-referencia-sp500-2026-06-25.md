---
tipo: "operacion"
titulo: "Operación #9 — NQ (Nasdaq 100); referencia SP500 — 2026-06-25"
title: "Operación #9 — NQ (Nasdaq 100); referencia SP500 — 2026-06-25"
confianza: "observado"
estado: "vigente"
video: "P6ynwaPPYyM"
timestamp: ""
fecha: "2026-06-25"
clasificacion: "Violación de reglas"
id: 9
---

> **Aviso:** P&L autodeclarado, no auditado. Las cifras provienen de lo que Xavi dice en el vídeo y no se han verificado con extractos de cuenta.

> **Clasificación:** Violación de reglas · **Confianza:** observado

## Contexto

Daily loss limit tocado: -1.063 $ por cuenta, balance 50.500 $ y -5.000 $ en total en evals; venía de una racha de 22-23 TP. Bias bajista por SMT con SP500, reswipe de un high dentro de un FVG de 4H, invalidación y cierre bajo la zona el día previo y gap diario tapeado con reacción bajista fuerte. En el open hubo open high, tapeo de FVG de 5m y 15m y SMT; el trade ideal del día era un inverse FVG de 30 segundos.

## Razonamiento

Quería quitar la low resistance liquidity; venía de quitar equal highs de 1m, tenía SMT con SP500 y había tapeado un gap de 15m. Reconoce que el razonamiento fue 'pura dopamina' y que se autoconvenció para pasar las evals: el checklist se cumplía, pero las condiciones del día no eran operables.

## Setup

Trade forzado tras una caída de ~1.000 puntos. El SP500 tapea un gap de 15m arriba, el Nasdaq tapea el gap de 15m intermedio formando uno, hay SMT, liquidez y trendline; recuperación de equal highs de 1m y tapeo del FVG de 15m con inverse. Él mismo describe el contexto como un QR/chopfest sin nada de alta probabilidad.

## Entrada

no consta (inverse FVG de 15 min tras recuperar equal highs de 1 min)

## Stop

no consta

## Objetivo

no consta (low resistance liquidity)

## Resultado

SL. -5.000 $ en total en evals; -1.063 $ por cuenta (daily loss limit); balance 50.500 $; las cuentas aún no están perdidas.

## Gestión

No fue a break-even hasta que se quitase toda la low resistance liquidity; aun así acabó en stop. No consta que hiciera parciales.

## Análisis posterior

Tras una caída inhumana (~1.000 puntos) lo normal es chop/QR; no operar.; Si te pierdes el trade A+, no fuerces un B para compensar.; No operes con prisa por pasar evals ni por dopamina.; Cumplir las condiciones de la estrategia no basta si el contexto del día no es operable.; Documentar las pérdidas y las 'cagadas' también forma parte del proceso.

## Notas

Fuente: recap del vídeo. Miedo/bloqueo: no tomó el A+ del open (inverse FVG de 30 s) por miedo a llegar al daily loss limit ('me he cagado').; Forzó un trade para pasar las evals, con prisa y razonamiento dopaminérgico; se autoconvenció.; Operó después de una caída de ~1.000 puntos, en un QR/chopfest donde él mismo dice que no hay nada de alta probabilidad.; Confundió cumplir el checklist con que el trade fuera bueno: el setup cumplía las condiciones de la estrategia, pero las condiciones del día no eran operables.. Citas: [32.88s] Al final, el trade no ha sido muy bueno y os voy a explicar cómo he perdido, pues, en total $5,000 operando el Nasdaq. | [95.28s] he tenido miedo, o sea, me he cagado, literalmente, he tenido miedo de llegar al daily los limit | [186.56s] ¿Qué he hecho? Forzar un trade porque quería pasar las evals, no sé, tenía prisa para pasarlas. | [216.76s] el razonamiento del trade ha sido pura dopamina

### Conceptos presentes

- [[liquidez-bsl-ssl|Liquidez (BSL/SSL)]]
- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[daily-bias|Daily Bias]]
- [[smt-smart-money-technique|SMT (Smart Money Technique)]]

### Reglas relacionadas (detección automática)

- [[secuencia-del-analisis-key-levels-fvg-1h-4h-reversion-o-continuacion-fvg|Secuencia del análisis: key levels → FVG 1H/4H → reversión o continuación → FVG en equilibrium → IFVG → BSL/SSL]]
- [[equilibrium-comprar-en-descuento-vender-en-premium|Equilibrium: comprar en descuento, vender en premium]]
- [[el-fvg-debe-estar-alineado-con-la-linea-0-5-del-equilibrium|El FVG debe estar alineado con la línea 0.5 del equilibrium]]
- [[la-confirmacion-de-entrada-en-equilibrium-es-el-ifvg|La confirmación de entrada en equilibrium es el IFVG]]

