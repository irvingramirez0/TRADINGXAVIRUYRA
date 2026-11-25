---
tipo: "regla"
titulo: "La manipulation leg se mide desde el último swing antes de la zona"
title: "La manipulation leg se mide desde el último swing antes de la zona"
confianza: "explícito"
estado: "vigente"
video: "1C4dgloDQrY"
timestamp: "16:51"
id: 101
version: 1
---

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

La manipulation leg empieza en el último swing high/low formado antes de que el precio llegue a la zona de interés y termina en el extremo de la manipulación.

## Contexto

Entradas Judas, reversal y continuación.

## Condiciones

Debe existir una zona de interés (FVG de 15m, 1H o 4H) y un desplazamiento hacia ella.

## Confirmaciones

El IFVG de la temporalidad más alta dentro de la leg.

## Condiciones de entrada

Se entra cuando ese IFVG se invierte.

## Invalidación

Si el precio rompe el swing que define la leg antes de la entrada.

## Gestión de riesgo

Stop al otro lado del extremo de la leg.

## Objetivos

1:1 o liquidez opuesta.

## Excepciones

En continuación, la leg se reconstruye con el nuevo high/low.

## Notas

Definición literal: 'Siempre tenemos que mirar el último alto que se ha creado antes de que el precio llegue a la zona.'

### Conceptos relacionados

- [[swing-high-swing-low|Swing High / Swing Low]]
- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[judas-swing|Judas Swing]]
- [[displacement|Displacement]]
- [[manipulation-leg|Manipulation leg]]

## Evidencia

- «Siempre tenemos que mirar el último alto que se ha creado antes de que el precio llegue a la zona.» — `1C4dgloDQrY` @ 16:51 (explícito)

