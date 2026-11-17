"""
Sistema Especialista com Aprendizado Supervisionado
Triagem de golpes de falsa central de atendimento (banco/operadora)
====================================================================
Arquitetura híbrida em duas fases:
  FASE 1 (machine learning): árvore de decisão lê o TEXTO da mensagem e gera o
          fato dinâmico "ml_golpe".
  FASE 2 (sistema especialista): Base de Conhecimento + Memória de Trabalho +
          Motor de Inferência (encadeamento para frente e para trás) combinam esse
          fato às respostas do usuário e entregam: grau de suspeita (fatores de
          certeza), tipo de golpe e plano de ação, com explicação.

Este arquivo é gerado a partir do notebook (notebooks/sistema_especialista_golpes.ipynb).
Use:  python src/sistema_golpes.py   (consulta interativa no terminal)

Aviso: dados de treino SIMULADOS; ferramenta educacional de apoio. Não substitui o
atendimento oficial do banco ou da operadora.
"""
# Importação das bibliotecas necessárias
import re                                   # re: expressões regulares (extração de atributos do texto)
import unicodedata                          # unicodedata: remove acentos para comparar palavras
from dataclasses import dataclass, field    # dataclass: cria classes de dados de forma enxuta
from typing import Callable, Optional       # tipos usados nas anotações das funções

# pandas: manipulação e análise de dados estruturados
import pandas as pd
# train_test_split: divisão em treino e teste; StratifiedKFold/cross_val_score: validação cruzada
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
# DecisionTreeClassifier: algoritmo de árvore de decisão para classificação
from sklearn.tree import DecisionTreeClassifier
# Métricas de avaliação: acurácia e matriz de confusão
from sklearn.metrics import accuracy_score, confusion_matrix

# Mensagens fictícias (texto, rótulo). Dados SIMULADOS, escritos pelo autor para fins didáticos.
MENSAGENS_SIMULADAS = [
    # ---------------- golpes (20) ----------------
    ("URGENTE! Sua conta foi bloqueada. Regularize agora em http://banco-seguro.exemplo.top/login e informe sua senha.", "golpe"),
    ("Identificamos uma compra suspeita no seu cartão. Para cancelar, informe o código enviado por SMS imediatamente.", "golpe"),
    ("Sou da central de segurança do Banco Exemplo. Sua conta foi invadida. Faça um Pix para uma conta segura agora para proteger seu saldo.", "golpe"),
    ("Seu cartão foi clonado. Um motoboy irá buscá-lo hoje. Corte o cartão sem danificar o chip e informe a senha.", "golpe"),
    ("Atenção: instale o aplicativo de suporte para liberar o acesso e resolver o bloqueio da sua conta imediatamente.", "golpe"),
    ("Parabéns! Você ganhou aumento de limite! Clique em www.limite-premiado.exemplo.link e confirme seu CPF e senha.", "golpe"),
    ("Operadora Exemplo: seu chip será suspenso hoje. Atualize seus dados em bit.ly/chip-ativo e informe o código recebido.", "golpe"),
    ("Cashback de R$ 500 liberado! Pague a taxa de liberação de R$ 29,90 via Pix para receber seu prêmio.", "golpe"),
    ("Detectamos um novo aparelho conectado à sua conta. Confirme sua senha e o token para cancelar a operação agora.", "golpe"),
    ("Seu Pix de R$ 3.200 foi bloqueado. Transferência pendente: regularize o pagamento em 1 hora para evitar multa.", "golpe"),
    ("BANCO EXEMPLO: SUA CONTA SERÁ ENCERRADA HOJE!!! ACESSE http://exemplo-banco.top E CONFIRME SEUS DADOS AGORA!!!", "golpe"),
    ("Houve tentativa de fraude. Para sua segurança, passe o código de 6 dígitos que enviamos por SMS.", "golpe"),
    ("Aqui é do setor antifraude. Precisamos validar seu CPF e a senha do cartão para estornar a compra indevida.", "golpe"),
    ("Seu cadastro expira hoje. Clique no link para atualizar e evitar o bloqueio do cartão: www.atualiza-cadastro.exemplo.com/app", "golpe"),
    ("Devolução disponível: informe seu token e faça uma transferência de validação de R$ 1,00.", "golpe"),
    ("Atendimento da Operadora Exemplo: você tem bônus de internet. Digite o código recebido para ativar agora.", "golpe"),
    ("Seu cartão foi bloqueado por segurança. Entregue o cartão ao nosso portador e informe a senha para desbloquear.", "golpe"),
    ("Compra de R$ 4.890 em andamento. Se não reconhece, ligue já para 0800 000 0000 e informe seu CPF e senha.", "golpe"),
    ("Boleto de regularização pendente. Pague agora via Pix para liberar seu limite. Chave aleatória abaixo.", "golpe"),
    ("Seu acesso será suspenso. Instale o app e informe o token para manter a conta ativa.", "golpe"),
    # ---------------- legítimas (20) ----------------
    ("Compra aprovada no cartão final 1234, R$ 54,90, em Mercado Exemplo.", "legitimo"),
    ("Sua fatura do cartão já está disponível no aplicativo. Vencimento em 10/12.", "legitimo"),
    ("Seu código de acesso é 482913. Não compartilhe com ninguém. Validade: 5 minutos.", "legitimo"),
    ("Pix recebido de Maria Silva no valor de R$ 120,00.", "legitimo"),
    ("Lembrete: sua fatura vence amanhã. Pague pelo aplicativo ou pelo internet banking.", "legitimo"),
    ("Olá! Seu pedido saiu para entrega e chega hoje entre 14h e 18h.", "legitimo"),
    ("Sua agência atende de segunda a sexta, das 10h às 16h.", "legitimo"),
    ("Aviso: nunca informe senha ou código por telefone. O banco nunca solicita esses dados.", "legitimo"),
    ("Seu extrato de novembro está disponível. Acesse o aplicativo para consultar.", "legitimo"),
    ("Transferência agendada para 20/11 no valor de R$ 300,00 realizada com sucesso.", "legitimo"),
    ("Seu plano foi renovado. Franquia de 20 GB disponível até 15/12.", "legitimo"),
    ("Confirmação: seu limite foi ajustado conforme solicitado por você no aplicativo.", "legitimo"),
    ("Código de verificação 771204. Se não foi você, ignore esta mensagem.", "legitimo"),
    ("O prazo para declarar o imposto termina em breve. Veja o guia no site oficial www.gov.exemplo.br/guia", "legitimo"),
    ("Oferta para clientes: 5% de desconto na primeira compra. Válido até domingo.", "legitimo"),
    ("Sua senha foi alterada com sucesso. Se não reconhece, ligue para o número do verso do cartão.", "legitimo"),
    ("Atualização do app disponível! Atualize pela loja oficial quando puder.", "legitimo"),
    ("Seu cartão foi enviado e chega em até 7 dias úteis. Acompanhe pelo aplicativo.", "legitimo"),
    ("Pagamento do boleto confirmado. Obrigado!", "legitimo"),
    ("Informe-nos sua opinião: avalie o atendimento em até 3 dias no aplicativo.", "legitimo"),
]

# Lista oficial de atributos (colunas de X). O rótulo "perfil" NUNCA entra aqui.
ATRIBUTOS = ["n_links", "n_urgencia", "n_dados_sensiveis",
             "n_verbos_pedido", "n_exclamacoes", "pct_maiusculas"]

# Dicionários de palavras (sem acento, em minúsculas). Cada item é um "prefixo" de palavra.
TERMOS_URGENCIA = ["urgente", "imediat", "agora", "hoje", "bloque", "ultimas horas",
                   "expira", "suspens", "prazo", "encerrad", "1 hora"]
TERMOS_SENSIVEIS = ["senha", "cvv", "codigo", "token", "cpf", "pix",
                    "transfer", "deposito"]
VERBOS_PEDIDO = ["informe", "envie", "digite", "confirme", "passe", "forneca",
                 "transfira", "instale", "clique", "atualiz", "regulariz",
                 "desbloque", "entregue", "pague", "faca", "corte", "ligue"]
# Um "token" (pedaço do texto entre espaços) é considerado link se casar com este padrão
PADRAO_LINK = re.compile(r"(https?://|www\.|bit\.ly|[a-z0-9-]+\.(?:com|net|org|app|link|top|xyz)\b)")

def normalizar(texto: str) -> str:
    """O QUE FAZ: padroniza o texto para comparação.
    Remove acentos e converte para minúsculas ("Código" -> "codigo").
    POR QUÊ: assim "SENHA", "senha" e "Senha" são tratadas como a mesma palavra."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sem_acento.lower()


def _contar_termos(texto_norm: str, termos: list) -> int:
    """Conta QUANTOS termos distintos da lista aparecem no texto (início de palavra)."""
    return sum(1 for t in termos if re.search(r"\b" + re.escape(t), texto_norm))


def extrair_atributos(texto: str) -> dict:
    """O QUE É: a ponte entre texto e machine learning.
    O QUE FAZ: transforma uma mensagem em 6 números (os atributos X) que o
    classificador consegue usar. É a "engenharia de atributos" do projeto."""
    norm = normalizar(texto)
    letras = [c for c in texto if c.isalpha()]
    maiusculas = sum(1 for c in letras if c.isupper())
    return {
        "n_links": sum(1 for tok in norm.split() if PADRAO_LINK.search(tok)),
        "n_urgencia": _contar_termos(norm, TERMOS_URGENCIA),
        "n_dados_sensiveis": _contar_termos(norm, TERMOS_SENSIVEIS),
        "n_verbos_pedido": _contar_termos(norm, VERBOS_PEDIDO),
        "n_exclamacoes": texto.count("!"),
        "pct_maiusculas": round(100 * maiusculas / len(letras), 1) if letras else 0.0,
    }


def construir_dataset(mensagens: list = MENSAGENS_SIMULADAS) -> pd.DataFrame:
    """O QUE FAZ: monta o DataFrame de treino: texto + 6 atributos + rótulo `perfil`.
    Cada mensagem passa por `extrair_atributos`, garantindo que treino e uso real
    calculem os atributos exatamente do mesmo jeito."""
    linhas = []
    for texto, perfil in mensagens:
        linhas.append({"texto": texto, **extrair_atributos(texto), "perfil": perfil})
    return pd.DataFrame(linhas)

@dataclass
class ResultadoTreino:
    """O QUE É: um "pacote" com tudo que saiu do treinamento (modelo, divisões
    treino/teste, previsões e métricas), para podermos exibir e reutilizar."""
    modelo: DecisionTreeClassifier
    X_treino: pd.DataFrame
    X_teste: pd.DataFrame
    y_treino: pd.Series
    y_teste: pd.Series
    previsoes: object
    acuracia: float
    classes: list
    matriz: object
    cv_media: float
    cv_desvio: float


def treinar_modelo(dados: pd.DataFrame, test_size: float = 0.25,
                   random_state: int = 42, max_depth: int = 3) -> ResultadoTreino:
    """O QUE FAZ: executa todo o fluxo de aprendizado supervisionado.
      1) separa X (atributos) e y (rótulo);
      2) divide em treino e teste (estratificado e reproduzível);
      3) treina uma árvore de decisão com profundidade limitada (evita overfitting);
      4) avalia no teste: acurácia e matriz de confusão;
      5) valida por validação cruzada (verificação extra de estabilidade)."""
    X = dados[ATRIBUTOS]          # atributos (o rótulo NÃO entra aqui)
    y = dados["perfil"]           # rótulo (resposta conhecida)

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y)

    modelo = DecisionTreeClassifier(max_depth=max_depth, min_samples_leaf=2,
                                    random_state=random_state)
    modelo.fit(X_treino, y_treino)                   # aprende SOMENTE com o treino
    previsoes = modelo.predict(X_teste)              # prevê o conjunto de teste

    classes = ["golpe", "legitimo"]
    matriz = confusion_matrix(y_teste, previsoes, labels=classes)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    scores = cross_val_score(
        DecisionTreeClassifier(max_depth=max_depth, min_samples_leaf=2,
                               random_state=random_state), X, y, cv=cv)

    return ResultadoTreino(modelo, X_treino, X_teste, y_treino, y_teste, previsoes,
                           float(accuracy_score(y_teste, previsoes)), classes, matriz,
                           float(scores.mean()), float(scores.std()))

# ----------------------------------------------------------------------
# Parâmetros do sistema
# ----------------------------------------------------------------------
LIMIAR = 0.2          # evidência mínima para considerar um fato "verdadeiro"
NIVEL_ALTO = 0.7      # suspeita >= 0.7  -> nível ALTO
NIVEL_MODERADO = 0.4  # suspeita >= 0.4  -> nível MODERADO
MIN_INFO = 4          # mínimo de sinais respondidos para concluir "baixo risco"

# De onde vem o CRITÉRIO de cada regra (justificativa da origem)
FONTES = {
    "FEB": "Orientações públicas da Febraban (campanha 'Pare & Pense #Pode ser Golpe' e dicas antigolpe)",
    "BCB": "Banco Central do Brasil (Mecanismo Especial de Devolução - MED do Pix)",
    "HEUR": "Heurística do autor, a validar com especialista",
    "ML": "Modelo de aprendizado de máquina (Fase 1)",
}


def combinar(a: float, b: float) -> float:
    """O QUE FAZ: combina dois fatores de certeza que apoiam a MESMA conclusão
    (fórmula do MYCIN). O resultado fica sempre entre -1 e +1."""
    if a >= 0 and b >= 0:
        return a + b * (1 - a)
    if a <= 0 and b <= 0:
        return a + b * (1 + a)
    den = 1 - min(abs(a), abs(b))
    return 0.0 if den < 1e-9 else (a + b) / den


def premissa_ok(cf: float, esperado: bool, limiar: float) -> bool:
    """O QUE FAZ: diz se uma premissa está satisfeita.
    Premissa 'verdadeira' exige cf >= limiar; premissa negada ('NÃO x') exige cf <= -limiar."""
    return cf >= limiar if esperado else cf <= -limiar

@dataclass(frozen=True)
class Regra:
    """O QUE É: uma regra de produção do especialista: SE premissas ENTÃO conclusão.
    Campos: id (nome da regra), premissas (lista de (fato, esperado)), conclusao (fato
    produzido), cf (confiança da regra, -1..1), limiar (evidência mínima das premissas),
    nota (justificativa em português, usada na explicação) e fonte (origem do critério)."""
    id: str
    premissas: tuple
    conclusao: str
    cf: float
    limiar: float = LIMIAR
    nota: str = ""
    fonte: str = "HEUR"

    @staticmethod
    def criar(id: str, premissas: str, conclusao: str, cf: float, nota: str = "",
              limiar: float = LIMIAR, fonte: str = "HEUR") -> "Regra":
        """O QUE FAZ: atalho para escrever regras como texto.
        Exemplo: Regra.criar("S2", "a & !b", "suspeita", 0.7) -> SE a E NÃO b ENTÃO suspeita.
        O prefixo '!' significa que o fato precisa ser FALSO."""
        ps = tuple((p.strip().lstrip("!"), not p.strip().startswith("!"))
                   for p in premissas.split("&"))
        return Regra(id, ps, conclusao, cf, limiar, nota, fonte)

    def __str__(self) -> str:
        p = " E ".join(("" if e else "NÃO ") + f for f, e in self.premissas)
        return f"{self.id}: SE {p} ENTÃO {self.conclusao} (cf {self.cf:+.2f})"


class BaseConhecimento:
    """O QUE É: o conhecimento estático do especialista.
    Contém: perguntas (fatos que o usuário informa), regras, rótulos legíveis, tipos de
    golpe, ações recomendadas, fatos de saída e fatos externos (vindos do modelo de ML)."""

    def __init__(self, perguntas: dict, regras: list, rotulos: dict, tipos: dict,
                 acoes: dict, saidas: set, externos: frozenset = frozenset()):
        self.perguntas = perguntas      # fato -> texto da pergunta (sim/não)
        self.regras = regras
        self.rotulos = rotulos          # fato -> nome legível
        self.tipos = tipos              # fato -> nome do tipo de golpe
        self.acoes = acoes              # fato -> texto da ação (a ordem define a prioridade)
        self.saidas = saidas            # fatos que são resultado final
        self.externos = externos        # fatos fornecidos por fora (ex.: modelo de ML)

    def regras_que_concluem(self, fato: str) -> list:
        """Devolve as regras cuja conclusão é `fato` (usado no encadeamento para trás)."""
        return [r for r in self.regras if r.conclusao == fato]

    def verificar(self) -> dict:
        """O QUE FAZ: VERIFICAÇÃO da base (falhas lógicas internas), sem precisar de usuário.
        Procura: regras duplicadas, premissas inalcançáveis, ciclos de dependência,
        pesos inválidos e perguntas/fatos que nunca são usados."""
        rel = {"duplicadas": [], "inalcancaveis": [], "ciclos": [],
               "cf_invalido": [], "nao_usados": []}
        derivados = {r.conclusao for r in self.regras}
        usados = {f for r in self.regras for f, _ in r.premissas}

        for i, r1 in enumerate(self.regras):
            for r2 in self.regras[i + 1:]:
                if set(r1.premissas) == set(r2.premissas) and r1.conclusao == r2.conclusao:
                    rel["duplicadas"].append(f"{r1.id} e {r2.id} têm mesmas premissas e conclusão")
        for r in self.regras:
            if not (0 < abs(r.cf) <= 1) or not (0 < r.limiar <= 1):
                rel["cf_invalido"].append(f"{r.id}: cf={r.cf}, limiar={r.limiar}")
            for f, _ in r.premissas:
                if f not in self.perguntas and f not in derivados and f not in self.externos:
                    rel["inalcancaveis"].append(
                        f"{r.id}: '{f}' não é perguntável, externo nem concluído por regra")
        for f in list(self.perguntas) + list(self.externos):
            if f not in usados:
                rel["nao_usados"].append(f"'{f}' não é usado por nenhuma regra")
        for f in derivados:
            if f not in usados and f not in self.saidas:
                rel["nao_usados"].append(f"fato '{f}' é concluído mas nunca usado")

        grafo: dict = {}
        for r in self.regras:
            grafo.setdefault(r.conclusao, set()).update(f for f, _ in r.premissas)

        def tem_ciclo(no, visitando, feitos):
            if no in visitando:
                return True
            if no in feitos:
                return False
            visitando.add(no)
            if any(tem_ciclo(v, visitando, feitos) for v in grafo.get(no, ())):
                return True
            visitando.discard(no)
            feitos.add(no)
            return False

        feitos: set = set()
        for no in list(grafo):
            if tem_ciclo(no, set(), feitos):
                rel["ciclos"].append(f"ciclo de dependência envolvendo '{no}'")
                break
        return rel


@dataclass
class MemoriaTrabalho:
    """O QUE É: a memória DINÂMICA da consulta atual.
    `fatos` guarda o fator de certeza de cada fato; `origem` diz quem o produziu
    ("usuário", "regras" ou "modelo de ML"); `desconhecidos` lista o que o usuário
    respondeu "não sei" (para nunca perguntar duas vezes)."""
    fatos: dict = field(default_factory=dict)
    origem: dict = field(default_factory=dict)
    desconhecidos: set = field(default_factory=set)

    def afirmar(self, fato: str, cf: float, origem: str) -> None:
        """Registra (ou atualiza) um fato com seu fator de certeza e sua origem."""
        self.fatos[fato] = cf
        self.origem[fato] = origem

    def limpar(self) -> None:
        """Esvazia a memória para começar uma nova consulta."""
        self.fatos.clear()
        self.origem.clear()
        self.desconhecidos.clear()


Provedor = Callable[[str, str], Optional[str]]   # (fato, pergunta) -> "sim" | "nao" | None


class MotorInferencia:
    """O QUE É: o "cérebro" do sistema especialista. Não sabe nada sobre golpes:
    apenas cruza os fatos da Memória de Trabalho com as regras da Base de Conhecimento."""

    def __init__(self, bc: BaseConhecimento, mt: Optional[MemoriaTrabalho] = None):
        self.bc = bc
        self.mt = mt or MemoriaTrabalho()
        self.contribuicoes: dict = {}   # id da regra -> (fato, contribuição) [para explicar]
        self.perguntadas: list = []     # perguntas efetivamente feitas ao usuário

    def registrar_resposta(self, fato: str, resposta: Optional[str]) -> None:
        """Converte a resposta do usuário em fato: sim -> +1, nao -> -1, outro -> desconhecido."""
        if resposta == "sim":
            self.mt.afirmar(fato, 1.0, "usuário")
        elif resposta == "nao":
            self.mt.afirmar(fato, -1.0, "usuário")
        else:
            self.mt.desconhecidos.add(fato)

    def _contribuicao(self, r: Regra) -> Optional[float]:
        """Calcula quanto uma regra contribui (cf × menor certeza das premissas).
        Devolve None se alguma premissa não estiver satisfeita."""
        forcas = []
        for f, esperado in r.premissas:
            cf = self.mt.fatos.get(f)
            if cf is None or not premissa_ok(cf, esperado, r.limiar):
                return None
            forcas.append(abs(cf))
        return r.cf * min(forcas)

    def encadeamento_frente(self) -> list:
        """ENCADEAMENTO PARA FRENTE (dirigido por dados).
        Parte dos fatos já presentes na memória e recalcula todas as conclusões possíveis
        até estabilizar. Devolve a lista de regras que dispararam."""
        derivados = {r.conclusao for r in self.bc.regras}
        for _ in range(len(self.bc.regras) + 2):
            self.contribuicoes.clear()
            novos: dict = {}
            for fato in derivados:
                total = None
                for r in self.bc.regras_que_concluem(fato):
                    c = self._contribuicao(r)
                    if c is None:
                        continue
                    self.contribuicoes[r.id] = (fato, c)
                    total = c if total is None else combinar(total, c)
                if total is not None:
                    novos[fato] = total
            mudou = False
            for fato in derivados:
                antigo = self.mt.fatos.get(fato)
                if fato in novos:
                    if antigo is None or abs(antigo - novos[fato]) > 1e-9:
                        self.mt.afirmar(fato, novos[fato], "regras")
                        mudou = True
                elif antigo is not None and self.mt.origem.get(fato) == "regras":
                    del self.mt.fatos[fato]
                    del self.mt.origem[fato]
                    mudou = True
            if not mudou:
                break
        return list(self.contribuicoes)

    def avaliar(self, fato: str, provedor: Provedor,
                _pilha: frozenset = frozenset()) -> Optional[float]:
        """ENCADEAMENTO PARA TRÁS (dirigido por objetivos).
        Descobre o fator de certeza de `fato`: se já está na memória, usa; se há regras
        que o concluem, avalia as premissas (recursivamente) e combina as contribuições;
        se é uma pergunta, consulta o usuário via `provedor`. Devolve None quando o dado
        é desconhecido (caso INCOMPLETO). Se uma premissa falha, as demais premissas
        daquela regra NÃO são perguntadas (curto-circuito: só pergunta o necessário)."""
        if fato in self.mt.fatos:
            return self.mt.fatos[fato]
        if fato in self.mt.desconhecidos or fato in _pilha:
            return None
        regras = self.bc.regras_que_concluem(fato)
        if regras:
            pilha = _pilha | {fato}
            total = 0.0
            for r in regras:
                forcas, ok = [], True
                for f, esperado in r.premissas:
                    cf = self.avaliar(f, provedor, pilha)
                    if cf is None or not premissa_ok(cf, esperado, r.limiar):
                        ok = False
                        break
                    forcas.append(abs(cf))
                if ok:
                    c = r.cf * min(forcas)
                    self.contribuicoes[r.id] = (fato, c)
                    total = combinar(total, c)
            self.mt.afirmar(fato, total, "regras")
            return total
        if fato in self.bc.perguntas:
            self.perguntadas.append(fato)
            self.registrar_resposta(fato, provedor(fato, self.bc.perguntas[fato]))
            return self.mt.fatos.get(fato)
        return None

    def explicar(self) -> str:
        """EXPLICAÇÃO ("como cheguei a isso"): lista as evidências informadas, o que o
        modelo de ML achou e as regras que pesaram, com a justificativa e a fonte de cada uma.
        É a transparência que distingue sistemas especialistas de uma "caixa-preta"."""
        rot = self.bc.rotulos
        regras = {r.id: r for r in self.bc.regras}
        linhas = ["Evidências informadas por você:"]
        sim = [rot.get(f, f) for f, cf in self.mt.fatos.items()
               if self.mt.origem[f] == "usuário" and cf > 0]
        linhas += [f"  - {s}" for s in sim] or ["  - (nenhum sinal de alerta confirmado)"]
        if "ml_golpe" in self.mt.fatos:
            p = (self.mt.fatos["ml_golpe"] + 1) / 2
            linhas.append(f"Leitura do texto pelo modelo de ML: {p:.0%} de chance de ser golpe.")

        evid, susp, tipo = [], [], []
        for rid, (fato, c) in self.contribuicoes.items():
            r = regras[rid]
            if fato.startswith("i_") and fato != "i_houve_dano":
                evid.append(f"  - {rid}: {rot.get(fato, fato)} ({c:.0%}). {r.nota} [fonte: {r.fonte}]")
            elif fato == "suspeita_golpe":
                sinal = "aumenta" if c > 0 else "reduz"
                susp.append(f"  - {rid} ({sinal} a suspeita em {abs(c):.0%}): {r.nota} [fonte: {r.fonte}]")
            elif fato in self.bc.tipos:
                tipo.append(f"  - {rid}: indica '{self.bc.tipos[fato]}' ({c:.0%}). {r.nota} [fonte: {r.fonte}]")
        for titulo, itens in (("Evidências deduzidas:", evid),
                              ("Regras que pesaram na suspeita:", susp),
                              ("Regras que indicam o tipo de golpe:", tipo)):
            if itens:
                linhas.append(titulo)
                linhas += itens
        if not (evid or susp or tipo):
            linhas.append("Nenhuma regra de alerta foi acionada.")
        return "\n".join(linhas)

def criar_bc_golpes() -> BaseConhecimento:
    """O QUE FAZ: constrói a Base de Conhecimento do domínio "golpes de falsa central".
    Para usar o motor em outro assunto, basta escrever outra função como esta."""
    perguntas = {
        # ---- sinais do contato ----
        "s_contato_inesperado": "Você foi contatado sem ter pedido nada (ligação, SMS, WhatsApp ou e-mail)?",
        "s_numero_nao_oficial": "O número ou remetente é diferente do oficial (verso do cartão, app ou site)?",
        "s_urgencia": "Falaram em urgência, bloqueio da conta ou prazo curto para você agir?",
        "s_cita_compra_suspeita": "Disseram que houve uma compra ou movimentação suspeita na sua conta?",
        "s_pede_codigo": "Pediram algum código (SMS, token, e-mail ou do aplicativo)?",
        "s_pede_senha": "Pediram senha, CVV ou a senha do cartão?",
        "s_pede_app_remoto": "Pediram para instalar um aplicativo ou liberar acesso remoto ao seu celular/computador?",
        "s_pede_transferencia": "Pediram Pix, transferência ou depósito (por exemplo, para uma 'conta segura')?",
        "s_pede_entregar_cartao": "Disseram que alguém iria buscar ou que você deveria entregar seu cartão?",
        "s_link": "Enviaram um link para 'regularizar', 'desbloquear' ou 'atualizar cadastro'?",
        "s_promessa_beneficio": "Ofereceram prêmio, aumento de limite, cashback ou desconto?",
        "s_pede_pagar_taxa": "Pediram pagamento de taxa, boleto ou tarifa para liberar algo?",
        "s_voce_iniciou": "Foi VOCÊ quem iniciou o contato, ligando para o número oficial (cartão, app ou site)?",
        # ---- o que a pessoa já fez (só perguntado se houver suspeita) ----
        "a_passou_codigo": "Você chegou a informar algum código?",
        "a_passou_senha": "Você chegou a informar senha ou CVV?",
        "a_instalou_app": "Você instalou o aplicativo ou liberou o acesso remoto?",
        "a_fez_transferencia": "Você chegou a fazer Pix, transferência ou pagamento?",
        "a_entregou_cartao": "Você entregou o cartão (ou deixou alguém buscá-lo)?",
        "a_clicou_link": "Você clicou no link ou preencheu dados nele?",
    }
    rotulos = {
        "s_contato_inesperado": "contato que você não solicitou",
        "s_numero_nao_oficial": "número/remetente não oficial",
        "s_urgencia": "urgência ou ameaça de bloqueio",
        "s_cita_compra_suspeita": "alegação de compra suspeita",
        "s_pede_codigo": "pedido de código",
        "s_pede_senha": "pedido de senha/CVV",
        "s_pede_app_remoto": "pedido de app de acesso remoto",
        "s_pede_transferencia": "pedido de Pix/transferência",
        "s_pede_entregar_cartao": "pedido para entregar o cartão",
        "s_link": "link para 'regularizar'",
        "s_promessa_beneficio": "promessa de prêmio/benefício",
        "s_pede_pagar_taxa": "cobrança de taxa",
        "s_voce_iniciou": "você iniciou o contato pelo canal oficial",
        "a_passou_codigo": "você informou um código",
        "a_passou_senha": "você informou senha/CVV",
        "a_instalou_app": "você instalou o app de acesso remoto",
        "a_fez_transferencia": "você fez Pix/transferência",
        "a_entregou_cartao": "você entregou o cartão",
        "a_clicou_link": "você clicou no link",
        "i_pressao": "pressão psicológica",
        "i_pede_credencial": "pedido de credencial",
        "i_canal_nao_oficial": "canal não oficial",
        "i_pede_acao_financeira": "pedido de ação financeira",
        "i_pede_acesso_remoto": "pedido de acesso remoto",
        "ml_golpe": "análise do texto pelo modelo de ML",
    }
    tipos = {
        "t_conta_segura": "Golpe da 'conta segura' (falsa central de segurança)",
        "t_motoboy": "Golpe do motoboy (retirada do cartão)",
        "t_acesso_remoto": "Golpe do acesso remoto (aplicativo espião)",
        "t_roubo_credenciais": "Roubo de código ou senha (engenharia social)",
        "t_phishing_link": "Phishing por link (site falso)",
        "t_falsa_oferta": "Falsa oferta ou prêmio (cobrança de taxa)",
    }
    acoes = {   # a ordem define a prioridade na tela
        "ac_contestar_pix": "URGENTE: ligue agora para o banco pelo canal oficial (verso do cartão ou app) e peça a contestação do Pix pelo MED (Mecanismo Especial de Devolução). O pedido tem prazo (confirme o atual no site do Banco Central) e, quanto antes for feito, maiores as chances de bloquear o valor, pois isso depende de ainda haver saldo na conta de quem recebeu.",
        "ac_bloquear_cartao": "URGENTE: bloqueie o cartão pelo app ou pela central oficial e solicite um novo. Não entregue o cartão a ninguém que apareça para 'buscar'.",
        "ac_remover_app": "URGENTE: desinstale o aplicativo de acesso remoto, desligue a internet do aparelho e confirme com o banco, pelo canal oficial, se houve movimentação. Se possível, restaure o aparelho de fábrica.",
        "ac_trocar_senha": "Troque agora as senhas do banco e do e-mail, encerre sessões/dispositivos conectados e, se informou a senha do cartão, peça a troca ou o bloqueio.",
        "ac_ligar_banco": "Avise o banco, pelo canal oficial, que você foi alvo de golpe, para que ele reforce a proteção da sua conta.",
        "ac_bo": "Registre boletim de ocorrência (delegacia virtual do seu estado) e guarde prints, números de telefone, horários e comprovantes.",
        "ac_monitorar": "Ative alertas de transações e acompanhe o extrato nos próximos dias; desconfie de novos contatos sobre o mesmo assunto.",
        "ac_encerrar": "Encerre o contato agora (desligue ou pare de responder) e não siga nenhuma instrução recebida.",
        "ac_canal_oficial": "Para confirmar, desligue e ligue você mesmo para o número oficial do verso do cartão ou do aplicativo, de preferência de outro aparelho (o golpista pode manter a linha aberta); nunca retorne para o número que te procurou.",
        "ac_bloquear_denunciar": "Bloqueie o número ou remetente e denuncie na própria plataforma (WhatsApp, SMS, e-mail).",
    }
    R = Regra.criar
    FEB, BCB, HEUR, ML = "FEB", "BCB", "HEUR", "ML"
    regras = [
        # --- sinais -> evidências intermediárias ---
        R("I1", "s_urgencia & s_contato_inesperado", "i_pressao", 0.9,
          "contato não solicitado com urgência é a tática central: o golpista quer que você aja antes de pensar.", fonte=HEUR),
        R("I2", "s_urgencia", "i_pressao", 0.6,
          "urgência e ameaça de bloqueio são usadas para impedir que você confirme a história.", fonte=HEUR),
        R("I3", "s_pede_codigo", "i_pede_credencial", 0.9,
          "banco e operadora nunca pedem o código recebido por SMS, token ou aplicativo.", fonte=FEB),
        R("I4", "s_pede_senha", "i_pede_credencial", 0.95,
          "nenhuma instituição legítima pede senha completa, CVV ou senha do cartão.", fonte=FEB),
        R("I5", "s_numero_nao_oficial", "i_canal_nao_oficial", 0.7,
          "o contato não veio de um canal que você possa confirmar como oficial (o número pode ser falsificado).", fonte=FEB),
        R("I6", "s_link", "i_canal_nao_oficial", 0.6,
          "links de 'regularização' ou 'atualização de cadastro' enviados por mensagem são a principal porta do phishing.", fonte=FEB),
        R("I7", "s_pede_transferencia", "i_pede_acao_financeira", 0.95,
          "não existe 'conta segura': nenhum banco manda você transferir dinheiro para protegê-lo.", fonte=FEB),
        R("I8", "s_pede_pagar_taxa", "i_pede_acao_financeira", 0.7,
          "cobrar taxa para liberar benefício ou desbloquear conta é típico de golpe.", fonte=HEUR),
        R("I9", "s_pede_app_remoto", "i_pede_acesso_remoto", 0.95,
          "apps de acesso remoto deixam o golpista operar seu celular e o app do banco (golpe da 'mão fantasma').", fonte=FEB),
        # --- evidências -> suspeita de golpe ---
        R("S1", "i_pressao & i_pede_credencial", "suspeita_golpe", 0.9,
          "pressão de tempo somada a pedido de credencial é o padrão clássico de golpe.", fonte=HEUR),
        R("S2", "i_pede_credencial", "suspeita_golpe", 0.75,
          "pedir código ou senha, por si só, já é sinal forte de golpe.", fonte=FEB),
        R("S3", "i_pede_acao_financeira", "suspeita_golpe", 0.8,
          "pedido de movimentação de dinheiro iniciado pelo atendente é sinal forte de golpe.", fonte=FEB),
        R("S4", "i_pede_acesso_remoto", "suspeita_golpe", 0.9,
          "pedido de acesso remoto é um dos sinais mais graves.", fonte=FEB),
        R("S5", "i_pressao & i_canal_nao_oficial", "suspeita_golpe", 0.7,
          "urgência vinda de canal não oficial indica tentativa de induzir ação precipitada.", fonte=HEUR),
        R("S6", "s_cita_compra_suspeita & i_canal_nao_oficial", "suspeita_golpe", 0.6,
          "'compra suspeita' por canal não oficial é o gancho mais usado pela falsa central.", fonte=FEB),
        R("S7", "s_cita_compra_suspeita & s_contato_inesperado", "suspeita_golpe", 0.4,
          "bancos reais também avisam sobre fraude, por isso o peso é só moderado sem outros sinais.", fonte=HEUR),
        R("S8", "s_pede_entregar_cartao", "suspeita_golpe", 0.95,
          "bancos não enviam motoboy para buscar cartão: isso é golpe.", fonte=FEB),
        R("S9", "s_promessa_beneficio & s_link", "suspeita_golpe", 0.7,
          "prêmio ou benefício acompanhado de link é padrão de phishing.", fonte=HEUR),
        R("S10", "s_promessa_beneficio & s_contato_inesperado", "suspeita_golpe", 0.45,
          "ofertas que você não pediu merecem desconfiança.", fonte=HEUR),
        R("S11", "s_pede_pagar_taxa & s_promessa_beneficio", "suspeita_golpe", 0.8,
          "pagar para receber prêmio ou liberação é o roteiro da falsa oferta.", fonte=HEUR),
        R("S12", "s_voce_iniciou & !s_numero_nao_oficial", "suspeita_golpe", -0.4,
          "você ligou para o número oficial, o que reduz o risco (mas golpistas podem manter a linha aberta; nunca informe código ou senha).", fonte=FEB),
        # --- Fase 1 (modelo de ML) -> suspeita ---
        R("M1", "ml_golpe", "suspeita_golpe", 0.5,
          "o modelo de ML, treinado com mensagens simuladas, achou o texto parecido com golpes (peso moderado: é só um apoio).", fonte=ML),
        R("M2", "!ml_golpe", "suspeita_golpe", -0.2,
          "o modelo achou o texto parecido com mensagens legítimas (peso baixo: ligações de golpe não têm texto).", fonte=ML),
        # --- tipo de golpe ---
        R("T1", "s_cita_compra_suspeita & i_pede_acao_financeira", "t_conta_segura", 0.9,
          "compra suspeita + pedido de transferência é o golpe da conta segura.", fonte=FEB),
        R("T2", "s_pede_transferencia & s_urgencia", "t_conta_segura", 0.6,
          "pedido urgente de transferência lembra o golpe da conta segura.", fonte=HEUR),
        R("T3", "s_pede_entregar_cartao", "t_motoboy", 0.95,
          "retirada do cartão por portador é o golpe do motoboy.", fonte=FEB),
        R("T4", "s_pede_entregar_cartao & s_cita_compra_suspeita", "t_motoboy", 0.9,
          "o motoboy costuma vir após a história da compra suspeita.", fonte=FEB),
        R("T5", "i_pede_acesso_remoto", "t_acesso_remoto", 0.9,
          "instalação de app de acesso remoto caracteriza o golpe do acesso remoto.", fonte=FEB),
        R("T6", "s_pede_codigo", "t_roubo_credenciais", 0.8,
          "o código serve para o golpista entrar na sua conta ou clonar seu WhatsApp.", fonte=FEB),
        R("T7", "s_pede_senha", "t_roubo_credenciais", 0.8,
          "senha ou CVV permitem acesso direto às suas contas e ao cartão.", fonte=FEB),
        R("T8", "s_link & i_canal_nao_oficial", "t_phishing_link", 0.8,
          "link por canal não oficial costuma levar a site falso que captura dados.", fonte=FEB),
        R("T9", "s_link", "t_phishing_link", 0.5,
          "qualquer link de regularização pode levar a site falso.", fonte=HEUR),
        R("T10", "s_promessa_beneficio & s_pede_pagar_taxa", "t_falsa_oferta", 0.9,
          "prêmio condicionado a pagamento de taxa é a falsa oferta.", fonte=HEUR),
        R("T11", "s_promessa_beneficio", "t_falsa_oferta", 0.5,
          "promessa de benefício não solicitado sugere falsa oferta.", fonte=HEUR),
        # --- nível de alerta (usado pelo plano de ação) ---
        R("N1", "suspeita_golpe", "f_alerta", 1.0, "suspeita moderada ou alta.",
          limiar=NIVEL_MODERADO, fonte=HEUR),
        # --- danos já ocorridos (só perguntados se houver alerta) ---
        R("D1", "f_alerta & a_passou_codigo", "i_houve_dano", 1.0),
        R("D2", "f_alerta & a_passou_senha", "i_houve_dano", 1.0),
        R("D3", "f_alerta & a_instalou_app", "i_houve_dano", 1.0),
        R("D4", "f_alerta & a_fez_transferencia", "i_houve_dano", 1.0),
        R("D5", "f_alerta & a_entregou_cartao", "i_houve_dano", 1.0),
        R("D6", "f_alerta & a_clicou_link", "i_houve_dano", 1.0),
        # --- plano de ação ---
        R("A1", "f_alerta & a_fez_transferencia", "ac_contestar_pix", 1.0, fonte=BCB),
        R("A2", "f_alerta & a_entregou_cartao", "ac_bloquear_cartao", 1.0, fonte=FEB),
        R("A3", "f_alerta & a_instalou_app", "ac_remover_app", 1.0, fonte=FEB),
        R("A4", "f_alerta & a_passou_senha", "ac_trocar_senha", 1.0, fonte=FEB),
        R("A5", "f_alerta & a_passou_codigo", "ac_trocar_senha", 1.0, fonte=FEB),
        R("A6", "f_alerta & a_clicou_link", "ac_trocar_senha", 0.9, fonte=HEUR),
        R("A7", "i_houve_dano", "ac_ligar_banco", 1.0, fonte=FEB),
        R("A8", "i_houve_dano", "ac_bo", 1.0, fonte=HEUR),
        R("A9", "i_houve_dano", "ac_monitorar", 1.0, fonte=HEUR),
        R("A10", "f_alerta", "ac_encerrar", 1.0, fonte=FEB),
        R("A11", "f_alerta", "ac_canal_oficial", 1.0, fonte=FEB),
        R("A12", "f_alerta", "ac_bloquear_denunciar", 1.0, fonte=HEUR),
    ]
    saidas = {"suspeita_golpe", *tipos, *acoes}
    return BaseConhecimento(perguntas, regras, rotulos, tipos, acoes, saidas,
                            externos=frozenset({"ml_golpe"}))

_RESULTADO_PADRAO: Optional[ResultadoTreino] = None


def obter_resultado_padrao() -> ResultadoTreino:
    """Treina o modelo padrão uma única vez e reaproveita nas próximas chamadas."""
    global _RESULTADO_PADRAO
    if _RESULTADO_PADRAO is None:
        _RESULTADO_PADRAO = treinar_modelo(construir_dataset())
    return _RESULTADO_PADRAO


def prob_para_cf(p_golpe: float) -> float:
    """O QUE FAZ: converte probabilidade (0 a 1) em fator de certeza (-1 a +1).
    50% -> 0 (modelo não sabe); 100% -> +1; 0% -> -1."""
    return max(-1.0, min(1.0, (p_golpe - 0.5) * 2))


def classificar_mensagem(texto: str, resultado: Optional[ResultadoTreino] = None) -> dict:
    """FASE 1 (machine learning). O QUE FAZ: classifica o texto de uma mensagem.
    Devolve: classe prevista, probabilidade de golpe, atributos calculados e um
    indicador `fora_do_intervalo` (True se algum atributo está fora do que o modelo viu
    no treino, caso em que a previsão é menos confiável)."""
    resultado = resultado or obter_resultado_padrao()
    atrib = extrair_atributos(texto)
    x = pd.DataFrame([atrib])[ATRIBUTOS]
    probas = dict(zip(resultado.modelo.classes_, resultado.modelo.predict_proba(x)[0]))
    p_golpe = float(probas.get("golpe", 0.0))
    fora = any(not (resultado.X_treino[c].min() <= atrib[c] <= resultado.X_treino[c].max())
               for c in ATRIBUTOS)
    return {"classe": "golpe" if p_golpe >= 0.5 else "legitimo",
            "prob_golpe": p_golpe, "atributos": atrib, "fora_do_intervalo": fora}


@dataclass
class Diagnostico:
    """O QUE É: o resultado final entregue ao usuário.
    suspeita (0 a 1), nivel (ALTO/MODERADO/BAIXO/INCOMPLETO), tipos [(nome, certeza)],
    acoes (em ordem de prioridade), explicacao (texto), perguntas_feitas, ml (saída da
    Fase 1, se houve texto) e aviso (sempre presente: revisão humana)."""
    suspeita: float
    nivel: str
    tipos: list
    acoes: list
    explicacao: str
    perguntas_feitas: int
    ml: Optional[dict] = None
    aviso: str = ""


ORIENTACAO_BAIXO = ("Não há indícios fortes de golpe nas suas respostas. Mesmo assim: "
                    "banco e operadora nunca pedem senha, CVV nem códigos recebidos por "
                    "SMS/aplicativo. Na dúvida, confirme pelo canal oficial.")
ORIENTACAO_INCOMPLETO = ("Informações insuficientes para concluir. Responda mais perguntas "
                         "ou, na dúvida, confirme pelo canal oficial e não compartilhe "
                         "códigos nem senhas.")


def classificar_nivel(cf: float, sinais_conhecidos: int) -> str:
    """O QUE FAZ: transforma o fator de certeza em nível: >=0.7 ALTO; >=0.4 MODERADO;
    abaixo disso BAIXO, mas só se houver informação suficiente (senão INCOMPLETO).
    Isso evita declarar "seguro" quando o usuário respondeu quase tudo "não sei"."""
    if cf >= NIVEL_ALTO:
        return "ALTO"
    if cf >= NIVEL_MODERADO:
        return "MODERADO"
    return "INCOMPLETO" if sinais_conhecidos < MIN_INFO else "BAIXO"


def diagnosticar(bc: BaseConhecimento, provedor: Provedor,
                 motor: Optional[MotorInferencia] = None) -> tuple:
    """FASE 2 (sistema especialista). O QUE FAZ: objetivo 1) suspeita de golpe;
    objetivo 2) tipo de golpe; objetivo 3) plano de ação. Cada objetivo é resolvido por
    encadeamento para trás, perguntando ao usuário (`provedor`) apenas o necessário.
    Perguntas sobre danos (a_*) só aparecem quando há alerta."""
    motor = motor or MotorInferencia(bc)
    suspeita = motor.avaliar("suspeita_golpe", provedor) or 0.0
    conhecidos = sum(1 for f in motor.mt.fatos
                     if f.startswith("s_") and motor.mt.origem[f] == "usuário")
    nivel = classificar_nivel(suspeita, conhecidos)

    tipos, acoes = [], []
    if nivel in ("ALTO", "MODERADO"):
        for t, nome in bc.tipos.items():
            cf = motor.avaliar(t, provedor) or 0.0
            if cf >= NIVEL_MODERADO:
                tipos.append((nome, cf))
        tipos.sort(key=lambda x: -x[1])
        for a, texto in bc.acoes.items():
            if (motor.avaliar(a, provedor) or 0.0) >= LIMIAR:
                acoes.append(texto)
    elif nivel == "BAIXO":
        acoes.append(ORIENTACAO_BAIXO)
    else:
        acoes.append(ORIENTACAO_INCOMPLETO)

    return Diagnostico(max(suspeita, 0.0), nivel, tipos, acoes,
                       motor.explicar(), len(motor.perguntadas)), motor


def analisar_contato(bc: BaseConhecimento, provedor: Provedor, texto: Optional[str] = None,
                     resultado: Optional[ResultadoTreino] = None) -> tuple:
    """INTEGRAÇÃO das duas fases. O QUE FAZ: se há texto, roda o modelo de ML e coloca a
    previsão na Memória de Trabalho como o fato dinâmico `ml_golpe`; depois roda o sistema
    especialista. Devolve (diagnostico, motor)."""
    motor = MotorInferencia(bc)
    ml = None
    if texto and texto.strip():
        ml = classificar_mensagem(texto, resultado)
        motor.mt.afirmar("ml_golpe", prob_para_cf(ml["prob_golpe"]), "modelo de ML")
    diag, motor = diagnosticar(bc, provedor, motor)
    diag.ml = ml
    diag.aviso = ("Entrada fora dos intervalos observados no treino: a leitura do modelo "
                  "pode ser menos confiável. Orientação sujeita a revisão humana."
                  if ml and ml["fora_do_intervalo"]
                  else "Exemplo didático; orientação sujeita a revisão humana.")
    return diag, motor

def provedor_cli(fato: str, pergunta: str) -> Optional[str]:
    """Pergunta ao usuário e converte a resposta: s/sim -> "sim"; n/não -> "nao"; Enter -> None (não sei)."""
    while True:
        r = input(f"{pergunta} [s/n, Enter = não sei]: ").strip().lower()
        if r == "":
            return None
        if r in ("s", "sim"):
            return "sim"
        if r in ("n", "nao", "não"):
            return "nao"
        print("  Responda s, n ou Enter.")


def mostrar(d: Diagnostico) -> None:
    """Imprime o resultado: grau de suspeita, leitura do ML, tipo, plano de ação, explicação e aviso."""
    print("\n" + "=" * 62)
    print(f"GRAU DE SUSPEITA: {d.nivel}" +
          (f" ({d.suspeita:.0%})" if d.nivel != "INCOMPLETO" else ""))
    if d.ml:
        print(f"Modelo de ML (texto): {d.ml['classe']} ({d.ml['prob_golpe']:.0%} de chance de golpe)")
    if d.tipos:
        print("\nTipo provável:")
        for nome, cf in d.tipos:
            print(f"  - {nome} ({cf:.0%})")
    print("\nO que fazer:")
    for i, a in enumerate(d.acoes, 1):
        print(f"  {i}. {a}")
    print("\n" + d.explicacao)
    print(f"\nAviso: {d.aviso}")
    print("=" * 62)


def main() -> None:
    """Ciclo de consultas: (opcional) cola o texto da mensagem; responde às perguntas; vê o resultado."""
    bc = criar_bc_golpes()
    problemas = {k: v for k, v in bc.verificar().items() if v}
    if problemas:
        print("Aviso: falhas na base de conhecimento:", problemas)
    print("=== Triagem de golpes: falsa central de atendimento ===")
    print("Ferramenta educacional de apoio. Não substitui o banco ou a operadora.\n")
    while True:
        texto = input("Cole o texto da mensagem recebida (Enter para pular): ")
        d, _ = analisar_contato(bc, provedor_cli, texto)
        mostrar(d)
        if input("\nNova consulta? [s/n]: ").strip().lower() not in ("s", "sim"):
            break


if __name__ == "__main__":
    main()
