---
tipo: "concepto"
titulo: "Manipulation leg"
title: "Manipulation leg"
confianza: "explícito"
estado: "vigente"
video: "1C4dgloDQrY"
timestamp: "16:51"
categoria: "CORE"
uso: ""
sinonimos: ["leg; pata de manipulación; manipulation leg"]
id: 79
---

> **Confianza:** explícito · **Estado:** vigente · **Categoría:** CORE

## Definición

Tramo entre el último swing high/low formado antes de que el precio llegue a la zona de interés y el punto donde se produce la manipulación.

## Interpretación de Xavi

Es la referencia para elegir el IFVG de entrada y colocar el stop. Siempre se mira el último alto/bajo creado antes de que el precio llegue a la zona; dentro de esa leg, manda el IFVG de la temporalidad más alta.

## Cómo identificarlo

Localizar la zona (FVG de 15m, 1H o 4H). Retroceder al último swing high/low previo al toque de la zona. El inicio de la leg es ese swing; el final, el extremo de la manipulación.

## Cuándo se usa

En los tres modelos de entrada de junio de 2026 (Judas, reversal y continuación); especialmente en el reversal, donde la leg da la estructura.

## Condiciones

Debe haber una zona de interés y un desplazamiento hacia ella que forme un swing previo claro.

## Temporalidades

El IFVG se busca en la temporalidad más alta dentro de la leg: 30s, 1m, 2m, 3m o 5m.

## Aplicación

Define qué IFVG se opera y dónde va el stop (al otro lado del extremo de la leg).

## Errores comunes

Coger un IFVG de temporalidad baja cuando dentro de la leg hay uno de temporalidad más alta.

## Excepciones

En el modelo de continuación la referencia se reconstruye con el nuevo high/low que se crea tras el primer rechazo.

## Notas

Primera definición completa encontrada en el corpus; antes el término aparecía sin desarrollar.

## Requiere / se combina con

- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]

## Evidencia

- «Siempre tenemos que mirar el último alto que se ha creado antes de que el precio llegue a la zona.» — `1C4dgloDQrY` @ 16:51 (explícito)

## Fragmentos visuales

![Manipulation leg en 1C4dgloDQrY](../media/manipulation-leg-683.webp)

**La SIMPLE ESTRATEGIA con la que he podido RETIRAR +25k$ en PAYOUTS** (`1C4dgloDQrY`) · **16:51** · **Confianza:** explícito · anotado · imagen de contexto, no muestra el concepto
> NQ 5 minutos, sesión del 30 de diciembre, con una zona gris (FVG) y una línea horizontal corta que marca el último alto previo a la entrada en la zona. El precio barre el mínimo y gira.

