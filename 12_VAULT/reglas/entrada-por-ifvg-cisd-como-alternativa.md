---
tipo: "regla"
titulo: "Entrada por IFVG; CISD como alternativa"
title: "Entrada por IFVG; CISD como alternativa"
confianza: "explícito"
estado: "vigente"
video: "oP7enoxXpfI"
timestamp: "10:24"
id: 53
version: 1
---

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

El trigger principal es el inverse fair value gap. El CISD es una confluencia secundaria y opcional; se usa cuando no hay IFVG usable y el contexto es claro.

## Contexto

Ejecución.

## Condiciones

Sweep previo; DOL; HTF alineado.

## Confirmaciones

IFVG con cierre de cuerpo; CISD con cierre sobre el cuerpo.

## Condiciones de entrada

IFVG + CISD es la forma más segura; CISD solo es avanzado.

## Invalidación

Si el trigger no cierra, no hay entrada.

## Gestión de riesgo

Stop estructural.

## Objetivos

1:1 o DOL.

## Excepciones

CISD solo si el DOL/Judas es muy claro.

## Notas

Documento 05.

## Conceptos relacionados

- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[draw-on-liquidity-dol|Draw on Liquidity (DOL)]]
- [[judas-swing|Judas Swing]]
- [[cisd-change-in-state-of-delivery|CISD (Change in State of Delivery)]]

## Evidencia

- «Paráfrasis: usa CISD cuando no hay inverse fair value en las temporalidades que mira y las condiciones son buenas, con DOL/objetivo muy claro.» — `_drb5sSmQZE` @ 06:45 (explícito)
- «Paráfrasis: cuando el precio crea y empieza a invertir FVG hacia arriba, es cuando se puede entrar.» — `oP7enoxXpfI` @ 10:24 (explícito)

