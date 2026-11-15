# 01 — LIQUIDEZ, BSL/SSL Y DOL

**Estado:** vigente. Liquidez pt1 y pt2 cubiertas.
**Última actualización:** 2026-11-05
**Fuente principal:** Bootcamp Día 6 `7HOAf7vHMqU` (2026-10-31) y Día 11 `OtYATAfCfRA` (2026-11-05).
**Fuentes de contraste:** `Urrb1b2kBso` (2025-12-22), `zcT31zmE5Uc` (2026-07-27), `u-fG6bYvK7k` (2025-12-24), `OdljBowQurk` (2026-10-22), `oP7enoxXpfI` (2026-10-05).

---

## 1. Definición

> "¿Qué es la liquidez? La liquidez es dinero." — `7HOAf7vHMqU` [01:08]

Xavi no presenta la liquidez como un concepto abstracto ni como una teoría del algoritmo. Dice explícitamente que no necesita saber qué hay detrás del mercado: si le funciona, lo aplica [00:03–00:36]. Reconoce que otra gente lo explica de forma distinta, incluido ICT, y que su explicación es "a mi manera" [00:36–01:08]. Da crédito a **TV Trading** como fuente de su explicación de liquidez [04:14].

**Implicación para la enseñanza:** no se debe completar esta definición con teoría ICT genérica. La definición operativa es: liquidez = dinero; los altos y bajos son zonas donde hay órdenes y stops; el precio va a buscarlas.

---

## 2. Todo alto y bajo tiene liquidez, pero no toda pesa igual

> "En cada alto y bajo tenemos liquidez, pero no toda esta liquidez tiene la misma importancia." — `7HOAf7vHMqU` [01:08]

La jerarquía es por temporalidad:

- La liquidez de **15 minutos, 1 hora y 4 horas** es más importante que la de 1 minuto o 5 minutos.
- Razón que da: una vela de 1 hora contiene muchas velas de 5 minutos y 60 velas de 1 minuto; por tanto, un alto de 1 hora contiene más órdenes que un alto de 1 minuto [01:08–02:11].
- "Las temporalidades altas mandan" [02:11].
- Matiz posterior: "sí que es más importante, pero no siempre" [20:22]. Es una prioridad, no una garantía.

**Certeza:** EXPLÍCITO.

---

## 3. Swing high y swing low

> "¿Qué es? Básicamente son altos y bajos de un rango que son prominentes... que resaltan, que despuntan, que están en los dos extremos del gráfico." — `7HOAf7vHMqU` [02:11–02:42]

Son los extremos que delimitan un rango, no cualquier mínimo o máximo interno.

### 3.1. Detalle importante: el color de las velas

En el Día 4, un alto se define como vela alcista seguida de vela bajista, y un bajo como vela bajista seguida de vela alcista. Para **liquidez**, Xavi dice que el color no tiene por qué cumplirse: puede haber dos velas del mismo color y aun así el extremo sirve [06:21–06:52].

Además, si en la temporalidad que está mirando no se forma el bajo según esa definición, **baja de temporalidad para localizar la mecha extrema**:

> "Como sabemos que dependiendo de la temporalidad vamos a tener un alto o un bajo, yo siempre voy a buscar el bajo de la temporalidad más baja." — `7HOAf7vHMqU` [07:23]

Ejemplo que da: en 15 minutos no hay un bajo válido, pero en 5 minutos sí; marca la mecha más baja. No es que cambie de temporalidad para operar, sino para **afinar el punto exacto** del swing.

**Certeza:** EXPLÍCITO.
**Nota de precisión:** "temporalidad más baja" aquí significa bajar hasta encontrar el extremo real dentro de la vela, no convertir la liquidez de 1 minuto en la principal. La jerarquía sigue siendo HTF.

---

## 4. BSL y SSL

> "Tenemos buy-side liquidity, que son normalmente los altos, y sell-side liquidity, que son los bajos." — `7HOAf7vHMqU` [07:23–07:55]

- **BSL (buy-side liquidity):** liquidez del lado de las compras; se representa con los **altos**. Es donde están los stops de los cortos y las órdenes de compra de ruptura.
- **SSL (sell-side liquidity):** liquidez del lado de las ventas; se representa con los **bajos**. Es donde están los stops de los largos y las órdenes de venta de ruptura.

Cada nuevo alto o bajo crea una nueva zona de liquidez. Xavi lo describe como "billetes": cada línea marcada es dinero [08:25–09:27].

**Certeza:** EXPLÍCITO.

---

## 5. Por qué el mercado va a buscar los stops

La explicación de Xavi es mecánica y sencilla [03:12–05:48]:

1. Las instituciones necesitan liquidez para llenar sus órdenes.
2. Para que alguien compre, tiene que haber alguien que venda, y viceversa.
3. El retail que entra en corto coloca su stop por encima del alto. Ese stop es una **orden de compra stop**.
4. El mercado sube a buscar esos stops, ejecuta esas compras, y con esa liquidez las instituciones colocan sus ventas.
5. Resultado: barrido del alto, el retail pierde, y el precio se mueve en la dirección institucional.
6. Lo mismo a la inversa: el retail en largo coloca stops debajo del bajo; el mercado baja a buscarlos y usa esa liquidez para comprar.

> "El mercado se mueve buscando liquidez a través de imbalances." — `7HOAf7vHMqU` [15:11]

**Certeza:** EXPLÍCITO en cuanto a cómo lo explica él. La existencia de "instituciones" la presenta como su modelo mental, no como un hecho demostrado: "puede que no sea así, pero yo lo entiendo así" [02:42–03:12].

**No convertir esto en una afirmación sobre el algoritmo del mercado.** Él mismo dice que no lo sabe [00:36–01:08].

---

## 6. La lógica de "más billetes" (heurística, no regla mecánica)

En los ejemplos, Xavi cuenta cuántos altos y cuántos bajos hay pendientes:

- Si hay tres BSL arriba y solo una SSL abajo, el precio tiende a subir a por los tres [08:25–09:27].
- Cuando quita la SSL y deja otra, y sigue acumulando BSL, el precio vuelve a subir [09:27–11:31].
- El movimiento se repite: barre un lado, deja una nueva liquidez, acumula del otro lado, y va a por el lado con más "billetes" [11:31–15:11].

**Pero él mismo advierte:** no siempre ocurre así, y en la parte 2 explicará cuándo sí y cuándo no [12:04, 15:44–16:45].

**Certeza:** EXPLÍCITO como patrón observado en sus ejemplos. **INFERIDO** si se formula como regla cuantitativa ("si hay 3 BSL y 1 SSL, siempre sube"). No es una regla mecánica.

---

## 7. Internal vs external liquidity

Fuente: `u-fG6bYvK7k` [13:00–13:31].

- **Internal liquidity:** highs/lows dentro del rango; gaps de 5, 15, 30 minutos; puntos donde el precio puede girar dentro del rango.
- **External liquidity:** previous highs/lows, relative equal highs/lows, London highs, etc., que están por encima o por debajo del rango.

Uso operativo que declara:
- En temporalidades bajas, **targetear liquidez interna** (gaps de 5/15 minutos, highs/lows internos).
- El **DOL grande** suele ser liquidez externa.
- Si solo miras 1H/4H, no ves por qué el precio reacciona en 5m/15m: son FVG y liquidez interna de esa temporalidad [13:31–14:01].

**Certeza:** EXPLÍCITO.

---

## 8. Niveles de liquidez que usa

El Día 11 cierra la liquidez con una lista cerrada. Él cuenta **seis tipos** y dice que usa **cinco**: el primero (PDH/PDL) es "incluso skipeable" [ `OtYATAfCfRA` 00:32–01:05].

| Tipo | Nombre | Uso declarado |
|---|---|---|
| 1 | PDH / PDL (previous day high/low) | Lo explica, pero "de normal solo uso estos cinco" [01:05] |
| 2 | Equal highs / equal lows | Uso habitual |
| 3 | Relative equal highs / lows | Uso habitual |
| 4 | Data highs / data lows | Uso habitual, sobre todo noticias de 8:30 |
| 5 | NWOG / NDOG | Uso habitual |
| 6 | Low resistance liquidity (LRL) | "La joya de la corona", el que más usa [14:31] |

Su ranking explícito de utilidad: LRL y NWOG/NDOG son "los que funcionan mejor", junto con los equal highs y los data highs [11:58–12:28].

### 8.1. PDH / PDL (previous day high / previous day low)

- Significa *previous day high* y *previous day low*: el alto y el bajo del día anterior [00:32–01:05].
- Se marcan **siempre en gráfico diario**: se toma la última vela cerrada y se marcan la mecha más alta y la más baja [01:36–02:07].
- El precio tiende a visitarlos y reaccionar, "como si fuese una buy side liquidity o una sell side liquidity" [01:05–01:36].
- No se usan aislados: en su ejemplo, el PDH coincide con un FVG bajista y desde ahí proyecta el PDL [02:37].
- Es el tipo que menos usa: dice que se puede saltar, aunque lo explica "porque obviamente sirve" [00:32–01:05].

**Certeza:** EXPLÍCITO en la definición y en el modo de marcado. Que sea el menos importante es EXPLÍCITO; que no lo use nunca, NO CONFIRMADO.

### 8.2. NWOG (New Week Opening Gap)

- Gap grande que se deja entre el cierre del viernes y la apertura del domingo/lunes.
- "Son sitios que suelen tener mucha liquidez" y no le gusta operar en contra [fuente: `1C4dgloDQrY`, 01:09:08; también `Urrb1b2kBso` 05:44].
- La mayoría de las veces el precio quiere **rellenarlo entero** [ `Urrb1b2kBso` 05:44].
- Actúa como un FVG [ `u-fG6bYvK7k` 10:24].
- **Día 11:** el que aparece al cambiar de viernes a lunes es NWOG; el que aparece en cualquier otro cambio de día es NDOG. "Tienen la misma importancia" [ `OtYATAfCfRA` 12:59–13:29].
- Actúa como un FVG: es imán y ayuda a continuar la tendencia. Se puede buscar una entrada hacia él o esperar a que lo toque y continúe [13:29–13:59].
- Regla tajante: "siempre que haya un New Day Opening Gap o New Week Opening Gap, nunca voy a operar en contra... nunca, nunca, nunca operéis en contra de uno de estos gaps" [14:31].

**Certeza:** EXPLÍCITO.

### 8.3. NDOG (New Day Opening Gap)

- Gap de apertura diaria; lo trata como excepción que puede cambiar el DOL [ `Urrb1b2kBso` 02:06–03:10].
- En el ejemplo del 4 de abril de 2025, el NDOG arriba es el objetivo de compra si se invierte el FVG bajista [03:10–04:12].
- **Día 11:** misma mecánica que el NWOG; se distingue solo por el día en que se forma (lunes = semanal; resto = diario) [ `OtYATAfCfRA` 12:59–13:29].

### 8.4. Equal highs / relative equal highs / equal lows

- **Equal highs/lows:** dos o más extremos **exactamente iguales**, sin quitar. "Si son iguales, me encanta" [ `1C4dgloDQrY` 43:14].
- **Relative equal highs/lows:** extremos **casi iguales**, que no se han acabado de quitar. "No son igualitos, pero son igual así" [ `1C4dgloDQrY` 43:45].
- **LRL:** muchos relative equal highs/lows juntos (ver §8.5).
- Son una de las excepciones que pueden cambiar el DOL [ `Urrb1b2kBso` 02:06–03:10].
- En el ejemplo del 22/10, los relative equal highs son objetivo y también razón para no entrar antes de que se limpien [ `OdljBowQurk` ].

**Desarrollo del Día 11:**

- **Equal** = dos mechas "exactamente a la misma altura". **Relative equal** = "casi iguales": al hacer zoom se ve que no coinciden [ `OtYATAfCfRA` 03:40–04:10].
- Si un bajo está más bajo que el otro, **no cuenta**: la liquidez de ese extremo ya se ha cogido. Lo que interesa es que el dinero siga ahí ("doble cash") [04:10–04:42].
- Se miran de **5 minutos al diario**; a mayor temporalidad, más importancia [04:42; 06:13].
- Indicador que recomienda: *Equal High/Low* de JZS Tour en TradingView, ajustado para mostrar solo equal highs/lows de 15 minutos en adelante [05:13–05:43]. La configuración exacta que muestra no queda clara en el audio (menciona un valor de 14 minutos y un ajuste desactivado): **NO CONFIRMADO**.
- **Regla sagrada:** "nunca operar en contra de equal highs". Con equal highs arriba no busca cortos, porque el stop no está protegido: es "un caramelito" para que el mercado vaya a por la liquidez y luego gire [06:48–07:19].
- Con relative equal lows, el precio suele quitarlos (stops) antes de subir; también pueden usarse como objetivo [07:50–08:53].

**Certeza:** EXPLÍCITO en definición y regla; configuración del indicador NO CONFIRMADA.

### 8.5. Low resistance liquidity (LRL)

**Definición explícita de Xavi:** "Muchos highs que están juntos o lows que no se han llegado a quitar nunca entre ellos." — `PzkT4SC47Jo` [12:28–12:58].

En `1C4dgloDQrY` la desarrolla: los **relative equal highs consecutivos** son LRL; el precio no es capaz de atravesarlos y crea más; cuando por fin da un inverse, "todo esto se lo va a mear y va a ir hacia ello" [43:45–44:48].

- No es un indicador; es una acumulación de extremos próximos sin gaps que los protejan. Cuantos más highs/lows juntos, más liquidez y más "objetivo" es la zona.
- Es una de las excepciones que pueden cambiar el DOL [ `Urrb1b2kBso` 02:06–03:10].
- En el ejemplo de 09:24–09:56, hay LRL arriba y el precio la usa como camino hacia el high.
- En `oP7enoxXpfI` la incluye entre los requisitos del setup: "low resistance liquidity, buena estructura" [09:52–10:24].
- En el backtest de marzo insiste: si hay mucha LRL abajo y ningún gap de 15m que reaccione, el precio "sí o sí" tiene que ir a tocarla antes de decidir si sigue subiendo o gira [ `PzkT4SC47Jo` 12:58–13:30].
- No se opera **contra** ella: es la regla 81.

**Cómo la identifica:** varios highs seguidos en 15m/5m/1m, o varios lows que nunca se han quitado entre sí; comprueba que no haya un FVG relevante entre ellos.

**Desarrollo del Día 11:**

- Es "la joya de la corona", el tipo que más usa [ `OtYATAfCfRA` 14:31].
- Se forma en subidas o bajadas "chinuchano", dejando lows (o highs) consecutivos sin quitar [15:02–15:36].
- Normalmente aparece en **1–5 minutos**; en 1 hora es posible pero raro (implicaría un día entero de subida lenta) y pesa más [15:36–16:08].
- La marca con una línea horizontal y la etiqueta "LRL" [16:38–17:09].
- Cuando el precio la toca, se la lleva con fuerza y continúa la tendencia [17:09].
- **No se opera con LRL en el stop:** "nunca quieras buscar unos largos teniendo todo esto en tu stop loss... el trade no va a dar resultado" [17:40].

**Certeza:** EXPLÍCITO.

### 8.6. Data highs / data lows

- Son los extremos que deja el precio alrededor de una noticia (CPI, FOMC, etc.).
- Los marca en días de dato y los usa como niveles de liquidez y como objetivo [ `oP7enoxXpfI` 27:15, 36:08].
- En el ejemplo de CPI: "Data high... hay que esperar a que el precio haga esto o esto; acumulación, manipulación, tocamos gap de 15, salimos de acumulación, dame un gap, dame un invers de 30 segundos... cuando toquemos los data, me piro" [27:15].
- En FOMC: "tenemos data lows de FOMC y estamos en un gap de 4 horas; idea clarísima: toque el gap y va para abajo" [36:08].
- **Día 11:** las noticias que más usa son las de las **8:30** (hora Nueva York). A las 9:30, al abrir el mercado, el precio suele buscar el data high o el data low y reaccionar hacia el otro extremo [ `OtYATAfCfRA` 09:24–09:54].
- Con una noticia **a las 10:00**: como no se puede operar antes, se espera a que salga, se marcan el alto y el bajo que deja, y se busca el barrido de un extremo hacia el otro [09:54–10:25].
- Se marca **la mecha**; si no hay mecha, el cuerpo [10:57].
- La liquidez del dato sirve como **objetivo y como punto de reacción**; a veces el precio no llega al extremo contrario y aun así el movimiento es aprovechable [11:28–11:58].

**Certeza:** EXPLÍCITO.

### 8.7. Internal highs / internal lows dentro de FVG

Es uno de sus objetivos preferidos, y lo dice en mayúsculas:

> "Internal highs, internal lows... que estén dentro de FVGs. Superimportante." — `1C4dgloDQrY` [45:18]

- No cualquier internal high/low: tiene que estar **dentro de un FVG**.
- Si solo hay liquidez y no hay FVG, no lo usa ni como target ni como break-even [ `1C4dgloDQrY` 24:08–24:38].
- Es la misma lógica que aplica en el modelo 2 y en el modelo 3: FVG + internal high/low, las dos cosas juntas [19:30–20:02].

### 8.8. Lo que NO usa como niveles: London highs/lows y Asian highs/lows

> "Yo no uso London high, London lows, Asian lows, Asian high, no, ya no los uso. Lo que simplemente uso son highs y lows de 1 hora y 4 horas." — `1C4dgloDQrY` [45:51–46:21]

- **No** usa los highs/lows de Londres o Asia como niveles de liquidez.
- Sí usa los highs/lows de **1H y 4H**, que muchas veces coinciden con esos niveles por alineación, pero el nivel que marca es el de 1H/4H.
- **Matiz:** esto no contradice que opere la **sesión de Londres** para evaluaciones (concepto 68, CONTEXTUAL). Una cosa es operar la sesión y otra usar sus extremos como niveles. No confundirlas.

**Certeza:** EXPLÍCITO. Se añade a la lista de conceptos no usados como niveles.

---

## 9. DOL (Draw on Liquidity)

### 9.1. Definición

El DOL es **el nivel de liquidez hacia el que el precio quiere ir**. No es cualquier alto o bajo: es el que tiene sentido dentro del contexto y que está asociado a una zona relevante (FVG/PD array).

> "¿Cuál es el high más prominente que tenemos? Este de aquí. ¿Qué queremos que el precio llegue a este high?" — `Urrb1b2kBso` [09:24]

> "Voy a marcar este low que está dentro de este fair value up de 4 horas... mi objetivo sería este low de aquí." — `zcT31zmE5Uc` [06:11]

**Certeza:** EXPLÍCITO.

### 9.2. Cómo lo identifica

Proceso declarado en `Urrb1b2kBso` [14:40–15:12] y `zcT31zmE5Uc` [00:02–01:33]:

1. Ir a **4 horas** y **1 hora**.
2. Ver si el precio está **respetando los FVG alcistas e invalidando los bajistas**, o al revés.
3. Si respeta alcistas → dirección alcista; el DOL es un high relevante por encima.
4. Si respeta bajistas → dirección bajista; el DOL es un low relevante por debajo.
5. Marcarse los highs/lows que estén **en tu zona, normalmente dentro del rango**, y buscar entrada hacia ellos.

Checklist que él mismo resume en `zcT31zmE5Uc` [15:07–15:38]:

> "Lo primero, ya sé lo que busco: compras o ventas. Luego te vas a 15 minutos, a una hora, 30 minutos y miras si se abren gaps. A que se abra un gap y se toque, miras la reacción hacia la dirección del high time frame y entras a través de inverse fair value."

**Certeza:** EXPLÍCITO.

### 9.3. DOL no es solo un high/low externo

Puede ser:
- Un **low dentro de un FVG de 4 horas** [ `zcT31zmE5Uc` 06:11].
- Un **daily gap** sin rellenar [06:11–06:41].
- Un **internal high dentro de un FVG** [09:48–10:20].
- Un **relative equal high/low** [ `Urrb1b2kBso` 06:16–06:46].
- El **NWOG** [ `Urrb1b2kBso` 05:44–06:16].
- La **LRL** [ `Urrb1b2kBso` 09:24–09:56].

**Certeza:** EXPLÍCITO.

### 9.4. Si el DOL no está claro

- Si hay DOL en ambos lados y el precio no se decanta, **no opera** [ `zcT31zmE5Uc` 01:33–02:04].
- Si el high time frame "no te dice nada", es un día de no operar [02:04–02:36].
- Si los objetivos se cumplen antes de que haya entrada, **se cierra el día**; no se fuerza [06:41–07:13].
- Si está confundido, se bloquea ("lockout") y no opera [ `Urrb1b2kBso` 15:12–15:42].

> "La gente que opera esto es gente que tiene ganas de operar, no se puede aguantar sin operar... se ha perdido el movimiento del día, ha forzado algo. Si se dan tus objetivos, haces así y te vas al siguiente día." — `zcT31zmE5Uc` [06:41–07:13]

**Certeza:** EXPLÍCITO.

### 9.5. Excepciones que pueden cambiar el DOL

En `Urrb1b2kBso` [02:06–03:10] enumera:

- **New Day Opening Gaps (NDOG).**
- **Low resistance liquidity (LRL).**
- **Relative equal highs / equal highs.**
- **SMT** (divergencia entre NQ y ES).

Son "pequeñas excepciones" que hacen que el DOL cambie. No sustituyen el análisis de FVG; lo condicionan.

**Certeza:** EXPLÍCITO. La lista puede no ser exhaustiva; él no dice que lo sea.

### 9.6. La vela de las 10:00

Cuando hay duda sobre si un FVG se respeta o se invierte:

> "Ante la duda te esperas a que cierre la vela de las 10... Cuando cierre la vela, la mayoría de las veces el mercado ya se va a orientar hacia la zona en la que quiere ir." — `Urrb1b2kBso` [04:43–05:13]

Esto es especialmente importante si hay NDOG, LRL o equal highs en la dirección contraria. Es una regla de **espera**, no de entrada automática.

**Certeza:** EXPLÍCITO.

---

## 10. Proceso operativo que se desprende de la liquidez

Pasos que Xavi resume al final del Día 6 [19:20–19:52]:

1. **Márcate tu BSL y tu SSL.**
2. **Espérate a que se quite esa BSL** (o SSL): que el mercado vaya a por ese dinero.
3. **Si todo está alineado con tu dirección**, busca el trade hacia la SSL (o BSL) opuesta.
4. Siempre con varias cosas alineadas, no solo por el barrido.

**Inferencia operativa (INFERIDO, no regla textual):** el barrido por sí solo no es entrada. Hace falta dirección HTF, zona relevante y confirmación LTF (IFVG/CISD). El propio Xavi lo dice: "si todo está alineado con tus direcciones... siempre y cuando tengas diferentes cosas alineadas" [19:52].

---

## 11. Errores que él señala

- **Marcar cualquier alto/bajo como liquidez.** Los swing points son los prominentes, los extremos del rango [02:11–02:42].
- **Usar liquidez de temporalidad baja como principal.** "Las temporalidades altas mandan" [02:11].
- **Pensar que el mercado siempre hace lo mismo.** "No es eterno... van a haber caídas, acumulaciones, de todo" [15:11–15:44].
- **Operar porque tienes ganas, no porque haya setup.** [ `zcT31zmE5Uc` 06:41–07:13].
- **Forzar un trade cuando los objetivos ya se cumplieron.** [06:41–07:13].
- **Confundir el color de las velas con la validez del swing para liquidez.** El color no importa para liquidez [06:21–06:52].
- **Operar contra equal highs/lows** [ `OtYATAfCfRA` 06:48].
- **Operar contra un NWOG o NDOG** [14:31].
- **Colocar el stop donde hay LRL** [17:40].
- **Dar por válido un equal low cuando uno está más bajo:** esa liquidez ya se cogió [04:10].

---

## 12. Evidencia

| Afirmación | Video | Timestamp | Tipo |
|---|---|---|---|
| Liquidez = dinero | `7HOAf7vHMqU` | 01:08 | EXPLÍCITO |
| HTF manda | `7HOAf7vHMqU` | 01:08–02:11 | EXPLÍCITO |
| Swing high/low = extremos prominentes del rango | `7HOAf7vHMqU` | 02:11–02:42 | EXPLÍCITO |
| Instituciones buscan stops | `7HOAf7vHMqU` | 03:12–05:48 | EXPLÍCITO |
| BSL = altos, SSL = bajos | `7HOAf7vHMqU` | 07:23–07:55 | EXPLÍCITO |
| Conteo de "billetes" | `7HOAf7vHMqU` | 08:25–15:11 | EXPLÍCITO / INFERIDO si se mechaniza |
| Precio busca liquidez a través de imbalances | `7HOAf7vHMqU` | 15:11 | EXPLÍCITO |
| Pasos: marcar, esperar barrido, buscar trade | `7HOAf7vHMqU` | 19:20–19:52 | EXPLÍCITO |
| Excepciones: NDOG, LRL, equal highs, SMT | `Urrb1b2kBso` | 02:06–03:10 | EXPLÍCITO |
| Esperar vela de las 10 | `Urrb1b2kBso` | 04:43–05:13 | EXPLÍCITO |
| No operar después de 11:25 | `Urrb1b2kBso` | 13:06–13:39 | EXPLÍCITO |
| Internal/external liquidity | `u-fG6bYvK7k` | 13:00–13:31 | EXPLÍCITO |
| Data highs/lows | `oP7enoxXpfI` | 27:15, 36:08 | EXPLÍCITO |
| DOL = high/low dentro de FVG | `zcT31zmE5Uc` | 06:11 | EXPLÍCITO |
| Si no hay DOL claro, no operar | `zcT31zmE5Uc` | 01:33–02:04 | EXPLÍCITO |
| Seis tipos de liquidez; usa cinco (PDH/PDL "skipeable") | `OtYATAfCfRA` | 00:32–01:05 | EXPLÍCITO |
| PDH/PDL se marcan en diario (mecha alta/baja de la última vela) | `OtYATAfCfRA` | 01:36–02:07 | EXPLÍCITO |
| Equal = exactamente iguales; relative = casi iguales | `OtYATAfCfRA` | 03:40–04:10 | EXPLÍCITO |
| Si un low está más bajo, el equal low no cuenta | `OtYATAfCfRA` | 04:10–04:42 | EXPLÍCITO |
| Equal highs/lows se miran de 5m al diario | `OtYATAfCfRA` | 04:42 | EXPLÍCITO |
| Nunca operar contra equal highs/lows | `OtYATAfCfRA` | 06:48 | EXPLÍCITO |
| NWOG (lunes) y NDOG (resto) tienen la misma importancia | `OtYATAfCfRA` | 12:59–13:29 | EXPLÍCITO |
| Nunca operar contra NWOG/NDOG | `OtYATAfCfRA` | 14:31 | EXPLÍCITO |
| LRL: "la joya de la corona"; normalmente 1–5m | `OtYATAfCfRA` | 14:31; 15:36–16:08 | EXPLÍCITO |
| No poner el stop donde hay LRL | `OtYATAfCfRA` | 17:40 | EXPLÍCITO |
| Data highs/lows: noticias de 8:30 y de 10:00 | `OtYATAfCfRA` | 09:24–10:25 | EXPLÍCITO |

---

## 13. Preguntas abiertas

- **Liquidez pt2 (resuelta en parte):** el Día 11 cierra la lista de tipos y sus reglas de uso. Sigue sin explicar **cuándo el precio va a por toda la liquidez o solo a por una parte**, que era la otra mitad de la pregunta anunciada en el Día 6 [02:11, 12:04].
- **Configuración exacta del indicador de equal highs/lows:** menciona *Equal High/Low* de JZS Tour y un valor de 14 minutos, pero el ajuste no se ve con claridad [ `OtYATAfCfRA` 05:13–05:43].
- **Jerarquía entre tipos cuando compiten:** dice que LRL y NWOG/NDOG son los que mejor funcionan, pero no da un orden para resolver un conflicto (p. ej., PDH contra un NWOG).
- **"Más billetes"**: ¿es una regla operativa o solo una forma de explicar el movimiento? Él dice que lo aclarará más adelante.
- **Stop exacto** tras el barrido: no está desarrollado en el Día 6; sí en videos de entradas.
- **Relación entre DOL y "true manipulation"**: el DOL puede ser el objetivo, pero la manipulación verdadera requiere que NQ y ES tengan motivo. Pendiente de unificar en el documento de PO3.
- **Uso de liquidez de 1 minuto**: dice que las HTF mandan, pero en entradas usa 1m/30s. La distinción es de **peso del nivel**, no de temporalidad de ejecución. Confirmar con nuevas clases.

---

## 14. Cómo enseñarlo (cuando toque)

No empezar por "qué es BSL/SSL" en abstracto. El orden que él usa en el Día 6 es:

1. La liquidez es dinero.
2. Todo alto/bajo tiene liquidez; las HTF pesan más.
3. Qué es un swing high/low.
4. Por qué las instituciones necesitan esos stops.
5. BSL/SSL.
6. Ejemplos de conteo y barridos.
7. Proceso: marcar, esperar, buscar trade hacia el otro lado.
8. Tipos de liquidez del Día 11, en su orden: PDH/PDL, equal/relative equal, data highs/lows, NWOG/NDOG, LRL.
9. Reglas de exclusión: no operar contra equal highs/lows ni contra NWOG/NDOG; no poner el stop en una LRL.
10. Deberes: marcar swings, BSL/SSL y los cinco tipos de liquidez en rangos.

Seguir ese orden, no el de un temario ICT.
