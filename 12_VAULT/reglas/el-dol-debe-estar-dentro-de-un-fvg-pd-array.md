---
tipo: "regla"
titulo: "El DOL debe estar dentro de un FVG/PD array"
title: "El DOL debe estar dentro de un FVG/PD array"
confianza: "explícito"
estado: "vigente"
video: "F3anMVV-VlI"
timestamp: "08:48"
id: 42
version: 1
---

# El DOL debe estar dentro de un FVG/PD array

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

El high/low que se usa como objetivo tiene que estar dentro de un fair value gap. Si no está dentro de una zona, no es DOL.

## Contexto

Selección del objetivo del día.

## Condiciones

FVG de 4H/1H; high/low relevante dentro de él.

## Confirmaciones

El precio respeta el FVG y se dirige al nivel.

## Condiciones de entrada

No es entrada; define el target.

## Invalidación

Si el FVG se invierte, el DOL deja de ser válido.

## Gestión de riesgo

No aplica.

## Objetivos

El high/low dentro del FVG.

## Excepciones

NDOG, LRL, relative equal highs/lows y SMT pueden cambiar el DOL.

## Notas

Documento 03.

## Conceptos relacionados

- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[pd-array|PD Array]]
- [[equal-highs-equal-lows|Equal Highs / Equal Lows]]
- [[draw-on-liquidity-dol|Draw on Liquidity (DOL)]]
- [[smt-smart-money-technique|SMT (Smart Money Technique)]]
- [[ndog-new-day-opening-gap|NDOG (New Day Opening Gap)]]

## Evidencia

- «Paráfrasis: marca como objetivo un low dentro de un fair value gap de 4H; después identifica el low del gap como uno de los objetivos alcanzados.» — `zcT31zmE5Uc` @ 06:11 (explícito)
- «Necesito un high relevante de cuatro horas y de una hora que esté dentro de un fair value gap.» — `F3anMVV-VlI` @ 08:48 (explícito)

