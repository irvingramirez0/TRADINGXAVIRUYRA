---
tipo: "regla"
titulo: "Data highs/lows: esperar la noticia y operar el barrido entre extremos"
title: "Data highs/lows: esperar la noticia y operar el barrido entre extremos"
confianza: "explícito"
estado: "vigente"
video: "OtYATAfCfRA"
timestamp: "09:54"
id: 133
version: 1
---

# Data highs/lows: esperar la noticia y operar el barrido entre extremos

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1
- **Clase del bootcamp:** [[../bootcamp/dia-11|Día 11 — Liquidez pt2]]

## Descripción

Con noticia a las 10:00 no se opera antes: se espera al dato, se marcan el alto y el bajo que deja y se busca el barrido de un extremo hacia el otro.

## Contexto

Días con noticia dentro de la sesión.

## Condiciones

Noticia programada a las 10:00 o dato de 8:30.

## Confirmaciones

El precio barre un extremo del dato y reacciona.

## Condiciones de entrada

Entrada tras el barrido, hacia el extremo contrario.

## Invalidación

Si el precio no respeta el extremo, no hay trade.

## Gestión de riesgo

Stop al otro lado del extremo barrido.

## Objetivos

El extremo contrario del dato.

## Excepciones

A veces el precio no llega al extremo contrario y el movimiento sigue siendo aprovechable.

## Notas

Bootcamp Día 11 [09:54–11:58].

## Conceptos relacionados

- [[data-highs-lows|Data Highs / Lows]]

## Evidencia

- «Esperemos a que la noticia salga y cuando se da la noticia... ahí ya nos podemos esperar a que quitemos el alto para ir a buscar el bajo o al revés.» — `OtYATAfCfRA` @ 09:54 (explícito)

