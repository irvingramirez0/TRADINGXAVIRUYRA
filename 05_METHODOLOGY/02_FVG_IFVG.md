# 02 — FVG E IFVG (FAIR VALUE GAP / INVERSE FAIR VALUE GAP)

**Estado:** vigente. El vídeo de referencia es de 2025-12-24; la actualización estratégica es de 2026-08-01; la sistematización docente es del Bootcamp Día 8 (2026-11-02), del Bootcamp Día 13 (2026-11-07), que convierte el IFVG en condición obligatoria de entrada y fija su ventana temporal, y del Bootcamp Día 15 (2026-11-09), que separa el FVG-key level del FVG-entrada.
**Última actualización:** 2026-11-07
**Fuente principal:** `u-fG6bYvK7k` (2025-12-24), `vz4rhIi5Joo` (2026-08-01), `1McPSXSSR48` (2026-11-02, Bootcamp Día 8), `ICOx4rdFSLg` (2026-11-07, Bootcamp Día 13).
**Fuentes de contraste:** `zcT31zmE5Uc` (2026-07-27), `Urrb1b2kBso` (2025-12-22), `_drb5sSmQZE` (2026-08-16), `oP7enoxXpfI` (2026-10-05).

---

## 1. Qué es un FVG

> "Es una secuencia de tres velas... las mechas de la primera vela y de la tercera no se van a tocar. Y el espacio que haya en blanco entre las dos va a ser vuestro fair value gap." — `u-fG6bYvK7k` [00:32–02:04]

Reglas de identificación:

1. **Tres velas consecutivas.** No tienen que ser del mismo color; pueden ser cualquier combinación [00:32–01:02].
2. Se mira siempre **la vela del medio** como referencia.
3. La **mecha de la vela 1** y la **mecha de la vela 3** no pueden tocarse.
4. El espacio entre ambas mechas es el FVG.
5. **El tamaño no importa.** Un FVG pequeño tiene exactamente la misma validez y función que uno grande [02:04–02:34].
6. Si no hay espacio entre las mechas, **no hay FVG** [02:34].

**Certeza:** EXPLÍCITO.

### 1.1. Confirmación en el Bootcamp (Día 8, 2026-11-02)

El Día 8 dedica la clase completa al FVG y repite la definición sin cambios: tres velas, el color y el orden no importan, el espacio entre la mecha de la primera y la de la tercera es el gap, y el tamaño no altera su validez [ `1McPSXSSR48` 00:31–02:45].

Añade dos matices docentes:

- El FVG **actúa como imán**: el precio tiende a volver a visitarlo [00:31–01:38].
- **No es una certeza**: "no es obligatorio, no 200% de porcentaje de acierto"; con una dirección bien leída funciona la mayoría de las veces, no siempre [05:58–06:30].

No introduce una definición nueva ni corrige la de diciembre de 2025. Es la misma regla explicada desde cero para el bootcamp.

**Certeza:** EXPLÍCITO.

---

## 2. FVG alcista y bajista

- **FVG alcista (bullish):** se forma en una subida; el precio visita la zona, la respeta y continúa hacia el **BSL** (buy-side liquidity).
- **FVG bajista (bearish):** se forma en una bajada; el precio lo visita, lo respeta y continúa hacia el **SSL** (sell-side liquidity).

> "Cuando tenemos un fair value bajista, ¿qué esperamos que haga el precio? Que vaya a visitarlo, lo respete y que tradee el precio hacia este sell-side liquidity." — `u-fG6bYvK7k` [03:04]

El FVG actúa como **imán**: la mayoría de las veces el precio lo revisita. No siempre; a veces el precio simplemente no tradea hacia él [00:32–01:02].

**Certeza:** EXPLÍCITO.

---

## 3. Respeto vs inversión

### 3.1. Respeto

El precio visita el FVG, reacciona y no lo atraviesa con el cuerpo. Puede dejar una mecha dentro, pero el cuerpo no cierra al otro lado.

> "Si la vela baja hasta aquí y luego rechaza... y deja una mecha así, lo está respetando porque el cuerpo no ha cerrado por debajo del cuadradito." — `u-fG6bYvK7k` [06:44]

En el Día 8 lo formula igual y añade que **el tamaño de la mecha es indiferente**: "el cuerpo nunca cierre por debajo"; si el cuerpo cierra dentro del FVG, aunque la mecha salga mucho, se considera respeto [ `1McPSXSSR48` 10:21–12:45]. Lo que invalida es el cierre del cuerpo al otro lado, no la mecha.

### 3.2. Inversión (IFVG)

> "Es básicamente cuando una vela, en vez de visitarlo para seguir subiendo, literalmente lo destruye, lo inversa." — `u-fG6bYvK7k` [06:11]

Condición exacta:

- La vela debe **cerrar**.
- El **cuerpo** debe invertir el FVG **por completo**.
- Una mecha que atraviesa el FVG y vuelve a cerrar dentro **no es inversión**; es respeto [06:44–07:16].

> "Es muy importante que os esperéis a que se inverse y se cierre el cuerpo por debajo del fair value marcado." — `u-fG6bYvK7k` [07:16]

### 3.3. Qué implica una inversión

Cuando un FVG se invierte, el precio empieza a respetar los FVG de la dirección contraria [08:20–09:51].

Ejemplo textual:
- Se invalida un FVG bajista → el precio empieza a respetar FVG alcistas.
- Se invalida un FVG alcista → el precio empieza a respetar FVG bajistas.

Esto es la base del **cambio de bias** y del **IFVG como entrada**.

**Certeza:** EXPLÍCITO.

---

## 4. Jerarquía de temporalidades

### 4.1. High time frame (1H y 4H)

Sirven para:

- Identificar el **DOL**.
- Saber si el precio está respetando un price action alcista o bajista.
- Definir la dirección del día.

> "Los fair values, si tú los miras en una hora o 4 horas, sirven para identificar tu draw on liquidity y, sobre todo, para saber si durante el día el precio va a respetar un price action bullish o bearish." — `u-fG6bYvK7k` [11:27]

### 4.2. Low time frame (5m, 15m, 30m, 1m)

Sirven para:

- **Entradas** (IFVG de 30s, 1m, 3m y 5m; el Día 13 excluye el 15m como entrada, ver §6.8).
- **Targets de liquidez interna**: gaps de 5/15/30 minutos, highs/lows internos.
- Detectar reacciones que no se ven en 1H/4H.

> "En los timeframes más bajos os centréis en tarjetear internal liquidity, porque en esta internal liquidity podemos tener fair values de 15 minutos y que no haya ninguno de una hora." — `u-fG6bYvK7k` [13:31]

### 4.3. Alineación

> "Tenéis que intentar tener todos los timeframes alineados. Cuando más alineados estén, mejor. Si podéis tener 5 minutos bullish, 15 minutos bullish, una hora bullish, 4 horas bullish, es perfecto." — `u-fG6bYvK7k` [17:06]

**Certeza:** EXPLÍCITO.

### 4.4. La validación se hace en la temporalidad del FVG

Regla añadida en el Bootcamp Día 8 [ `1McPSXSSR48` 14:20–15:26]:

**Paráfrasis de la regla (no es cita literal):** si el FVG se marca en 5 minutos, su respeto o invalidación se juzga en 5 minutos; una vela de 1 minuto que cierre al otro lado no invalida el FVG de 5 minutos si la vela de 5 minutos sigue aguantando.

En el ejemplo de la clase, el precio cierra por debajo del gap en 1 minuto, pero en 5 minutos el cuerpo todavía no ha cerrado al otro lado; Xavi lo lee como FVG intacto y pide mirar siempre la temporalidad en la que se marcó el gap.

Esto no contradice la alineación de §4.3: la alineación sirve para elegir contexto y dirección; la validación de un FVG concreto se hace en su propia temporalidad. Una temporalidad menor puede dar señales de ruido sin invalidar la zona.

**Alcance:** el ejemplo explícito es 5m. Que la misma lógica se aplique a 15m, 1H o 4H es **INFERIDO**, no formulado por él en esta clase. Queda como pregunta abierta (§10).

**Certeza:** EXPLÍCITO para 5m; INFERIDO para el resto.

---

## 5. NWOG como FVG

> "Se crea un new week opening gap, que es como un fair value, actúa como un fair value gap. ¿Qué hace? Se respeta y sube." — `u-fG6bYvK7k` [10:24]

El NWOG se trata como una zona más de imbalance/liquidez. No es un FVG de tres velas, pero funcionalmente se usa igual: como imán y como zona de reacción.

**Certeza:** EXPLÍCITO.

---

## 6. IFVG como sistema de entrada (actualización 2026)

Fuente: `vz4rhIi5Joo` (2026-08-01).

### 6.1. Dos sistemas de entrada

> "Yo tengo dos sistemas de entrada... Judas Swing... y luego tengo otro sistema de entrada que es básicamente el open de las 10, el Power of 3 de las 10, que es lo mismo, o el open de la vela de 4 horas." — `vz4rhIi5Joo` [00:02–01:06]

1. **Judas Swing:** normalmente 9:30–9:45.
2. **Open de las 10:00 / PO3 de las 10:00 / open de 4 horas:** todo el mismo concepto.

### 6.2. Horario vigente

> "Yo antes siempre operaba de 9:30 a 11, pero ahora... solo opero de 9:30 a 10:30, es decir, solo estoy en el mercado 1 hora." — `vz4rhIi5Joo` [01:06]

**Esto corrige la versión anterior de 9:30–11:00.** La versión vigente es 9:30–10:30. Se conserva la anterior como historia.

### 6.3. PO3 = AMD + tiempo

> "El Power of 3, el PO3, significa básicamente AMD, es exactamente lo mismo... Buscamos una acumulación, una manipulación y una distribución. ¿Qué es lo importante? Que hay que tener en cuenta los timings y sobre todo la hora." — `vz4rhIi5Joo` [01:36]

No es un patrón de velas aislado: es un ciclo con **hora**. El mismo AMD se repite en cada apertura de 15 minutos [05:45–06:15].

### 6.4. Judas Swing

Secuencia:

1. **Acumulación en premarket.** El precio no hace nada antes de Nueva York; está esperando la volatilidad del open [02:09–02:39].
2. **Manipulación en el market open.** Velón hacia arriba o hacia abajo, hacia una zona donde el precio puede reaccionar: gap de 1H, relative equal highs, gap diario, etc. [03:09–03:39].
3. **Distribución.** Entrada con el **primer IFVG** que aparezca tras la manipulación [04:11].

Condición de contexto: el Judas debe alinearse con el **DOL**. Si el DOL está muy claro y el price action también, puede entrar con IFVG de **1 minuto** sin esperar al de 3 minutos [04:11–05:13]. Si espera al de 3, a veces el precio se va sin él.

**Certeza:** EXPLÍCITO.

### 6.5. Open de las 10:00

Por qué importa:

- Es el open de la vela de **4 horas**.
- Es el open de la vela de **1 hora**.
- Es un open con más volumen.
- Muchas veces hay noticia y el precio espera [09:23–10:24].

Secuencia:

1. **Acumulación antes de las 10:00.** El movimiento se ralentiza; puede haber chop.
2. **Liquidity sweep en la apertura.** Para buscar largos, quiere que la vela de las 10:00 **manipule hacia abajo** (open low) y luego cierre alcista. Para cortos, al revés: open high y cierre bajista [10:24–11:24].
3. **Open high/low se mira en 1 minuto, pero solo cuenta si hay liquidity sweep.** No basta con que la primera vela de 1m sea roja o verde; tiene que barrer un high/low [11:24–11:55].
4. **Zona de la manipulación:** idealmente un key level, una zona de conflicto o un gap de **5 minutos o más** (5m, 15m, 30m, 1H, 4H) [11:55].
5. **Entrada:** IFVG de 1 minuto (o CISD) tras el sweep.
6. **Target:** gap/liquidez interna de 5m/15m/30m/1H/4H; DOL.

> "Si vosotros queréis buscar largos, tenéis que tener un open low... y si no, un open high para buscar cortos." — `vz4rhIi5Joo` [10:54]

> "Las velas de las 10... esto no es algo que tenéis que tener rajatabla, porque si no seríamos todos millonarios." — `vz4rhIi5Joo` [10:54]

**Certeza:** EXPLÍCITO, con la advertencia de que no es mecánico.

### 6.6. Stacking de PO3

Si el PO3 de las 9:30 no distribuye, se espera al de las 9:45. Si tampoco, al de las 10:00, y así sucesivamente [06:15–07:18].

> "Cada vez que abre una vela de 15 minutos y manipula aún más sin afectar al primer nivel... cuanto más tiempo pasa y cuanto más manipulamos hacia arriba, siempre y cuando esté alineado con nuestro draw on liquidity y sobre todo siempre y cuando haya buena estructura, el precio va a estar en descuento." — `vz4rhIi5Joo` [07:18–07:48]

Esto es el **descuento por tiempo**: cada nuevo high sin romper el primer nivel deja el precio más caro para cortos, pero solo es válido si hay estructura (LRL, equal lows, subida lenta). Si son velones verticales, **no** se buscan shorts [08:20–08:52].

> "Si ves que empezamos a subir lento, creando low resistance liquidity, se crean equal lows... todas estas confluencias... para luego pillar tus shorts." — `vz4rhIi5Joo` [08:20–08:52]

**Certeza:** EXPLÍCITO.

### 6.7. Día de baja probabilidad

Ejemplo del propio vídeo [15:01–16:04]:

- Solo hay un gap en premarket; no hay gaps de 5 minutos.
- El price action es malo.
- No hay IFVG de 30 segundos ni de 1 minuto usable.
- Aun así, aparece un IFVG de 3 minutos y da TP, pero él lo considera un día feo.
- "High swings no vais a poder pillarlos si no hay estructura; si no tenéis gaps en el premarket, no vais a poder pillar nada."

**Certeza:** EXPLÍCITO.

### 6.8. El IFVG como condición obligatoria de entrada (Bootcamp Día 13, 2026-11-07)

El Día 13 no añade un concepto nuevo: convierte el IFVG en **requisito absoluto** y acota su uso operativo. Es la clase que cierra el anuncio del Día 11, pero **excluye deliberadamente el CISD** (ver §6.8.6).

#### 6.8.1. Sin IFVG no hay entrada

> "Los inverse fair value gaps son nuestro sistema de entrada... yo nunca, nunca, nunca voy a darle al botón de comprar o vender sin un inverse fair value gap. Es nuestra confirmación." — `ICOx4rdFSLg` [03:21–03:52]

- El IFVG no es una confluencia más: es la **confirmación obligatoria**.
- Lo que confirma es que **el precio quiere cambiar de tendencia** [03:21–03:52].
- Mecánica que repite: el precio va de un punto de liquidez a otro a través de imbalances, y esos imbalances son los FVGs [03:52–04:23]. Cuando un FVG deja de aguantar y el precio lo atraviesa con cierre, hay más fuerza en la dirección contraria y empieza la tendencia opuesta [05:29–06:00].

**Certeza:** EXPLÍCITO.

#### 6.8.2. Solo IFVG de 30 segundos a 5 minutos

> "Solo vamos a estar tomando inverse fair value gaps de entre 30 segundos a 5 minutos... Nunca vamos a estar pillando un inverse fair value de 15 minutos." — `ICOx4rdFSLg` [10:45–11:15]

Esto **precisa** la horquilla que ya se usaba en la práctica (1m, 3m, 5m) y añade dos límites:

- **Suelo:** 30 segundos, ya documentado como gatillo en recaps y backtesting.
- **Techo:** 5 minutos. Un IFVG de 15m **no se usa como entrada**, aunque en la clase se muestre un ejemplo de 15m para explicar el concepto [10:45–11:15].

Motivo que da: sus trades duran poco. "Yo nunca estoy en un trade más de media hora, más de 20 minutos, es raro. Normalmente estoy en el trade entre 1 minuto y 10 minutos" [11:47]. Es coherente con que la ejecución sea en temporalidad baja.

**Certeza:** EXPLÍCITO para la ventana 30s–5m y para la exclusión del 15m como entrada. El detalle de **cuándo** prefiere 30s frente a 1m/3m/5m no se desarrolla en esta clase.

#### 6.8.3. El IFVG debe invertirse en 3–4 velas como máximo

> "Un inverse fair value no puede tardar más de tres velas, tres, cuatro velas en darse... Cuando digo darse me refiero a invertirse." — `ICOx4rdFSLg` [17:41–18:44]

- La cuenta se hace en la **temporalidad en la que está marcado el FVG**.
- Si tarda más de 3–4 velas en cerrar al otro lado, "no nos acaba gustando" [18:13–18:44].
- Lo que busca es una **vela fuerte** que invierta el gap, no una agonía de cierres pequeños.
- En el ejemplo que muestra, el precio acaba cerrando por debajo del FVG, pero tarda demasiado; lo descarta como entrada válida [18:13–18:44].

**Certeza:** EXPLÍCITO en la regla. Queda **NO CONFIRMADO** si las 3–4 velas se cuentan desde la creación del FVG o desde el primer toque, y si el límite es exactamente 3 o 4. Registrado como pregunta abierta (§10).

#### 6.8.4. La inversión se valida en la temporalidad del FVG (reiteración)

El Día 13 repite con más fuerza la regla del Día 8:

> "Si yo me marco un FVG en 5 minutos, necesito que la inversión sea en 5 minutos. No me sirve que sea una vela de 1 minuto, no me sirve que sea una vela de 2 minutos." — `ICOx4rdFSLg` [07:07–08:10]

Añade el criterio de lectura: lo que invierte es el **cierre**, no la mecha. Si la vela perfora el gap y cierra dentro, el FVG se está respetando; si cierra al otro lado, se ha invertido [07:39–08:10]. Es la misma regla de §3.2 y §4.4, sin cambios.

**Certeza:** EXPLÍCITO para 5m; el alcance a 15m/1H/4H sigue siendo INFERIDO.

#### 6.8.5. Ejemplo: equal lows, sweep y IFVG de 5m

Ejemplo desarrollado en [12:18–16:39]:

1. Hay **equal lows** que funcionan como sell-side liquidity; el precio los barre y deja un nuevo SSL [12:50–13:22].
2. Durante la caída previa se han creado varios FVG bajistas de 5m que el precio respeta bajando [13:53–14:25].
3. El último FVG bajista de 5m **no se respeta**: el precio cierra por encima [14:25–14:59].
4. A partir de ahí se crean FVG alcistas que el precio respeta y sube a quitar buy-side liquidity [14:59–15:34].
5. Arriba se forman **equal highs** y hay un gap bajista alineado. El precio los barre y después invierte el FVG hacia abajo [15:34–16:08].
6. La entrada sería ese IFVG. La justificación que da: "aquí arriba en nuestro stop loss tenemos solo una liquidez, una sell-side liquidity. ¿Y qué tenemos abajo? Uno, dos, tres, cuatro, cinco, seis" [16:08–16:39].

De ahí sale una regla de colocación de stop que se añade en §7.2: **no se pone el stop donde hay equal highs/lows**, porque es donde el mercado va a recoger liquidez [15:34].

**Certeza:** EXPLÍCITO en la lectura del ejemplo; la asimetría "una liquidez en el stop frente a varias en el target" es su explicación verbal, no una fórmula numérica.

#### 6.8.6. CISD: exclusión explícita del bootcamp

> "No uso CISD casi. Hago una entry con CISD... de cada 100 trades igual lo uso una vez. Entonces no creo que sea algo que tenga que explicar porque os vais a liar." — `ICOx4rdFSLg` [00:34–01:05]

- El Día 11 había anunciado IFVG **y CISD**; el Día 13 explica solo IFVG y **decide no enseñar CISD** [00:34–01:05].
- Justificación: lo usa aproximadamente **1 de cada 100 trades** y considera que añadirlo al bootcamp confunde.
- Remite a un vídeo antiguo del canal (`_drb5sSmQZE`) para quien tenga curiosidad; no forma parte del temario.
- Esto no borra lo documentado en `05_ENTRADAS.md` §4: sigue existiendo como recurso residual, pero **no es el sistema de entrada** ni se enseña en el bootcamp.

**Certeza:** EXPLÍCITO.

#### 6.8.7. Lo que anuncia para después

Para los siguientes episodios: **key levels**, **SMT**, **SMT control manipulation** y **dirección del día**; después la estrategia, backtesting, prop firms y gestión de riesgo [01:05–01:36]. No pone fechas.

**Certeza:** EXPLÍCITO.

### 6.9. El FVG como key level (Bootcamp Día 15, 2026-11-09)

El Día 15 separa dos usos del FVG que hasta entonces estaban mezclados:

- **Como key level (zona de conflicto):** FVG de **15 minutos, 1 hora y 4 horas**. Nunca un FVG de 5 minutos como key level [ `J7Dh-aj9-e0` 02:09].
- **Como condición:** los gaps de 15 minutos se usan "más como condiciones y no tanto como key levels" [02:40].
- **Como entrada:** IFVG de 30 segundos a 5 minutos (Día 13; repetido en el Día 17: "no cogemos inversiones de 15 minutos, cogemos solo inversiones de 1 a 5 minutos" [ `sTS-iWJvTf0` 05:50]).

**Regla de alineación:** un FVG de 1H o 4H solo es un key level fuerte si contiene **altos o bajos dentro**; esos extremos son liquidez que el precio suele ir a buscar [02:40–03:44]. La reacción en el gap puede eximir de esperar el barrido del low interno si es fuerte; si el precio consolida justo encima del low, Xavi prefiere que lo quiten antes de buscar largos [06:49–07:52].

**Certeza:** EXPLÍCITO. No hay contradicción con el Día 13: el 15m sigue prohibido como **entrada**, pero es válido como **key level**.

---

## 7. IFVG: reglas de entrada

### 7.1. Qué IFVG usar

- **Ventana obligatoria:** de **30 segundos a 5 minutos**. Nunca un IFVG de 15m como entrada [ `ICOx4rdFSLg` 10:45–11:15].
- **Judas:** primer IFVG tras la manipulación. Puede ser de 1m, 3m o 5m.
- **Open de las 10:** IFVG de 1 minuto tras el liquidity sweep; a veces 3m/5m.
- **Contexto de DOL muy claro:** puede saltarse el 3m e ir al 1m [04:11–05:13].
- **Sin IFVG usable:** el CISD queda como recurso residual muy poco usado (1 de cada 100 trades) y **no se enseña en el bootcamp** [ `ICOx4rdFSLg` 00:34–01:05].

### 7.2. Dónde va el stop

- Al otro lado de la manipulación / del swing que generó el IFVG.
- En el ejemplo de `u-fG6bYvK7k` [16:36]: "ponías los stops aquí y si tomo liquidity era aquí, pues lo jodeabas hasta aquí".
- **No se coloca el stop donde hay equal highs/lows** [ `ICOx4rdFSLg` 15:34]: es liquidez que el mercado va a recoger antes de continuar.
- No se documenta un stop fijo en ticks; es estructural.

### 7.3. Target

- **1:1** habitual.
- En `Urrb1b2kBso` [05:13] menciona un **1:2,26** en un ejemplo concreto, no como regla general.
- Target: gap/liquidez interna opuesta, DOL, relative equal highs/lows.
- En `u-fG6bYvK7k` [16:36]: "si tomo liquidity era aquí, pues lo jodeabas hasta aquí y hubiese sido un full TP".

### 7.4. Confirmaciones

- IFVG con cierre de cuerpo.
- Alineación de timeframes.
- Liquidity sweep previo.
- DOL claro.
- Estructura (no vertical).
- Contexto de equilibrium/descuento (ver documento 06).

**Certeza:** EXPLÍCITO en su mayoría; el stop exacto es OBSERVADO/INFERIDO.

---

## 8. Errores que él señala

- **Creer que un FVG pequeño no vale.** Vale igual [02:04–02:34].
- **Pensar que las tres velas deben ser del mismo color.** No [00:32–01:02].
- **Invertir un FVG con una mecha.** Tiene que cerrar el cuerpo [06:44–07:16].
- **Entrar antes de que cierre la vela.** Esperar el cierre [07:16].
- **Mirar solo 1H/4H y no ver los FVG de 5m/15m.** El precio reacciona ahí [13:31–14:01].
- **No alinear timeframes.** [17:06].
- **Buscar shorts después de una subida vertical de 400 puntos.** "Es una pirada" [23:06–23:36].
- **Entrar en un día sin gaps en premarket.** No hay estructura para el Judas [15:01–15:31].
- **Pensar que el open de las 10 es mecánico.** No todas las velas de las 10 abren al revés y cierran en la dirección; solo tiene más probabilidad si está alineado con el DOL [19:25–19:56].
- **Invalidar un FVG de 5m porque una vela de 1m cerró al otro lado.** La validación se hace en la temporalidad en la que se marcó el gap [ `1McPSXSSR48` 14:20–15:26].
- **Tratar el FVG como una certeza.** No acierta el 100% de las veces; con buena dirección funciona la mayoría, no siempre [ `1McPSXSSR48` 05:58–06:30].

---

## 9. Evidencia

| Afirmación | Video | Timestamp | Tipo |
|---|---|---|---|
| FVG = 3 velas, mechas 1 y 3 no se tocan | `u-fG6bYvK7k` | 00:32–02:04 | EXPLÍCITO |
| Color irrelevante | `u-fG6bYvK7k` | 00:32–01:02 | EXPLÍCITO |
| Tamaño irrelevante | `u-fG6bYvK7k` | 02:04–02:34 | EXPLÍCITO |
| FVG actúa como imán | `u-fG6bYvK7k` | 00:32–01:02 | EXPLÍCITO |
| Inversión = cierre de cuerpo completo | `u-fG6bYvK7k` | 06:11–07:16 | EXPLÍCITO |
| Mechazo no es inversión | `u-fG6bYvK7k` | 06:44 | EXPLÍCITO |
| Tras inversión se respetan FVG contrarios | `u-fG6bYvK7k` | 08:20–09:51 | EXPLÍCITO |
| HTF para DOL, LTF para entradas | `u-fG6bYvK7k` | 11:27–14:01 | EXPLÍCITO |
| Internal/external liquidity | `u-fG6bYvK7k` | 13:00–13:31 | EXPLÍCITO |
| Alinear timeframes | `u-fG6bYvK7k` | 17:06 | EXPLÍCITO |
| NWOG actúa como FVG | `u-fG6bYvK7k` | 10:24 | EXPLÍCITO |
| Dos sistemas de entrada | `vz4rhIi5Joo` | 00:02–01:06 | EXPLÍCITO |
| Horario 9:30–10:30 | `vz4rhIi5Joo` | 01:06 | EXPLÍCITO |
| PO3 = AMD + tiempo | `vz4rhIi5Joo` | 01:36 | EXPLÍCITO |
| Judas: acumulación, manipulación, distribución | `vz4rhIi5Joo` | 02:09–04:11 | EXPLÍCITO |
| Puede usar IFVG 1m si DOL claro | `vz4rhIi5Joo` | 04:11–05:13 | EXPLÍCITO |
| Open 10 = open 4H y 1H | `vz4rhIi5Joo` | 09:23 | EXPLÍCITO |
| Open low para longs / open high para shorts | `vz4rhIi5Joo` | 10:54–11:24 | EXPLÍCITO |
| Requiere liquidity sweep | `vz4rhIi5Joo` | 11:24–11:55 | EXPLÍCITO |
| Zona: gaps de 5m o más | `vz4rhIi5Joo` | 11:55 | EXPLÍCITO |
| Stacking de PO3 | `vz4rhIi5Joo` | 06:15–07:18 | EXPLÍCITO |
| Descuento por tiempo solo con estructura | `vz4rhIi5Joo` | 07:18–08:52 | EXPLÍCITO |
| Día de baja probabilidad sin gaps | `vz4rhIi5Joo` | 15:01–16:04 | EXPLÍCITO |
| No shortear subida vertical | `vz4rhIi5Joo` | 23:06–23:36 | EXPLÍCITO |
| Definición de FVG confirmada en bootcamp | `1McPSXSSR48` | 00:31–02:45 | EXPLÍCITO |
| El FVG actúa como imán | `1McPSXSSR48` | 00:31–01:38 | EXPLÍCITO |
| El FVG no es una certeza (no 100%) | `1McPSXSSR48` | 05:58–06:30 | EXPLÍCITO |
| Mecha grande no invalida si el cuerpo cierra dentro | `1McPSXSSR48` | 10:21–12:45 | EXPLÍCITO |
| Validar el FVG en su temporalidad (ejemplo 5m) | `1McPSXSSR48` | 14:20–15:26 | EXPLÍCITO |
| IFVG = FVG que se ha invertido | `1McPSXSSR48` | 16:34–17:09 | EXPLÍCITO |
| IFVG obligatorio: sin IFVG no se opera | `ICOx4rdFSLg` | 03:21–03:52 | EXPLÍCITO |
| El precio va de liquidez a liquidez a través de FVGs | `ICOx4rdFSLg` | 03:52–04:23 | EXPLÍCITO |
| Al atravesar un FVG cambia la fuerza y la tendencia | `ICOx4rdFSLg` | 04:56–06:00 | EXPLÍCITO |
| Validar la inversión en la temporalidad del FVG | `ICOx4rdFSLg` | 07:07–08:10 | EXPLÍCITO |
| IFVG solo de 30s a 5m; nunca 15m como entrada | `ICOx4rdFSLg` | 10:45–11:15 | EXPLÍCITO |
| Duración habitual del trade: 1–10 min; máximo 20–30 | `ICOx4rdFSLg` | 11:47 | EXPLÍCITO |
| Ejemplo: equal lows → sweep → IFVG de 5m | `ICOx4rdFSLg` | 12:18–16:39 | EXPLÍCITO |
| No poner el stop en equal highs/lows | `ICOx4rdFSLg` | 15:34 | EXPLÍCITO |
| El IFVG debe invertirse en 3–4 velas como máximo | `ICOx4rdFSLg` | 17:41–18:44 | EXPLÍCITO |
| CISD: 1 de cada 100 trades; no se enseña en el bootcamp | `ICOx4rdFSLg` | 00:34–01:05 | EXPLÍCITO |
| Próximo temario: key levels, SMT, SMT control manipulation y dirección del día | `ICOx4rdFSLg` | 01:05–01:36 | EXPLÍCITO |

---

## 10. Preguntas abiertas

- **Stop exacto** en cada variante (Judas 1m vs 3m vs 10:00): no hay una regla numérica; es estructural. Pendiente de ejemplos visuales.
- **IFVG de 30 segundos:** el Día 13 confirma que la ventana de entrada es 30s–5m [ `ICOx4rdFSLg` 10:45–11:15], pero no detalla cuándo prefiere 30s frente a 1m/3m/5m. Sigue sin criterio de selección explícito.
- **Regla de las 3–4 velas:** el Día 13 la formula [17:41–18:44], pero no aclara si se cuentan desde la creación del FVG o desde el primer toque, ni si el límite exacto es 3 o 4. **NO CONFIRMADO** en esos dos detalles.
- **"Primer IFVG"**: ¿el primero en la dirección de la distribución, o el primero que se forma tras el sweep? En los ejemplos parece el primero alineado con el DOL. Pendiente de precisar.
- **Relación IFVG + CISD:** el Día 13 excluye el CISD del bootcamp porque lo usa "1 de cada 100 trades" [ `ICOx4rdFSLg` 00:34–01:05]. Queda documentado como recurso residual, no como parte del sistema de entrada. La relación operativa con el IFVG ya no es prioritaria.
- **FVG de 4H como entrada**: normalmente usa 30s–5m para ejecutar; el 4H es contexto. El Día 13 cierra la puerta al IFVG de 15m como entrada; confirmar si alguna vez entra con IFVG de 1H/4H. **INFERIDO que no.**
- **Alcance de la validación por temporalidad:** el Día 8 lo ejemplifica con 5m frente a 1m y el Día 13 lo repite con las mismas palabras [ `ICOx4rdFSLg` 07:07–08:10]. No confirma si un cierre de 5m invalida un FVG de 15m, ni si un cierre de 1H invalida un FVG de 4H. La generalización sigue siendo INFERIDA.

---

## 11. Cómo enseñarlo (cuando toque)

Orden del vídeo de FVG:

1. Qué es un FVG (3 velas, mechas, espacio).
2. Color y tamaño no importan.
3. FVG alcista/bajista y su función (imán hacia BSL/SSL).
4. Respeto vs inversión (cierre de cuerpo).
5. Qué implica la inversión (se respetan los FVG contrarios).
6. HTF para DOL; LTF para entradas y liquidez interna.
7. Alineación de timeframes.
8. Ejemplos.

Después, el vídeo de estrategia 2026:
1. Dos sistemas de entrada.
2. Horario.
3. PO3 = AMD + tiempo.
4. Judas Swing.
5. Open de las 10.
6. Stacking.
7. Contexto y estructura.

No empezar por "IFVG" sin haber explicado antes qué es un FVG y qué significa inversión.

**Secuencia del Bootcamp Día 8:** definición (tres velas, mechas, tamaño) → FVG como imán → respeto (cierre de cuerpo, mecha indiferente) → invalidación en la temporalidad del FVG → mención del IFVG como FVG invertido. Cierra anunciando "liquidez parte dos" [ `1McPSXSSR48` 20:18–20:43].
