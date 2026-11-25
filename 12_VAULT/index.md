---
tipo: portada
titulo: "Metodología Xavi Ruyra — estudio no oficial"
title: "Metodología Xavi Ruyra — estudio no oficial"
confianza: "no confirmado"
estado: vigente
video: ""
timestamp: ""
anotaciones: false
panel:
  titulo: "El proyecto en cifras"
  bloques:
    - {etiqueta: "clases de bootcamp", valor: 29}
    - {etiqueta: "conceptos", valor: 58}
    - {etiqueta: "reglas", valor: 156}
    - {etiqueta: "operaciones", valor: 54, nota: "P&L autodeclarado"}
    - {etiqueta: "cambios", valor: 67}
    - {etiqueta: "preguntas abiertas", valor: 34}
  barras:
    - {etiqueta: "Fotogramas con anotación verificable", hecho: 129, total: 1456, nota: "el resto está extraído pero sin revisar, y no se publica como prueba visual"}
  pie: "Todo lo que aparece en este sitio se regenera desde una base SQLite con `python 09_AUTOMATION/pipeline.py`. Las cifras de esta portada se cuentan en cada generación, no se escriben a mano."
---


> **Proyecto de estudio no oficial.** Este sitio es un resumen estructurado y trazable de contenido público de Xavi Ruyra. No es un curso oficial, no está afiliado ni respaldado por él, y no sustituye a sus vídeos. Todo lo que no tiene fuente con vídeo y minuto se marca como **no confirmado**.

**Fecha de corte de las cifras:** 2026-11-23. 
Es la fecha del vídeo más reciente que **ya tiene evidencia citada**: lo anunciado pero aún sin trabajar no cuenta como contenido.

## Por dónde entrar

<div class="xr-tarjetas">
<a class="xr-tarjeta" href="./00-empieza-aqui"><span class="xr-tarjeta-titulo">Empieza aquí</span><span class="xr-tarjeta-desc">La metodología, en orden y con minuto.</span></a>
<a class="xr-tarjeta" href="./bootcamp"><span class="xr-tarjeta-titulo">Bootcamp</span><span class="xr-tarjeta-desc">Las 29 clases en orden, con lo que da cada una.</span></a>
<a class="xr-tarjeta" href="./conceptos"><span class="xr-tarjeta-titulo">Conceptos</span><span class="xr-tarjeta-desc">58 conceptos con definición, condiciones y errores.</span></a>
<a class="xr-tarjeta" href="./reglas"><span class="xr-tarjeta-titulo">Reglas operativas</span><span class="xr-tarjeta-desc">156 reglas, incluidas las obsoletas con su sustituto.</span></a>
<a class="xr-tarjeta" href="./operaciones"><span class="xr-tarjeta-titulo">Operaciones</span><span class="xr-tarjeta-desc">54 operaciones analizadas, con el P&L autodeclarado.</span></a>
<a class="xr-tarjeta" href="./cambios"><span class="xr-tarjeta-titulo">Cambios</span><span class="xr-tarjeta-desc">67 cambios de criterio documentados.</span></a>
<a class="xr-tarjeta" href="./preguntas"><span class="xr-tarjeta-titulo">Preguntas abiertas</span><span class="xr-tarjeta-desc">34 preguntas sin cerrar.</span></a>
<a class="xr-tarjeta" href="./contradicciones"><span class="xr-tarjeta-titulo">Contradicciones</span><span class="xr-tarjeta-desc">Dos versiones conviven; la vigente se lee primero.</span></a>
<a class="xr-tarjeta" href="./comprobador"><span class="xr-tarjeta-titulo">Comprobador de fuentes</span><span class="xr-tarjeta-desc">Lo que el sitio no puede respaldar, dicho en voz alta.</span></a>
</div>

## Cómo leer una nota

Cada nota empieza con una **ficha de fuente**: tipo, confianza, estado y un botón que salta al minuto exacto del vídeo. Debajo, la nota en sí. Al final, las **anotaciones**: se puede comentar por sección, sin cuenta.

| Nivel | Significado |
|---|---|
| **explícito** | Xavi lo dice literalmente en un vídeo; hay cita y minuto. |
| **observado** | Se desprende de lo que hace en un ejemplo o recap, no de una regla formulada. |
| **inferido** | Interpretación del proyecto a partir de varias fuentes; no está formulado. |
| **no confirmado** | No hay fuente suficiente. Se deja anotado como pregunta abierta. |

## Conceptos núcleo

- [[liquidez-bsl-ssl|Liquidez (BSL/SSL)]]
- [[swing-high-swing-low|Swing High / Swing Low]]
- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]
- [[draw-on-liquidity-dol|Draw on Liquidity (DOL)]]
- [[daily-bias|Daily Bias]]
- [[pd-array|PD Array]]
- [[po3-power-of-3|PO3 (Power of 3)]]
- [[amd-acumulacion-manipulacion-distribucion|AMD (Acumulación, Manipulación, Distribución)]]
- [[stacked-po3|Stacked PO3]]
- [[judas-swing|Judas Swing]]
- [[open-de-las-10-00|Open de las 10:00]]
- [[equilibrium-premium-descuento|Equilibrium (premium/descuento)]]
- [[true-manipulation|True Manipulation]]
- [[manipulation-leg|Manipulation leg]]
- [[key-levels|Key Levels]]

## Fuente y límites

Los datos se regeneran desde SQLite con `09_AUTOMATION/pipeline.py`. Los fotogramas son capturas de vídeos públicos usadas como cita visual; las transcripciones completas y los Reels de Instagram quedan fuera de este sitio.

Las cifras de operaciones son **autodeclaradas**: no hay extractos de cuenta que las respalden. El sitio lo repite en cada ficha porque es la diferencia entre documentar y auditar.
