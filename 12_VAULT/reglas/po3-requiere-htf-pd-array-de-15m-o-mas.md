---
tipo: "regla"
titulo: "PO3 requiere HTF PD array de 15m o más"
title: "PO3 requiere HTF PD array de 15m o más"
confianza: "explícito"
estado: "vigente"
video: "oP7enoxXpfI"
timestamp: "07:19"
id: 49
version: 1
---

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

Para validar un PO3 tiene que haber un PD array (FVG) de 15 minutos o superior; el de 5m no cuenta para este filtro.

## Contexto

Selección de setup.

## Condiciones

FVG de 15m/1H/4H; equilibrium/descuento; DOL; LRL; estructura.

## Confirmaciones

El precio reacciona en la zona.

## Condiciones de entrada

Solo se busca PO3 si existe el PD array HTF.

## Invalidación

Si no hay PD array de 15m+, no hay PO3 válido.

## Gestión de riesgo

No aplica.

## Objetivos

DOL.

## Excepciones

La zona inmediata de manipulación del open de las 10:00 puede ser un gap de 5m; es un uso distinto.

## Notas

Documento 04. Contradicción aparente con el 5m documentada en 11_PREGUNTAS_ABIERTAS.

## Conceptos relacionados

- [[pd-array|PD Array]]
- [[open-de-las-10-00|Open de las 10:00]]
- [[equilibrium-premium-descuento|Equilibrium (premium/descuento)]]
- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[draw-on-liquidity-dol|Draw on Liquidity (DOL)]]
- [[po3-power-of-3|PO3 (Power of 3)]]

## Evidencia

- «Paráfrasis: el PD array tiene que ser de 15 minutos para arriba; el 5m no cuenta.» — `oP7enoxXpfI` @ 07:19 (explícito)

