---
tipo: "regla"
titulo: "Break-even solo en high/low dentro de FVG/gap de 3m+"
title: "Break-even solo en high/low dentro de FVG/gap de 3m+"
confianza: "explícito"
estado: "vigente"
video: "5aBdJLMDGJc"
timestamp: "06:53"
id: 58
version: 1
---

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

Mover el stop a break-even solo cuando hay un high/low relevante dentro de un FVG/gap de 3 minutos o más.

## Contexto

Gestión de la posición abierta.

## Condiciones

FVG/gap de 3m+; high/low dentro; zona de conflicto.

## Confirmaciones

Si el SP500 ya quitó su high/low, se puede mover BE.

## Condiciones de entrada

No aplica.

## Invalidación

Si el nivel no está dentro de una zona, no se mueve.

## Gestión de riesgo

Protege el trade sin cortar la idea.

## Objetivos

No aplica.

## Excepciones

Si no hay gap relevante, dejar correr hasta TP o stop.

## Notas

Documento 07.

### Conceptos relacionados

- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[key-levels|Key Levels]]

## Evidencia

- «Paráfrasis: break-even solo en un high/low dentro de un FVG/gap de 3m+.» — `5aBdJLMDGJc` @ 06:53 (explícito)
- «Quitamos el internal high que está dentro de un fair value gap de 15 y de 5 minutos; es un buen motivo para ir break even.» — `mCMpxc0NaN4` @ 19:42 (explícito)

