# Sistema Especialista para Análise de Crédito Bancário

**Disciplina:** Inteligência Artificial e Linguagens Formais e Autômatos (IA/LFA)
**Professora:** Kadidja Valéria
**Área:** Finanças, análise de crédito e concessão de empréstimos
**Linguagem:** Python 3 (biblioteca padrão, sem dependências)
**Estratégia de inferência:** encadeamento para trás (*backward chaining*, dirigido por objetivo)

---

## 1. Escopo do Domínio

| Item | Descrição |
|---|---|
| **Quem consulta** | Analista de crédito ou atendente de agência que faz a triagem inicial de uma proposta de empréstimo pessoal. |
| **Decisão que o sistema apoia** | Qual encaminhamento dar à proposta: aprovar, negar, ofertar limite reduzido, enviar ao gerente ou orientar financeiramente o cliente. |
| **O que fica de fora** | Cálculo de score (é um dado de entrada), taxas de juros e CET, garantias e colaterais, prazo, modalidades PJ, consignado, prevenção à lavagem de dinheiro e antifraude, e a decisão final de alçada. O sistema é uma **ferramenta didática de triagem**, não substitui a política de crédito de uma instituição. |
| **Natureza do conhecimento** | Regras simplificadas a partir de práticas amplamente conhecidas de análise de crédito. Parâmetros como "corte do score" e "compatibilidade de renda" são definidos pela instituição e aqui são tratados apenas como respostas do usuário. |

---

## 2. Os 3 Fatos Observáveis

Cada fato é respondido com `s`, `n` ou `?`.

| # | Fato | Pergunta feita ao usuário | `s` (sim) | `n` (não) | `?` (não informado) |
|---|---|---|---|---|---|
| F1 | `score_credito_bom` | O score de crédito do cliente é bom (acima do corte da política)? | Score acima do corte | Score abaixo do corte | Score ainda não consultado |
| F2 | `possui_restricao_cadastral` | O cliente possui restrição cadastral (negativação, protesto, cheque sem fundos)? | Há restrição ativa | Nada consta | Consulta não realizada |
| F3 | `renda_compativel` | A renda comprovada é compatível com a parcela solicitada? | Parcela cabe na renda | Parcela não cabe | Renda ainda não comprovada |

**Tratamento da ausência de dados:** `?` não é tratado como "não". Um fato desconhecido torna a regra **indeterminada**: o sistema não confirma nem descarta a decisão, e informa que faltam dados. Isso evita negar ou aprovar crédito por falta de informação.

---

## 3. Base de Conhecimento: 5 Regras SE-ENTÃO

| Regra | SE (premissas, em ordem de verificação) | ENTÃO (conclusão) | Fonte / justificativa do conhecimento |
|---|---|---|---|
| **R1** | `score_credito_bom = s` **E** `possui_restricao_cadastral = n` **E** `renda_compativel = s` | **Aprovação Imediata do Crédito** | Os 5 Cs do crédito (caráter e capacidade): bom histórico somado à capacidade de pagamento. |
| **R2** | `possui_restricao_cadastral = s` | **Negação Automática** | Política interna de crédito e compliance: restrição ativa impede a concessão, independentemente dos demais fatos. |
| **R3** | `score_credito_bom = s` **E** `possui_restricao_cadastral = n` **E** `renda_compativel = n` | **Oferta de Limite Reduzido** | Gestão de risco (Res. CMN 4.557/2017): bom pagador sem capacidade total recebe exposição menor. |
| **R4** | `score_credito_bom = n` **E** `possui_restricao_cadastral = n` **E** `renda_compativel = s` | **Análise Manual pelo Gerente** | Alçada gerencial: há capacidade de pagamento, mas o histórico exige julgamento humano. |
| **R5** | `score_credito_bom = n` **E** `possui_restricao_cadastral = n` **E** `renda_compativel = n` | **Programa de Reeducação Financeira** | Educação financeira: sem histórico favorável e sem capacidade, prioriza-se orientação antes de crédito. |

**Propriedades da base:** as regras são mutuamente exclusivas e cobrem as 8 combinações de F1, F2 e F3 com respostas conhecidas. R2 cobre as 4 combinações com restrição, e R1, R3, R4 e R5 cobrem as 4 combinações sem restrição.

> **Nota sobre as fontes:** as referências (5 Cs do crédito, Resolução CMN nº 4.557/2017 sobre gerenciamento de riscos, Resolução CMN nº 2.682/1999 sobre classificação de risco) servem de embasamento conceitual. Valide-as com o material da disciplina ou com um especialista antes de citá-las como fonte formal.

---

## 4. Arquitetura

```
┌───────────────────┐   perguntas / respostas   ┌────────────────────┐
│ InterfaceConsole  │◄─────────────────────────►│ MotorInferencia    │
│ (entrada, saída)  │      callback obter_fato  │ (backward chaining)│
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
| `MotorInferencia` | Prova uma hipótese percorrendo as premissas das regras e gera o rastro de justificativa. | Não imprime, não lê do teclado e não conhece regras específicas de crédito. |
| `InterfaceConsole` | Menu, perguntas, validação das entradas e exibição da justificativa. | Não toma decisões. |

Não existe cadeia de `if/else` com a lógica do domínio: as regras são dados e o motor é genérico. Trocar o domínio exige apenas trocar a `BaseConhecimento`.

---

## 5. Encadeamento para Trás (Goal-Driven)

O motor parte de uma **hipótese** (a decisão escolhida) e procura as regras que a concluem. Para cada regra, verifica as premissas em ordem:

1. Se o fato já está na memória de trabalho, reutiliza o valor sem perguntar de novo.
2. Se não está, pergunta ao usuário e registra a resposta.
3. Premissa **verdadeira**: segue para a próxima.
4. Premissa **falsa**: interrompe a regra (curto-circuito), sem perguntar as premissas restantes.
5. Premissa **desconhecida (`?`)**: interrompe a regra e marca a hipótese como indeterminada.
6. Todas verdadeiras: regra confirmada e hipótese confirmada.

### 5.1 Simulação A: hipótese confirmada

**Objetivo:** provar *Aprovação Imediata do Crédito*. **Respostas do usuário:** `s`, `n`, `s`.

| Passo | Ação do motor | Pergunta / resposta | Resultado |
|---|---|---|---|
| 1 | Seleciona R1 como única regra que conclui o objetivo | n/a | Regra candidata |
| 2 | Premissa 1: `score_credito_bom = s`? | Pergunta F1, resposta `s` | Verdadeira |
| 3 | Premissa 2: `possui_restricao_cadastral = n`? | Pergunta F2, resposta `n` | Verdadeira |
| 4 | Premissa 3: `renda_compativel = s`? | Pergunta F3, resposta `s` | Verdadeira |
| 5 | Todas as premissas de R1 verdadeiras | n/a | **Hipótese CONFIRMADA (R1)** |

Saída real do sistema:

```text
HIPÓTESE: 'Aprovação Imediata do Crédito'
  Regra R1 concluiria a hipótese; verificando premissas:
    [pergunta] 'score_credito_bom' -> resposta: sim.
    Premissa 1 (score_credito_bom = sim): VERDADEIRA.
    [pergunta] 'possui_restricao_cadastral' -> resposta: não.
    Premissa 2 (possui_restricao_cadastral = não): VERDADEIRA.
    [pergunta] 'renda_compativel' -> resposta: sim.
    Premissa 3 (renda_compativel = sim): VERDADEIRA.
    Todas as premissas de R1 verdadeiras -> regra CONFIRMADA.
  => Hipótese CONFIRMADA.
CONCLUSÃO: Aprovação Imediata do Crédito -> CONFIRMADA pela regra R1.
Perguntas feitas nesta consulta: 3
```

### 5.2 Simulação B: curto-circuito (premissa desnecessária não é perguntada)

**Objetivo:** *Aprovação Imediata do Crédito*. **Resposta do usuário:** `n` ao score.

| Passo | Ação do motor | Resultado |
|---|---|---|
| 1 | Seleciona R1 | Regra candidata |
| 2 | Pergunta F1 e recebe `n` | Premissa 1 **falsa** |
| 3 | Interrompe R1; F2 e F3 **não são perguntados** | Hipótese **REFUTADA** com 1 pergunta |

### 5.3 Simulação C: reaproveitamento da memória

Após a Simulação A, o usuário escolhe provar *Oferta de Limite Reduzido* (R3). F1 (`s`) e F2 (`n`) são lidos da memória, e F3 (`s`) contradiz a premissa 3 (`renda_compativel = n`). A hipótese é refutada com **0 novas perguntas**.

---

## 6. Plano de Testes

| # | Objetivo do teste | Hipótese | Entradas (na ordem das perguntas) | Resultado esperado |
|---|---|---|---|---|
| T1 | Confirmação de regra (R1) | Aprovação Imediata | F1=`s`, F2=`n`, F3=`s` | Confirmada por R1; 3 perguntas |
| T2 | Confirmação de regra (R3) | Limite Reduzido | F1=`s`, F2=`n`, F3=`n` | Confirmada por R3; 3 perguntas |
| T3 | Confirmação de regra (R4) | Análise Manual | F1=`n`, F2=`n`, F3=`s` | Confirmada por R4; 3 perguntas |
| T4 | Confirmação de regra (R5) | Reeducação Financeira | F1=`n`, F2=`n`, F3=`n` | Confirmada por R5; 3 perguntas |
| T5 | Premissa falsa (curto-circuito) | Aprovação Imediata | F1=`n` | Refutada; apenas 1 pergunta; F2 e F3 não perguntados |
| T6 | Premissa desconhecida | Aprovação Imediata | F1=`s`, F2=`?` | Indeterminada; 2 perguntas; F3 não perguntado |
| T7 | Negação (restrição presente) | Negação Automática | F2=`s` | Confirmada por R2; 1 pergunta |
| T8 | Negação (restrição ausente) | Negação Automática | F2=`n` | Refutada (a decisão não se aplica) |
| T9 | Restrição vence os demais fatos | Negação Automática, depois Aprovação Imediata (mesma memória) | F2=`s`; depois a Aprovação pergunta F1=`s` e encontra F2=`s` | Negação confirmada; Aprovação refutada na premissa 2 |
| T10 | Reuso de memória | Aprovação Imediata e depois Limite Reduzido | T1 seguido de nova prova de R3 | Segunda consulta com 0 perguntas; refutada pela premissa 3 |
| T11 | Entrada inválida | Qualquer | Digitar `talvez` ou Enter vazio, e depois `s` | Mensagem de erro e a pergunta se repete; nenhuma resposta inválida é gravada |
| T12 | Variações aceitas de entrada | Qualquer | `S`, `SIM`, `nao`, `não`, `ND` | Interpretadas como sim, sim, não, não e desconhecido |
| T13 | Opção de menu inválida | n/a | `9` no menu | Mensagem "Opção inválida" e o menu é exibido de novo |
| T14 | Nova consulta | Qualquer | Menu `4` (limpar) e nova prova | Memória vazia e todas as perguntas refeitas |

---

## 7. Como Executar

```bash
python3 sistema_credito.py
```

Fluxo sugerido: escolha `1` no menu, selecione uma decisão como hipótese e responda às perguntas com `s`, `n` ou `?`. A opção `2` testa as decisões em sequência até achar a aplicável, e a `3` mostra a memória de trabalho.

## 8. Estrutura do Repositório

```text
.
├── sistema_credito.py   # base de conhecimento, memória, motor e interface
└── README.md            # esta documentação
```

## 9. Limitações e Extensões Possíveis

- Os fatos são binários. Um modelo real usaria faixas (score, comprometimento de renda) e fatores de certeza.
- Cada decisão é concluída por uma única regra. A engenharia suporta várias regras por objetivo, e o motor tenta cada uma em ordem.
- Extensão natural: encadeamento para frente (*forward chaining*) a partir dos fatos, para comparar as duas estratégias.
