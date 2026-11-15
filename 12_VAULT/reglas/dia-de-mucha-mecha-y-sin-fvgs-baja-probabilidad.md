---
tipo: "regla"
titulo: "Día de mucha mecha y sin FVGs: baja probabilidad"
title: "Día de mucha mecha y sin FVGs: baja probabilidad"
confianza: "explícito"
estado: "vigente"
video: "3ChwQZ8hRN0"
timestamp: "16:19"
id: 84
version: 1
---

# Día de mucha mecha y sin FVGs: baja probabilidad

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 1

## Descripción

Si el día tiene muchas mechas y el precio no abre fair value gaps, el sistema no tiene estructura para operar; es un día de baja probabilidad.

## Contexto

Filtro de día, especialmente viernes o sesiones de chop.

## Condiciones

Predominio de mechas; ausencia de FVGs relevantes en 5m/15m.

## Confirmaciones

No hay desplazamientos que abran gaps.

## Condiciones de entrada

No operar.

## Excepciones

Puede operar si aparece un setup A+ aislado, pero no lo busca.

## Notas

Concreta el filtro general de 'día de baja probabilidad' (regla 76).

## Evidencia

- «no te ha creado ningún gap. De hecho, lo único que ves es una mecha» — `_drb5sSmQZE` @ 11:21 (explícito)
- «Los días que veáis que hay mucha mecha son días de baja probabilidad... porque no se abren fair value gaps» — `3ChwQZ8hRN0` @ 16:19 (explícito)

