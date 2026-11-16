---
tipo: "regla"
titulo: "Equilibrium: comprar en descuento, vender en premium"
title: "Equilibrium: comprar en descuento, vender en premium"
confianza: "explícito"
estado: "vigente"
video: "56ES-W1d0xw"
timestamp: "06:22"
id: 163
version: 2
---

> **Confianza:** explícito · **Estado:** vigente · **Versión:** 2
- **Clase del bootcamp:** [[../bootcamp/dia-19|Día 19 — Equilibrium (premium y discount)]]

## Descripción

La zona operativa depende de la dirección: en compras se busca la mitad inferior (descuento); en ventas, la mitad superior (premium). Premium está siempre arriba y descuento siempre abajo.

## Contexto

Filtro de zona.

## Condiciones

Equilibrium dibujado con retroceso de Fibonacci; precio en la zona gris (descuento para compras, premium para ventas).

## Confirmaciones

FVG alineado con la línea 0.5 + reacción + IFVG.

## Condiciones de entrada

Entrada tras la reacción y el IFVG, no antes.

## Invalidación

Si el precio está en la zona contraria, no hay trade.

## Gestión de riesgo

No aplica.

## Objetivos

BSL/SSL.

## Excepciones

La versión antigua llamaba 'descuento' a la mitad superior en cortos; la zona era la misma. Se conserva como histórica.

## Notas

Día 19 [06:22–06:52]. Sustituye en la práctica a 'Equilibrium: no comprar ni vender en premium', que queda obsoleta.

## Conceptos relacionados

- [[equilibrium-premium-descuento|Equilibrium (premium/descuento)]]
- [[liquidez-bsl-ssl|Liquidez (BSL/SSL)]]
- [[fair-value-gap-fvg|Fair Value Gap (FVG)]]
- [[inverse-fair-value-gap-ifvg|Inverse Fair Value Gap (IFVG)]]

## Reemplaza a

- [[equilibrium-no-comprar-ni-vender-en-premium|Equilibrium: no comprar ni vender en premium]]

## Evidencia

- «La mayoría de las veces vas a intentar no vender estando en la zona de descuento.» — `56ES-W1d0xw` @ 02:41 (explícito)
- «Cuando buscamos compras, buscamos siempre la zona de descuento... y cuando buscamos ventas, buscamos siempre la zona premium.» — `56ES-W1d0xw` @ 06:22 (explícito)

