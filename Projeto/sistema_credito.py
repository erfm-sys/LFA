#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Especialista - Análise de Crédito Bancário e Concessão de Empréstimos
Disciplina: Inteligência Artificial e Linguagens Formais e Autômatos (IA/LFA)
Professora: Kadidja Valéria

Arquitetura (separação estrita):
  1. BaseConhecimento  -> fatos observáveis e regras SE-ENTÃO (somente dados declarativos)
  2. MemoriaTrabalho   -> fatos já informados na sessão (s / n / ?)
  3. MotorInferencia   -> raciocínio dedutivo: avalia regras sobre a memória, poda hipóteses
                          incompatíveis e DECIDE quais perguntas são necessárias
  4. InterfaceConsole  -> entrada de fatos, validação e exibição das justificativas

O motor não conhece o console nem as regras de crédito: ele recebe um callback
(obter_fato) para pedir fatos ausentes e opera sobre qualquer base de regras.
Não há if/else de domínio: trocar a BaseConhecimento troca o domínio inteiro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

# Valor de um fato: True = sim, False = não, None = desconhecido ("?")
Valor = Optional[bool]


class Veredito(Enum):
    CONFIRMADA = "CONFIRMADA"
    REFUTADA = "REFUTADA"
    INDETERMINADA = "INDETERMINADA"


class EstadoRegra(Enum):
    CONFIRMADA = "confirmada"   # todas as premissas verdadeiras
    REFUTADA = "refutada"       # alguma premissa falsa
    BLOQUEADA = "bloqueada"     # nenhuma falsa, mas alguma premissa desconhecida (?)
    PENDENTE = "pendente"       # faltam fatos a perguntar, sem contradição até aqui


# ============================================================================
# 1. BASE DE CONHECIMENTO (somente declarações)
# ============================================================================
@dataclass(frozen=True)
class Fato:
    nome: str
    pergunta: str
    significado: str


@dataclass(frozen=True)
class Regra:
    id: str
    premissas: Tuple[Tuple[str, bool], ...]  # (nome_do_fato, valor_esperado)
    conclusao: str                           # chave em BaseConhecimento.DECISOES
    fonte: str


class BaseConhecimento:
    """Conhecimento declarativo: 3 fatos observáveis e 5 regras de produção."""

    FATOS: Dict[str, Fato] = {
        "score_credito_bom": Fato(
            "score_credito_bom",
            "O score de crédito do cliente é bom (acima do corte da política)?",
            "s = score acima do corte; n = abaixo do corte; ? = score não consultado",
        ),
        "possui_restricao_cadastral": Fato(
            "possui_restricao_cadastral",
            "O cliente possui restrição cadastral (negativação, protesto, cheque sem fundos)?",
            "s = há restrição ativa; n = nada consta; ? = consulta não realizada",
        ),
        "renda_compativel": Fato(
            "renda_compativel",
            "A renda comprovada é compatível com a parcela solicitada?",
            "s = parcela cabe na renda; n = não cabe; ? = renda não comprovada ainda",
        ),
    }

    DECISOES: Dict[str, str] = {
        "APROVACAO_IMEDIATA": "Aprovação Imediata do Crédito",
        "NEGACAO_AUTOMATICA": "Negação Automática",
        "LIMITE_REDUZIDO": "Oferta de Limite Reduzido",
        "ANALISE_MANUAL": "Encaminhar para Análise Manual do Gerente",
        "REEDUCACAO_FINANCEIRA": "Encaminhar ao Programa de Reeducação Financeira",
    }

    REGRAS: Tuple[Regra, ...] = (
        Regra("R1",
              (("score_credito_bom", True),
               ("possui_restricao_cadastral", False),
               ("renda_compativel", True)),
              "APROVACAO_IMEDIATA",
              "Os 5 Cs do crédito (caráter, capacidade): bom histórico + capacidade de pagamento"),
        Regra("R2",
              (("possui_restricao_cadastral", True),),
              "NEGACAO_AUTOMATICA",
              "Política interna de crédito / compliance: restrição ativa impede a concessão"),
        Regra("R3",
              (("score_credito_bom", True),
               ("possui_restricao_cadastral", False),
               ("renda_compativel", False)),
              "LIMITE_REDUZIDO",
              "Gestão de risco: bom pagador sem capacidade total recebe exposição menor"),
        Regra("R4",
              (("score_credito_bom", False),
               ("possui_restricao_cadastral", False),
               ("renda_compativel", True)),
              "ANALISE_MANUAL",
              "Alçada do gerente: capacidade existe, mas o histórico exige julgamento humano"),
        Regra("R5",
              (("score_credito_bom", False),
               ("possui_restricao_cadastral", False),
               ("renda_compativel", False)),
              "REEDUCACAO_FINANCEIRA",
              "Educação financeira: sem histórico e sem capacidade, prioriza-se orientação"),
    )

    def regras_para(self, objetivo: str) -> List[Regra]:
        return [r for r in self.REGRAS if r.conclusao == objetivo]

    def objetivos(self) -> List[str]:
        return list(self.DECISOES)


# ============================================================================
# 2. MEMÓRIA DE TRABALHO
# ============================================================================
class MemoriaTrabalho:
    """Fatos informados na sessão. Ausência da chave = ainda não perguntado."""

    def __init__(self) -> None:
        self._fatos: Dict[str, Valor] = {}

    def conhece(self, nome: str) -> bool:
        return nome in self._fatos

    def valor(self, nome: str) -> Valor:
        return self._fatos[nome]

    def registrar(self, nome: str, valor: Valor) -> None:
        self._fatos[nome] = valor

    def limpar(self) -> None:
        self._fatos.clear()

    def itens(self) -> Dict[str, Valor]:
        return dict(self._fatos)


# ============================================================================
# 3. MOTOR DE INFERÊNCIA
# ============================================================================
@dataclass
class Resultado:
    objetivo: Optional[str]            # decisão provada/deduzida (None se nada foi deduzido)
    veredito: Veredito
    regra_confirmada: Optional[str] = None
    rastro: List[str] = field(default_factory=list)
    perguntas_feitas: List[str] = field(default_factory=list)


def _txt(valor: Valor) -> str:
    return {True: "sim", False: "não", None: "desconhecido"}[valor]


class MotorInferencia:
    """
    Raciocínio dedutivo sobre regras declarativas.

    Princípios:
      * Avaliação simbólica: o estado de cada regra é DEDUZIDO da memória de trabalho
        (confirmada / refutada / bloqueada / pendente) sem perguntar nada.
      * Poda: regra com premissa falsa é descartada; premissas restantes não são perguntadas.
      * Pergunta dirigida: o motor escolhe o próximo fato a perguntar pelo maior alcance,
        isto é, o fato que aparece em mais regras ainda vivas (resposta mais informativa).
      * Dois modos: provar(objetivo) = backward chaining; recomendar() = todas as decisões
        como hipóteses simultâneas, podadas conforme os fatos chegam.
    """

    def __init__(self, base: BaseConhecimento, memoria: MemoriaTrabalho,
                 obter_fato: Callable[[Fato], Valor]) -> None:
        self.base = base
        self.memoria = memoria
        self.obter_fato = obter_fato

    # ---------- deduções sobre a memória (nunca perguntam) ----------
    def estado_da_regra(self, regra: Regra) -> EstadoRegra:
        refutada = bloqueada = pendente = False
        for nome, esperado in regra.premissas:
            if not self.memoria.conhece(nome):
                pendente = True
                continue
            valor = self.memoria.valor(nome)
            if valor is None:
                bloqueada = True
            elif valor != esperado:
                refutada = True
        if refutada:
            return EstadoRegra.REFUTADA
        if bloqueada:
            return EstadoRegra.BLOQUEADA
        if pendente:
            return EstadoRegra.PENDENTE
        return EstadoRegra.CONFIRMADA

    def _regras_vivas(self) -> List[Regra]:
        vivas = (EstadoRegra.PENDENTE, EstadoRegra.CONFIRMADA)
        return [r for r in self.base.REGRAS if self.estado_da_regra(r) in vivas]

    @staticmethod
    def _alcance(nome: str, universo: List[Regra]) -> int:
        return sum(1 for r in universo if any(n == nome for n, _ in r.premissas))

    def _proxima_pergunta(self, candidatas: List[Regra],
                          universo: List[Regra]) -> Tuple[str, int]:
        """Escolhe o fato ainda desconhecido de maior alcance (empate: ordem da base)."""
        pendentes: List[str] = []
        for r in candidatas:
            for nome, _ in r.premissas:
                if not self.memoria.conhece(nome) and nome not in pendentes:
                    pendentes.append(nome)
        ordem = {n: i for i, n in enumerate(self.base.FATOS)}
        nome = min(pendentes, key=lambda n: (-self._alcance(n, universo), ordem[n]))
        return nome, self._alcance(nome, universo)

    def _perguntar(self, nome: str, alcance: int, rastro: List[str],
                   perguntas: List[str], recuo: str) -> None:
        valor = self.obter_fato(self.base.FATOS[nome])
        self.memoria.registrar(nome, valor)
        perguntas.append(nome)
        rastro.append(f"{recuo}[pergunta] '{nome}' (aparece em {alcance} regra(s) viva(s)) "
                      f"-> resposta: {_txt(valor)}.")

    # ---------- modo 1: backward chaining ----------
    def provar(self, objetivo: str) -> Resultado:
        rastro: List[str] = [f"HIPÓTESE: '{self.base.DECISOES[objetivo]}'"]
        perguntas: List[str] = []
        vereditos: List[Veredito] = []
        confirmada: Optional[str] = None

        for regra in self.base.regras_para(objetivo):
            rastro.append(f"  Regra {regra.id} concluiria a hipótese; premissas a provar:")
            for nome, esperado in regra.premissas:
                if self.memoria.conhece(nome):
                    rastro.append(f"    [memória] '{nome}' já conhecido: "
                                  f"{_txt(self.memoria.valor(nome))} (sem nova pergunta).")

            while self.estado_da_regra(regra) is EstadoRegra.PENDENTE:
                nome, alc = self._proxima_pergunta([regra], self._regras_vivas())
                self._perguntar(nome, alc, rastro, perguntas, "    ")

            estado = self.estado_da_regra(regra)
            self._explicar(regra, estado, rastro)
            if estado is EstadoRegra.CONFIRMADA:
                vereditos.append(Veredito.CONFIRMADA)
                confirmada = regra.id
                break
            vereditos.append(Veredito.INDETERMINADA if estado is EstadoRegra.BLOQUEADA
                             else Veredito.REFUTADA)

        if confirmada:
            final = Veredito.CONFIRMADA
        elif Veredito.INDETERMINADA in vereditos:
            final = Veredito.INDETERMINADA
        else:
            final = Veredito.REFUTADA
        rastro.append(f"  => Hipótese {final.value}.")
        return Resultado(objetivo, final, confirmada, rastro, perguntas)

    def _explicar(self, regra: Regra, estado: EstadoRegra, rastro: List[str]) -> None:
        rastro.append(f"  Verificação das premissas de {regra.id}:")
        for passo, (nome, esperado) in enumerate(regra.premissas, start=1):
            alvo = f"{nome} = {_txt(esperado)}"
            if not self.memoria.conhece(nome):
                rastro.append(f"    {passo}. ({alvo}): NÃO AVALIADA (desnecessária, regra já decidida).")
                continue
            valor = self.memoria.valor(nome)
            if valor is None:
                rastro.append(f"    {passo}. ({alvo}): DESCONHECIDA -> regra não pode ser comprovada.")
            elif valor != esperado:
                rastro.append(f"    {passo}. ({alvo}): FALSA (informado: {_txt(valor)}) "
                              f"-> regra descartada (curto-circuito).")
            else:
                rastro.append(f"    {passo}. ({alvo}): VERDADEIRA.")
        if estado is EstadoRegra.CONFIRMADA:
            rastro.append(f"    Todas verdadeiras -> {regra.id} CONFIRMADA.")

    # ---------- modo 2: dedução autônoma ----------
    def recomendar(self) -> Resultado:
        rastro: List[str] = ["MODO AUTÔNOMO: todas as decisões são hipóteses; "
                             "o motor poda regras e escolhe as perguntas."]
        perguntas: List[str] = []
        rotulo = lambda rs: ", ".join(r.id for r in rs) or "nenhuma"

        while True:
            estados = {r.id: self.estado_da_regra(r) for r in self.base.REGRAS}
            conf = [r for r in self.base.REGRAS if estados[r.id] is EstadoRegra.CONFIRMADA]
            vivas = [r for r in self.base.REGRAS if estados[r.id] is EstadoRegra.PENDENTE]
            ref = [r for r in self.base.REGRAS if estados[r.id] is EstadoRegra.REFUTADA]
            blo = [r for r in self.base.REGRAS if estados[r.id] is EstadoRegra.BLOQUEADA]
            rastro.append(f"  Estado: pendentes [{rotulo(vivas)}] | descartadas [{rotulo(ref)}] "
                          f"| bloqueadas por dado desconhecido [{rotulo(blo)}]")
            if conf:
                r = conf[0]
                rastro.append(f"  => {r.id} confirmada: deduz-se '{self.base.DECISOES[r.conclusao]}'.")
                return Resultado(r.conclusao, Veredito.CONFIRMADA, r.id, rastro, perguntas)
            if not vivas:
                break
            nome, alc = self._proxima_pergunta(vivas, vivas)
            self._perguntar(nome, alc, rastro, perguntas, "  ")

        final = Veredito.INDETERMINADA if blo else Veredito.REFUTADA
        rastro.append("  => Nenhuma decisão pôde ser deduzida: restam apenas regras "
                      "descartadas ou bloqueadas por falta de dados.")
        return Resultado(None, final, None, rastro, perguntas)


# ============================================================================
# 4. INTERFACE COM O USUÁRIO (console)
# ============================================================================
class InterfaceConsole:
    ENTRADAS: Dict[str, Valor] = {
        "s": True, "sim": True,
        "n": False, "nao": False, "não": False,
        "?": None, "nd": None, "desconhecido": None,
    }

    def __init__(self, base: BaseConhecimento, memoria: MemoriaTrabalho) -> None:
        self.base = base
        self.memoria = memoria

    # ---- entrada de fatos (callback entregue ao motor) ----
    def perguntar_fato(self, fato: Fato) -> Valor:
        print(f"\n  >> {fato.pergunta}")
        print(f"     ({fato.significado})")
        while True:
            bruto = input("     Resposta [s/n/?]: ").strip().lower()
            if bruto in self.ENTRADAS:
                return self.ENTRADAS[bruto]
            print("     Entrada inválida. Digite 's' (sim), 'n' (não) ou '?' (não informado).")

    # ---- saída ----
    def exibir_resultado(self, res: Resultado) -> None:
        print("\n" + "=" * 70)
        print("JUSTIFICATIVA (rastro do raciocínio)")
        print("-" * 70)
        for linha in res.rastro:
            print(linha)
        print("-" * 70)
        if res.objetivo is None:
            print("CONCLUSÃO: nenhuma decisão pôde ser deduzida com os dados informados.")
        else:
            nome = self.base.DECISOES[res.objetivo]
            if res.veredito is Veredito.CONFIRMADA:
                print(f"CONCLUSÃO: {nome} -> CONFIRMADA pela regra {res.regra_confirmada}.")
            elif res.veredito is Veredito.REFUTADA:
                print(f"CONCLUSÃO: {nome} -> NÃO se aplica a este cliente.")
            else:
                print(f"CONCLUSÃO: {nome} -> INDETERMINADA (faltam dados para decidir).")
        print(f"Perguntas feitas nesta consulta: {len(res.perguntas_feitas)}")
        print("=" * 70)

    def exibir_memoria(self) -> None:
        itens = self.memoria.itens()
        print("\nMemória de trabalho:")
        if not itens:
            print("  (vazia)")
        for nome, valor in itens.items():
            print(f"  - {nome}: {_txt(valor)}")

    # ---- fluxo de menu ----
    def escolher_objetivo(self) -> Optional[str]:
        objetivos = self.base.objetivos()
        print("\nEscolha a decisão (hipótese) a ser provada:")
        for i, chave in enumerate(objetivos, start=1):
            print(f"  {i}) {self.base.DECISOES[chave]}")
        print("  0) Voltar")
        while True:
            op = input("Opção: ").strip()
            if op == "0":
                return None
            if op.isdigit() and 1 <= int(op) <= len(objetivos):
                return objetivos[int(op) - 1]
            print("Opção inválida.")

    def executar(self, motor: MotorInferencia) -> None:
        print("=== SISTEMA ESPECIALISTA: ANÁLISE DE CRÉDITO BANCÁRIO ===")
        while True:
            print("\nMENU")
            print("  1) Provar uma decisão específica (encadeamento para trás)")
            print("  2) Deduzir a recomendação automaticamente (o motor escolhe as perguntas)")
            print("  3) Ver memória de trabalho")
            print("  4) Nova consulta (limpar memória)")
            print("  0) Sair")
            op = input("Opção: ").strip()
            if op == "1":
                objetivo = self.escolher_objetivo()
                if objetivo:
                    self.exibir_resultado(motor.provar(objetivo))
            elif op == "2":
                self.exibir_resultado(motor.recomendar())
            elif op == "3":
                self.exibir_memoria()
            elif op == "4":
                self.memoria.limpar()
                print("Memória limpa. Nova consulta iniciada.")
            elif op == "0":
                print("Encerrando.")
                break
            else:
                print("Opção inválida.")


def main() -> None:
    base = BaseConhecimento()
    memoria = MemoriaTrabalho()
    interface = InterfaceConsole(base, memoria)
    motor = MotorInferencia(base, memoria, obter_fato=interface.perguntar_fato)
    interface.executar(motor)


if __name__ == "__main__":
    main()
