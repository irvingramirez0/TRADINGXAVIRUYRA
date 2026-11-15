# 07 — GESTIÓN DE RIESGO, BREAK-EVEN Y CUENTAS DE FONDEO

**Estado:** vigente.
**Última actualización:** 2026-11-02
**Fuente principal:** `ndABd2MECBA` (2026-07-18) — versión actual.
**Fuentes de contraste:** `L-gy9cAIvjc` (2026-03-07) — versión anterior, se conserva como historia; `5aBdJLMDGJc` (2026-05-16) — break-even; `6FkSzKDvlX0` (2026-05-19) — pérdida y revenge trading; `T9kUqk-NzRM` (2026-06-28) — cautela ante cambios por presión de payout; `mBHtx-BfWWg` (2026-10-30) — perfil de estrategia.

---

## 1. Principio general

> "Al final el trading es 100% gestión de riesgo." — `mBHtx-BfWWg` [aproximado, Día 5]

La gestión de riesgo de Xavi no es un porcentaje fijo universal: **depende de la fase en la que esté el trader y del tipo de cuenta**. Él lo dice explícitamente:

> "No toda la gestión de riesgo que yo utilizo estándar, es decir, 1% de riesgo aquí y 2% de riesgo aquí... sino que os voy a decir cómo cambia mi riesgo, cómo lo ajusto según en la situación en la que estoy." — `L-gy9cAIvjc` [00:04–00:36]

Esto sigue siendo válido en la versión de julio de 2026: la lógica es la misma, los números y la estructura se refinan.

**Certeza:** EXPLÍCITO.

---

## 2. Perfil de la estrategia (punto de partida)

Todo el esquema de riesgo está calibrado sobre su estrategia:

| Parámetro | Valor | Fuente |
|---|---|---|
| Win rate normal | ~70–73% | `mBHtx-BfWWg`; `5aBdJLMDGJc` [31:10] |
| RR habitual | 1:1 | `5aBdJLMDGJc`; `ndABd2MECBA` |
| RR en evaluación (intermedio) | 1:1,5 | `ndABd2MECBA` [05:50] |
| Trades por día | 1 | `ndABd2MECBA`; `5aBdJLMDGJc` |
| Tiempo en el trade | corto | `mBHtx-BfWWg` |
| Instrumento | MNQ para empezar; NQ después | `mBHtx-BfWWg` |

> "Mi estrategia... bajo el perfil de tener un 70% de win rate." — `ndABd2MECBA` [01:34]

**Certeza:** EXPLÍCITO.

**Advertencia:** el 70–73% es **su** win rate con **su** estrategia y **su** operativa de un trade al día. No es una promesa ni una estadística trasladable sin backtesting. Él mismo rebaja el 86% de una muestra pequeña a "73, 72% que es mi win rate normal" [ `5aBdJLMDGJc` 31:10].

### 2.1. El objetivo suele estar en el nivel, no a 1:1 exacto

En los tickets visibles de las sesiones de backtesting, el TP no se calcula a 1:1 exacto: se coloca en el high/low de liquidez.

- `sKSAh5gky1M` [11:02–11:06]: entrada 21.418,38; stop 21.451,79 (33,41 puntos); objetivo 21.364,04 (54,34 puntos) = **1:1,63**.
- `mCMpxc0NaN4` [29:29–29:33]: entrada 14.686,25; stop 14.651,50 (34,75 puntos); objetivo 14.740,75 (54,50 puntos) = **1:1,57**.
- `PzkT4SC47Jo` [14:00]: short del 6 de marzo de 2024 con stop 29,25 puntos y objetivo 62,75 puntos = **1:2,15**. El panel de FX Replay marca el trade cerrado con +62,75 puntos. El objetivo está en los lows de la LRL, no a 1:1 (`03_FRAMES/PzkT4SC47Jo/be_sin_miedo.jpg`).

**Certeza:** OBSERVADO en tres operaciones. No lo formula como regla. La referencia declarada sigue siendo 1:1; cuando el nivel de liquidez está más lejos, el objetivo se coloca en el nivel y el RR sube.

---

## 3. Fase 1 — Principiante

**Definición:** nunca ha tenido un payout, o solo ha tenido uno "con suerte".

> "Gente que no ha tenido nunca ningún payout o ha conseguido algún payout con suerte... un payout con una noticia como CPI, un payout gambleando, un payout yendo super agresivo, sin saber exactamente qué hacían." — `ndABd2MECBA` [01:03–01:34]

### 3.1. Evaluación

| Parámetro | Valor |
|---|---|
| Cuenta de referencia | $50.000 |
| Riesgo por trade | $500 = **1%** |
| RR | 1:1 o 1:1,5 |
| Trades por día | **1** |
| Sesiones por día | **1** |
| Setups | solo **A+** |
| Trades necesarios para pasar | ~6 (para llegar a $3.000) |

> "Un trade al día y una sesión al día. Sobre todo una sesión al día." — `ndABd2MECBA` [02:05]

> "Solo A plus setups... simplemente vas a necesitar asegurar seis trades para poder pasar la cuenta, solo seis, ya que tienes que llegar a $3,000." — `ndABd2MECBA` [02:05–02:36]

La razón de una sola sesión: construir hábitos y no dispersarse operando mañana, tarde y noche.

> "Tenéis que entrar en los buenos hábitos de entender que lo más efectivo y lo más eficiente para pasar una cuenta y más si estás empezando es un trade al día, una sesión al día." — `ndABd2MECBA` [02:05]

**Certeza:** EXPLÍCITO.

### 3.2. Fase fondeada

Se mantiene **exactamente el mismo riesgo**:

> "Vas a seguir literalmente la misma gestión del riesgo. Si tú eres capaz de pasar una cuenta con este riesgo, en la fondeada deberías hacer lo mismo." — `ndABd2MECBA` [03:06]

> "500 de riesgo donde vas a tener que confiar en el sistema. Piensa que nada ha cambiado." — `ndABd2MECBA` [03:06]

**Certeza:** EXPLÍCITO.

### 3.3. Cuándo pasar a intermedio

No es por tiempo ni por resultados puntuales: es por **consistencia demostrada con retiros**.

> "Antes de pasar de esta fase a la que vamos a ver ahora, retires con una misma cuenta... al menos dos veces." — `ndABd2MECBA` [03:37]

Ejemplo que él da:

1. Llegar a **$3.000** de balance.
2. Retirar **$1.500**.
3. Quedarse **$1.500** en la cuenta.
4. Volver a construir hasta **$3.000**.
5. Retirar otros **$1.500**.

> "Llegáis a 3,000, retiráis 1500 y luego con estos 1500 volvéis a llegar a 3,000 para retirar 1500." — `ndABd2MECBA` [04:17–04:49]

Alternativa aceptada: llegar a $2.000 y retirar $1.000, dos veces [04:49].

**Certeza:** EXPLÍCITO.

---

## 4. Fase 2 — Intermedio

**Definición:** ya ha retirado varias veces, tiene confianza y busca escalar.

### 4.1. Evaluación

| Parámetro | Valor |
|---|---|
| Riesgo por trade | $1.000 = **2%** |
| RR | **1:1,5** |
| TP | $1.500, priorizado en dólares |
| Objetivo | pasar o quemar la cuenta en **2 días** |
| Colchón necesario | $1.000–3.000 de retiros previos |
| Sesión de evaluación | Londres |
| Sesión de cuentas fondeadas | Nueva York |

> "Arriesgo $1,000 por cada trade en una evaluación. Esto implica un riesgo de 2%... estiro los RRs y busco un 1 a 1,5." — `ndABd2MECBA` [05:50]

> "Pongo el TP en base a los dólares... priorizar siempre los $1,500 de take profit. ¿Por qué hacemos esto? Para pasar o quemar la cuenta en dos días." — `ndABd2MECBA` [05:50–06:22]

Él mismo reconoce que priorizar dólares está "mal hecho" en términos de ejecución, pero lo usa **solo en evaluación** porque el objetivo es pasar rápido, no operar óptimo [06:22].

> "Es algo que está mal hecho porque si tú te centras en los dólares, la mayoría de veces vas a operar mal." — `ndABd2MECBA` [06:22]

**Certeza:** EXPLÍCITO.

### 4.2. Advertencia psicológica

> "Cuando empezamos a permitirnos arriesgar $1,000, 1200, $900 por trade, empezamos a asociar este riesgo con gamblear, con no seguir nuestras reglas... el hecho de que tú te permitas subir el riesgo del doble porque estás más avanzado no significa que seas mejor que el mercado." — `ndABd2MECBA` [07:24]

> "Tienes que ser agresivo, pero ir con cabeza y sobre todo pillar aún mejores setups que los que pillabas antes." — `ndABd2MECBA` [07:24]

**Certeza:** EXPLÍCITO.

### 4.3. Separación de sesiones

> "Si ya tienes dos, tres, cuatro payouts y quieres empezar a priorizar la sesión de Nueva York para operar cuentas que ya tienes fondeadas, lo que puedes hacer es intentar pasar evaluaciones en Londres." — `ndABd2MECBA` [07:54]

- **Londres:** evaluaciones.
- **Nueva York:** cuentas fondeadas.
- Recomienda backtestear antes de adoptar Londres.

**Certeza:** EXPLÍCITO.

---

## 5. Fase fondeada — dos tipos de cuenta

Xavi divide las cuentas fondeadas en dos grupos, según la **regla de consistencia de la prop firm** (no según la consistencia del trader):

> "Lo primero que hago es dividir las cuentas que tienen consistencia con las cuentas que no tienen consistencia." — `ndABd2MECBA` [08:55]

### 5.1. Cuentas con consistencia

| Parámetro | Valor |
|---|---|
| Riesgo | $500 = 1% |
| Setups | solo plus / A+ |
| Objetivo | construir balance poco a poco |
| Trato | como cuenta de capital propio |

> "Es clavada a esto... 500 de riesgo y simplemente confiar en el sistema. Nada ha cambiado... la voy a tratar como una cuenta de capital propio... sin ninguna prisa." — `ndABd2MECBA` [08:55–09:25]

**Certeza:** EXPLÍCITO.

### 5.2. Cuentas sin consistencia

| Parámetro | Valor |
|---|---|
| Riesgo | $2.000 = 4% |
| TP principal | $3.250 |
| Días adicionales | 4 días de $150 |
| Max payout | ~$2.000 |
| Requisito | estar protegido por cuentas con consistencia |

> "$2,000 de riesgo para construir un colchón rápido... un take profit de $3,250... las prop firms... te hacen tener 5 días de consistencia, cinco winning days de $150... un día positivo de 3,250 y luego 4 días positivos de $150... consigo retirar los 2000 de máximo payout." — `ndABd2MECBA` [09:25–10:27]

> "Es super importante que para tú tener esta gestión del riesgo en cuentas sin consistencia, necesitas estar protegido con otras cuentas." — `ndABd2MECBA` [09:25]

**Regla de protección:** si solo tienes cuentas sin consistencia y no tienes un colchón en cuentas con consistencia, **no** apliques el riesgo de $2.000.

> "Si vosotros tenéis dos cuentas de 50k... que no tenga consistencia en Fondeada y no tenéis respaldadas estas cuentas con cuentas... con consistencia... yo no haría lo de arriesgar $2,000." — `ndABd2MECBA` [10:59]

**Certeza:** EXPLÍCITO.

### 5.3. Lógica de cartera

La combinación que él describe:

- Cuentas con consistencia → colchón lento y estable.
- Cuentas sin consistencia → intentos agresivos de max payout.
- Si se queman las agresivas, las consistentes siguen generando retiros y financian más evals.
- El resultado mensual se calcula sumando payouts y restando coste de evals [11:30–12:01].

**Certeza:** EXPLÍCITO.

---

## 6. Break-even

Fuente: `5aBdJLMDGJc` (2026-05-16). Es una **regla de gestión**, no una obligación.

### 6.1. Regla central

El break-even solo se mueve a un **high/low que esté dentro de un FVG/gap relevante**, normalmente de **3 minutos o más**. En junio de 2026 concreta el umbral en **5 minutos o más**, o una zona de conflicto.

> "¿Este low está dentro de algo? No... ¿Este low entra algo de algo? Sí, porque está justo dentro de un gap de 5 minutos. Aquí va nuestro break even." — `5aBdJLMDGJc` [28:35]

> "Normalmente yo suelo mirar de 3 minutos hacia arriba." — `5aBdJLMDGJc` [11:31]

> "Si yo aquí por algún motivo tengo un low, un low random de un minuto, no voy a ir break even aquí. ¿Para qué?" — `1C4dgloDQrY` [24:08]

**Evolución del umbral:** mayo de 2026 dice 3m o más; junio de 2026 dice 5m o más, o zona de conflicto (FVG de 5m, 15m, 1H o 4H) [ `1C4dgloDQrY` 24:08–24:38; 35:30]. La versión de junio es la más reciente con un número explícito; agosto no da cifra, habla de "zona de valor". Se conservan las tres.

Si el high/low no está dentro de ninguna zona, **no** se mueve a break-even:

> "Todos estos lows son lows irrelevantes. No son lows que estén dentro de ningún fair value gap... Si el precio te llega aquí y se gira y te hace stop, no es que tendrías que haber ido break even, es que simplemente tu dirección del día no ha sido la correcta." — `5aBdJLMDGJc` [06:53–07:23]

**Certeza:** EXPLÍCITO.

### 6.2. Cuándo sí mover

1. **El low/high está dentro de un FVG/gap de 3m o más** [06:53–07:23, 11:01]. En la sesión de junio se ve el caso: entrada 14.191,25, stop 14.161,25 y BE en el high interior del FVG, no en el high de la vela de entrada (`03_FRAMES/mCMpxc0NaN4/be_fvg_2226.jpg`).
2. **El precio llega a una zona de conflicto** (FVG) aunque la convicción sea alta: proteger [07:54–08:25].
3. **El SP500 quita su high/low primero** y el NQ aún no: se puede mover a BE [14:37–15:08].
4. **El high/low es relevante** aunque el trade tenga mucha convicción: si está dentro de un FVG de 4H/1H, se protege [09:26–09:57].
5. **SMT como salida:** si el ES alcanza la zona objetivo y el NQ todavía no, y ya hay 1:1, cierra el trade; si no lo hay, mueve a BE y deja correr [ `1C4dgloDQrY` 38:07–39:39].

### 6.3. Cuándo no mover

- **No hay ningún gap relevante en el camino**: dejar correr hasta TP o stop.

> "No voy break even porque es o mi idea del trade es correcta o mi idea del trade es incorrecta. No hay nada aquí que pueda frenar mi trade." — `5aBdJLMDGJc` [30:39]

- **El low/high es irrelevante** (no está en ninguna zona): no tiene sentido proteger ahí [06:53–07:23].
- **La estructura es fuerte y no hay conflicto**: dejar correr [10:28–11:01].
- **Es miedo, no estructura:** en el backtest de marzo lo dice sin rodeos: "No vayáis break even por miedo. Si vuestra idea del trade es correcta, os va a aguantar las zonas y os va a dar TP" [ `PzkT4SC47Jo` 14:00]. Si el high está protegido por gaps y hay mucha LRL, no mueve el stop aunque pudiera salvar el trade [ `PzkT4SC47Jo` 26:07].

### 6.4. Efecto sobre el win rate

> "86% de win rate casi. Obviamente es un win rate tan alto porque hemos hecho pocos trades. Yo creo que si seguimos haciendo trades, este win rate se va a ajustar al 73, 72% que es mi win rate normal." — `5aBdJLMDGJc` [31:10]

El break-even no convierte perdedores en ganadores: **evita stops que no tenían sentido estructural**. Si el precio se gira en una zona irrelevante, el problema era la dirección del día, no la falta de BE.

**Certeza:** EXPLÍCITO.

### 6.5. Reglas de tiempo y número de trades

- **Un trade al día.**
- **Después del TP, se acaba el día** [10:28–11:01].
- **10:21 puede ser una buena hora de entrada** [10:28].
- **Después de las 11:10 ya no es su horario** [26:33].
- Si se salta un trade por no cumplir condiciones, no se fuerza el siguiente [26:33–27:04].

**Certeza:** EXPLÍCITO.

### 6.6. Excepción por payout

En el recap de la racha de 14 take profits (`Dfx9SQYerVQ`, 2026-06-03) va a break-even aunque él mismo reconoce que no era la mejor zona:

> "No considero que sea un día para ir break even. Yo he ido break even porque este es un día del payout y porque llevo 14 wins seguidas y simplemente quería asegurar... tampoco era la mejor zona de BreakEven." — `Dfx9SQYerVQ` [01:06–01:38]

Es una **excepción discrecional**: protege el payout o una racha, no la estructura. No convierte el BE en una regla automática. El fotograma del momento (`03_FRAMES/Dfx9SQYerVQ/be_payout_66.jpg`) muestra el 5m del día: la caída desde el máximo y la mecha de las 10:00.

### 6.7. Tensión posterior sobre BE por presión de payout

En `T9kUqk-NzRM` (2026-06-28) recomienda no tocar el stop-loss ni el take-profit bajo presión de una fecha importante. También describe que adelantar el break-even a un día del payout puede acabar en frustración y una reentrada con más riesgo [09:01–10:08].

Esto limita la lectura de la excepción de §6.6, pero **no la revoca formalmente**: la excepción del 3 de junio fue una decisión discrecional para proteger un payout y una racha de 14 wins; el vídeo del 28 de junio advierte contra cambiar el plan por la presión de una fecha y contra la espiral de reentrada. No convertir la excepción en una regla técnica ni en una orden automática de mover BE antes de un payout.

**Certeza:** explícita para la recomendación y la advertencia; no hay retractación explícita de la excepción anterior.

### 6.8. Límites en backtesting

En las sesiones de backtesting aparecen límites que no siempre formula como reglas de fondeo:

- **FOMC:** no operar o reducir el riesgo al mínimo; solo aceptar algo que encante [ `sKSAh5gky1M` 27:40; `3ChwQZ8hRN0` 05:18].
- **Dos pérdidas seguidas:** en la sesión de enero dice "si nos llevamos dos loses... para casa" [ `sKSAh5gky1M` 11:34]. No está confirmado como límite de fondeo.
- **Después de un TP, no quedarse en el mercado** [ `3ChwQZ8hRN0` 04:46].
- **Si se piensa demasiado, no entrar** [ `3ChwQZ8hRN0` 24:10].

**Certeza:** EXPLÍCITO en el contexto del backtesting; su traslado a fondeo es INFERIDO.

---

## 7. La pérdida de $8.098 — errores y reglas

Fuente: `6FkSzKDvlX0` (2026-05-19). Es el caso práctico que da contenido a las reglas anteriores.

### 7.1. Qué pasó

- Cuatro cuentas Lucid fondeadas esa misma mañana + una cuenta grande.
- Pérdida de **$8.098** en cuatro cuentas, más **$3.790** en la cuenta grande.
- Máxima asignación Lucid ($250k en cinco cuentas) quemada.

> "Hemos perdido 8.098 dólares en cuatro funded... En total hemos perdido max allocation en Lucid, cinco cuentas, 250k funded, fuera." — `6FkSzKDvlX0` [00:33–01:07]

### 7.2. Cadena de errores

1. **Error de configuración del copy trading.** La cuenta líder seleccionada era la cuenta grande, no las evals que quería operar.

   > "En Trade Copia te puedes vincular estas cuatro cuentas, pero cuando entras en Trade Bait tienes que seleccionar la Leader Account... en mi caso era la cuenta tocha." — `6FkSzKDvlX0` [02:38–03:40]

2. **No cerrar al ver −$500.** Esperó a que se diera la vuelta y cerró en −$800.

   > "Ahí ya primer error, no cerrar instantáneamente... he pensado: 'Bua, no puedo cerrar, que es espero que se dé la vuelta'." — `6FkSzKDvlX0` [03:40–04:11]

3. **Reentrada en las cuatro cuentas para recuperar.** Stop de $2.000 por cuenta; las cuatro quemadas.

4. **Revenge trading.** Intentó recuperar el día sin stop, "gambleando", y quemó otra cuenta.

   > "Me he calentado muchísimo y qué he empezado a hacer, pues intentar recuperar... haciendo el tonto, gambleando, intentando sacar max con sin stop." — `6FkSzKDvlX0` [05:44–06:14]

### 7.3. Reglas que extrae

- **Logout inmediato tras un error evitable.**

  > "He perdido 800 por un error mío... ahí era logout y me voy." — `6FkSzKDvlX0` [08:18–08:50]

- **Un payout no es tuyo hasta que está solicitado y aprobado.**

  > "Hasta que no esté el payout requesteado y aprobado, no es tu dinero." — `6FkSzKDvlX0` [07:16]

- **No hacer revenge trading.** Lo dice explícitamente: "eso ni de coña lo hagáis" [10:21].
- **Normalizar que las cuentas se pueden quemar** no es excusa para picarse [10:21].
- **El riesgo agresivo tiene doble cara:** puede dar ROI alto o quemar varias cuentas a la vez [09:51–10:52].
- **Reset:** paró, esperó Nueva York y operó bien; hizo TP en tres cuentas [06:14–06:45].

**Certeza:** EXPLÍCITO / OBSERVADO.

---

## 8. Evolución de la gestión de riesgo

| Fecha | Video | Versión |
|---|---|---|
| 2026-03-07 | `L-gy9cAIvjc` | Dos perfiles: lento (1%, 1 trade/día, A+) y agresivo ($1.000–1.500 por trade, RR 1:1 o 1:1,5). Break-even no se trata. Buffer mínimo $1.000; ideal llegar a $4.000 y retirar $2.000. |
| 2026-05-16 | `5aBdJLMDGJc` | Regla de break-even basada en FVG/gap de 3m+. Un trade/día; 10:21 válido; después de 11:10 no. WR normal 72–73%. |
| 2026-05-19 | `6FkSzKDvlX0` | Caso real de pérdida: copy trading mal configurado, no cerrar, reentrada, revenge trading. Regla de logout. |
| 2026-07-18 | `ndABd2MECBA` | Versión actual: estructura por fases (principiante / intermedio), separación evaluación Londres vs fondeada NY, dos tipos de cuenta fondeada (con/sin consistencia), cifras concretas. |

**Versión vigente:** `ndABd2MECBA` (2026-07-18) para la estructura general; `5aBdJLMDGJc` (2026-05-16) para break-even; `6FkSzKDvlX0` para las reglas de corte tras error.

**Cambios relevantes respecto a marzo:**

- El perfil agresivo ya no es "1k–1.5k según el día": se separa en **$1.000 (2%) en evaluación** y **$2.000 (4%) en cuentas sin consistencia**, con requisito de protección.
- Se añade la **separación Londres/Nueva York**.
- Se añade la **regla de dos payouts** antes de subir de fase.
- Se mantiene el 1% y el 1:1 para el perfil conservador.

---

## 9. Errores que él señala

- **Arriesgar más de lo que el sistema justifica** por haber pasado una eval [ `ndABd2MECBA` 07:24].
- **Confundir subir el riesgo con ser mejor trader** [07:24].
- **Operar varias sesiones al día** siendo principiante [02:05].
- **Priorizar dólares sobre estructura en una cuenta normal** (solo aceptable en evaluación agresiva) [06:22].
- **Usar cuentas sin consistencia como únicas cuentas** [10:59].
- **Mover break-even a un low/high irrelevante** [ `5aBdJLMDGJc` 06:53–07:23].
- **No mover break-even en una zona de conflicto** [07:54–08:25].
- **Reentrar tras un stop por calentón** [ `6FkSzKDvlX0` 05:44].
- **No cerrar inmediatamente un error de configuración** [03:40–04:11].
- **Contar un payout antes de que esté aprobado** [07:16].
- **Hacer revenge trading** [10:21].
- **Tener prisa por retirar** [ `L-gy9cAIvjc` 15:47].

---

## 10. Evidencia

| Afirmación | Video | Timestamp | Tipo |
|---|---|---|---|
| Trading = 100% gestión de riesgo | `mBHtx-BfWWg` | Día 5 | EXPLÍCITO |
| Perfil: WR ~70%, RR 1:1, 1 trade/día | `ndABd2MECBA` | 01:34; 02:05 | EXPLÍCITO |
| Principiante: $500 = 1%, RR 1:1–1:1,5 | `ndABd2MECBA` | 01:34 | EXPLÍCITO |
| Una sesión y un trade al día | `ndABd2MECBA` | 02:05 | EXPLÍCITO |
| Solo A+; ~6 trades para pasar | `ndABd2MECBA` | 02:05–02:36 | EXPLÍCITO |
| Fondeada conservadora = mismo riesgo | `ndABd2MECBA` | 03:06 | EXPLÍCITO |
| Dos payouts antes de subir de fase | `ndABd2MECBA` | 03:37–04:49 | EXPLÍCITO |
| Intermedio: $1.000 = 2%, RR 1:1,5 | `ndABd2MECBA` | 05:50 | EXPLÍCITO |
| TP en dólares solo en evaluación | `ndABd2MECBA` | 05:50–06:22 | EXPLÍCITO |
| Evaluaciones en Londres, fondeadas en NY | `ndABd2MECBA` | 07:54 | EXPLÍCITO |
| Cuentas con consistencia: $500, A+ | `ndABd2MECBA` | 08:55–09:25 | EXPLÍCITO |
| Cuentas sin consistencia: $2.000, TP $3.250 | `ndABd2MECBA` | 09:25–10:27 | EXPLÍCITO |
| Requisito de protección con cuentas consistentes | `ndABd2MECBA` | 09:25; 10:59 | EXPLÍCITO |
| Break-even solo en low/high dentro de FVG 3m+ | `5aBdJLMDGJc` | 06:53–07:23; 11:31 | EXPLÍCITO |
| Si no hay gap relevante, no mover BE | `5aBdJLMDGJc` | 30:39 | EXPLÍCITO |
| SP500 quita su high/low primero → BE | `5aBdJLMDGJc` | 14:37–15:08 | EXPLÍCITO |
| Zona de conflicto → proteger | `5aBdJLMDGJc` | 07:54–08:25 | EXPLÍCITO |
| WR normal 72–73% | `5aBdJLMDGJc` | 31:10 | EXPLÍCITO |
| 10:21 válido; después de 11:10 no | `5aBdJLMDGJc` | 10:28; 26:33 | EXPLÍCITO |
| Pérdida de $8.098 por copy trading mal configurado | `6FkSzKDvlX0` | 00:33–03:40 | OBSERVADO |
| No cerrar al ver −$500 | `6FkSzKDvlX0` | 03:40–04:11 | OBSERVADO |
| Reentrada y revenge trading | `6FkSzKDvlX0` | 05:44–06:14 | OBSERVADO |
| Logout tras error evitable | `6FkSzKDvlX0` | 08:18–08:50 | EXPLÍCITO |
| Payout no es tuyo hasta aprobado | `6FkSzKDvlX0` | 07:16 | EXPLÍCITO |
| Versión anterior: $1.000–1.500 agresivo | `L-gy9cAIvjc` | 05:14 | EXPLÍCITO (histórico) |
| Versión anterior: buffer $1.000 / retirar $2.000 de $4.000 | `L-gy9cAIvjc` | 11:36–12:06 | EXPLÍCITO (histórico) |
| BE discrecional por payout/racha | `Dfx9SQYerVQ` | 01:06–01:38 | EXPLÍCITO |
| FOMC: no operar o riesgo mínimo | `sKSAh5gky1M`; `3ChwQZ8hRN0` | 27:40; 05:18 | EXPLÍCITO |
| Dos pérdidas y parar (backtesting) | `sKSAh5gky1M` | 11:34 | EXPLÍCITO (contexto) |
| Después del TP, fuera del mercado | `3ChwQZ8hRN0` | 04:46 | EXPLÍCITO |
| Si se piensa, no se entra | `3ChwQZ8hRN0` | 24:10 | EXPLÍCITO |

---

## 11. Preguntas abiertas

- **Porcentaje exacto en cuentas de $25k/$100k:** resuelto en lo esencial. El frame de `ndABd2MECBA` 01:03 confirma 500 $ = 1% en 50k. La conversión es aritmética: 250 $ en 25k y 1.000 $ en 100k para el 1%; 500 $/2.000 $ para el 2%; 1.000 $/4.000 $ para el 4%.
- **"Cuentas sin consistencia" vs "con consistencia":** la terminología se refiere a la regla de la prop firm, pero en el vídeo se mezcla con el requisito de 5 días de $150. Precisar con un frame de la tabla.
- **Break-even en Londres:** la regla está explicada en NY; no se ha documentado si cambia en Londres.
- **Break-even con CISD de 30s:** en la sesión de junio entra con CISD/IFVG de 30s y mueve el BE usando highs/lows dentro de FVG; el criterio de 3m+ parece seguir aplicando a la **zona**, no a la temporalidad de entrada. Queda como INFERIDO.
- **Break-even por payout:** en `Dfx9SQYerVQ` (2026-06-03) va a BE aunque él mismo dice que no era la mejor zona, solo para asegurar el payout y la racha de 14 wins. Es una **excepción discrecional**, no una regla estructural.
- **Reentrada tras stop:** la permite si el riesgo es bajo y el DOL sigue claro (masterclass), pero no hay un límite numérico; en junio dice que normalmente no hace reentries.
- **Máximo de cuentas simultáneas:** no fija un número; depende del colchón.
- **Rejection blocks:** él los prueba en backtesting y dice que no los operaría en fondeo [ `5aBdJLMDGJc` 19:16–20:18]. **No son parte de la metodología establecida.**

---

## 12. Cómo enseñarlo (cuando toque)

1. Principio: el riesgo se adapta a la fase, no es un porcentaje universal.
2. Perfil de la estrategia: WR, RR, un trade al día.
3. Fase principiante: 1%, 1:1–1:1,5, una sesión, A+, seis trades.
4. Fase fondeada conservadora: mismo riesgo, confiar en el sistema.
5. Cómo saber que estás listo para subir: dos payouts en la misma cuenta.
6. Fase intermedia: 2%, 1:1,5, Londres para evals, NY para fondeadas.
7. Cuentas fondeadas: con consistencia vs sin consistencia; regla de protección.
8. Break-even: solo en lows/highs dentro de FVG 3m+; cuándo no mover.
9. Errores reales: la pérdida de $8.098 y la regla de logout.
10. Psicología: no contar el payout hasta que esté aprobado; no revenge trading.

No enseñar el riesgo como una tabla fija. Enseñar **por qué** cambia: fase, tipo de cuenta, colchón y objetivo.
