---
tipo: "regla"
titulo: "Stop estructural al otro lado de la manipulación"
title: "Stop estructural al otro lado de la manipulación"
confianza: "observado"
estado: "vigente"
video: "OdljBowQurk"
timestamp: "07:15"
id: 55
version: 1
---

# Stop estructural al otro lado de la manipulación

> **Confianza:** observado · **Estado:** vigente · **Versión:** 1

## Descripción

El stop se coloca al otro lado del swing/manipulación que originó la entrada, no a un número fijo de ticks.

## Contexto

Ejecución de cualquier setup.

## Condiciones

Identificar el high/low de la manipulación.

## Confirmaciones

El nivel protegido se mantiene.

## Condiciones de entrada

Se calcula antes de entrar.

## Invalidación

Si el precio rompe el nivel, la idea deja de ser válida.

## Gestión de riesgo

Define el riesgo en dólares; se ajusta el tamaño para no superar el % de la fase.

## Objetivos

No aplica.

## Excepciones

El stop exacto por setup no está fijado; es OBSERVADO/INFERIDO.

## Notas

Documento 07 y 09.

## Evidencia

- «Paráfrasis: el stop queda protegido por el high del sweep de las 10:00.» — `OdljBowQurk` @ 07:15 (observado)

