---
tipo: "regla"
titulo: "Un FVG de 1H o 4H es key level si tiene highs/lows dentro"
title: "Un FVG de 1H o 4H es key level si tiene highs/lows dentro"
confianza: "explícito"
estado: "vigente"
video: "J7Dh-aj9-e0"
timestamp: "04:46"
id: 144
version: 1
---

# Un FVG de 1H o 4H es key level si tiene highs/lows dentro

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

Los FVG de 1 hora y 4 horas necesitan liquidez dentro: altos y bajos que estén dentro del FVG. Sin esa liquidez, el gap no se considera un key level de la misma calidad.

## Contexto

Validación de key levels.

## Condiciones

FVG de 1H/4H con un high o un low dentro.

## Confirmaciones

El precio toca el gap y reacciona sobre esa liquidez interna.

## Condiciones de entrada

No aplica: es un filtro de zona.

## Invalidación

FVG de 1H/4H sin highs/lows dentro.

## Gestión de riesgo

No colocar el stop donde está esa liquidez interna.

## Objetivos

La liquidez interna puede ser el objetivo de la manipulación.

## Excepciones

El bajo puede quedar cerca del FVG sin tocarlo exactamente y seguir valiendo.

## Notas

Bootcamp Día 15 [02:40–04:46].

## Conceptos relacionados

- [[key-levels|Key Levels]]
- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[internal-external-liquidity|Internal / External Liquidity]]

## Evidencia

- «Necesito altos y bajos que estén dentro de FVGs.» — `J7Dh-aj9-e0` @ 04:46 (explícito)

