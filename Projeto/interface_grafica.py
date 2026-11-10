#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface gráfica (Tkinter) do Sistema Especialista de Crédito Bancário.

Reaproveita, SEM alterações, a base de conhecimento, a memória de trabalho e o
motor de inferência de sistema_credito.py. Só a camada de interface muda:
o motor pede fatos por meio de um callback e, aqui, esse callback abre uma
janela com os botões Sim / Não / Não informado.

Execução:  python interface_grafica.py   (os dois .py devem estar na mesma pasta)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

from sistema_credito import (
    BaseConhecimento, MemoriaTrabalho, MotorInferencia,
    EstadoRegra, Fato, Resultado, Veredito,
)

_CANCELADO = object()  # sentinela: usuário fechou a janela de pergunta


class ConsultaCancelada(Exception):
    """Interrompe o motor quando o usuário fecha a janela de pergunta."""


def _txt(valor):
    return {True: "sim", False: "não", None: "desconhecido"}[valor]


# ============================================================================
# Janela modal de pergunta (substitui o input() do console)
# ============================================================================
class DialogoFato(tk.Toplevel):
    def __init__(self, mestre: tk.Tk, fato: Fato) -> None:
        super().__init__(mestre)
        self.title("O motor precisa de um dado")
        self.resizable(False, False)
        self.transient(mestre)
        self.resultado = _CANCELADO

        corpo = ttk.Frame(self, padding=18)
        corpo.pack(fill="both", expand=True)

        ttk.Label(corpo, text="O motor de inferência pergunta:",
                  font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
        ttk.Label(corpo, text=fato.pergunta, wraplength=440,
                  font=("TkDefaultFont", 12)).pack(anchor="w", pady=(6, 4))
        ttk.Label(corpo, text=fato.significado, wraplength=440,
                  foreground="#555555").pack(anchor="w", pady=(0, 14))

        botoes = ttk.Frame(corpo)
        botoes.pack(fill="x")
        for texto, valor, atalho in (("Sim  (s)", True, "s"),
                                     ("Não  (n)", False, "n"),
                                     ("Não informado  (?)", None, "question")):
            ttk.Button(botoes, text=texto,
                       command=lambda v=valor: self._responder(v)
                       ).pack(side="left", expand=True, fill="x", padx=3)
            self.bind(f"<KeyPress-{atalho}>", lambda e, v=valor: self._responder(v))
        self.bind("<KeyPress-S>", lambda e: self._responder(True))
        self.bind("<KeyPress-N>", lambda e: self._responder(False))
        self.bind("<Escape>", lambda e: self._cancelar())
        self.protocol("WM_DELETE_WINDOW", self._cancelar)

        # centraliza sobre a janela principal
        self.update_idletasks()
        x = mestre.winfo_rootx() + (mestre.winfo_width() - self.winfo_width()) // 2
        y = mestre.winfo_rooty() + (mestre.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass
        self.focus_force()

    def _responder(self, valor) -> None:
        self.resultado = valor
        self.destroy()

    def _cancelar(self) -> None:
        self.resultado = _CANCELADO
        self.destroy()


# ============================================================================
# Janela principal
# ============================================================================
class App(tk.Tk):
    ROTULO_ESTADO = {
        EstadoRegra.CONFIRMADA: "✔ Confirmada",
        EstadoRegra.REFUTADA: "✘ Refutada (descartada)",
        EstadoRegra.BLOQUEADA: "? Bloqueada (dado desconhecido)",
        EstadoRegra.PENDENTE: "… Pendente (faltam dados)",
    }
    COR_VEREDITO = {
        Veredito.CONFIRMADA: ("#1b7f3b", "#d8f3e0"),
        Veredito.REFUTADA: ("#9b1c1c", "#fde2e2"),
        Veredito.INDETERMINADA: ("#8a5a00", "#fff1cc"),
    }

    def __init__(self) -> None:
        super().__init__()
        self.title("Sistema Especialista - Análise de Crédito Bancário")
        self.geometry("1120x760")
        self.minsize(980, 660)

        # --- núcleo do sistema (inalterado) ---
        self.base = BaseConhecimento()
        self.memoria = MemoriaTrabalho()
        self.motor = MotorInferencia(self.base, self.memoria, obter_fato=self._perguntar)

        self.modo = tk.StringVar(value="provar")
        self.nome_para_chave = {v: k for k, v in self.base.DECISOES.items()}

        ttk.Style(self).theme_use("clam")
        self._montar()
        self._atualizar_paineis()

    # ------------------------------------------------------------------
    # Montagem da tela
    # ------------------------------------------------------------------
    def _montar(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # --- barra de controle ---
        barra = ttk.LabelFrame(self, text=" Consulta ", padding=10)
        barra.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        ttk.Radiobutton(barra, text="Provar uma decisão (encadeamento para trás)",
                        variable=self.modo, value="provar",
                        command=self._ajustar_modo).grid(row=0, column=0, sticky="w")
        self.combo = ttk.Combobox(barra, state="readonly", width=52,
                                  values=list(self.nome_para_chave))
        self.combo.current(0)
        self.combo.grid(row=0, column=1, padx=10)
        ttk.Radiobutton(barra, text="Deduzir a recomendação automaticamente "
                                    "(o motor escolhe as perguntas)",
                        variable=self.modo, value="autonomo",
                        command=self._ajustar_modo).grid(row=1, column=0, columnspan=2,
                                                          sticky="w", pady=(6, 0))
        ttk.Button(barra, text="▶ Executar", command=self._executar
                   ).grid(row=0, column=2, rowspan=2, padx=(20, 6), ipadx=12, ipady=6)
        ttk.Button(barra, text="↺ Nova consulta", command=self._nova_consulta
                   ).grid(row=0, column=3, rowspan=2, padx=6, ipadx=6, ipady=6)

        # --- tabela de regras (estado deduzido ao vivo) ---
        quadro_regras = ttk.LabelFrame(
            self, text=" Base de conhecimento: regras e estado deduzido pelo motor ",
            padding=6)
        quadro_regras.grid(row=1, column=0, sticky="ew", padx=10, pady=4)
        quadro_regras.columnconfigure(0, weight=1)
        self.tabela = ttk.Treeview(quadro_regras, columns=("regra", "se", "entao", "estado"),
                                   show="headings", height=5)
        for col, titulo, larg in (("regra", "Regra", 50), ("se", "SE (premissas)", 470),
                                  ("entao", "ENTÃO (decisão)", 270),
                                  ("estado", "Estado", 220)):
            self.tabela.heading(col, text=titulo)
            self.tabela.column(col, width=larg, anchor="w", stretch=(col != "regra"))
        self.tabela.grid(row=0, column=0, sticky="ew")
        self.tabela.tag_configure("confirmada", background="#d8f3e0", foreground="#14532d")
        self.tabela.tag_configure("refutada", background="#f1f1f1", foreground="#8a8a8a")
        self.tabela.tag_configure("bloqueada", background="#fff1cc", foreground="#7a4d00")
        self.tabela.tag_configure("pendente", background="#e6f0ff", foreground="#1e3a8a")

        # --- memória (esquerda) e justificativa (direita) ---
        meio = ttk.Frame(self)
        meio.grid(row=2, column=0, sticky="nsew", padx=10, pady=4)
        meio.columnconfigure(1, weight=1)
        meio.rowconfigure(0, weight=1)

        quadro_mem = ttk.LabelFrame(meio, text=" Memória de trabalho ", padding=10)
        quadro_mem.grid(row=0, column=0, sticky="ns", padx=(0, 8))
        self.rotulos_fatos = {}
        for i, nome in enumerate(self.base.FATOS):
            ttk.Label(quadro_mem, text=nome, font=("TkDefaultFont", 9, "bold")
                      ).grid(row=2 * i, column=0, sticky="w", pady=(8 if i else 0, 0))
            lbl = tk.Label(quadro_mem, text="não perguntado", width=22, anchor="w",
                           padx=8, pady=3, relief="flat")
            lbl.grid(row=2 * i + 1, column=0, sticky="w")
            self.rotulos_fatos[nome] = lbl

        quadro_just = ttk.LabelFrame(meio, text=" Justificativa (rastro do raciocínio) ",
                                     padding=6)
        quadro_just.grid(row=0, column=1, sticky="nsew")
        quadro_just.columnconfigure(0, weight=1)
        quadro_just.rowconfigure(0, weight=1)
        self.texto = tk.Text(quadro_just, wrap="word", state="disabled",
                             font=tkfont.nametofont("TkFixedFont"), padx=8, pady=6)
        rolagem = ttk.Scrollbar(quadro_just, command=self.texto.yview)
        self.texto.configure(yscrollcommand=rolagem.set)
        self.texto.grid(row=0, column=0, sticky="nsew")
        rolagem.grid(row=0, column=1, sticky="ns")
        for tag, cor, negrito in (("titulo", "#1e3a8a", True), ("pergunta", "#7c3aed", False),
                                  ("ok", "#15803d", False), ("falsa", "#b91c1c", False),
                                  ("desc", "#b45309", False), ("nao", "#6b7280", False),
                                  ("conclusao", "#111827", True)):
            fonte = tkfont.nametofont("TkFixedFont").copy()
            if negrito:
                fonte.configure(weight="bold")
            self.texto.tag_configure(tag, foreground=cor, font=fonte)

        # --- faixa de conclusão ---
        self.conclusao = tk.Label(self, text="Escolha o modo e clique em Executar.",
                                  font=("TkDefaultFont", 13, "bold"), anchor="w",
                                  padx=14, pady=10, bg="#e5e7eb")
        self.conclusao.grid(row=3, column=0, sticky="ew", padx=10, pady=(4, 10))

    # ------------------------------------------------------------------
    # Atualização visual
    # ------------------------------------------------------------------
    def _ajustar_modo(self) -> None:
        self.combo.configure(state="readonly" if self.modo.get() == "provar" else "disabled")

    def _atualizar_paineis(self) -> None:
        # regras: o estado é DEDUZIDO pelo motor a partir da memória, sem perguntar nada
        self.tabela.delete(*self.tabela.get_children())
        for r in self.base.REGRAS:
            estado = self.motor.estado_da_regra(r)
            se = "  E  ".join(f"{n} = {'s' if v else 'n'}" for n, v in r.premissas)
            self.tabela.insert("", "end", tags=(estado.value,),
                               values=(r.id, se, self.base.DECISOES[r.conclusao],
                                       self.ROTULO_ESTADO[estado]))
        # memória de trabalho
        for nome, lbl in self.rotulos_fatos.items():
            if not self.memoria.conhece(nome):
                lbl.configure(text="não perguntado", bg="#e5e7eb", fg="#4b5563")
            else:
                valor = self.memoria.valor(nome)
                texto, bg, fg = {True: ("sim (s)", "#d8f3e0", "#14532d"),
                                 False: ("não (n)", "#fde2e2", "#7f1d1d"),
                                 None: ("desconhecido (?)", "#fff1cc", "#7a4d00")}[valor]
                lbl.configure(text=texto, bg=bg, fg=fg)

    def _escrever(self, linhas) -> None:
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        for linha in linhas:
            tag = ()
            if linha.startswith(("HIPÓTESE", "MODO")):
                tag = ("titulo",)
            elif "[pergunta]" in linha:
                tag = ("pergunta",)
            elif "VERDADEIRA" in linha or "CONFIRMADA" in linha and "=>" in linha:
                tag = ("ok",)
            elif "FALSA" in linha or "descartada" in linha and "Estado" not in linha:
                tag = ("falsa",)
            elif "DESCONHECIDA" in linha:
                tag = ("desc",)
            elif "NÃO AVALIADA" in linha:
                tag = ("nao",)
            elif linha.strip().startswith("=>"):
                tag = ("conclusao",)
            self.texto.insert("end", linha + "\n", tag)
        self.texto.configure(state="disabled")

    def _exibir(self, res: Resultado) -> None:
        self._escrever(res.rastro)
        fg, bg = self.COR_VEREDITO[res.veredito]
        if res.objetivo is None:
            msg = "Nenhuma decisão pôde ser deduzida com os dados informados."
        else:
            nome = self.base.DECISOES[res.objetivo]
            if res.veredito is Veredito.CONFIRMADA:
                msg = f"{nome}  →  CONFIRMADA pela regra {res.regra_confirmada}"
            elif res.veredito is Veredito.REFUTADA:
                msg = f"{nome}  →  NÃO se aplica a este cliente"
            else:
                msg = f"{nome}  →  INDETERMINADA (faltam dados para decidir)"
        msg += f"      [perguntas feitas: {len(res.perguntas_feitas)}]"
        self.conclusao.configure(text=msg, fg=fg, bg=bg)

    # ------------------------------------------------------------------
    # Callback do motor e ações dos botões
    # ------------------------------------------------------------------
    def _perguntar(self, fato: Fato):
        """Chamado pelo motor sempre que ele precisa de um fato que não conhece."""
        dialogo = DialogoFato(self, fato)
        self.wait_window(dialogo)
        if dialogo.resultado is _CANCELADO:
            raise ConsultaCancelada()
        # grava já na memória para as regras mudarem de cor ao vivo
        # (o motor registra o mesmo valor em seguida; a operação é idempotente)
        self.memoria.registrar(fato.nome, dialogo.resultado)
        self._atualizar_paineis()
        self.update_idletasks()
        return dialogo.resultado

    def _executar(self) -> None:
        try:
            if self.modo.get() == "provar":
                res = self.motor.provar(self.nome_para_chave[self.combo.get()])
            else:
                res = self.motor.recomendar()
        except ConsultaCancelada:
            self._escrever(["Consulta cancelada: a janela de pergunta foi fechada.",
                            "Os fatos já respondidos continuam na memória de trabalho."])
            self.conclusao.configure(text="Consulta cancelada.", fg="#374151", bg="#e5e7eb")
            self._atualizar_paineis()
            return
        self._atualizar_paineis()
        self._exibir(res)

    def _nova_consulta(self) -> None:
        if self.memoria.itens() and not messagebox.askyesno(
                "Nova consulta", "Limpar a memória de trabalho e começar de novo?"):
            return
        self.memoria.limpar()
        self._escrever([])
        self.conclusao.configure(text="Memória limpa. Escolha o modo e clique em Executar.",
                                 fg="#111827", bg="#e5e7eb")
        self._atualizar_paineis()


if __name__ == "__main__":
    App().mainloop()
