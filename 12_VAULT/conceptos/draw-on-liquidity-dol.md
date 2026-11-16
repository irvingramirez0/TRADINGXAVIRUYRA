---
tipo: "concepto"
titulo: "Draw on Liquidity (DOL)"
title: "Draw on Liquidity (DOL)"
confianza: "explícito"
estado: "vigente"
video: "Urrb1b2kBso"
timestamp: "00:32"
categoria: "CORE"
uso: ""
sinonimos: ["dol", "draw on liquidity", "objetivo", "target"]
id: 44
---

> **Confianza:** explícito · **Estado:** vigente · **Categoría:** CORE

## Definición

Nivel de liquidez hacia el que se espera que vaya el precio: un high/low relevante dentro de un FVG/PD array.

## Interpretación de Xavi

El DOL es el high/low relevante que está dentro de un FVG. No cualquier high/low: si no está dentro de una zona, no tiene peso. Se usa casi como sinónimo de daily bias, aunque el bias es la dirección y el DOL el nivel.

## Cómo identificarlo

Abrir 4H; ver si respeta FVG alcistas e invalida bajistas (o al revés); localizar el high/low relevante dentro de un FVG de 4H/1H. Si hay dos DOL o ninguno, no operar.

## Cuándo se usa

Antes de buscar entradas; define la dirección y el target.

## Condiciones

Tiene que estar dentro de un FVG/PD array. Excepciones: NDOG, LRL, relative equal highs/lows, SMT.

## Temporalidades

4H/1H para DOL principal; 15m/5m para DOL interno.

## Aplicación

Fijar el DOL; buscar PO3 en su dirección; target en el DOL o en la liquidez intermedia.

## Errores comunes

Usar un high/low que no está en ninguna zona; operar con DOL en ambos lados; forzar cuando el DOL ya se cumplió; sobreanalizar cada gap.

## Excepciones

NDOG, LRL, relative equal highs/lows y SMT pueden cambiar el DOL.

## Notas

Documento 03.

## Requiere / se combina con

- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[po3-power-of-3|PO3 (Power of 3)]]
- [[equilibrium-premium-descuento|Equilibrium (premium/descuento)]]
- [[smt-smart-money-technique|SMT (Smart Money Technique)]]

## Evidencia

- «Paráfrasis: el high marcado como DOL es el objetivo; el FVG queda por debajo.» — `TxoOh3MFdO0` @ 00:30 (observado)
- «Paráfrasis: el Asian low es el target de la proyección.» — `DbWKWSy5ycY` @ 01:10 (observado)
- «Paráfrasis: el FVG sin filar arriba es el TP final.» — `gNsZXb8j1So` @ 01:30 (observado)
- «Días en los que podemos tener un DOL aquí y un DOL aquí en los dos lados... son días en los que simplemente no puedes hacer nada.» — `zcT31zmE5Uc` @ 01:33 (explícito)
- «Paráfrasis: el high dentro de un FVG de 15 minutos es el TP.» — `8gs6HOHXMsc` @ 05:47 (explícito)
- «Necesito un high relevante de cuatro horas y de una hora que esté dentro de un fair value gap... un PD array viene a ser un fair value gap.» — `F3anMVV-VlI` @ 08:48 (explícito)

## Fragmentos visuales

![Draw on Liquidity (DOL) en TxoOh3MFdO0](../media/draw-on-liquidity-dol-727.webp)

**BIAS 03/11/25** (`TxoOh3MFdO0`) · **00:30** · **Confianza:** explícito · anotado
> Gráfico MNQZ25 1H. Líneas 'high' y 'DOL' sobre dos highs; zona verde 'FVG' por debajo del precio.

