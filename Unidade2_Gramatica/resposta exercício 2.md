# Exercícios Unidade 2 / Gramáticas

## 1) Alfabeto
1. No alfabeto existem 3 símbolos;
2. Os símbolos são a, b e c;
3. Sim, pois $a \in \Sigma$;
4. Não, pois o $d$ não faz parte de $\Sigma$;
5. $abc$ (ou qualquer outra variação como: $a$, $ab$, $cb$, $ac$, $bca$, $cba$...).

---

## 2) Palavras sobre um alfabeto

| Sequência | Válida? | Justificativa |
| :--- | :--- | :--- |
| **0101** | Sim | Possui apenas elementos presentes no alfabeto |
| **00110** | Sim | Possui apenas elementos presentes no alfabeto |
| **012** | Não | O 2 não faz parte do alfabeto |
| **111** | Sim | Possui apenas elementos presentes no alfabeto |
| **10a** | Não | O símbolo *a* não faz parte do alfabeto mencionado na questão |

---

## 3) Pertinência de símbolos e palavras
1. **Verdadeiro** — O 0 faz parte do alfabeto;
2. **Verdadeiro** — O 1 faz parte do alfabeto;
3. **Falso** — 01 é uma palavra de comprimento 2;
4. **Verdadeiro** — O $\Sigma^*$ representa o conjunto de todas as palavras possíveis;
5. **Falso** — O 2 não faz parte do alfabeto mencionado.

---

## 4) Linguagem
1. Pertence
2. Pertence
3. Pertence
4. Não pertence
5. Não pertence
6. Pertence

---

## 5) Descrevendo uma linguagem por padrão
1. $b, bb, bbb, bbbb, bbbbb$;
2. Representa a quantidade de repetição do símbolo $b$ multiplicado $n$ vezes com ele mesmo;
3. **Sim**, pois a palavra possui seis repetições de $b$ ($b^6$), o que satisfaz a condição $n = 6 \ge 1$;
4. **Não**, pois a palavra vazia corresponderia a $n = 0$ ($b^0 = \epsilon$), mas a definição restringe para $n \ge 1$.

---

## 6) Linguagem vazia e palavra vazia
* **Diferença:** A linguagem $L = \emptyset$ é a linguagem vazia, um conjunto que não possui nenhuma palavra. Já a linguagem $L = \{\epsilon\}$ é um conjunto que contém exatamente uma palavra (a palavra vazia).
* **Respostas:**
  1. **B** ($L = \{\epsilon\}$);
  2. **A** ($L = \emptyset$);
  3. **0** (o comprimento da palavra vazia é zero).

---

## 7) Estrutura de uma gramática
1. **Conjunto de variáveis:** $V = \{S, A\}$
2. **Conjunto de terminais:** $\Sigma = \{0, 1\}$;
3. **Conjunto de produções:** $P = \{S \to 0A, A \to 1\}$;
4. **Símbolo inicial:** $S$;
5. **Palavra gerada:** $01$.

---

## 8) Como ler e aplicar uma produção
1. $0S$ (depois de aplicar $S \to 0S$)
2. $00S$ (após aplicar novamente $S \to 0S$)
3. $000S$
4. **Sequência completa de derivação:** $S \to 0S \to 00S \to 000S$

---

## 9) Derivação completa de uma palavra
**Passos da derivação para gerar aaab:**
1. $S \to aS$
2. $aS \to aaS$
3. $aaS \to aaaS$
4. $aaaS \to aaab$

---

## 10) Identificando palavras geradas por uma gramática
1. Pode ser gerada;
2. Pode ser gerada;
3. Pode ser gerada;
4. Pode ser gerada;
5. Não pode ser gerada;
6. Não pode ser gerada.
