---
tipo: "regla"
titulo: "Usar el IFVG de la temporalidad más alta de la manipulation leg"
title: "Usar el IFVG de la temporalidad más alta de la manipulation leg"
confianza: "explícito"
estado: "vigente"
video: "1C4dgloDQrY"
timestamp: "14:40"
id: 102
version: 1
---

# Usar el IFVG de la temporalidad más alta de la manipulation leg

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

Dentro de la manipulation leg, el IFVG válido es el de la temporalidad más alta; si hay uno de 5m y otro de 3m, espera el de 5m.

## Contexto

Selección del gatillo de entrada.

## Condiciones

Debe haber varios IFVG dentro de la leg.

## Confirmaciones

Cierre del IFVG de mayor temporalidad.

## Condiciones de entrada

Entrada tras ese cierre.

## Invalidación

Si el IFVG de mayor temporalidad no se invierte.

## Gestión de riesgo

Stop estructural al otro lado de la leg.

## Objetivos

1:1 o liquidez.

## Excepciones

Si el DOL es muy claro y el primer IFVG se invierte con fuerza, puede entrar del primero (Judas).

## Notas

'Cuanto más alta la temporalidad, más fuerza y más decisión tiene.'

## Conceptos relacionados

- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[draw-on-liquidity-dol|Draw on Liquidity (DOL)]]
- [[judas-swing|Judas Swing]]
- [[manipulation-leg|Manipulation leg]]

## Evidencia

- «Si tengo un fair value de 5 minutos, pero también tengo uno de 2 y uno de 1, no voy a entrar después del inverso... me voy a esperar a que se inverse el de 5, porque cuanto más alta la temporalidad, más fuerza y más decisión tiene.» — `1C4dgloDQrY` @ 14:40 (explícito)
- «el invers del time frame de la temporalidad más alta» — `sKSAh5gky1M` @ 28:11 (explícito)

