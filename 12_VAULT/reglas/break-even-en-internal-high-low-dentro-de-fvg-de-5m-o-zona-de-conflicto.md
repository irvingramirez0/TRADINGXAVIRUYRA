---
tipo: "regla"
titulo: "Break-even en internal high/low dentro de FVG de 5m+ o zona de conflicto"
title: "Break-even en internal high/low dentro de FVG de 5m+ o zona de conflicto"
confianza: "explícito"
estado: "vigente"
video: "1C4dgloDQrY"
timestamp: "24:08"
id: 105
version: 1
---

# Break-even en internal high/low dentro de FVG de 5m+ o zona de conflicto

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

El break-even se mueve solo si el internal high/low está dentro de un FVG de 5 minutos o más, o en una zona de conflicto (FVG de 5m, 15m, 1H o 4H).

## Contexto

Gestión del trade.

## Condiciones

Hay un internal high/low relevante.

## Confirmaciones

Está dentro de un FVG de 5m+ o de una zona de conflicto.

## Condiciones de entrada

No aplica.

## Invalidación

Si el high/low es random y no está dentro de nada.

## Gestión de riesgo

Mover el stop a break-even en ese nivel.

## Objetivos

No aplica.

## Excepciones

Excepción por payout/racha (regla 93).

## Notas

Precisa el umbral de la regla 58 (3m+) para el caso de internal high/low; no la invalida.

## Conceptos relacionados

- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[key-levels|Key Levels]]

## Evidencia

- «Quitamos el internal high que está dentro de un fair value gap de 15 y de 5 minutos; es un buen motivo para ir break even.» — `mCMpxc0NaN4` @ 19:42 (explícito)
- «Si yo aquí por algún motivo tengo un low, un low random de un minuto, no voy a ir break even aquí. ¿Para qué?» — `1C4dgloDQrY` @ 24:08 (explícito)

