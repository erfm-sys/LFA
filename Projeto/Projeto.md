# Sistema Especialista para Análise de Crédito Bancário

**Disciplina:** Linguagens Formais e Autômatos (LFA)
**Professora:** Kadidja Valéria
**Área:** Finanças, análise de crédito e concessão de empréstimos
**Linguagem:** Python 3 (biblioteca padrão, sem dependências)
**Inferência:** encadeamento para trás (*backward chaining*, dirigido por objetivo) com poda de hipóteses e escolha dinâmica de perguntas

---

## 1. Escopo do Domínio

| Item | Descrição |
|---|---|
| **Quem consulta** | Analista de crédito ou atendente de agência que faz a triagem inicial de uma proposta de empréstimo pessoal. |
| **Decisão que o sistema apoia** | Qual encaminhamento dar à proposta: aprovar, negar, ofertar limite reduzido, enviar ao gerente ou orientar financeiramente o cliente. |
| **O que fica de fora** | Cálculo do score (é um dado de entrada), taxas de juros e CET, garantias, prazo, modalidades PJ, consignado, prevenção à lavagem de dinheiro e antifraude, e a decisão final de alçada. O sistema é uma **ferramenta didática de triagem** e não substitui a política de crédito de uma instituição. |
| **Natureza do conhecimento** | Regras simplificadas a partir de práticas amplamente conhecidas de análise de crédito. Parâmetros como "corte do score" e "compatibilidade de renda" são definidos pela instituição e aqui entram apenas como respostas do usuário. |

---

## 2. Mudança de Paradigma: de Processar Dados a Inferir e Decidir

Um programa procedural de crédito costuma seguir uma sequência fixa: lê score, restrição e renda, aplica `if/else` encadeados e imprime um resultado. A ordem das perguntas, a lógica de decisão e os dados ficam misturados no mesmo código.

Este sistema inverte essa lógica:

| Aspecto | Programa procedural (processamento de dados) | Este sistema especialista (inferência) |
|---|---|---|
| **Onde está o conhecimento** | Dentro do fluxo de `if/else` | Em dados declarativos (`BaseConhecimento`), separados do controle |
| **Quem decide a ordem das perguntas** | O programador, fixa | O motor, dinamicamente, a partir da memória de trabalho |
| **Perguntas desnecessárias** | Feitas sempre | Evitadas: premissa falsa descarta a regra e as demais premissas não são perguntadas |
| **Dado desconhecido (`?`)** | Costuma virar "não" ou gerar erro | Tratado como terceiro valor: a regra fica **bloqueada** e o sistema não afirma nada sem prova |
| **Conclusões** | Só as programadas, na ordem codificada | **Deduzidas** pelo motor: estado de cada regra (confirmada, refutada, bloqueada, pendente) calculado sobre os fatos conhecidos |
| **Explicação** | Nenhuma | Rastro de justificativa mostra por que cada pergunta foi feita e por que cada regra foi aceita ou descartada |
| **Mudança de regra ou de domínio** | Reescrever o código | Alterar apenas a base de conhecimento; o motor não muda |

### O que o motor deduz sozinho

1. **Estado das regras:** a partir da memória de trabalho, cada regra é classificada em `CONFIRMADA`, `REFUTADA`, `BLOQUEADA` (premissa desconhecida) ou `PENDENTE`, sem perguntar nada.
2. **Poda:** um único fato falso elimina a regra e todas as premissas restantes dela. Se a restrição cadastral é `s`, as regras R1, R3, R4 e R5 são descartadas de uma vez.
3. **Pergunta dirigida:** o motor escolhe o próximo fato a perguntar pelo **maior alcance**, ou seja, o fato que aparece em mais regras ainda vivas (empate: ordem da base). Na primeira pergunta, `possui_restricao_cadastral` aparece nas 5 regras e é sempre perguntado primeiro, o que o torna o fato mais informativo.
4. **Reaproveitamento:** fatos já respondidos ficam na memória e alimentam qualquer hipótese seguinte sem nova pergunta.

---

## 3. Os 3 Fatos Observáveis

Cada fato é respondido com `s`, `n` ou `?`.

| # | Fato | Pergunta feita ao usuário | `s` (sim) | `n` (não) | `?` (não informado) |
|---|---|---|---|---|---|
| F1 | `score_credito_bom` | O score de crédito do cliente é bom (acima do corte da política)? | Score acima do corte | Score abaixo do corte | Score ainda não consultado |
| F2 | `possui_restricao_cadastral` | O cliente possui restrição cadastral (negativação, protesto, cheque sem fundos)? | Há restrição ativa | Nada consta | Consulta não realizada |
| F3 | `renda_compativel` | A renda comprovada é compatível com a parcela solicitada? | Parcela cabe na renda | Parcela não cabe | Renda ainda não comprovada |

**Tratamento da ausência de dados:** `?` não equivale a "não". Um fato desconhecido **bloqueia** as regras que dependem dele: o sistema não confirma nem descarta a decisão e informa que faltam dados, em vez de aprovar ou negar crédito sem base.

---

## 4. Base de Conhecimento: 5 Regras SE-ENTÃO

| Regra | SE (premissas) | ENTÃO (conclusão) | Fonte / justificativa do conhecimento |
|---|---|---|---|
| **R1** | `score_credito_bom = s` **E** `possui_restricao_cadastral = n` **E** `renda_compativel = s` | **Aprovação Imediata do Crédito** | Os 5 Cs do crédito (caráter e capacidade): bom histórico somado à capacidade de pagamento. |
| **R2** | `possui_restricao_cadastral = s` | **Negação Automática** | Política interna de crédito e compliance: restrição ativa impede a concessão, independentemente dos demais fatos. |
| **R3** | `score_credito_bom = s` **E** `possui_restricao_cadastral = n` **E** `renda_compativel = n` | **Oferta de Limite Reduzido** | Gestão de risco (Res. CMN 4.557/2017): bom pagador sem capacidade total recebe exposição menor. |
| **R4** | `score_credito_bom = n` **E** `possui_restricao_cadastral = n` **E** `renda_compativel = s` | **Análise Manual pelo Gerente** | Alçada gerencial: há capacidade de pagamento, mas o histórico exige julgamento humano. |
| **R5** | `score_credito_bom = n` **E** `possui_restricao_cadastral = n` **E** `renda_compativel = n` | **Programa de Reeducação Financeira** | Educação financeira: sem histórico favorável e sem capacidade, prioriza-se orientação antes de crédito. |

**Propriedades da base:** as regras são mutuamente exclusivas e cobrem as 8 combinações de F1, F2 e F3 com respostas conhecidas (R2 cobre as 4 com restrição; R1, R3, R4 e R5 cobrem as 4 sem restrição).

> **Nota sobre as fontes:** 5 Cs do crédito, Resolução CMN nº 4.557/2017 (gerenciamento de riscos) e Resolução CMN nº 2.682/1999 (classificação de risco) são referências conceituais. Valide-as com o material da disciplina antes de citá-las como fonte formal.

---

## 5. Arquitetura

```
┌───────────────────┐   perguntas / respostas   ┌────────────────────┐
│ InterfaceConsole  │◄─────────────────────────►│ MotorInferencia    │
│ (entrada, saída)  │      callback obter_fato  │ (dedução e poda)   │
└───────────────────┘                           └─────┬────────┬─────┘
                                                      │        │
                                      lê regras/fatos │        │ lê/grava fatos
                                                      ▼        ▼
                                           ┌────────────────┐ ┌────────────────┐
                                           │ Base de        │ │ Memória de     │
                                           │ Conhecimento   │ │ Trabalho       │
                                           └────────────────┘ └────────────────┘
```

| Componente | Responsabilidade | O que **não** faz |
|---|---|---|
| `BaseConhecimento` | Declara fatos, decisões e regras como dados. | Não contém lógica de controle. |
| `MemoriaTrabalho` | Guarda respostas (`True`, `False`, `None`) da sessão. | Não decide nada. |
| `MotorInferencia` | Deduz o estado das regras, poda hipóteses, escolhe perguntas e gera o rastro. | Não imprime, não lê do teclado e não conhece regras específicas de crédito. |
| `InterfaceConsole` | Menu, perguntas, validação de entradas e exibição das justificativas. | Não toma decisões. |

---

## 6. Encadeamento para Trás (Goal-Driven)

No modo **1**, o usuário escolhe uma decisão como **hipótese**. O motor busca as regras que a concluem e procede assim:

1. Lê da memória as premissas já conhecidas (sem perguntar de novo).
2. Enquanto a regra estiver `PENDENTE`, escolhe o fato de maior alcance entre as premissas desconhecidas e pergunta.
3. A cada resposta reavalia a regra: **premissa falsa** a descarta (curto-circuito), **premissa desconhecida** a bloqueia, e **todas verdadeiras** a confirmam.
4. Explica, premissa por premissa, o que foi verificado e o que se tornou desnecessário.

### 6.1 Simulação A: hipótese confirmada

**Objetivo:** *Aprovação Imediata do Crédito*. **Respostas do usuário, na ordem em que o motor perguntou:** F2 = `n`, F1 = `s`, F3 = `s`.

| Passo | Ação do motor | Pergunta e resposta | Resultado |
|---|---|---|---|
| 1 | Seleciona R1 (única regra que conclui o objetivo); memória vazia, regra `PENDENTE` | n/a | Três premissas a provar |
| 2 | Escolhe o fato de maior alcance: `possui_restricao_cadastral` (5 regras vivas) | F2, resposta `n` | Premissa 2 verdadeira; R2 passa a refutada |
| 3 | Reavalia: R1 ainda `PENDENTE`; maior alcance entre os restantes: `score_credito_bom` (4 regras vivas) | F1, resposta `s` | Premissa 1 verdadeira; R4 e R5 refutadas |
| 4 | Reavalia: resta `renda_compativel` (2 regras vivas: R1 e R3) | F3, resposta `s` | Premissa 3 verdadeira |
| 5 | Todas as premissas verdadeiras | n/a | **R1 CONFIRMADA; hipótese CONFIRMADA** |

Saída real do sistema:

```text
HIPÓTESE: 'Aprovação Imediata do Crédito'
  Regra R1 concluiria a hipótese; premissas a provar:
    [pergunta] 'possui_restricao_cadastral' (aparece em 5 regra(s) viva(s)) -> resposta: não.
    [pergunta] 'score_credito_bom' (aparece em 4 regra(s) viva(s)) -> resposta: sim.
    [pergunta] 'renda_compativel' (aparece em 2 regra(s) viva(s)) -> resposta: sim.
  Verificação das premissas de R1:
    1. (score_credito_bom = sim): VERDADEIRA.
    2. (possui_restricao_cadastral = não): VERDADEIRA.
    3. (renda_compativel = sim): VERDADEIRA.
    Todas verdadeiras -> R1 CONFIRMADA.
  => Hipótese CONFIRMADA.
CONCLUSÃO: Aprovação Imediata do Crédito -> CONFIRMADA pela regra R1.
Perguntas feitas nesta consulta: 3
```

### 6.2 Simulação B: curto-circuito (premissas desnecessárias não são perguntadas)

**Objetivo:** *Aprovação Imediata do Crédito*. **Resposta:** F2 = `s`.

```text
HIPÓTESE: 'Aprovação Imediata do Crédito'
  Regra R1 concluiria a hipótese; premissas a provar:
    [pergunta] 'possui_restricao_cadastral' (aparece em 5 regra(s) viva(s)) -> resposta: sim.
  Verificação das premissas de R1:
    1. (score_credito_bom = sim): NÃO AVALIADA (desnecessária, regra já decidida).
    2. (possui_restricao_cadastral = não): FALSA (informado: sim) -> regra descartada (curto-circuito).
    3. (renda_compativel = sim): NÃO AVALIADA (desnecessária, regra já decidida).
  => Hipótese REFUTADA.
Perguntas feitas nesta consulta: 1
```

Duas premissas foram descartadas sem custo. O sistema chegou à conclusão com **1 pergunta em vez de 3**.

### 6.3 Simulação C: dedução autônoma (modo 2)

Aqui nenhuma decisão é escolhida pelo usuário. Todas as regras são hipóteses simultâneas, e o motor decide sozinho o que perguntar. **Respostas:** F2 = `n`, F1 = `s`, F3 = `n`.

```text
MODO AUTÔNOMO: todas as decisões são hipóteses; o motor poda regras e escolhe as perguntas.
  Estado: pendentes [R1, R2, R3, R4, R5] | descartadas [nenhuma] | bloqueadas por dado desconhecido [nenhuma]
  [pergunta] 'possui_restricao_cadastral' (aparece em 5 regra(s) viva(s)) -> resposta: não.
  Estado: pendentes [R1, R3, R4, R5] | descartadas [R2] | bloqueadas por dado desconhecido [nenhuma]
  [pergunta] 'score_credito_bom' (aparece em 4 regra(s) viva(s)) -> resposta: sim.
  Estado: pendentes [R1, R3] | descartadas [R2, R4, R5] | bloqueadas por dado desconhecido [nenhuma]
  [pergunta] 'renda_compativel' (aparece em 2 regra(s) viva(s)) -> resposta: não.
  Estado: pendentes [nenhuma] | descartadas [R1, R2, R4, R5] | bloqueadas por dado desconhecido [nenhuma]
  => R3 confirmada: deduz-se 'Oferta de Limite Reduzido'.
CONCLUSÃO: Oferta de Limite Reduzido -> CONFIRMADA pela regra R3.
Perguntas feitas nesta consulta: 3
```

Se a primeira resposta fosse F2 = `s`, o motor descartaria R1, R3, R4 e R5 de uma vez e concluiria **Negação Automática com 1 pergunta**. Se fosse F2 = `?`, as cinco regras ficariam bloqueadas e o sistema responderia que nenhuma decisão pode ser deduzida.

### 6.4 Simulação D: reaproveitamento da memória

Depois da Simulação A (F1 = `s`, F2 = `n`, F3 = `s`), o usuário escolhe provar *Oferta de Limite Reduzido* (R3). O motor lê os três fatos da memória, constata que a premissa `renda_compativel = n` contradiz F3 = `s` e refuta a hipótese com **0 novas perguntas**.

---

## 7. Plano de Testes

Nos testes, "ordem das perguntas" é a escolhida pelo motor: F2, depois F1, depois F3 (modo 1 com regras de três premissas e modo 2 a partir da memória vazia).

| # | Tipo | Modo e hipótese | Entradas (na ordem das perguntas) | Resultado esperado |
|---|---|---|---|---|
| T1 | Confirmação de regra (R1) | 1: Aprovação Imediata | F2=`n`, F1=`s`, F3=`s` | R1 confirmada; 3 perguntas |
| T2 | Confirmação de regra (R3) | 1: Limite Reduzido | F2=`n`, F1=`s`, F3=`n` | R3 confirmada; 3 perguntas |
| T3 | Confirmação de regra (R4) | 1: Análise Manual | F2=`n`, F1=`n`, F3=`s` | R4 confirmada; 3 perguntas |
| T4 | Confirmação de regra (R5) | 1: Reeducação Financeira | F2=`n`, F1=`n`, F3=`n` | R5 confirmada; 3 perguntas |
| T5 | Premissa falsa (curto-circuito) | 1: Aprovação Imediata | F2=`s` | Refutada; 1 pergunta; F1 e F3 "não avaliadas" |
| T6 | Premissa falsa (curto-circuito) | 1: Aprovação Imediata | F2=`n`, F1=`n` | Refutada; 2 perguntas; F3 "não avaliada" |
| T7 | Premissa desconhecida | 1: Aprovação Imediata | F2=`n`, F1=`?` | Indeterminada; 2 perguntas; F3 não perguntada |
| T8 | Premissa desconhecida (restrição) | 1: Aprovação Imediata | F2=`?` | Indeterminada; 1 pergunta |
| T9 | Negação confirmada | 1: Negação Automática | F2=`s` | R2 confirmada; 1 pergunta |
| T10 | Negação (decisão não se aplica) | 1: Negação Automática | F2=`n` | Refutada |
| T11 | Reuso da memória | 1: Aprovação, depois 1: Limite Reduzido | T1; depois escolher Limite Reduzido | Segunda consulta com 0 perguntas; refutada pela premissa 3 |
| T12 | Poda por memória | 2: autônomo (F2=`s`), depois 1: Aprovação | F2=`s`; depois escolher Aprovação | Aprovação refutada com 0 perguntas |
| T13 | Dedução autônoma com confirmação | 2: autônomo | F2=`n`, F1=`s`, F3=`n` | R3 deduzida; 3 perguntas; ordem F2, F1, F3 |
| T14 | Dedução autônoma com poda total | 2: autônomo | F2=`s` | R2 deduzida; 1 pergunta; R1, R3, R4 e R5 descartadas |
| T15 | Dedução autônoma inconclusiva | 2: autônomo | F2=`?` | Nenhuma decisão deduzida; 1 pergunta; 5 regras bloqueadas |
| T16 | Entrada inválida | Qualquer | `talvez`, Enter vazio, depois `s` | Mensagem de erro e a pergunta se repete; nada inválido é gravado |
| T17 | Variações aceitas | Qualquer | `S`, `SIM`, `nao`, `não`, `ND` | Lidas como sim, sim, não, não e desconhecido |
| T18 | Opção de menu inválida | n/a | `9` no menu | "Opção inválida" e o menu volta |
| T19 | Nova consulta | Qualquer | Menu `4` e nova prova | Memória vazia; todas as perguntas refeitas |

---

## 8. Como Executar

```bash
python3 sistema_credito.py
```

Menu:

| Opção | Ação |
|---|---|
| `1` | Escolher uma decisão como hipótese e prová-la (encadeamento para trás) |
| `2` | Deixar o motor deduzir a recomendação, escolhendo ele mesmo as perguntas |
| `3` | Ver a memória de trabalho |
| `4` | Nova consulta (limpa a memória) |
| `0` | Sair |

## 9. Estrutura do Repositório

```text
.
├── sistema_credito.py   # base de conhecimento, memória, motor e interface
└── README.md            # esta documentação
```

## 10. Limitações e Extensões

- Os fatos são binários. Um modelo real usaria faixas (score, comprometimento de renda) e fatores de certeza.
- Cada decisão é concluída por uma única regra. O motor já suporta várias regras por objetivo e tenta cada uma em ordem.
- O alcance é uma heurística simples. Alternativas: ordenar por custo da consulta (por exemplo, consultar o score custa mais que perguntar a renda) ou por probabilidade a priori.
- Extensão natural: encadeamento para frente (*forward chaining*) puro, para comparar as duas estratégias.
