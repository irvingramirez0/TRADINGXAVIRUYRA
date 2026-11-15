---
tipo: "regla"
titulo: "Open de las 10:00: sweep + open low/high"
title: "Open de las 10:00: sweep + open low/high"
confianza: "explícito"
estado: "vigente"
video: "vz4rhIi5Joo"
timestamp: "10:54"
id: 48
version: 1
---

# Open de las 10:00: sweep + open low/high

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

Para largos se busca un open low (manipulación abajo) y cierre alcista; para cortos, open high y cierre bajista. Sin liquidity sweep, el open high/low no cuenta.

## Contexto

10:00–10:30.

## Condiciones

Sweep de un high/low; zona de manipulación (gap de 5m o más); DOL claro.

## Confirmaciones

IFVG de 1m o CISD; true manipulation.

## Condiciones de entrada

Entrada tras el sweep y el cierre de la vela de las 10:00.

## Invalidación

Si no hay sweep, no hay trade.

## Gestión de riesgo

Stop al otro lado del sweep.

## Objetivos

Gap/liquidez de 5m/15m/30m/1H/4H; DOL.

## Excepciones

No es mecánico; no todas las velas de las 10:00 abren al revés.

## Notas

Documento 05.

## Conceptos relacionados

- [[open-de-las-10-00|Open de las 10:00]]
- [[true-manipulation|True Manipulation]]
- [[liquidez-bsl-ssl|Liquidez (BSL/SSL)]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[draw-on-liquidity-dol|Draw on Liquidity (DOL)]]
- [[cisd-change-in-state-of-delivery|CISD (Change in State of Delivery)]]

## Evidencia

- «una apertura alcista para tener un close bajista» — `OdljBowQurk` @ 04:10 (explícito)
- «Si queréis buscar largos, tenéis que tener un open low... y un open high para buscar cortos.» — `vz4rhIi5Joo` @ 10:54 (explícito)
- «si tiene un open high va a tener un low close. No siempre, obviamente» — `1C4dgloDQrY` @ 40:10 (explícito)

