---
tipo: "regla"
titulo: "No entrar en continuación de 5m si se abre un gap de 15m en minutos"
title: "No entrar en continuación de 5m si se abre un gap de 15m en minutos"
confianza: "explícito"
estado: "vigente"
video: "1C4dgloDQrY"
timestamp: "36:01"
id: 104
version: 1
---

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

Antes de entrar en una continuación de 5m hay que mirar la hora: si en pocos minutos se abre una vela de 15m que va a crear un gap, no se entra.

## Contexto

Modelo 3; gestión del timing.

## Condiciones

IFVG de 5m formado cerca del open de una vela de 15m.

## Confirmaciones

Reloj y apertura de 15m inminente.

## Condiciones de entrada

Solo si queda margen suficiente antes del open de 15m.

## Invalidación

Si el gap de 15m se crea antes de la entrada.

## Gestión de riesgo

Evitar quedar atrapado por el gap de 15m.

## Objetivos

No aplica.

## Excepciones

Si el DOL es clarísimo puede aceptarlo; es discrecional.

## Notas

Ejemplo: a las 9:56 no entra aunque tenga el IFVG, porque a las 10:00 se crea el gap.

### Conceptos relacionados

- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[draw-on-liquidity-dol|Draw on Liquidity (DOL)]]

## Evidencia

- «no nos interesa buscar longs con un stop loss colocado en una vela de 15 minutos» — `vz4rhIi5Joo` @ 10:24 (explícito)
- «Si me ha dado el invers y son las 9:56, ni de coña voy a entrar... se va a crear aquí un gap de 15 minutos enorme.» — `1C4dgloDQrY` @ 36:01 (explícito)

