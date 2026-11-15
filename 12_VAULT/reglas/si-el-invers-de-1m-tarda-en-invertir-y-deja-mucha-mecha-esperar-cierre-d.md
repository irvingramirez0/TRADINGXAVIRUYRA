---
tipo: "regla"
titulo: "Si el invers de 1m tarda en invertir y deja mucha mecha, esperar cierre del CISD"
title: "Si el invers de 1m tarda en invertir y deja mucha mecha, esperar cierre del CISD"
confianza: "explícito"
estado: "vigente"
video: "PzkT4SC47Jo"
timestamp: "27:41"
id: 98
version: 1
---

# Si el invers de 1m tarda en invertir y deja mucha mecha, esperar cierre del CISD

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

Cuando el invers de 1m tarda mucho en formarse y deja una mecha grande, no entra: espera un cierre por debajo/encima del CISD, aunque el RR sea peor.

## Contexto

Entrada fina en 1m.

## Condiciones

Invers lento y con mecha grande.

## Condiciones de entrada

Cierre de vela que confirme el CISD.

## Invalidación

Si el precio se va sin cierre, no se persigue.

## Gestión de riesgo

Acepta peor RR a cambio de dirección.

## Notas

Backtest de marzo. Regla explícita en el vídeo; no formulada como norma numerada.

## Conceptos relacionados

- [[cisd-change-in-state-of-delivery|CISD (Change in State of Delivery)]]

## Evidencia

- «Porque tarda muchísimo en invertir y deja mucha mecha. Normalmente... esperarme a un cierre por debajo del change state of delivery... a pesar de pillar un RR peor, me aseguro que mi dirección del trade tiene más sentido.» — `PzkT4SC47Jo` @ 27:41 (explícito)

