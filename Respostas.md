# Atividade: Máquinas de Turing

**Disciplina:** Teoria da Computação | **Professora:** Kadidja Valéria

Abaixo estão os arquivos da atividade. Clique nos links para acessar os PDFs diretamente:

- 📄 [Documento Principal da Atividade](Atividade%20-%20Máquinas%20de%20Turing.pdf)
- ✅ [Teste 1 - Entrada aceita (0011)](Teste%201%20Entrada%20aceita%200011.pdf)
- ✅ [Teste 2 - Entrada aceita (000111)](Teste%202%20Entrada%20aceita%20000111.pdf)
- ❌ [Teste 3 - Entrada rejeitada (00111)](Teste%203%20Entrada%20rejeitada%2000111.pdf)



Etapa 3 — Registro da simulação

Basicamente, a máquina funciona fazendo pares ela lê o primeiro '0' da fita e troca o por um 'X' a seguir, avança até encontrar o primeiro '1' e troca o por um 'Y'. Depois de fazer este primeiro par, ela volta para trás até ao último 'X' e repete todo o processo. Quando já não houver mais zeros para marcar, ela verifica o que sobrou na fita. Se só lá estiverem letras 'Y' até ao final, está tudo certo e ela aceita a palavra. Mas se, por acaso, sobrar algum '0' ou '1' pendurado sem par, a máquina percebe logo que a conta não bate certo, encrava e rejeita a palavra.


Etapa 4 — Reflexão sobre os limites computacionais

Não, a Máquina de Turing não consegue resolver qualquer problema. Como o próprio Alan Turing provou, a computação possui limites matemáticos e existem as chamadas funções não computáveis. Isso acontece porque nem toda questão pode ser transformada num algoritmo, ou seja, numa sequência finita de regras e passos. Um grande exemplo é o Problema da Parada : é impossível criar um algoritmo capaz de prever com 100% de certeza se outro programa vai concluir a sua tarefa ou ficar preso num loop infinito. Portanto, a limitação não é por falta de poder ou memória nos computadores, mas sim uma barreira estrutural da própria lógica. Se não existe um caminho lógico passo a passo para resolver algo, nenhum computador conseguirá fazê lo.


6. Questão final

Para eu descobrir se esse problema complexo é apenas ifícil ou se realmente não tem solução, eu usaria os conceitos de computabilidade e limites computacionais que estudamos no material da Aula 09 .  

Como vimos na disciplina e no vídeo indicado para a atividade, a Máquina de Turing serve justamente para traçar a linha do que é ou não possível de ser calculado. Se eu conseguir formular uma Máquina de Turing definindo a fita, os estados e as transições que consiga chegar a uma resposta passo a passo, eu sei que o problema é computável. Ou seja, ele pode até exigir muito tempo e memória, mas é apenas 'difícil', e não impossível.   Por outro lado, o material mostrou nos que a computação tem limites e que existem problemas não computáveis. 

Se eu notar que esse meu problema tem a mesma estrutura lógica de problemas que já foram matematicamente provados como sem solução como o famoso Problema da Parada de Turing, então eu sei que ele esbarra nos limites computacionais. Nesse caso, eu chego à conclusão de que não existe algoritmo capaz de resolvê-lo para todos os casos, não importa o quão potente seja o computador que eu estiver a usar.
