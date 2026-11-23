---
tipo: "operacion"
titulo: "Operación #24 — NQ — 2026-05-12"
title: "Operación #24 — NQ — 2026-05-12"
confianza: "observado"
estado: "vigente"
video: "b2H3Q3dQhi8"
timestamp: ""
fecha: "2026-05-12"
clasificacion: "Mixto"
id: 24
---

> **Aviso:** P&L autodeclarado, no auditado. Las cifras provienen de lo que Xavi dice en el vídeo y no se han verificado con extractos de cuenta.

> **Clasificación:** Mixto · **Confianza:** observado

## Contexto

En 4 horas el Nasdaq tapea un FVG alcista; también hay un FVG alcista diario y un FVG de 1 hora, por lo que idealmente buscaría compras aunque esté en all time highs. Ha habido una bajada de casi un 2%; no lo considera un sell model en 4 horas (sigue en compras), pero sí un retroceso con mucha fuerza. Se marca condiciones ('si pasa esto, hago esto'). Zona de interés: FVG de 1 hora sin filear.

## Razonamiento

Trade 1: confluencia de FVG de 4 horas, diario y 1 hora, más IFVG de 1 minuto y cierre sobre el order block, buscando el high de 1 hora. Trade 2: SMT con el SP500, desplazamiento fuerte e IFVG de 3 minutos; el SP500 y el Nasdaq buscan el mismo objetivo y el SP500 confirma con su desplazamiento.

## Setup

Trade 1 (long): la primera vela tapea 5 y 15 minutos; IFVG de 1 minuto; cierre por encima del CHSD/order block; a 27 puntos del high de 1 hora. Trade 2 (short): tras tapeo del FVG de 1 hora por SP y NQ, el SP500 quita los highs y el Nasdaq no (SMT); desplazamiento fuerte e IFVG de 3 minutos; target internal low dentro del FVG de 1 hora.

## Entrada

Trade 1: IFVG de 1 minuto. Trade 2: IFVG de 3 minutos. Precios exactos no constan.

## Stop

Trade 1: no consta. Trade 2: en el body.

## Objetivo

Trade 1: 1:1. Trade 2: internal low dentro del FVG de 1 hora, 1:1 (TP de 500 $).

## Resultado

Trade 1: break-even (aunque habría dado TP; él dice que se equivocó yendo a BE). Trade 2: TP de 500 $ con 5 contratos. Total del día: 1.008,88 $ de profit.

## Gestión

Trade 1: BE cuando el SP500 filea el FVG de 5 minutos a las 9:40, por baja correlación y para asegurar. Trade 2: BE dos ticks antes de que el SP500 quitara el low más grande; luego TP. Parciales: no consta.

## Análisis posterior

Escribir condiciones antes de operar: 'si pasa esto, hago esto' evita dudas y permite ejecutar.; En all time highs, las continuaciones de 5 minutos son los trades más seguros.; La baja correlación entre NQ y SP500 es una señal de cautela.; El break-even puede ser incorrecto ex-post pero razonable ex-ante; él lo califica de error porque conocía el resultado.; Stop en el body y reducir contratos cuando sube la volatilidad para mantener el mismo riesgo.; Shortear en ATH solo cuando ambos índices apuntan al mismo objetivo y el SP500 confirma con desplazamiento.

## Notas

Fuente: recap del vídeo. Escribir condiciones antes de operar: 'si pasa esto, hago esto' evita dudas y permite ejecutar.; En all time highs, las continuaciones de 5 minutos son los trades más seguros.; La baja correlación entre NQ y SP500 es una señal de cautela.; El break-even puede ser incorrecto ex-post pero razonable ex-ante; él lo califica de error porque conocía el resultado.; Stop en el body y reducir contratos cuando sube la volatilidad para mantener el mismo riesgo.; Shortear en ATH solo cuando ambos índices apuntan al mismo objetivo y el SP500 confirma con desplazamiento.. Citas: [2.87s] nunca o casi nunca eh shorteo all time highs | [94.96s] Y cuando digo condiciones, me refiero a si pasa esto, hago esto. | [313.07s] creo que me he equivocado yendo break even | [530.32s] entonces he reducido contratos simplemente para arriesgar lo mismo y hemos hecho un TP de 500 dólares | Clasificación original: Trade 1: Error de ejecución (break-even prematuro; el propio Xavi dice 'creo que me he equivocado yendo break even'), aunque la entrada era correcta y el resultado fue BE. Trade 2: Bien ejecutado ganador.

## Conceptos presentes

- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[smt-smart-money-technique|SMT (Smart Money Technique)]]
- [[break-even-estructural|Break-even estructural]]
- [[displacement|Displacement]]

## Reglas relacionadas (detección automática)

- [[no-coger-el-primer-ifvg-tras-un-desplazamiento-fuerte|No coger el primer IFVG tras un desplazamiento fuerte]]
- [[la-manipulation-leg-se-mide-desde-el-ultimo-swing-antes-de-la-zona|La manipulation leg se mide desde el último swing antes de la zona]]
- [[hacer-backtesting-con-nq-y-es-abiertos-y-en-sesion-de-nueva-york|Hacer backtesting con NQ y ES abiertos y en sesión de Nueva York]]
- [[el-dol-debe-estar-dentro-de-un-fvg-pd-array|El DOL debe estar dentro de un FVG/PD array]]

