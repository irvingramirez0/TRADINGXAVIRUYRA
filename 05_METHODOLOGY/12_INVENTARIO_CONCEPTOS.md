# 12 — INVENTARIO DE CONCEPTOS

**Estado:** vivo. Se actualiza cuando se añade o reclasifica un concepto.
**Última actualización:** 2026-11-14
**Fuente:** tabla `concepts` de `07_KNOWLEDGE_BASE/xavi_ruyra.db`; definiciones ya documentadas en los documentos 01–09. Este documento no añade interpretación nueva: ordena y hace auditable lo que ya está registrado.

---

## 1. Para qué sirve

Es el inventario completo y la clasificación de los 53 conceptos registrados. Responde a tres preguntas: qué es CORE, qué es apoyo y qué queda fuera. No resuelve la lista de los "cuatro conceptos" que Xavi menciona en el Día 5: esa lista sigue sin confirmar y no se deduce de este inventario.

**Criterio de clasificación:**

- **CORE:** aparece en la construcción del bias, la zona o la entrada; sin él no se puede explicar la operativa.
- **SUPPORTING:** confluencia, filtro o herramienta de gestión; mejora la decisión pero no la sustituye.
- **CONTEXTUAL:** instrumento, tipo de cuenta, sesión o evento; condiciona la aplicación, no genera señal.
- **NOT USED:** él lo ha excluido explícitamente o no aparece en el corpus. Se registra para no atribuírselo.

---

## 2. Resumen

| Categoría | Conceptos |
|---|---|
| CORE | 16 |
| SUPPORTING | 12 |
| CONTEXTUAL | 14 |
| NOT USED | 11 |
| **Total** | **53** |

---

## 3. Inventario

### 3.1. CORE — núcleo operativo

Conceptos sin los cuales no se puede describir su operativa: construyen el bias, la zona o la entrada.

| Concepto | Definición operativa registrada | Primera fuente | Evidencias | Estado / certeza |
|---|---|---|---|---|
| **Liquidez (BSL/SSL)** | Dinero en forma de órdenes/stops que descansa por encima de los máximos (BSL) y por debajo de los mínimos (SSL). | `7HOAf7vHMqU` 1:08 | 3 | vigente / EXPLICITO |
| **Swing High / Swing Low** | Máximo o mínimo prominente en los extremos de un rango. En el Día 4: un high se forma con una vela alcista seguida de una bajista; se marca la mecha más alta de las dos. Un low se forma con una vela bajista… | `SuRgJd8ONIc` | 2 | vigente / EXPLICITO |
| **Fair Value Gap (FVG)** | Secuencia de tres velas consecutivas en la que las mechas de la primera y la tercera no se tocan; el espacio entre ambas es el FVG. La vela del medio es la referencia. | `u-fG6bYvK7k` 0:32 | 5 | vigente / EXPLICITO |
| **Inverse Fair Value Gap (IFVG)** | FVG que ha sido invertido: una vela cierra con el cuerpo completamente al otro lado del FVG. | `u-fG6bYvK7k` 6:11 | 4 | vigente / EXPLICITO |
| **Draw on Liquidity (DOL)** | Nivel de liquidez hacia el que se espera que vaya el precio: un high/low relevante dentro de un FVG/PD array. | `Urrb1b2kBso` 0:32 | 6 | vigente / EXPLICITO (3 históricas OBSERVADAS) |
| **Daily Bias** | Dirección que se espera para el día (compras o ventas), construida desde el respeto/inversión de FVG en 4H y 1H. | `Urrb1b2kBso` 0:32 | 6 | vigente / EXPLICITO (5 históricas OBSERVADAS) |
| **PD Array** | Para Xavi, un PD array es un fair value gap. | `F3anMVV-VlI` 8:48 | 2 | vigente / EXPLICITO |
| **PO3 (Power of 3)** | AMD (acumulación, manipulación, distribución) acompañado de tiempo. Se busca en aperturas concretas, especialmente cada open de 15 minutos. | `oP7enoxXpfI` 2:42 | 2 | vigente / EXPLICITO |
| **AMD (Acumulación, Manipulación, Distribución)** | Tres fases: acumulación (el precio se prepara), manipulación (movimiento contra el DOL para barrer liquidez) y distribución (movimiento hacia el DOL). | `oP7enoxXpfI` 2:42 | 2 | vigente / EXPLICITO |
| **Stacked PO3** | Secuencia de PO3 en aperturas consecutivas de 15m (9:30 → 9:45 → 10:00 → 10:15 → 10:30) mientras se respetan los key levels. | `oP7enoxXpfI` 6:17 | 2 | vigente / EXPLICITO |
| **Judas Swing** | Primer PO3 del día: acumulación en premarket, manipulación en el market open (9:30) y distribución en la dirección del DOL. | `vz4rhIi5Joo` 2:09 | 3 | vigente / EXPLICITO |
| **Open de las 10:00** | Apertura de la vela de las 10:00 NY, que coincide con el open de la vela de 4H y de 1H. Se busca un PO3 con liquidity sweep y entrada por IFVG/CISD. | `vz4rhIi5Joo` 9:23 | 2 | vigente / EXPLICITO |
| **Equilibrium (premium/descuento)** | Línea media de un rango que separa la zona premium (cara, arriba) de la zona de descuento (barata, abajo). En el bootcamp se dibuja con el retroceso de Fibonacci (0.5); la cuadrícula de Gann es la versión histórica de 2025. Compras en descuento; ventas en premium. | `AacVWPPYK8Y` 0:02; `56ES-W1d0xw` 0:35 | 8 | vigente / EXPLICITO (config. Fibonacci NO CONFIRMADA; Gann histórica) |
| **True Manipulation** | Situación en la que los dos índices correlacionados (NQ y ES) están en un punto donde tiene sentido que distribuyan. | `OdljBowQurk` 4:40 | 3 | vigente / EXPLICITO; las 3 referencias son del mismo vídeo |
| **Manipulation leg** | Tramo entre el último swing high/low formado antes de que el precio llegue a la zona de interés y el punto donde se produce la manipulación. | `1C4dgloDQrY` 16:51 | 1 | vigente / EXPLICITO |
| **Key Levels** | Zonas de conflicto donde se espera que el precio se frene o se dé la vuelta. Se identifican con FVG de 15m, 1H y 4H (nunca 5m) más liquidez (altos/bajos dentro del gap). Incluye NDOG, NWOG y altos/bajos de 1H y 4H. | `J7Dh-aj9-e0` 00:03 | 8 | vigente / EXPLICITO |

### 3.2. SUPPORTING — confluencias y herramientas

Refinan la decisión, pero no sustituyen a los CORE. Algunos son opcionales.

| Concepto | Definición operativa registrada | Primera fuente | Evidencias | Estado / certeza |
|---|---|---|---|---|
| **CISD (Change in State of Delivery)** | Cierre de una vela por encima del cuerpo de una vela alcista anterior (CISD alcista) o por debajo del cuerpo de una vela bajista anterior (CISD bajista). | `_drb5sSmQZE` 0:33 | 2 | vigente / EXPLICITO |
| **SMT (Smart Money Technique)** | Divergencia entre dos índices correlacionados: uno barre un high/low y el otro no. | `F3anMVV-VlI` 5:11 | 2 | vigente / EXPLICITO |
| **NWOG (New Week Opening Gap)** | Gap de apertura semanal. Funcionalmente actúa como un FVG. | `u-fG6bYvK7k` 10:24 | 1 | vigente / EXPLICITO |
| **NDOG (New Day Opening Gap)** | Gap de apertura diaria. | `Urrb1b2kBso` 2:06 | 1 | vigente / EXPLICITO |
| **Equal Highs / Equal Lows** | Dos o más highs/lows al mismo nivel o muy cercanos; generan una bolsa de liquidez. | `Urrb1b2kBso` 2:06 | 1 | vigente / EXPLICITO |
| **Low Resistance Liquidity (LRL)** | Muchos highs que están juntos o lows que no se han llegado a quitar nunca entre ellos. | `Urrb1b2kBso` 9:24 | 4 | vigente / EXPLICITO |
| **Internal / External Liquidity** | Liquidez interna: highs/lows dentro del rango. Liquidez externa: highs/lows fuera del rango. | `u-fG6bYvK7k` 13:00 | 1 | vigente / EXPLICITO |
| **Break-even estructural** | Mover el stop al precio de entrada solo cuando hay un high/low relevante dentro de un FVG/gap de 5 minutos o más, o en una zona de conflicto (FVG de 5m, 15m, 1H o 4H). La versión de mayo de 2026 decía 3m o más. | `5aBdJLMDGJc` 6:53 | 3 | vigente / EXPLICITO |
| **Displacement** | Movimiento impulsivo del precio que deja un FVG y muestra intención. | `oP7enoxXpfI` 10:24 | 1 | vigente / EXPLICITO |
| **Protected High / Low** | High/low que el precio no debería romper si la idea direccional es correcta; sirve de referencia para el stop y para la gestión. | `5aBdJLMDGJc` 6:22 | 1 | vigente / OBSERVADO |
| **Pattern trades** | Trades que a simple vista cumplen la estrategia pero que, por el contexto (normalmente un desplazamiento agresivo previo), no son ideales y suelen acabar en stop. | `1C4dgloDQrY` 27:47 | 1 | vigente / EXPLICITO |
| **PDH / PDL (previous day high/low)** | Alto y bajo de la última vela diaria cerrada; el precio tiende a visitarlos y reaccionar. Se marcan en gráfico diario. Es el tipo de liquidez que Xavi considera menos esencial ("skipeable"). | `OtYATAfCfRA` 1:36 | 1 | vigente / EXPLICITO |

### 3.3. CONTEXTUAL — contexto de aplicación

Instrumentos, cuentas, sesiones y eventos. No son señal por sí mismos.

| Concepto | Definición operativa registrada | Primera fuente | Evidencias | Estado / certeza |
|---|---|---|---|---|
| **Data Highs / Lows** | Highs/lows que deja una noticia (CPI, FOMC, etc.) y que se usan como referencia de liquidez. | `oP7enoxXpfI` 27:15 | 1 | vigente / EXPLICITO |
| **Rejection Block** | Zona de rechazo que Xavi estaba probando en backtesting. | `5aBdJLMDGJc` 19:16 | 1 | experimental / EXPLICITO |
| **MNQ / MES** | Contratos micro de Nasdaq y SP500, con menor riesgo que NQ/ES. | `mBHtx-BfWWg` 0:35 | 1 | vigente / EXPLICITO |
| **Cuentas de fondeo** | Cuentas de empresas de fondeo que se pagan, se pasan en evaluación y luego generan payouts. | `3aG0N7aHu4s` | 1 | vigente / EXPLICITO |
| **Sesión de Londres** | Sesión europea; la usa para pasar evaluaciones. Se mueve más lenta que Nueva York, pero con la misma lógica de liquidez e imbalances. El recap de mayo de 2026 es la única operación documentada; la secuencia horaria no está confirmada. | `ndABd2MECBA` 7:54 | 5 | vigente / EXPLICITO (lógica); horario NO CONFIRMADO |
| **Prisa (psicología)** | Presión por alcanzar un resultado antes de una fecha autoimpuesta; se corrige con un objetivo de proceso (60 días) y revisando el motivo de cada objetivo. | `GO9GLSF_vLo` 1:08 | 4 | vigente / EXPLICITO |
| **Miedo a perder (psicología)** | Bloqueo o duda al ejecutar un setup por temor a perder. Se diagnostica (riesgo alto / desconfianza en el sistema) y se corrige bajando el riesgo o construyendo confianza con backtesting y diario. | `WHz8ySmAcnQ` 2:02 | 8 | vigente / EXPLICITO |
| **Gambling vs trading (psicología)** | Acepta que el trading es una apuesta, pero con estadística a favor; la frontera es seguir el plan. Cada trade es aleatorio; la ventaja está en la muestra. La fase de gambling es obligatoria y hay que acortarla. | `ZOxEUWwDSoQ` 1:05 | 9 | vigente / EXPLICITO |
| **Sesión de Nueva York** | Ventana en la que opera: 9:30–11:00 hora de Nueva York (15:30–17:00 en España). Su ventana de entradas declarada es 9:30–10:30. | `j4f8fV13GQM` 0:37 | 1 | vigente / EXPLICITO |
| **No News Monday** | Lunes sin noticias de impacto; lo trata como día de cautela porque el precio suele moverse lento. No lo prohíbe. | `j4f8fV13GQM` 5:19 | 1 | vigente / EXPLICITO |
| **Bank Holiday (festivo EE. UU.)** | Festivo en EE. UU. con el mercado cerrado; ese día no se opera. | `j4f8fV13GQM` 5:31 | 1 | vigente / EXPLICITO |
| **Revenge Trading (psicología)** | Después de una pérdida, subir el riesgo y reentrar para recuperarla; el bucle puede acabar en sobreoperar, sobrelotear y quemar la cuenta. No hay truco externo: la solución es que uno mismo pare. | `eH7QCo2d0TU` 00:02 | 7 | vigente / EXPLICITO |
| **FOMO (psicología)** | Miedo a perderse un movimiento que se sabe que va a ocurrir. Se evita no entrando si la estrategia no se ha presentado; el backtesting no tiene FOMO. | `2kBd2-bLuwU` 00:32 | 6 | vigente / EXPLICITO |
| **Ego (psicología)** | Exceso de confianza que aparece tras una racha de victorias y lleva a creer que el resultado está garantizado; puede relajar el filtro de entrada, subir el riesgo o replicar cuentas en exceso. | `ygJya0srm8g` 0:33 | 5 | vigente / EXPLICITO |

### 3.4. NOT USED — excluidos

Lo que no forma parte de su metodología. Se registran para no atribuírselos.

| Concepto | Definición operativa registrada | Primera fuente | Evidencias | Estado / certeza |
|---|---|---|---|---|
| **RSI** | Indicador de fuerza relativa. | — | 1 | no usado / OBSERVADO |
| **MACD** | Indicador de convergencia/divergencia de medias. | — | 1 | no usado / OBSERVADO |
| **Medias móviles** | Indicadores de media móvil. | — | 1 | no usado / OBSERVADO |
| **Bandas de Bollinger** | Indicador de volatilidad. | — | 1 | no usado / OBSERVADO |
| **Volumen** | Indicador de volumen. | `3aG0N7aHu4s` | 1 | no usado / EXPLICITO |
| **Order Flow** | Análisis de flujo de órdenes. | `mBHtx-BfWWg` 6:21 | 1 | no usado / EXPLICITO |
| **Elliott Wave** | Teoría de ondas. | — | 1 | no usado / OBSERVADO |
| **Armónicos** | Patrones armónicos. | — | 1 | no usado / OBSERVADO |
| **Patrones chartistas clásicos** | Patrones de gráfico clásicos. | — | 1 | no usado / OBSERVADO |
| **Fundamentales** | Análisis fundamental o macro como método direccional. | — | 1 | no usado / OBSERVADO |
| **Breakaway Gap** | Gap de ruptura. Xavi declara que no lo usa porque no sabe distinguirlo con seguridad y prefiere no complicarse. | `sTS-iWJvTf0` 21:21 | 1 | no usado / EXPLICITO |

---

## 4. Lectura del inventario

- **16 CORE, 12 SUPPORTING, 14 CONTEXTUAL y 11 NOT USED.** El núcleo documentado es amplio; la simplificación a cuatro conceptos es una afirmación suya, no una consecuencia de este recuento.
- **Rejection Block** es el único concepto marcado como `experimental`: él lo prueba en backtesting y dice que no lo operaría en fondeo. No se enseña como parte de la metodología.
- **Protected High / Low** es el único SUPPORTING con certeza `OBSERVADO`: se infiere de cómo coloca el stop y el break-even, no de una definición explícita.
- **Equilibrium** tiene ocho evidencias: la definición antigua y la configuración visual de la cuadrícula de Gann (`AacVWPPYK8Y` 01:38 y frame 0037, 03:06, históricas) y seis del Día 19 (`56ES-W1d0xw`): la herramienta Fibonacci [00:35], para qué sirve el equilibrium [01:06], la combinación con swings y FVG [01:37], la implicación en cortos [04:19], el 0.5 con premium arriba/descuento abajo [05:21] y compras en descuento/ventas en premium [06:22]. La configuración exacta de Fibonacci sigue NO CONFIRMADA.
- **Daily Bias y DOL** se densificaron con cinco BIAS diarios de 2025 (frames 724–728). Son ejemplos históricos del método antiguo con niveles de Londres/Asia; no sustituyen la versión vigente de 2026.
- **Revisión CORE (2026-11-01):** Swing High/Low tiene 2 fuentes independientes (`SuRgJd8ONIc`, Día 4; `7HOAf7vHMqU`, Día 6). IFVG tiene 4 vídeos (`u-fG6bYvK7k`, `vz4rhIi5Joo`, `mCMpxc0NaN4`, `1McPSXSSR48`), pero la definición de inversión por cierre de cuerpo sigue anclada en el primero; los otros documentan usos contextuales o, en el Día 8, una mención introductoria. PD Array tiene 2 fuentes explícitas; la captura de `oP7enoxXpfI` es contexto y no etiqueta visualmente el PD array. PO3 y AMD tienen 2 fuentes independientes (`oP7enoxXpfI`, `vz4rhIi5Joo`), con definiciones apoyadas en audio. Stacked PO3 tiene 2 ejemplos del mismo vídeo, no confirmaciones independientes. Judas Swing tiene 3 referencias en 2 vídeos (`vz4rhIi5Joo`, `F3anMVV-VlI`). Manipulation leg conserva 1 fuente (`1C4dgloDQrY`); las menciones del vídeo no cuentan como fuentes independientes.
- **Sesión de Londres** pasa de 1 a 5 evidencias: el recap de 2026-05-14 (frames 729–732) y los BIAS de 2025 (frames 724–726). La lógica es la misma que Nueva York, más lenta; lo que falta es la secuencia horaria.
- Los **11 NOT USED** no son "conceptos de ICT que él usa poco": son excluidos o ausentes. Varios tienen certeza `OBSERVADO` porque la exclusión se deduce de su configuración y sus explicaciones, no de una frase única.
- La definición de **Break-even estructural** se actualizó a 5m+ (junio de 2026); la versión de 3m+ de mayo se conserva como antecedente en `10_EVOLUCION.md` y en la tabla `changes`.

---

## 5. Cómo se mantiene

1. Todo concepto nuevo se inserta primero en `concepts` con definición, fuente y certeza.
2. Se le asigna categoría solo si hay evidencia; si no, queda `UNKNOWN`.
3. Se añade aquí en la sección correspondiente.
4. Si cambia de categoría o de definición, se registra en `changes` y en `10_EVOLUCION.md`.
5. `validate_kb.py` comprueba que ningún concepto quede sin evidencia.

**Regla:** este inventario no cierra preguntas abiertas. La lista de los cuatro conceptos, la definición de RDR y la regla general del double SMT siguen en `11_PREGUNTAS_ABIERTAS.md`.
