---
tipo: "regla"
titulo: "IFVG obligatorio: nunca entrar sin IFVG"
title: "IFVG obligatorio: nunca entrar sin IFVG"
confianza: "explícito"
estado: "vigente"
video: "ICOx4rdFSLg"
timestamp: "03:21"
id: 138
version: 1
---

# IFVG obligatorio: nunca entrar sin IFVG

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

El IFVG es el sistema de entrada: nunca se pulsa comprar o vender sin un inverse fair value gap. Es la confirmación de que el precio quiere cambiar de tendencia.

## Contexto

Entrada.

## Condiciones

Hay una zona (key level, DOL, manipulación) y el precio invierte un FVG con cierre de cuerpo.

## Confirmaciones

Cierre de cuerpo al otro lado del FVG en la temporalidad en la que se marcó.

## Condiciones de entrada

IFVG de 30s–5m alineado con la distribución.

## Invalidación

No hay IFVG: no hay entrada, aunque el resto del contexto parezca claro.

## Gestión de riesgo

Stop al otro lado de la manipulación/swing.

## Objetivos

Liquidez opuesta / DOL.

## Excepciones

Ninguna documentada: es obligatorio.

## Notas

Bootcamp Día 13 [03:21–03:52].

## Conceptos relacionados

- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[draw-on-liquidity-dol|Draw on Liquidity (DOL)]]
- [[key-levels|Key Levels]]

## Evidencia

- «Yo nunca, nunca, nunca voy a darle al botón de comprar o vender sin un inverse fair value gap.» — `ICOx4rdFSLg` @ 03:21 (explícito)

