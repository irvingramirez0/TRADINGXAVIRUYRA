---
tipo: "regla"
titulo: "Validar el FVG en la temporalidad en la que se marcó"
title: "Validar el FVG en la temporalidad en la que se marcó"
confianza: "explícito"
estado: "vigente"
video: "1McPSXSSR48"
timestamp: "14:21"
id: 115
version: 1
---

# Validar el FVG en la temporalidad en la que se marcó

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1
- **Clase del bootcamp:** [[../bootcamp/dia-08|Día 8 — FVG: definición, respeto y validación por temporalidad]]

## Descripción

Un FVG marcado en 5 minutos se juzga en 5 minutos: un cierre de 1 minuto al otro lado no lo invalida si la vela de 5 minutos sigue aguantando. La temporalidad menor no sustituye el cierre de la temporalidad del gap.

## Contexto

Lectura de FVG/IFVG.

## Condiciones

Esperar el cierre de la vela de la temporalidad en la que se marcó el FVG.

## Confirmaciones

El cuerpo de esa temporalidad no cierra al otro lado del gap.

## Condiciones de entrada

No aplica: es una regla de validación, no de entrada.

## Invalidación

Cierre de cuerpo completo al otro lado del gap en la temporalidad del FVG.

## Gestión de riesgo

No aplica.

## Objetivos

No aplica.

## Excepciones

Alcance explícito 5m; la generalización a 15m/1H/4H es inferida.

## Notas

Documento 02 §4.4. No contradice la alineación de timeframes (regla 73): la alineación elige contexto; la validación se hace en la temporalidad del gap.

## Conceptos relacionados

- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]

## Evidencia

- «Paráfrasis: mirar siempre la temporalidad de 5 minutos; aunque en 1 minuto se haya invertido, en 5 minutos seguimos aguantando.» — `1McPSXSSR48` @ 14:20 (explícito)
- «Paráfrasis: el FVG se valida en la temporalidad en la que se marcó; un cierre de 1 minuto al otro lado no invalida un FVG de 5 minutos si la vela de 5 minutos sigue aguantando.» — `1McPSXSSR48` @ 14:21 (explícito)

