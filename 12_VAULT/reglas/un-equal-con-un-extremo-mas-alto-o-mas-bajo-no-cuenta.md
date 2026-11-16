---
tipo: "regla"
titulo: "Un equal con un extremo más alto o más bajo no cuenta"
title: "Un equal con un extremo más alto o más bajo no cuenta"
confianza: "explícito"
estado: "vigente"
video: "OtYATAfCfRA"
timestamp: "04:10"
id: 129
version: 1
---

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1
- **Clase del bootcamp:** [[../bootcamp/dia-11|Día 11 — Liquidez pt2]]

## Descripción

Si uno de los dos extremos está más alto (o más bajo) que el otro, esa liquidez ya se ha cogido y no se considera equal: se busca liquidez intacta.

## Contexto

Validación de equal highs/lows.

## Condiciones

Dos o más extremos próximos.

## Confirmaciones

Los extremos están exactamente a la misma altura (equal) o casi (relative equal).

## Condiciones de entrada

No aplica.

## Invalidación

Si un extremo está más bajo, el equal low no es válido.

## Gestión de riesgo

No aplica.

## Objetivos

No aplica.

## Excepciones

En relative equal se admite la diferencia mínima.

## Notas

Bootcamp Día 11 [04:10–04:42].

## Conceptos relacionados

- [[equal-highs-equal-lows|Equal Highs / Equal Lows]]

## Evidencia

- «No podemos decir, 'Ah, mira, un bajo aquí y aquí un más bajo.' No cuenta.» — `OtYATAfCfRA` @ 04:10 (explícito)

