# 05 — ENTRADAS: JUDAS SWING, OPEN DE LAS 10:00, IFVG Y CISD

**Estado:** vigente.
**Última actualización:** 2026-11-01
**Fuente principal:** `vz4rhIi5Joo` (2026-08-01), `_drb5sSmQZE` (2026-08-16), `oP7enoxXpfI` (2026-10-05).
**Fuentes de contraste:** `u-fG6bYvK7k` (2025-12-24), `Imr4TPKUD-c` (2026-09-25), `OdljBowQurk` (2026-10-22), `F3anMVV-VlI` (2026-07-10), `8gs6HOHXMsc` (2026-05-14, London).

---

## 1. Los dos sistemas de entrada

> "Yo tengo dos sistemas de entrada... Judas Swing... y luego tengo otro sistema de entrada que es básicamente el open de las 10, el Power of 3 de las 10, que es lo mismo, o el open de la vela de 4 horas." — `vz4rhIi5Joo` [00:02–01:06]

1. **Judas Swing:** 9:30–9:45.
2. **Open de las 10:00 / PO3 de las 10:00 / open de 4H:** el mismo concepto con tres nombres.

**Horario vigente:** 9:30–10:30. Antes operaba 9:30–11:00; la versión de agosto de 2026 corrige la anterior [01:06].

**Certeza:** EXPLÍCITO.

### 1.1. La versión de junio de 2026: tres modelos

En `1C4dgloDQrY` (2026-06-17), Xavi explica **tres modelos de entrada**, no dos:

1. **Judas Swing / AMD de market open:** acumulación en premarket, manipulación a un FVG de 15m/1H/4H y distribución hacia el DOL.
2. **Reversal en zona de interés:** el precio tapea un FVG y quita un internal high/low; se forma una manipulation leg y se entra con el IFVG de la temporalidad más alta de esa leg.
3. **Continuación:** se espera a que se cree un gap de 5m o 15m, se tapea y se entra con su IFVG. Nunca 3m.

> "He dicho que había dos, realmente hay tres. Luego os voy a explicar el tercero, pero es el más sencillo." — `1C4dgloDQrY` [26:13]

La versión de agosto de 2026 reorganiza la enseñanza en **dos sistemas** (Judas y open de las 10:00/PO3/4H). La de agosto es la vigente. La de junio se conserva porque desarrolla dos piezas que agosto no explica: la **manipulation leg** y el **modelo de continuación**. No se mezclan como si fueran la misma versión.

**Certeza:** EXPLÍCITO en ambas fechas. La diferencia es de organización, no necesariamente de operativa.

---

## 2. Sistema 1 — Judas Swing

### 2.1. Contexto necesario

- **Acumulación en premarket:** el precio no hace nada antes de Nueva York; espera la volatilidad del open [02:09–02:39].
- **DOL claro:** relative equal highs, gap diario sin rellenar, gap de 1H, etc. [02:39–03:09].
- **Zona de manipulación:** un gap o key level donde el precio pueda reaccionar [03:09–03:39].
- **HTF PD array:** el Judas se busca dentro de una zona de 15m o más (ver documento 04).
- **Dirección alineada con el DOL.**

### 2.2. Secuencia

1. Acumulación premarket.
2. Market open: velón de manipulación hacia la zona opuesta al DOL.
3. Distribución en la dirección del DOL.
4. Entrada con el **primer IFVG** alineado.

> "El Judas Swing simplemente se trata de esperar esta acumulación, una manipulación hacia arriba y tú lo que vas a hacer es pillar la distribución. Vas a pillar el primer inverse fair value gap que veas." — `vz4rhIi5Joo` [03:39–04:11]

### 2.2.1. La manipulation leg

> "Siempre tenemos que mirar el último alto que se ha creado antes de que el precio llegue a la zona." — `1C4dgloDQrY` [16:51]

- Es el tramo entre el **último swing high/low que se forma antes de que el precio llegue a la zona** y el punto donde se produce la manipulación.
- Sirve para dos cosas: saber **qué IFVG buscar** y dónde va el **stop**.
- El IFVG válido es el de la **temporalidad más alta dentro de esa leg**: si hay uno de 5m y otro de 3m, espera el de 5m; el de 3m no le sirve si el de 5m manda [14:40–15:11].
- En el modelo de continuación, la leg se reconstruye con el nuevo high/low que se crea tras el primer rechazo [32:23–32:54].

**Certeza:** EXPLÍCITO. Es la definición más completa encontrada en el corpus; antes solo aparecía el término sin desarrollar.

### 2.3. Qué IFVG usar

- Normalmente el primer IFVG de 3m o 5m.
- Si el DOL está muy claro y el price action también, puede usar el de **1 minuto** sin esperar al de 3 [04:11–05:13].
- Riesgo de saltarse el 3m: que el precio toque el 3m, te saque el stop y luego dé el trade. Él lo acepta porque la mayoría de las veces el precio se va sin ti [05:13].
- **Excepción importante:** después de una caída o subida muy fuerte, **no suele coger el primer IFVG**. Prefiere dejar que ese primero se pierda, que se cree uno nuevo en la dirección contraria y que le confirme el giro. Motivo: el primer IFVG suele ser una trampa; te saca y luego el precio se va sin ti [ `mCMpxc0NaN4` 05:45–06:16].
- **Pattern trades (nombre que le da en junio de 2026):** si el precio venía subiendo **poco a poco, creando low resistance liquidity**, el IFVG con potencia sí es una entrada buena: "va a ser un ascensor". Si venía **con mucha agresividad**, el primer inverse es una trampa y lo que hay que hacer es esperar a que se abran gaps de 5m/15m y buscar la continuación [ `1C4dgloDQrY` 27:47–30:50].
- **Si el invers de 1m tarda en formarse y deja mucha mecha**, no entra: espera un cierre por debajo/encima del CISD. Acepta peor RR a cambio de que la dirección tenga más sentido [ `PzkT4SC47Jo` 27:41]. Es una regla explícita del backtest de marzo; no contradice el "primer IFVG", lo matiza cuando el gatillo es sucio.

### 2.4. Stop

- Al otro lado de la manipulación / del swing que originó el IFVG.
- No es un stop en ticks; es estructural.
- En el ejemplo de `u-fG6bYvK7k` [16:36]: stop debajo del low de la manipulación, target en el gap/liquidez de arriba.
- **Colocación fina:** en la sesión de backtesting de junio dice que prefiere poner el stop en las **mechas**, no en los cuerpos: "yo tengo probado que me va mejor ir a wicks" [ `mCMpxc0NaN4` 29:29]. Reconoce que un stop más ajustado en el cuerpo habría dado TP en ese ejemplo, pero no lo considera una regla fiable. El fotograma de ese momento muestra el ticket: entrada 14.686,25, stop 14.651,50 (34,75 puntos), objetivo 14.740,75 (54,50 puntos) → 1:1,57 (`03_FRAMES/mCMpxc0NaN4/stop_mechas_1769.jpg`).

### 2.5. Target

- **1:1** habitual.
- Gap/liquidez interna opuesta.
- DOL.
- Relative equal highs/lows.
- En `Urrb1b2kBso` [05:13] un ejemplo dio 1:2,26, pero no es la regla.
- **El nivel manda sobre el ratio:** en los tickets visibles de backtesting el objetivo está en el low anterior y el RR resultante es 1:1,63 (`sKSAh5gky1M` 11:02), 1:1,57 (`mCMpxc0NaN4` 29:29) y 1:2,15 en el short del 6 de marzo de 2024 (`PzkT4SC47Jo` 14:00). No lo formula como regla; es OBSERVADO. Ver `07_GESTION_RIESGO.md` §2.1.

### 2.6. Invalidación

- El precio invierte el FVG que sostenía la idea.
- El precio rompe el swing de la manipulación.
- El DOL se cumple antes de la entrada.
- El contexto HTF cambia (se invierte el gap de 1H/4H).
- La entrada sería entre 9:41 y 9:44.

**Certeza:** EXPLÍCITO en su mayoría; el stop exacto es OBSERVADO/INFERIDO.

---

## 3. Sistema 2 — Open de las 10:00 / PO3

### 3.1. Por qué las 10:00

- Es el open de la vela de **4 horas**.
- Es el open de la vela de **1 hora**.
- Entra más volumen.
- Muchas veces hay noticia y el precio espera [ `vz4rhIi5Joo` 09:23–10:24].

### 3.2. Secuencia

1. **Acumulación antes de las 10:00.** El movimiento se ralentiza; puede haber chop.
2. **Liquidity sweep en la apertura.** Para largos: que la vela de las 10:00 manipule hacia abajo (open low) y luego cierre alcista. Para cortos: open high y cierre bajista [10:24–11:24].
3. **Open high/low se mira en 1 minuto, pero solo cuenta si hay sweep.** No basta con el color de la primera vela [11:24–11:55].
4. **Zona de manipulación:** key level, zona de conflicto, gap de 5m, 15m, 30m, 1H o 4H [11:55].
5. **Entrada:** IFVG de 1m (o CISD) tras el sweep.
6. **Target:** gap/liquidez interna de 5m/15m/30m/1H/4H; DOL.

> "Si vosotros queréis buscar largos, tenéis que tener un open low... y si no, un open high para buscar cortos." — `vz4rhIi5Joo` [10:54]

> "Esto no es algo que tenéis que tener rajatabla, porque si no seríamos todos millonarios." — `vz4rhIi5Joo` [10:54]

**Ventana antes de la noticia de las 10:00.** Hay dos formulaciones con fechas distintas:

- En junio: si hay noticia a las 10:00, operar hasta las 9:45 y esperar [ `mCMpxc0NaN4` 02:10–02:40].
- En agosto: entra a las **9:49–9:50** y dice que diez minutos antes de la noticia le parecen suficientes "siempre y cuando tengas el bias claro" [ `PzkT4SC47Jo` 05:40–06:12].

No se borra ninguna. La versión de agosto es la más reciente y añade una excepción: la noticia no impide entrar si el DOL está claro y hay margen para proteger antes del dato. La regla general sigue siendo no operar pegado a la noticia.

### 3.3. Stop

- Al otro lado del sweep de las 10:00.
- Si el sweep barre un low, el stop va debajo de ese low.
- Si el sweep barre un high, el stop va encima.
- En el ejemplo del 22/10, el stop estaba protegido por el high del sweep y el trade tenía "95% de win rate" según él [ `OdljBowQurk` 09:50].

### 3.4. Target

- Gap de 15m abierto a las 10:00 [ `OdljBowQurk` 08:17].
- Internal lows/highs.
- DOL.
- 1:1.

### 3.5. Invalidación

- No hay liquidity sweep → no hay setup.
- El open high/low no se confirma con cierre.
- El precio invierte el gap que sostenía la idea.
- El correlacionado no tiene motivo para distribuir (true manipulation).
- La entrada llega demasiado tarde (ejemplo: 10:54, no entra) [ `oP7enoxXpfI` 32:26].

**Certeza:** EXPLÍCITO.

### 3.6. Modelo de continuación (versión junio 2026)

Es el tercer modelo de `1C4dgloDQrY`. No aparece como sistema separado en la versión de agosto, pero se sigue viendo en su operativa.

1. Ya hay un DOL claro y una dirección.
2. El precio crea estructura y deja un **gap de 5m o 15m**.
3. Se espera a que **tapee ese gap** y dé un **IFVG** en la dirección del DOL.
4. Target: 1:1 a un internal low/high dentro de un FVG, o el gap opuesto.
5. Break-even: internal high/low dentro de un FVG de 5m o más, o zona de conflicto.

> "Las continuaciones que yo voy a pillar siempre van a ser de 5 o de 15 minutos. Nunca voy a pillar una continuación de 3 minutos." — `1C4dgloDQrY` [34:27]

**Regla de tiempo:** no entra en una continuación de 5m si en pocos minutos se abre una vela de 15m que va a crear un gap de 15m. Ejemplo: a las 9:56 no entra aunque tenga el IFVG, porque a las 10:00 se crea el gap [36:01–38:07].

**Certeza:** EXPLÍCITO.

### 3.7. SMT como herramienta de salida

> "No es obligatorio que mis entradas tengan SMTs... Lo que me gusta ver de los SMTs es para cerrar los trades." — `1C4dgloDQrY` [38:07–38:37]

- El SMT no es un requisito de entrada.
- Con NQ y ES en dos pantallas, si el **ES alcanza la zona objetivo** y el NQ todavía no, interpreta que el NQ también la ha tocado por correlación.
- Si en ese momento ya tiene **1:1**, cierra el trade; si no, pone break-even y deja correr [39:07–39:39].

**Certeza:** EXPLÍCITO. Es un uso del SMT distinto del de entrada: sirve para gestionar la salida.

---

## 4. CISD (Change in State of Delivery)

### 4.1. Definición

> "Es cuando el precio cierra por encima del cuerpo de una vela o cierra por debajo del cuerpo de otra." — `_drb5sSmQZE` [00:33]

- **CISD alcista:** cierre por encima del **cuerpo** de una vela alcista anterior.
- **CISD bajista:** cierre por debajo del **cuerpo** de una vela bajista anterior.
- Es casi lo mismo que un **break of structure** [00:33].

### 4.2. Cómo se marca

- Se marca el **cuerpo**, no la mecha [01:36].
- Si hay varios candidatos, se marca **el cuerpo más alto** (para alcista) o el más bajo (para bajista) [01:36–02:08].
- Se espera el **cierre** de la vela [04:11–04:41].

### 4.3. Dos formas de usarlo

**Forma 1 — principiante / segura:**

- IFVG + CISD.
- Peor RR, pero trade más probable.
- Se usa cuando no estás 100% seguro del setup.
- El stop va en el mismo sitio; el CISD solo da mejor entrada [02:38–03:39].

**Forma 2 — avanzada:**

- CISD solo, cuando **no hay IFVG usable** y las condiciones son buenas.
- Condiciones: DOL muy claro, Judas Swing clarísimo, estructura clara [05:13–07:47].
- "Es una excusa para entrar", pero también una confirmación de que la tendencia está girando [08:18].

### 4.4. Qué CISD usar

> "Yo CISD pillo solo de un minuto, y el primero." — `_drb5sSmQZE` [03:39]

- Solo 1 minuto.
- El primero.
- No se raya con 2m/3m.
- El CISD de 15 segundos es demasiado ruidoso; no lo usa [06:14–06:44].

### 4.5. Antes de entrar

> "Muy importante: mirar el high time frame antes de entrar al trade... 15 minutos, 5 minutos, una hora." — `_drb5sSmQZE` [13:30–14:31]

Esto es especialmente importante en Judas con CISD de 30s: si el HTF acompaña, entra; si no, no.

### 4.6. Estatus

> "El concepto de CISD es un concepto peligroso para mucha gente... no es obligatorio usarlo... es una confluencia secundaria." — `_drb5sSmQZE` [02:38–05:13]

No es un requisito del sistema. Es opcional y secundario.

**Certeza:** EXPLÍCITO.

---

## 5. IFVG como entrada

Resumen operativo (desarrollo completo en `02_FVG_IFVG.md`):

- IFVG = FVG invertido con **cierre de cuerpo** completo.
- Entrada tras el cierre, no antes.
- Stop al otro lado del swing/manipulación.
- Target 1:1 o liquidez opuesta.
- En Judas: primer IFVG alineado; puede ser 1m si el DOL es claro.
- En 10:00: IFVG de 1m tras el sweep.
- En CISD: IFVG + CISD es la versión segura.

**Certeza:** EXPLÍCITO.

---

## 6. Reglas de tiempo

| Regla | Fuente | Timestamp |
|---|---|---|
| Operar solo 9:30–10:30 | `vz4rhIi5Joo` | 01:06 |
| Judas normalmente 9:30–9:45 | `vz4rhIi5Joo` | 00:34 |
| No entrar 9:41–9:44 | `oP7enoxXpfI` | 13:00–13:33; 40:24 |
| 9:45 puede manipular | `oP7enoxXpfI` | 13:00–13:33 |
| 10:00 es el open de 4H y 1H | `vz4rhIi5Joo` | 09:23 |
| 10:00 suele dar reversiones | `oP7enoxXpfI` | 10:54 |
| 10:15/10:30 continuaciones | `oP7enoxXpfI` | 12:28 |
| No operar después de 11:00/11:25 | `Urrb1b2kBso` | 13:06–13:39 |
| Si hay duda, esperar cierre de vela de las 10 | `Urrb1b2kBso` | 04:43–05:13 |
| Si hay noticia a las 10:00, operar hasta 9:45 y luego esperar | `mCMpxc0NaN4` | 02:10–02:40 |
| Excepción: 9:49–9:50 con DOL claro y 10 minutos de margen | `PzkT4SC47Jo` | 05:40–06:12 |
| No entrar en continuación de 5m si se abre un gap de 15m en minutos | `1C4dgloDQrY` | 36:01–38:07 |

**Certeza:** EXPLÍCITO.

---

## 7. Checklist para descartar un trade

Antes de entrar, Xavi verifica (explícito o observado):

1. **¿Hay DOL claro?** Si hay DOL en ambos lados o no está claro, no.
2. **¿El precio está en un HTF PD array de 15m+?** Si no, no hay PO3.
3. **¿Hay true manipulation?** ¿NQ y ES tienen motivo para distribuir? Si solo uno, el SMT no vale.
4. **¿Hay liquidity sweep?** Sin sweep, no hay open high/low válido.
5. **¿Hay estructura/LRL?** Sin estructura, no se shortea una subida vertical.
6. **¿Es entre 9:41 y 9:44?** No entrar.
7. **¿Ya se cumplió el objetivo?** Si sí, no forzar.
8. **¿Es un día de baja probabilidad?** Sin gaps en premarket, mejor no operar.
9. **¿El precio ha invertido el gap que sostenía la idea?** Si sí, no hay PO3 en esa dirección.
10. **¿La entrada llega demasiado tarde?** Si el precio lleva mucho acumulando, mejor fuera.
11. **¿Voy contra una low resistance liquidity?** Si sí, no se compra ni se vende contra ella [ `sKSAh5gky1M` 11:02].
12. **¿El día tiene muchas mechas y no abre FVGs?** Es un día de baja probabilidad; mejor no operar [ `3ChwQZ8hRN0` 16:19].
13. **¿Estoy dudando o pensando demasiado?** "Si se piensa, no se entra" [ `3ChwQZ8hRN0` 24:10].
14. **¿Es FOMC?** No operar o reducir el riesgo al mínimo [ `sKSAh5gky1M` 27:40; `3ChwQZ8hRN0` 05:18].

**Certeza:** los puntos 1–4 y 6–14 son EXPLÍCITOS; el 5 y el 10 son EXPLÍCITOS en ejemplos; la lista como checklist es **INFERIDA** de sus explicaciones.

---

## 8. Ejemplos reales

### 8.1. 22/10/2026 — +15.000$ (true manipulation)

- Contexto: Daily/4H/1H bajista; todos los gaps invertidos; "motivos para compras, cero" [ `OdljBowQurk` 01:35–02:06].
- DOL: low dentro de gap de 1H + low del rango de 4H [02:06].
- Trade rechazado 1: compras tras barrido de low en gap de 5m; iba contra HTF y contra equal lows [02:37–03:38].
- Trade rechazado 2: inverse de 15s a las 9:59:45; antes del open de las 10:00 y sin true manipulation [03:38–04:40].
- Trade rechazado 3: short de 15s tras el stop hunt, pero el SP500 aún no tenía motivo [06:44–07:15].
- Trade válido: SP500 toca su gap de 4H → true manipulation → CISD de 30s → TP [07:15–07:45].
- Break-even: gap de 5m alineado con el open de las 10:00 [08:17].

### 8.2. 25/09/2026 — masterclass (error y reentrada)

- Empieza buscando compras; cambia a ventas tras triple relative equal low [ `Imr4TPKUD-c` 03:41–04:51].
- Entra a las 9:43; lo llama error evitable: "nunca entro a 44" [18:56–19:26, 36:39].
- Le saltan el stop; vuelve a entrar tras la manipulación de las 9:45; TP [21:14–36:08].
- Regla: no cerrar el trade antes ni después del resultado [20:05–20:36].
- Low risk permite reentrada [21:14].

### 8.3. 10/07/2026 — daily bias simplificado

- 4H alcista; DOL = high dentro de gap de 4H [ `F3anMVV-VlI` 01:36–03:08].
- Ignora el Judas de 3m porque el SP500 no estaba en la zona [04:09–05:11].
- Entra con IFVG de 1m tras el cierre; TP [07:46–08:17].
- "No os rayéis tanto con el bias" [08:17].

### 8.4. 14/05/2026 — London Session (+1.038 $)

- Contexto: 4H/1H alcista; muchos highs juntos (LRL); bajada lenta con buena estructura; resweep del intermediate low de 1H; FVG de 4H tapeado; ATH [ `8gs6HOHXMsc` 02:10–03:14].
- SMT: en 4H el NQ tapa el FVG y el ES no; el ES rechaza un FVG de 15m [04:15–05:47].
- Entrada: FVG de 5m tapeado + inverse FVG de 5m; long con 1 NQ (10 MNQ); riesgo 500 $; BE instantáneo [03:14–04:15].
- TP: high dentro de un FVG de 15m; RR 1,29; +1.038 $ en dos cuentas FA Future [00:35–01:06, 05:47–06:17].
- "La sesión de Londres es menos volátil, se mueve más lenta... el precio busca liquidez, se mueve a través de imbalances" [06:17].
- Frames: 729 (setup 5m), 730 (4H), 731 (posición/RR), 732 (SMT 4H).
- Límite: no hay secuencia horaria de Londres; es una operación documentada, no una regla completa.

**Certeza:** OBSERVADO en los recaps; las reglas que extrae él son EXPLÍCITAS.

---

## 9. Evidencia

| Afirmación | Video | Timestamp | Tipo |
|---|---|---|---|
| Dos sistemas de entrada | `vz4rhIi5Joo` | 00:02–01:06 | EXPLÍCITO |
| Horario 9:30–10:30 | `vz4rhIi5Joo` | 01:06 | EXPLÍCITO |
| Judas: acumulación, manipulación, distribución | `vz4rhIi5Joo` | 02:09–04:11 | EXPLÍCITO |
| Primer IFVG; puede ser 1m si DOL claro | `vz4rhIi5Joo` | 04:11–05:13 | EXPLÍCITO |
| Open 10 = 4H y 1H | `vz4rhIi5Joo` | 09:23 | EXPLÍCITO |
| Open low para longs / open high para shorts | `vz4rhIi5Joo` | 10:54–11:24 | EXPLÍCITO |
| Requiere liquidity sweep | `vz4rhIi5Joo` | 11:24–11:55 | EXPLÍCITO |
| CISD = cierre sobre cuerpo | `_drb5sSmQZE` | 00:33 | EXPLÍCITO |
| Marcar cuerpo, no mecha | `_drb5sSmQZE` | 01:36–02:08 | EXPLÍCITO |
| Esperar cierre | `_drb5sSmQZE` | 04:11–04:41 | EXPLÍCITO |
| IFVG + CISD = forma segura | `_drb5sSmQZE` | 02:38–03:39 | EXPLÍCITO |
| CISD solo = forma avanzada | `_drb5sSmQZE` | 05:13–07:47 | EXPLÍCITO |
| CISD solo 1m, el primero | `_drb5sSmQZE` | 03:39 | EXPLÍCITO |
| Mirar HTF antes de entrar | `_drb5sSmQZE` | 13:30–14:31 | EXPLÍCITO |
| No entrar 9:41–9:44 | `oP7enoxXpfI` | 13:00–13:33; 40:24 | EXPLÍCITO |
| True manipulation | `OdljBowQurk` | 04:40–06:13 | EXPLÍCITO |
| Error 9:43 en masterclass | `Imr4TPKUD-c` | 18:56–19:26; 36:39 | EXPLÍCITO |
| No cerrar antes/después del resultado | `Imr4TPKUD-c` | 20:05–20:36 | EXPLÍCITO |
| No operar contra low resistance liquidity | `sKSAh5gky1M` | 11:02 | EXPLÍCITO |
| Stop en mechas, no en cuerpos | `mCMpxc0NaN4` | 29:29 | EXPLÍCITO |
| No coger el primer IFVG tras caída fuerte | `mCMpxc0NaN4` | 05:45–06:16 | EXPLÍCITO |
| Días de mucha mecha = baja probabilidad | `3ChwQZ8hRN0` | 16:19 | EXPLÍCITO |
| "Si se piensa, no se entra" | `3ChwQZ8hRN0` | 24:10 | EXPLÍCITO |
| No operar FOMC | `sKSAh5gky1M` | 27:40 | EXPLÍCITO |
| Noticia a las 10: operar hasta 9:45 | `mCMpxc0NaN4` | 02:10–02:40 | EXPLÍCITO |

---

## 10. Preguntas abiertas

- **Stop exacto** por setup: no hay una regla numérica; es estructural y, en la versión de junio, se coloca en **mechas**, no en cuerpos [ `mCMpxc0NaN4` 29:29]. Queda por confirmar si cambia según el setup.
- **"Primer IFVG"**: en el Judas es el primero alineado con el DOL, pero después de un desplazamiento fuerte prefiere **no** coger el primero y esperar un segundo IFVG que confirme [ `mCMpxc0NaN4` 05:45–06:16]. No es una contradicción: es una condición de contexto.
- **IFVG de 30s**: lo menciona, pero no lo usa como base.
- **CISD de 30s**: lo usa en el recap del 22/10 y en la sesión de backtesting de junio [ `mCMpxc0NaN4` 07:20, 22:45], pero en el vídeo de CISD dice que solo usa 1m. Es una evolución/uso discrecional; conservar ambas versiones.
- **"RDRs cortos"**: sin definir.
- **Reentrada tras stop**: en septiembre reentra si el riesgo es bajo y el DOL sigue claro [ `Imr4TPKUD-c` 21:14]; en junio dice "normalmente no hago re-entries" [ `mCMpxc0NaN4` 16:29]. Tensión no reconciliada; depende del contexto.
- **Máximo de trades al día**: normalmente uno; con low risk puede reentrar. No hay un número fijo.

---

## 11. Cómo enseñarlo (cuando toque)

1. Primero, contexto: DOL, HTF PD array, liquidez.
2. Después, los dos sistemas de entrada y su horario.
3. Judas: acumulación → manipulación → distribución.
4. Open de las 10:00: sweep → open high/low → IFVG/CISD.
5. IFVG: qué es y cómo se invierte.
6. CISD: qué es, cómo se marca, las dos formas de usarlo.
7. Stops y targets.
8. Checklist de descarte.
9. Ejemplos reales.

No enseñar IFVG/CISD como "estrategias" separadas del contexto. Son herramientas de ejecución dentro de un PO3.
