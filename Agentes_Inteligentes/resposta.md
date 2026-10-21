# Atividade sobre agentes inteligentes

Aula 20/10/2026 | Professora Kadidja Valéria | Inteligência artificial

**Disciplina:** Linguagens Formais e Autômatos | ciência da Computação

**Estudante:** [João Pedro Figueiredo Ajouz] | **Turma:** [N1]

Realize os exercícios 2.3, 2.4 e 2.5 do Capítulo 2 sobre agentes inteligentes. Analise a racionalidade, descreva ambientes de tarefa por meio do modelo PEAS e explique os conceitos com suas próprias palavras. Utilize o capítulo disponibilizado e justifique suas respostas.

**Modalidade sugerida:** individual com consulta. **Tempo estimado:** 2h30. **Prazo:** conforme orientação da professora.

## Preparação
Leia os tópicos sobre racionalidade, ambientes e estrutura dos agentes, especialmente a Seção 2.3.2.

## Exercício 2.3
Para cada afirmação, indique V ou F, justifique e forneça exemplo ou contraexemplo. Explicite as hipóteses utilizadas.

### a. Um agente que detecta apenas informações parciais sobre o estado não pode ser perfeitamente racional.

- Julgamento: Falso
- Justificativa: A racionalidade depende das percepções recebidas, do conhecimento prévio e das ações possíveis. Ser racional significa tomar a melhor decisão possível dada a informação disponível, e não ter omnisciência (conhecimento absoluto do estado real do mundo).
- Exemplo ou contraexemplo: Um robô aspirador de pó num ambiente parcialmente observável que limpa perfeitamente a divisão onde se encontra, maximizando o seu desempenho esperado sem saber o estado exato das outras divisões da casa.

### b. Existem ambientes de tarefa nos quais nenhum agente reativo puro pode comportar-se racionalmente.

- Julgamento: Verdadeiro
- Justificativa: Ambientes parcialmente observáveis com dependências sequenciais requerem memória (estado interno) sobre o passado. Um agente reativo puro apenas considera a percepção atual, podendo ficar preso em laços infinitos sem tomar a decisão correta.
- Exemplo ou contraexemplo: Navegar num labirinto com divisões idênticas parcialmente observáveis; sem memória, um agente reativo puro pode repetir a mesma ação perpetuamente sem alcançar a saída.

### c. Existe um ambiente de tarefa em que todo agente é racional.

- Julgamento: Verdadeiro
- Justificativa: Se o conjunto de ações possíveis for unitário (apenas uma ação disponível) ou se todas as ações resultarem na pontuação máxima de desempenho, qualquer agente será considerado racional.
- Exemplo ou contraexemplo: Um ambiente em que a única ação permitida ao agente é "NADA" e a medida de desempenho recompensa unicamente a permanência no estado.

### d. A entrada para o programa de agente é a mesma que a entrada para a função de agente.

- Julgamento: Falso
- Justificativa: A função de agente recebe como entrada todo o histórico completo de percepções desde o início ($P^*$). O programa de agente recebe apenas a percepção atual no instante $t$, gerindo internamente a sua própria memória ou estado interno.
- Exemplo ou contraexemplo: Num carro autónomo, a função de agente mapeia abstratamente todas as sequências de imagens passadas; o programa de agente recebe o frame atual da câmara e atualiza o seu modelo interno.

### e. Toda função de agente é implementável por uma combinação de programa/máquina.

- Julgamento: Falso
- Justificativa: O espaço de sequências de percepção pode ser infinito ou computacionalmente intratável (problemas indecidíveis ou de complexidade impraticável), além da limitação física de memória e tempo das máquinas reais.
- Exemplo ou contraexemplo: Uma função de agente que requeira a resolução do Problema da Paragem (Halting Problem) ou que exija um mapeamento em tabela inviável de $2^{1000}$ estados.

### f. Suponha que um agente selecione sua ação uniformemente ao acaso do conjunto de ações possíveis. Existe um ambiente de tarefa determinista em que esse agente é racional.

- Julgamento: Verdadeiro
- Justificativa: Se todas as ações possíveis no ambiente levarem exatamente ao mesmo resultado ideal segundo a medida de desempenho, escolher qualquer ação ao acaso garante o desempenho ótimo.
- Exemplo ou contraexemplo: Um ambiente no qual o agente precisa apenas pressionar qualquer um dos botões disponíveis para desativar um alarme, e todos os botões desempenham essa função com idêntico sucesso.

### g. É possível para um dado agente ser perfeitamente racional em dois ambientes de tarefa distintos.

- Julgamento: Verdadeiro
- Justificativa: Se a estratégia de ações do agente maximizar a medida de desempenho esperada em ambos os cenários, ele é racional em ambos os ambientes.
- Exemplo ou contraexemplo: Um robô aspirador simples que limpa uma sala limpa e uma sala muito suja usando a mesma regra racional ("se detetar poeira, limpe; senão, mova-se").

### h. Todo agente é racional em um ambiente não observável.

- Julgamento: Falso
- Justificativa: Em ambientes não observáveis, o agente não recebe percepções dos sensores, mas ainda deve usar o seu conhecimento prévio para executar a sequência de ações com maior probabilidade de sucesso. Executar ações aleatórias ou ineficientes continua a ser irracional.
- Exemplo ou contraexemplo: Um agente num quarto escuro (sem luz ou sensores) que precisa sair: andar em linha reta em direção à porta (sabendo a planta do quarto) é racional; girar em círculos indefinidamente é irracional.

### i. Um agente jogador de pôquer perfeitamente racional nunca perde.

- Julgamento: Falso
- Justificativa: O pôquer é um jogo de informação imperfeita com elementos estocásticos (distribuição aleatória das cartas). A racionalidade maximiza a expectativa de ganho a longo prazo, mas não garante o sucesso em todos os episódios individuais.
- Exemplo ou contraexemplo: O agente faz a aposta matematicamente ideal com base nas probabilidades, mas o oponente vence a mão com uma carta altamente improvável no *river*.

## Exercício 2.4
Para cada caso, delimite o agente, preencha o PEAS e justifique todas as classificações. Considere Titã como cenário hipotético do exercício.

### Caso 1 — Jogar futebol.

- Agente analisado: Jogador individual
- Objetivo e hipóteses: Maximizar os golos da equipa e vencer a partida respeitando as regras do futebol.
- P — Medida de desempenho: Golos marcados, passes certos, desarmes bem-sucedidos, vitória da equipa.
- E — Ambiente: Campo de futebol, bola, colegas de equipa, adversários, condições do relvado e arbitragem.
- A — Atuadores: Pernas/pés (chutar, correr, passar), corpo (cabecear), voz (comunicação).
- S — Sensores: Visão (olhos/câmaras para localizar a bola e jogadores), audição (apito do árbitro, comunicação dos colegas).

| Propriedade | Classificação | Justificativa |
|---|---|---|
| Observabilidade | Parcialmente observável | O jogador não consegue visualizar todo o campo a 360° simultaneamente. |
| Número de agentes | Multiagente (Cooperativo e Competitivo) | Coopera com os colegas de equipa e compete contra os adversários. |
| Previsibilidade | Estocástico | O movimento da bola e o comportamento dos outros jogadores têm componentes imprevisíveis. |
| Dependência entre decisões | Sequencial | Cada decisão e movimento afeta o posicionamento e as opções de jogadas futuras. |
| Mudança durante a decisão | Dinâmico | O jogo continua em tempo real enquanto o agente toma decisões. |
| Natureza dos elementos | Contínuo | Posição, velocidade, trajetória e tempo variam de forma contínua. |
| Conhecimento do funcionamento | Conhecido | As regras formais e a física básica do futebol são conhecidas pelo agente. |

### Caso 2 — Explorar os oceanos subterrâneos de Titã.

- Agente analisado: Sonda/Submarino autónomo de exploração
- Objetivo e hipóteses: Mapear o oceano subterrâneo, recolher amostras e transmitir dados científicos com segurança.
- P — Medida de desempenho: Área mapeada, volume e relevância das amostras recolhidas, integridade física preservada, dados transmitidos.
- E — Ambiente: Oceano subterrâneo de Titã (líquidos criogênicos, escuridão, correntes submarinas, pressão elevada, relevo desconhecido).
- A — Atuadores: Propulsores, braço robótico, broca de recolha, antenas de comunicação.
- S — Sensores: Sonar, sensores de temperatura e pressão, analisador químico de líquidos, giroscópio.

| Propriedade | Classificação | Justificativa |
|---|---|---|
| Observabilidade | Parcialmente observável | A visibilidade no meio aquático subterrâneo é limitada pelo alcance dos sensores. |
| Número de agentes | Agente único | Opera isoladamente no oceano subterrâneo de Titã. |
| Previsibilidade | Estocástico | A presença de correntes fluidas imprevistas e obstáculos desconhecidos introduz incerteza. |
| Dependência entre decisões | Sequencial | A navegação e recolha de amostras num ponto afetam a energia e posição para as etapas seguintes. |
| Mudança durante a decisão | Dinâmico | As correntes marítimas e as condições do meio alteram-se enquanto a sonda processa dados. |
| Natureza dos elementos | Contínuo | Pressão, profundidade, temperatura e movimentação no espaço 3D variam continuamente. |
| Conhecimento do funcionamento | Desconhecido | O ambiente extraterrestre possui propriedades físicas e químicas que o agente precisa de descobrir *in situ*. |

### Caso 3 — Comprar livros usados de IA na Internet.

- Agente analisado: Bot comprador de livros
- Objetivo e hipóteses: Encontrar e adquirir exemplares de livros de IA pelo menor preço total e com bom estado de conservação.
- P — Medida de desempenho: Menor preço pago, boa avaliação do estado do livro, reputação do vendedor, menor tempo de entrega.
- E — Ambiente: Websites de e-commerce, plataformas de alfarrabistas, APIs de lojas online.
- A — Atuadores: Requisições HTTP, preenchimento de formulários de compra, envio de confirmações.
- S — Sensores: Leitura de código HTML/JSON das páginas, consulta de preços, taxas de envio e qualificações de vendedores.

| Propriedade | Classificação | Justificativa |
|---|---|---|
| Observabilidade | Parcialmente observável | O agente não consegue inspecionar fisicamente o livro antes da compra, dependendo de descrições e fotos. |
| Número de agentes | Multiagente (Competitivo) | Outros compradores na internet competem pelas mesmas ofertas de livros usados. |
| Previsibilidade | Estocástico | Vendedores podem atualizar preços, esgotar stock ou cancelar anúncios inesperadamente. |
| Dependência entre decisões | Sequencial | Uma compra efetuada consome o orçamento disponível para transações futuras. |
| Mudança durante a decisão | Semidinâmico | Os preços e a disponibilidade na rede podem mudar com o tempo, mas o ambiente não se altera durante a computação interna se a página não for atualizada. |
| Natureza dos elementos | Discreto | Preços, número de livros, páginas e estados de formulários são valores discretos. |
| Conhecimento do funcionamento | Conhecido | As regras de navegação na web e os mecanismos de e-commerce são conhecidos pelo programa. |

### Caso 4 — Jogar uma partida de tênis.

- Agente analisado: Jogador de tênis
- Objetivo e hipóteses: Maximizar os pontos ganhos para vencer sets e a partida contra um oponente.
- P — Medida de desempenho: Número de pontos ganhos, jogos/sets vencidos, taxa de acerto de serviços.
- E — Ambiente: Campo de tênis, rede, bola, adversário, vento, piso do campo.
- A — Atuadores: Braços/mãos (movimento da raqueta), pernas (deslocamento no campo), corpo.
- S — Sensores: Visão (acompanhamento da bola e do adversário), audição (som do impacto na raqueta).

| Propriedade | Classificação | Justificativa |
|---|---|---|
| Observabilidade | Completamente observável | O jogador consegue visualizar todo o campo, a bola e a posição do adversário a qualquer momento. |
| Número de agentes | Multiagente (Competitivo) | Enfrenta um oponente direto cujos objetivos são estritamente opostos aos seus. |
| Previsibilidade | Estocástico | Rajadas de vento, deformaçoes da bola e ressaltos imprevisíveis no piso introduzem estocasticidade. |
| Dependência entre decisões | Sequencial | A devolução de uma bola condiciona a posição e o tipo de resposta disponível no ponto seguinte. |
| Mudança durante a decisão | Dinâmico | A bola move-se continuamente pelo ar enquanto o jogador decide o movimento a realizar. |
| Natureza dos elementos | Contínuo | A posição, velocidade da bola e trajetória corporal variam no espaço-tempo contínuo. |
| Conhecimento do funcionamento | Conhecido | As regras do tênis e a física do movimento são conhecidas pelo agente. |

### Caso 5 — Praticar tênis contra uma parede.

- Agente analisado: Jogador em treino
- Objetivo e hipóteses: Manter a troca de bolas com a parede com precisão e controlo para aprimorar a técnica.
- P — Medida de desempenho: Número de batidas consecutivas, precisão do local de impacto na parede, ritmo mantido.
- E — Ambiente: Parede rígida, solo, bola de tênis, vento.
- A — Atuadores: Movimentos corporais e batida com a raqueta.
- S — Sensores: Visão e audição.

| Propriedade | Classificação | Justificativa |
|---|---|---|
| Observabilidade | Completamente observável | O jogador observa todo o espaço de treino e a trajetória da bola. |
| Número de agentes | Agente único | A parede é apenas um objeto físico passivo que reage de forma mecânica, sem intenções estratégicas. |
| Previsibilidade | Determinístico | Assumindo ausência de vento forte, o ressalto na parede obedece estritamente às leis da física elástica. |
| Dependência entre decisões | Sequencial | A força e a direção da batida atual determinam como a bola regressará na jogada seguinte. |
| Mudança durante a decisão | Dinâmico | A bola continua a mover-se enquanto o praticante prepara o golpe. |
| Natureza dos elementos | Contínuo | Parâmetros de trajetória, velocidade e força são contínuos. |
| Conhecimento do funcionamento | Conhecido | As regras do exercício e a resposta da parede são previsíveis e conhecidas. |

### Caso 6 — Realizar um salto de altura.

- Agente analisado: Atleta de salto em altura
- Objetivo e hipóteses: Ultrapassar a fasquia sem a derrubar, atingindo a maior altura possível.
- P — Medida de desempenho: Sucesso em ultrapassar a altura da fasquia sem a derrubar, altura máxima registada.
- E — Ambiente: Pista de corrida, fasquia, suportes, colchão de queda, vento.
- A — Atuadores: Músculos das pernas (corrida e impulso), flexão do tronco e membros.
- S — Sensores: Visão (distância até à fasquia e orientação), propriocepção (noção do próprio corpo e equilíbrio).

| Propriedade | Classificação | Justificativa |
|---|---|---|
| Observabilidade | Completamente observável | A pista, a altura da fasquia e o colchão estão totalmente visíveis ao atleta. |
| Número de agentes | Agente único | A tentativa de salto é executada individualmente sem interferência direta de outros agentes durante o salto. |
| Previsibilidade | Determinístico | O resultado depende estritamente da mecânica corporal e do impulso aplicado na corrida e salto. |
| Dependência entre decisões | Episódico | Cada tentativa de salto é um episódio isolado; o desempenho num salto não altera a física do próximo salto. |
| Mudança durante a decisão | Dinâmico | O corpo está em movimento acelerado durante a corrida e a fase de voo. |
| Natureza dos elementos | Contínuo | Altura, velocidade, ângulo de impulso e rotação corporal são magnitudes contínuas. |
| Conhecimento do funcionamento | Conhecido | A mecânica do salto e os critérios de validação são conhecidos do atleta. |

### Caso 7 — Participar de um leilão de um item, realizando lances.

- Agente analisado: Bot/Licitador de leilão
- Objetivo e hipóteses: Arrematar o item desejado pelo menor valor possível, sem ultrapassar o limite financeiro estipulado.
- P — Medida de desempenho: Obtenção do item por um valor inferior à avaliação máxima, economia realizada em relação ao orçamento.
- E — Ambiente: Plataforma de leilão online ou presencial, leiloeiro, licitantes concorrentes.
- A — Atuadores: Submissão de lance (envio de sinal digital ou levantamento de placa).
- S — Sensores: Leitura do lance atual, tempo restante de contagem, estado do leilão.

| Propriedade | Classificação | Justificativa |
|---|---|---|
| Observabilidade | Parcialmente observável | O agente desconhece o limite financeiro máximo e a estratégia exata dos outros licitantes. |
| Número de agentes | Multiagente (Competitivo) | Disputa a aquisição do item com outros licitantes cujo objetivo também é vencer. |
| Previsibilidade | Estocástico | Os comportamentos, tempos de resposta e valores oferecidos pelos adversários são incertos. |
| Dependência entre decisões | Sequencial | Cada lance submetido altera o valor corrente do item e influencia a reação dos concorrentes. |
| Mudança durante a decisão | Semidinâmico | O relógio do leilão avança continuamente, mas o estado do preço só se altera mediante a submissão de novos lances. |
| Natureza dos elementos | Discreto | O valor dos lances, o número de participantes e os passos de contagem são discretos. |
| Conhecimento do funcionamento | Conhecido | As regras do leilão (ex.: leilão inglês, holandês ou de envelope fechado) são conhecidas. |

### Opções para classificação
- **Observabilidade:** Completamente observável, parcialmente observável ou não observável.
- **Número de agentes:** Agente único ou multiagente; indique cooperação ou competição quando pertinente.
- **Previsibilidade:** Determinístico ou estocástico; considere a influência estratégica de outros agentes.
- **Dependência entre decisões:** Episódico ou sequencial.
- **Mudança durante a decisão:** Estático, dinâmico ou semidinâmico.
- **Natureza dos elementos:** Discretos, contínuos ou combinação; considere estados, tempo, percepções e ações.
- **Conhecimento do funcionamento:** Conhecido ou desconhecido para o agente.

### Comparação final
1. O que muda entre jogar tênis contra outra pessoa e praticar contra uma parede?
   - **Resposta:** A partida contra outra pessoa é um ambiente *multiagente e estocástico*, onde o adversário adota estratégias deliberadamente para enganar o agente. Por outro lado, a prática contra a parede é um ambiente de *agente único e determinístico*, onde a parede atua apenas como um elemento passivo que reflete a bola segundo leis físicas previsíveis.

2. Por que comprar livros usados pode exigir decisões com informações incompletas?
   - **Resposta:** Porque o ambiente é *parcialmente observável*. O agente não consegue avaliar fisicamente o desgaste real, páginas sublinhadas ou defeitos ocultos do livro antes da entrega, tendo de confiar apenas nas descrições/fotos do vendedor e na incerteza da concorrência com outros compradores em tempo real.

3. Como outros agentes influenciam futebol e leilões?
   - **Resposta:** No futebol, os outros agentes exercem uma oposição *física e tática direta e contínua* no espaço real, exigindo coordenação espacial instantânea. Num leilão, a influência dos outros agentes é *estratégica e discreta*, impactando a tomada de decisão através da alteração do valor financeiro necessário para cobrir o lance e da gestão do tempo limite do leilão.

## Exercício 2.5
Defina cada termo com suas palavras em duas a quatro linhas e apresente um exemplo.

### Agente

- Definição: Entidade capaz de perceber o meio em que está inserida através de sensores e de executar ações sobre esse mesmo ambiente por meio de atuadores, procurando cumprir determinado objetivo.
- Exemplo: Um robô aspirador de pó autónomo que limpa divisões de uma casa.

### Função de agente

- Definição: Abstração matemática que define o comportamento do agente ao mapear qualquer sequência histórica de percepções recebidas para uma ação correspondente ($f: P^* \rightarrow A$).
- Exemplo: Uma tabela teórica que indica a ação "Aspirar" sempre que a percepção anterior detetar "Poeira".

### Programa de agente

- Definição: A implementação computacional concreta da função de agente, que executa sobre uma arquitetura física ou computacional para processar percepções e emitir comandos.
- Exemplo: Um script escrito em Python executado no microcontrolador do robô aspirador.

### Racionalidade

- Definição: Propriedade do comportamento de um agente que escolhe a ação esperada para maximizar a sua medida de desempenho, com base no histórico de percepções recebidas e no seu conhecimento prévio.
- Exemplo: Um sistema de GPS que escolhe o percurso com o menor tempo estimado considerando o estado atual do tráfego.

### Autonomia

- Definição: Capacidade de um agente de aprender, adaptar-se e tomar decisões com base na sua própria experiência e no ambiente, reduzindo a dependência de conhecimentos pré-programados pelo seu criador.
- Exemplo: Um carro autónomo que ajusta a distância de travagem à medida que aprende sobre o desgaste dos seus travões ao longo do tempo.

### Agente reativo

- Definição: Agente simples que decide a sua ação presente com base exclusivamente na percepção atual, ignorando totalmente o histórico de percepções passadas.
- Exemplo: Um termóstato simples que liga o ar condicionado no momento em que a temperatura medida ultrapassa $25^\circ\text{C}$.

### Agente baseado em modelo

- Definição: Agente que mantém um estado interno para acompanhar aspetos não observáveis do ambiente atual, atualizando a sua visão do mundo à medida que o tempo passa.
- Exemplo: Um carro autónomo que mantém na memória a posição de um peão que entrou temporariamente num ponto cego.

### Agente baseado em objetivos

- Definição: Agente que combina informações do estado do ambiente com metas/objetivos definidos para planejar e selecionar a sequência de ações que o levará ao estado desejado.
- Exemplo: Um algoritmo de planeamento de rotas que procura caminhos para alcançar uma morada de destino definida pelo utilizador.

### Agente baseado em utilidade

- Definição: Agente que utiliza uma função de utilidade para quantificar e avaliar o quão "desejável" é um determinado estado, permitindo escolher a melhor opção em cenários com objetivos concorrentes.
- Exemplo: Um sistema de navegação que escolhe um trajeto ponderando tempo de viagem, consumo de combustível e custo de portagens.

### Agente com aprendizagem

- Definição: Agente composto por elementos de aprendizagem, desempenho, crítica e gerador de problemas, capaz de aprender com erros passados para aperfeiçoar o seu desempenho futuro.
- Exemplo: Um filtro de correio eletrónico que aprende a identificar novos padrões de *spam* com base na marcação manual feita pelos utilizadores.

## Síntese com autômatos
Escolha um caso do item 2.4. Apresente três estados internos, três percepções, três ações e duas regras no formato estado atual + percepção → próximo estado e ação. Explique como estados internos representam informação passada e cite uma limitação da simplificação.

Resposta:
- **Cenário Escolhido:** Robô Aspirador de Pó (Análogo ao Caso 5 / Ambiente de Navegação).
- **3 Estados Internos:**
  1. $S_0$: Procurando Sujidade (Navegação padrão)
  2. $S_1$: Aspirando (Executando limpeza local)
  3. $S_2$: Desviando de Obstáculo (Afastamento de parede/objeto)
- **3 Percepções:**
  1. $p_1$: `[Sujo]` (Poeira detetada no piso)
  2. $p_2$: `[Obstáculo]` (Contacto ou proximidade com objeto)
  3. $p_3$: `[Livre]` (Caminho desimpedido e limpo)
- **3 Ações:**
  1. $a_1$: Aspirar
  2. $a_2$: Girar 90°
  3. $a_3$: Mover em frente
- **2 Regras de Transição (Estado Atual + Percepção $\rightarrow$ Próximo Estado e Ação):**
  1. $(S_0, p_1) \rightarrow S_1 \text{ e ação } a_1$
  2. $(S_0, p_2) \rightarrow S_2 \text{ e ação } a_2$

- **Como o estado interno representa informação passada:** O estado interno sintetiza os acontecimentos e percepções passadas num resumo compacto (por exemplo, guardar $S_2$ indica que o agente colidiu recentemente com algo), permitindo tomar decisões adequadas no presente sem a necessidade de manter e pesquisar uma lista com todo o histórico de percepções desde o início.
- **Limitação da simplificação:** A modelação por autómato de estados finitos assume uma representação discreta e finita do mundo. Em cenários reais complexos ou contínuos, a quantidade de variações possíveis gera uma explosão do número de estados, tornando inviável mapear manualmente todas as transições do ambiente.

## Entrega e avaliação
Confira: identificação; nove análises no item 2.3; sete casos completos no item 2.4; dez conceitos no item 2.5; síntese; referências.
Nome sugerido: `NomeSobrenome_Atividade_AgentesInteligentes`. Prazo e envio conforme orientação da professora.

| Critério | Atividade avaliativa (1,0 ponto) A2 |
|---|---:|
| Item 2.3 — correção e argumentação | 30% |
| Item 2.4 — PEAS e classificação justificada | 40% |
| Item 2.5 — precisão conceitual e exemplos | 20% |
| Síntese, organização e referências | 10% |

## Referências
Material-base: Capítulo 2 — Agentes inteligentes, disponibilizado para a aula de 19/10/2026.
Referências adicionais: RUSSELL, Stuart; NORVIG, Peter. *Inteligência Artificial: uma abordagem moderna*. 4. ed. Rio de Janeiro: GEN LTC, 2022.
