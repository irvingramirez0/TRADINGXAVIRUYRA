---
tipo: "regla"
titulo: "Hacer backtesting con NQ y ES abiertos y en sesión de Nueva York"
title: "Hacer backtesting con NQ y ES abiertos y en sesión de Nueva York"
confianza: "explícito"
estado: "vigente"
video: "nxlZJ6abOYA"
timestamp: "03:08"
id: 195
version: 1
---

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1
- **Clase del bootcamp:** [[../bootcamp/dia-29|Día 29 — Backtesting integrado]]

## Descripción

En la práctica integrada muestra NQ y ES a la vez, configura la sesión de Nueva York y mantiene sincronizadas las temporalidades en ambos gráficos para buscar SMT y key levels.

## Contexto

Backtesting del sistema completo antes de evaluaciones.

## Condiciones

Sesión de backtesting con dos instrumentos correlacionados y reloj en hora NY.

## Confirmaciones

La web abre en 09:29 y permite pasar vela a vela; los intervalos sincronizan el cambio de temporalidad entre ambos gráficos.

## Condiciones de entrada

Analizar primero contexto diario/4H/1H, después condiciones 5m/15m y ejecutar solo con IFVG de 30s–5m.

## Invalidación

Sin IFVG no entra aunque el precio haya respetado la zona.

## Gestión de riesgo

Usar una cuenta de práctica de 50.000 $ en el ejemplo; el riesgo mostrado es ilustrativo, no una regla nueva.

## Objetivos

Objetivos estructurales ya documentados: liquidez/zonas de conflicto; los importes de la sesión son ejemplos.

## Excepciones

La herramienta concreta es opcional: Xavi usa una web de pago y muestra una gratuita para el bootcamp.

## Notas

Bootcamp Día 29 [01:34–04:08, 13:39–14:10, 24:45–25:16]. No convierte la plataforma en metodología.

### Conceptos relacionados

- [[key-levels|Key Levels]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[smt-smart-money-technique|SMT (Smart Money Technique)]]
- [[cuentas-de-fondeo|Cuentas de fondeo]]
- [[sesion-de-nueva-york|Sesión de Nueva York]]

## Evidencia

- «Vais a poner NQ... More Instruments ES... una cuenta de $50.000...» — `nxlZJ6abOYA` @ 02:37 (explícito)
- «Para hacer backtesting siempre vamos a tener los dos gráficos abiertos... buscamos esos SMTs, esos key levels.» — `nxlZJ6abOYA` @ 03:08 (explícito)
- «Días así es obligatorio el IFVG, por lo tanto, no entramos. Si no tenemos ese IFVG, no entramos.» — `nxlZJ6abOYA` @ 13:39 (explícito)

