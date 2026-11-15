---
tipo: "regla"
titulo: "Esperar el cierre de la vela de las 10:00 si hay duda"
title: "Esperar el cierre de la vela de las 10:00 si hay duda"
confianza: "explícito"
estado: "vigente"
video: "Urrb1b2kBso"
timestamp: "04:43"
id: 68
version: 1
---

# Esperar el cierre de la vela de las 10:00 si hay duda

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

Cuando el 1H o el DOL no están claros, esperar a que cierre la vela de las 10:00; la mayoría de las veces el mercado se orienta después.

## Contexto

Duda de dirección.

## Condiciones

FVG de 1H ambiguo o DOL poco claro.

## Confirmaciones

Cierre de la vela de las 10:00.

## Condiciones de entrada

Después del cierre, buscar IFVG/CISD.

## Invalidación

No aplica.

## Gestión de riesgo

Evita operar a ciegas.

## Objetivos

No aplica.

## Excepciones

Ninguna.

## Notas

Documento 03.

## Conceptos relacionados

- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[draw-on-liquidity-dol|Draw on Liquidity (DOL)]]
- [[cisd-change-in-state-of-delivery|CISD (Change in State of Delivery)]]

## Evidencia

- «esperarme al close de la vela de las 10» — `PQD0dAH-8eQ` @ 03:43 (explícito)
- «Paráfrasis: si hay duda con el FVG de 1H, esperar el cierre de la vela de las 10:00.» — `Urrb1b2kBso` @ 04:43 (explícito)

