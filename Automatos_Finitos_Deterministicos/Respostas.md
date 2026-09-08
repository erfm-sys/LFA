# Autômatos Finitos Determinísticos (AFD)

---
## Identificação do grupo

| Campo | Preenchimento |
|---|---|
| Turma | N1 |
| Data | 08/09/2026 |
| Integrante 1 |João Pedro Figueiredo Ajouz|
| Integrante 2 |Luis Fernando Vieira Borges |
| Integrante 3 | João Victor Santos de Oliveira Vieira |
| Integrante 4 |Enzo |

---

## Questão 1
* **Estados:** Existem dois estados, sendo eles `Ligado` e `Desligado`.
* **Estado inicial:** Quando a lâmpada inicia apagada, o estado é `Desligado`.
* **Entrada:** `pressionar`.
* **Comportamento após acionamentos:**
  * Após **1 acionamento** partindo de `Desligado`, o estado será `Ligado`.
  * Após **2 acionamentos** partindo de `Desligado`, o estado será `Desligado` novamente.
* **Funcionamento:** O sistema funciona de forma manual. Se o usuário pressionar o disjuntor e a lâmpada estiver acesa, o estado dela passa a ser `Desligado` e vice-versa.

---

## Questão 2

### Tabela de Transição

| Estado atual | Entrada | Próximo estado |
| :--- | :--- | :--- |
| **Fechado** | `pessoa_detectada` | Aberto |
| **Fechado** | `nenhuma_pessoa` | Fechado |
| **Aberto** | `pessoa_detectada` | Aberto |
| **Aberto** | `nenhuma_pessoa` | Fechado |

### Transições
* $\text{Fechado} \xrightarrow{\text{pessoa\_detectada}} \text{Aberto}$
* $\text{Fechado} \xrightarrow{\text{nenhuma\_pessoa}} \text{Fechado}$
* $\text{Aberto} \xrightarrow{\text{pessoa\_detectada}} \text{Aberto}$
* $\text{Aberto} \xrightarrow{\text{nenhuma\_pessoa}} \text{Fechado}$

---

## Questão 3
* **Alfabeto ($\Sigma$):** Representa os símbolos de entrada que o autômato pode processar.
* **Conjunto dos estados ($Q$):** Representa todos os estados possíveis dos autômatos.
* **Estado inicial ($q_0$):** É o estado $q_0$, de onde o processamento da cadeia de caracteres sempre se inicia.
* **Conjunto de estados finais ($F$):** É o conjunto que contém $q_1$. Se a cadeia terminar de ser lida e o autômato estiver neste estado, ela é aceita.
* **Símbolos que podem ser lidos:** Os símbolos $0$ e $1$, que pertencem ao alfabeto $\Sigma$.
* **Significado do círculo duplo no diagrama:** Indica que o estado é um **estado de aceitação** (final).
* **Significado da seta sem origem:** Indica qual é o **estado inicial** do autômato.

---

## Questão 4

| Elemento | Significado |
| :---: | :--- |
| **$\Sigma$** | Alfabeto de entrada. Conjunto finito de símbolos que podem ser lidos. |
| **$Q$** | Conjunto finito de estados do autômato. |
| **$\delta$** | Função de transição. Define para qual estado o autômato vai, dado o estado atual e o símbolo lido ($\delta: Q \times \Sigma \to Q$). |
| **$q_0$** | Estado inicial. O estado em que o autômato começa a computação ($q_0 \in Q$). |
| **$F$** | Conjunto de estados de aceitação ou estados finais ($F \subseteq Q$). |

> **Explicação:** Esses elementos descrevem tudo o que o sistema precisa para funcionar: qual a memória disponível ($Q$), como o sistema começa ($q_0$), quais eventos externos ele compreende ($\Sigma$), as regras exatas de como ele reage a cada evento ($\delta$) e qual a condição de sucesso/aceitação ($F$).

---

## Questão 5
* $\delta(q_0, 0) = q_0$
* $\delta(q_0, 1) = q_1$
* $\delta(q_1, 0) = q_2$
* $\delta(q_2, 1) = q_1$
* **Estado de aceitação:** $q_1$ (pois $F = \{q_1\}$)

---

## Questão 6

1. **Cadeia: `1`**
   * **Caminho:** $q_0 \xrightarrow{1} q_1$
   * **Estado final:** $q_1$
   * **Resultado:** **ACEITA**

2. **Cadeia: `0011001`**
   * **Caminho:** $q_0 \xrightarrow{0} q_0 \xrightarrow{0} q_0 \xrightarrow{1} q_1 \xrightarrow{1} q_1 \xrightarrow{0} q_2 \xrightarrow{0} q_1 \xrightarrow{1} q_1$
   * **Estado final:** $q_1$
   * **Resultado:** **ACEITA**

3. **Cadeia: `010010`**
   * **Caminho:** $q_0 \xrightarrow{0} q_0 \xrightarrow{1} q_1 \xrightarrow{0} q_2 \xrightarrow{0} q_1 \xrightarrow{1} q_1 \xrightarrow{0} q_2$
   * **Estado final:** $q_2$
   * **Resultado:** **REJEITA**

4. **Cadeia: `1101`**
   * **Caminho:** $q_0 \xrightarrow{1} q_1 \xrightarrow{1} q_1 \xrightarrow{0} q_2 \xrightarrow{1} q_1$
   * **Estado final:** $q_1$
   * **Resultado:** **ACEITA**

---

## Questão 7
* **Alfabeto:** $\Sigma = \{0, 1\}$
* **Estados:** $Q = \{q_0, q_1\}$
* **Estado inicial:** $q_0$
* **Estados finais:** $F = \{q_1\}$

### Tabela de Transição

| Estado | 0 | 1 |
| :--- | :---: | :---: |
| $\to q_0$ | $q_0$ | $q_1$ |
| $* q_1$ | $q_0$ | $q_1$ |

---

## Questão 8
* **Quíntupla:** $M = (\{q_{\text{par}}, q_{\text{ímpar}}\}, \{0, 1\}, \delta, q_{\text{par}}, \{q_{\text{par}}\})$
* **Estado inicial:** $q_{\text{par}}$ (representa ter visto 0 uns, que é par).

### Tabela de Transição

| Estado | 0 | 1 |
| :--- | :---: | :---: |
| $\to * q_{\text{par}}$ | $q_{\text{par}}$ | $q_{\text{ímpar}}$ |
| $q_{\text{ímpar}}$ | $q_{\text{ímpar}}$ | $q_{\text{par}}$ |

### Processamento de Cadeias
* $\epsilon$ (vazia): Fica em $q_{\text{par}}$ $\to$ **Aceita**
* `1`: $q_{\text{par}} \xrightarrow{1} q_{\text{ímpar}}$ $\to$ **Rejeita**
* `11`: $q_{\text{par}} \xrightarrow{1} q_{\text{ímpar}} \xrightarrow{1} q_{\text{par}}$ $\to$ **Aceita**
* `101`: $q_{\text{par}} \xrightarrow{1} q_{\text{ímpar}} \xrightarrow{0} q_{\text{ímpar}} \xrightarrow{1} q_{\text{par}}$ $\to$ **Aceita**

---

## Questão 9
1. Representa que ainda não vimos nenhum 0 consecutivo na expressão.
2. O autômato vai para um estado intermediário, registrando que um `'0'` foi visto.
3. O autômato vai para o estado final/de aceitação.
4. **Não**, o estado final será um **estado absorvente** (poço/terminal), ou seja, qualquer símbolo lido o manterá lá.
5. **3 estados**.

---

## Questão 10
* **Definição formal:** $M = (\{\text{Verde}, \text{Amarelo}, \text{Vermelho}\}, \{\text{tempo}\}, \delta, \text{Verde}, \emptyset)$
* **Entrada:** `tempo`
* **Explicação:** O sistema muda linearmente com a entrada `tempo`. Não há propriamente uma "aceitação" (estado final, $F = \emptyset$), pois trata-se de um laço infinito de controle reativo.
