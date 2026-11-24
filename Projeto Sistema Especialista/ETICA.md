# Ética e impactos da inteligência artificial

**Projeto A1:** Sistema especialista de triagem de golpes de falsa central de atendimento  
**Disciplina:** Inteligência Artificial e LFA  
**Professora:** Kadidja Valéria — UDF  
**Estudante:** Enzo Roberto Fernandes Montenegro  
**Matrícula:** 38946211  
**Turma:** N1

## 1. Leitura e vídeo

### Artigo

O artigo de Francisco Pires de Lacerda Júnior (2026) analisa o uso ético da inteligência artificial generativa no ensino superior. Segundo o resumo, o autor realizou uma revisão de 14 estudos científicos e três documentos normativos, considerando questões de autoria, avaliação acadêmica, formação para o uso da IA, regras institucionais e proteção de dados.

A ideia central é que proibir a IA de forma geral ou permitir seu uso sem critérios não resolve os problemas éticos. É necessário definir quando seu uso é adequado, declarar o auxílio recebido e manter a responsabilidade humana pelo resultado.

No desenvolvimento deste sistema especialista, essa questão se relaciona ao uso do Claude para melhorar minhas ideias e do ChatGPT para auxiliar na revisão do projeto. A IA pode contribuir para o aprendizado, mas não deve substituir o conhecimento do estudante.

Referência: LACERDA JÚNIOR, Francisco Pires de. [Da proibição à governança: uso ético da inteligência artificial generativa na educação superior — uma revisão integrativa (2023–2026)](https://doi.org/10.54751/revistafoco.v19n8-017). Revista Foco, v. 19, n. 8, e12330, 2026. Análise baseada no resumo publicado pela revista; o texto integral não foi consultado nesta revisão.

### Vídeo

[O Estado da Arte em Ética na Inteligência Artificial](https://www.youtube.com/watch?v=SHDtABmGhNw). Instituto de Estudos Avançados da USP, 9 de junho de 2026. Duração: 2h01.

**Trecho escolhido para análise:** apresentação de Steven Gouveia (Universidade do Porto) sobre o livro e as linhas atuais de pesquisa em ética na IA. A minutagem efetiva na gravação não foi verificada.

**Tema escolhido:** responsabilidade humana e impactos sociais das decisões automatizadas. A descrição oficial do evento inclui responsabilidade, privacidade e viés algorítmico entre os assuntos da obra apresentada. Não atribuo uma fala específica ao palestrante sem confirmação da gravação.

A relação que faço com o projeto é que uma recomendação incorreta pode influenciar diretamente a decisão de uma pessoa diante de um possível golpe. Por isso, o sistema deve apresentar os motivos da classificação, reconhecer suas limitações e orientar a confirmação do contato por canais oficiais. A decisão final não deve depender exclusivamente do resultado da IA.

## 2. Projeto e pessoas afetadas

O sistema foi desenvolvido para ajudar pessoas a reconhecer sinais de possíveis golpes de falsas centrais de atendimento. Ele combina uma árvore de decisão com 52 regras de produção e considera tanto o texto da mensagem quanto as respostas do usuário.

A ferramenta pode ajudar consumidores, principalmente aqueles que têm pouca familiaridade com segurança digital. Porém, uma classificação incorreta também pode prejudicar o usuário ou fazer com que ele desconfie de um contato legítimo.

## 3. Análise ética

| Aspecto | Risco | Medida adotada | O que ainda precisa ser avaliado |
|---|---|---|---|
| Privacidade | Exposição de dados pessoais, senhas ou códigos. | O sistema orienta a não inserir dados reais e não mantém armazenamento persistente das mensagens pelo módulo principal. | Evitar dados sensíveis e limpar saídas do Colab antes de compartilhar o notebook. |
| Equidade | Erros com diferentes formas de escrever ou tipos de mensagem. | A base utiliza exemplos simulados variados. | Testar mensagens inéditas e diferentes perfis de linguagem. |
| Transparência | O usuário interpretar a classificação como certeza de fraude. | O resultado apresenta os fatos, regras aplicadas e fatores de certeza, separados da saída do modelo. | Revisar os pesos das regras com especialistas. |
| Supervisão humana | O usuário tomar decisões apenas com base no resultado automático. | A previsão do texto, sozinha, gera no máximo um alerta fraco. A orientação inclui a verificação por canais oficiais. | Verificar se os usuários compreendem as recomendações. |
| Impacto social | Uma fraude passar despercebida ou um contato legítimo gerar alarme. | A previsão negativa não reduz a suspeita indicada pelas regras. Possíveis danos relatados são investigados independentemente da suspeita inicial. | Avaliar o sistema com casos independentes e orientação especializada. |

## 4. Dilema ético

Um dos principais dilemas do projeto é o equilíbrio entre alertar sobre um possível golpe e evitar alarmes desnecessários. No teste da árvore de decisão, foram classificados corretamente 15 dos 25 exemplos, o que corresponde a 60% de acurácia. Houve três golpes não detectados e sete mensagens legítimas classificadas incorretamente como golpes.

Por isso, o modelo não deve tomar a decisão sozinho. As regras consideram informações adicionais, como a solicitação de senhas e a existência de possível exposição de dados. Caso exista risco, o sistema recomenda medidas de proteção e a confirmação do contato pelos canais oficiais da instituição.

Os dados utilizados são simulados.

## 5. Reflexão individual

Não participei do debate em sala, mas assisti ao vídeo indicado. Ao analisar o projeto, considero importante que a inteligência artificial seja utilizada como uma ferramenta de apoio, e não como a única responsável pela decisão. A árvore de decisão pode cometer erros, por isso as regras do sistema especialista ajudam a considerar outras informações antes de recomendar uma ação.

Um dos cuidados que considero necessários é evitar que uma classificação de mensagem legítima seja interpretada como garantia de segurança. O usuário precisa conhecer as limitações do sistema e confirmar contatos suspeitos pelos canais oficiais. Novos testes com mensagens diferentes das utilizadas no treinamento podem ajudar a avaliar e melhorar essa orientação.

## 6. Declaração de uso de inteligência artificial

O ChatGPT foi utilizado como apoio na análise dos materiais da disciplina, na realização de testes e na organização do notebook e da documentação. Também utilizei o Claude para melhorar minhas ideias durante o desenvolvimento do projeto.

A versão revisada apresentou 101 testes automatizados aprovados, o que verifica aspectos do funcionamento do código, mas não substitui a validação por especialistas nem comprova sua eficácia em situações reais.
