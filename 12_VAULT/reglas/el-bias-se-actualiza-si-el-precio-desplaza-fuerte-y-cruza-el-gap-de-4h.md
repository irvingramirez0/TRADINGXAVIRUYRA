---
tipo: "regla"
titulo: "El bias se actualiza si el precio desplaza fuerte y cruza el gap de 4H"
title: "El bias se actualiza si el precio desplaza fuerte y cruza el gap de 4H"
confianza: "explícito"
estado: "vigente"
video: "PzkT4SC47Jo"
timestamp: "24:27"
id: 100
version: 1
---

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

Si el precio desplaza con fuerza, cierra velas fuertes en 15m/1H y cruza el gap de 4H cerca de las 10:00, cambia el bias y marca nuevos objetivos.

## Contexto

Intradía, cerca de la apertura de las 10:00.

## Condiciones

Desplazamiento fuerte; cierre de velas; cruce del gap de 4H.

## Condiciones de entrada

Se busca el nuevo escenario con confirmación (invers/CISD).

## Invalidación

Si el precio recupera el gap, vuelve al escenario anterior.

## Objetivos

Nuevos lows/highs marcados.

## Excepciones

No cambia el bias por una sola vela; lo hace cuando el desplazamiento es claro.

## Notas

Backtest de marzo. Regla explícita en el vídeo; no formulada como norma numerada.

## Conceptos relacionados

- [[daily-bias|Daily Bias]]
- [[cisd-change-in-state-of-delivery|CISD (Change in State of Delivery)]]
- [[displacement|Displacement]]

## Evidencia

- «o adapto mi bias a ventas» — `F3anMVV-VlI` @ 06:44 (explícito)
- «Cuando empezamos a desplazar así de fuerte hacia abajo, ya sabéis que muchas veces cambio mi bias... estamos atravesando este gap de 4 horas, así que igual mi bias está mal.» — `PzkT4SC47Jo` @ 24:27 (explícito)

