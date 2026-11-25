---
tipo: indice
title: "Empieza aquí"
titulo: "Empieza aquí"
confianza: "explícito"
estado: "vigente"
video: ""
timestamp: ""
corte: "2026-11-23"
---


# Empieza aquí

**Corte de la metodología: 2026-11-23.** Sigue este orden; cada etapa enlaza a la clase y al minuto donde se explica.

> [!warning] La ruta, no el archivo
> Esto es lo que Xavi hace, en el orden en que lo hace. El resto del sitio es la evidencia.

- 4H/1H
- DOL
- liquidez
- PO3
- entradas
- gestión
- riesgo
- psicología

## El mapa, paso a paso

## 3. La metodología en una página

### 3.1 Contexto y dirección

Xavi empieza en **4 horas**, no en diario. Comprueba si el precio está **respetando los FVG alcistas e invalidando los bajistas** (o al revés). Eso le da la dirección del high time frame. Luego baja a **1 hora** para afinar.

El **DOL (draw on liquidity)** es el nivel que el precio quiere alcanzar: un alto o un bajo relevante que esté dentro de un **PD array** (en su uso, un FVG/gap). No cualquier alto o bajo. Si hay DOL claros en ambos sentidos y no se decanta, no opera.

El **SP500 (ES)** se usa solo como referencia de correlación. Un **SMT** (divergencia entre NQ y ES) solo es válido si el nivel barrido por uno de los dos está dentro de una zona relevante (FVG/PD array). Eso es la **true manipulation**: no basta con que un índice barra un alto y el otro no; los dos tienen que tener motivos para distribuir.

El **equilibrium** (retroceso de Fibonacci en el bootcamp; cuadrícula de Gann solo en la versión histórica de 2025) separa premium de descuento: premium siempre arriba, descuento siempre abajo. Compra en descuento y vende en premium. El FVG debe estar alineado con la línea 0.5 y la confirmación es el IFVG. Si el precio no toca equilibrium, normalmente no toma el trade.

El **FVG se valida en la temporalidad en la que se marca**: un cierre de 1 minuto al otro lado no invalida un FVG de 5 minutos si la vela de 5 minutos sigue aguantando [ `1McPSXSSR48` 14:20–15:26].

### 3.2 Liquidez

La liquidez es dinero. Cada alto y cada bajo tienen liquidez, pero la de temporalidades altas (15m, 1h, 4h) pesa más. Los **swing highs** son BSL (buy-side liquidity); los **swing lows** son SSL (sell-side liquidity). El precio se mueve buscando liquidez a través de imbalances.

Distingue **liquidez interna** (dentro del rango: highs/lows internos, gaps de 15m/5m) y **externa** (fuera del rango: previous highs/lows, relative equal highs/lows). En temporalidades bajas targetea liquidez interna; el DOL grande suele ser liquidez externa.

También usa **NWOG** (New Week Opening Gap), **NDOG** (New Day Opening Gap), **data highs/lows** en días de noticia, **equal highs/lows**, **relative equal highs/lows** y **low resistance liquidity (LRL)**.

Su objetivo preferido son los **internal highs/lows que están dentro de un FVG**; si solo hay liquidez y no hay FVG, no los usa ni como target ni como break-even [ `1C4dgloDQrY` 24:08–24:38, 45:18].

**No usa los highs/lows de Londres ni de Asia como niveles.** Usa highs/lows de 1H y 4H, que a veces coinciden con ellos por alineación, pero el nivel que marca es el de 1H/4H [ `1C4dgloDQrY` 45:51–46:21]. Esto no contradice que opere la sesión de Londres: una cosa es la sesión y otra los niveles.

**Antecedente:** en 2025 sí marcaba los highs/lows de Asia y Londres. Aparece en `vUt2D7S3ss8` (2025-12-02, 00:31: "lo que vamos a hacer es marcarnos los de las sesiones... London lows, Asia low") y en `p6wC7iWh_Ps` (2025-07-28, 00:32). En junio de 2026 dice "ya no los uso". Es una evolución documentada, no una contradicción: la versión vigente es la de junio.

### 3.3 Tiempo y PO3

Su ventana operativa actual es **9:30–10:30 NY**. Antes operaba 9:30–11:00; la versión vigente es la de agosto de 2026.

**PO3 = AMD + tiempo.** Acumulación en premarket, manipulación en la apertura, distribución hacia el DOL. Los PO3 se dan en cada apertura de vela de 15 minutos: 9:30 (Judas Swing), 9:45, 10:00, 10:15, 10:30. Si uno falla, se **estaquea** y se espera al siguiente, siempre que el contexto siga alineado.

La **vela de las 10:00** es central: es el open de 4 horas y de 1 hora. Para buscar largos quiere un **open low** (manipulación abajo) y cierre alcista; para cortos, un **open high** y cierre bajista. Antes de las 10 puede haber acumulación. No entra entre **9:41 y 9:44**; considera que esos minutos suelen acabar en stop por la manipulación de las 9:45.

### 3.4 Entradas

La versión vigente (agosto de 2026) tiene **dos sistemas de entrada**:

1. **Judas Swing (9:30–9:45):** acumulación premarket, manipulación hacia un gap/PD array de 15m o más, y entrada con el primer **IFVG** o **CISD** tras el desplazamiento. Si el DOL está muy claro, puede entrar con IFVG de 1 minuto sin esperar al de 3.
2. **Open de las 10:00 / PO3 de las 10:00 / open de 4 horas:** liquidity sweep, open high/low, entrada con IFVG o CISD, target en el gap/liquidez opuesta.

**Antecedente documentado (junio de 2026):** durante ese mes enseñó **tres modelos** —Judas, reversal en zona de interés y continuación— y los presentó como "los tres modelos que tengo" [ `1C4dgloDQrY` 10:27, 26:13]. La versión de agosto los reorganiza en dos sistemas; el modelo de continuación no desaparece, queda cubierto por el open de las 10:00. No se borra la versión de junio porque es la única que desarrolla la continuación y la **manipulation leg**.

**Manipulation leg:** tramo entre el último swing high/low formado antes de que el precio llegue a la zona y el extremo de la manipulación. Sirve para elegir qué IFVG se opera —el de la temporalidad más alta dentro de la leg— y dónde va el stop [ `1C4dgloDQrY` 14:40–16:51].

**Pattern trades:** trades que parecen cumplir la estrategia pero que, tras un desplazamiento agresivo previo, no son ideales; el primer IFVG suele ser trampa y lo correcto es esperar gaps de 5m/15m y la continuación [ `1C4dgloDQrY` 27:47–30:50].

**CISD** (change in state of delivery) = cierre de una vela por encima o por debajo del **cuerpo** de una vela anterior. Usa el primer CISD de 1 minuto. Es una confluencia secundaria y opcional: prefiere IFVG + CISD; si no hay IFVG y el DOL/Judas está claro, puede entrar solo con CISD. Espera el cierre de la vela.

### 3.5 Gestión

Stop al otro lado de la manipulación/leg. Objetivo habitual **1:1**; en evaluaciones puede estirar a **1:1,5**. Un trade al día. Break-even solo cuando hay un alto/bajo relevante dentro de un FVG/gap de **5 minutos o más**, o en una **zona de conflicto** (junio de 2026); la versión de mayo decía 3 minutos o más. No mueve el stop en lows/highs random: "¿para qué?" [ `1C4dgloDQrY` 24:08]. Si el precio toca una zona de conflicto, protege. No cierra el trade antes ni después del resultado: deja que haga TP o SL.

**Salida con SMT:** mantiene NQ y ES en pantalla. Si el ES llega a la zona objetivo y el NQ todavía no, y ya hay **1:1**, cierra; si no hay 1:1, pone break-even y deja correr [ `1C4dgloDQrY` 38:07–39:39].

### 3.6 Riesgo

Perfil principiante: **1%** de la cuenta ($500 en 50k), RR 1:1 o 1:1,5, un trade/día, una sesión/día, solo setups A+, seis trades para pasar una evaluación de $3.000. Perfil intermedio: **2%** ($1.000), 1:1,5, prioriza $1.500 de TP, puede pasar o quemar en dos días. Fondeada: cuentas con consistencia a $500 de riesgo; cuentas sin consistencia a $2.000 buscando TP de $3.250 + cuatro días de $150 para max payout de $2.000, siempre protegidas por cuentas con consistencia.

### 3.7 Psicología

Una sola estrategia, una sola persona. No hacer strategy hopping. Todas las estrategias funcionan; lo que falla es la gestión del riesgo y la disciplina. El trading es gambling, pero con la estadística a favor: la diferencia es seguir el plan, no el instrumento. La fase de ruptura inicial es formativa y hay que acortarla, no negarla. Diario de trades, revisar pérdidas, no ser avaricioso, no operar por venganza. Después de una pérdida evitable, desconectar. Un payout no es tuyo hasta que se solicita y se aprueba. Tras una racha ganadora, el ego sube: la muestra de un mes no es significativa, hay que esperar más stops, mantener el riesgo y no replicar cuentas en exceso.

---

## Cómo leer los enlaces

Cada botón «Ver en YouTube» abre el vídeo en el minuto citado. Si una etapa no tiene minuto, el botón dice «Ver clase completa»: no se inventa el segundo cero.
