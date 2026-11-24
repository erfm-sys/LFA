"""Testes automáticos: Fase 1 (ML), Fase 2 (sistema especialista) e integração."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sistema_golpes import (ATRIBUTOS, MENSAGENS_SIMULADAS, BaseConhecimento,
                            MemoriaTrabalho, MotorInferencia, Regra,
                            analisar_contato, classificar_mensagem,
                            classificar_nivel, combinar, construir_dataset,
                            criar_bc_golpes, diagnosticar, extrair_atributos,
                            obter_resultado_padrao, prob_para_cf,
                            treinar_modelo)

SINAIS = ["s_contato_inesperado", "s_numero_nao_oficial", "s_urgencia",
          "s_cita_compra_suspeita", "s_pede_codigo", "s_pede_senha",
          "s_pede_app_remoto", "s_pede_transferencia", "s_pede_entregar_cartao",
          "s_link", "s_promessa_beneficio", "s_pede_pagar_taxa", "s_voce_iniciou"]

TEXTO_GOLPE = "URGENTE! Informe sua senha e o código agora em http://falso.exemplo.top !!!"
TEXTO_LEGITIMO = "Seu extrato de novembro está disponível no aplicativo."


def cenario(**sim):
    """Todos os sinais 'nao', exceto os informados como 'sim'."""
    r = {s: "nao" for s in SINAIS}
    for k, v in sim.items():
        r[k] = v if v in ("sim", "nao") else "sim"
    return r


def rodar(respostas, texto=None):
    """Roda o sistema completo (Fase 1 se houver texto + Fase 2)."""
    bc = criar_bc_golpes()
    return analisar_contato(bc, lambda f, p: respostas.get(f), texto)


# ======================================================================
# FASE 1: machine learning
# ======================================================================
class TestExtracaoDeAtributos(unittest.TestCase):
    def test_conta_links(self):
        self.assertEqual(extrair_atributos("Acesse http://a.exemplo.top e www.b.exemplo.com")["n_links"], 2)
        self.assertEqual(extrair_atributos("Sem links aqui.")["n_links"], 0)

    def test_conta_termos_de_urgencia_distintos(self):
        self.assertEqual(extrair_atributos("Urgente: sua conta será bloqueada hoje")["n_urgencia"], 3)

    def test_ignora_acentos_e_maiusculas(self):
        a = extrair_atributos("CÓDIGO e Senha")
        self.assertEqual(a["n_dados_sensiveis"], 2)

    def test_conta_verbos_de_pedido(self):
        self.assertEqual(extrair_atributos("Informe e confirme seus dados")["n_verbos_pedido"], 2)

    def test_exclamacoes_e_maiusculas(self):
        a = extrair_atributos("ABCD!!")
        self.assertEqual(a["n_exclamacoes"], 2)
        self.assertEqual(a["pct_maiusculas"], 100.0)

    def test_texto_vazio_nao_quebra(self):
        a = extrair_atributos("")
        self.assertEqual(a["pct_maiusculas"], 0.0)
        self.assertEqual(sum(a[k] for k in ATRIBUTOS), 0)

    def test_devolve_todos_os_atributos(self):
        self.assertEqual(list(extrair_atributos("oi").keys()), ATRIBUTOS)


class TestDataset(unittest.TestCase):
    def setUp(self):
        self.df = construir_dataset()

    def test_tamanho_e_balanceamento(self):
        self.assertEqual(len(self.df), 100)
        self.assertEqual(self.df["perfil"].value_counts().to_dict(), {"golpe": 50, "legitimo": 50})

    def test_rotulo_nao_vaza_para_os_atributos(self):
        self.assertNotIn("perfil", ATRIBUTOS)
        self.assertNotIn("texto", ATRIBUTOS)

    def test_sem_valores_ausentes(self):
        self.assertFalse(self.df[ATRIBUTOS + ["perfil"]].isna().any().any())

    def test_sem_textos_duplicados(self):
        self.assertEqual(len({t for t, _ in MENSAGENS_SIMULADAS}), len(MENSAGENS_SIMULADAS))

    def test_atributos_batem_com_o_extrator(self):
        linha = self.df.iloc[0]
        self.assertEqual(extrair_atributos(linha["texto"])["n_links"], linha["n_links"])


class TestModeloML(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = obter_resultado_padrao()

    def test_divisao_treino_teste(self):
        self.assertEqual((len(self.res.X_treino), len(self.res.X_teste)), (75, 25))

    def test_divisao_estratificada(self):
        self.assertEqual(set(self.res.y_teste), {"golpe", "legitimo"})
        self.assertEqual(set(self.res.y_treino), {"golpe", "legitimo"})

    def test_nao_ha_exemplo_em_treino_e_teste(self):
        self.assertTrue(set(self.res.X_treino.index).isdisjoint(self.res.X_teste.index))

    def test_metricas_coerentes(self):
        self.assertTrue(0.0 <= self.res.acuracia <= 1.0)
        self.assertEqual(int(self.res.matriz.sum()), 25)
        acertos = int(self.res.matriz.trace())
        self.assertAlmostEqual(self.res.acuracia, acertos / 25)

    def test_validacao_cruzada_coerente(self):
        self.assertTrue(0 <= self.res.cv_media <= 1)
        self.assertTrue(0 <= self.res.cv_desvio <= 0.5)

    def test_treino_e_reprodutivel(self):
        outro = treinar_modelo(construir_dataset())
        self.assertEqual(outro.acuracia, self.res.acuracia)
        self.assertEqual(list(outro.previsoes), list(self.res.previsoes))

    def test_classifica_golpe_obvio(self):
        r = classificar_mensagem(TEXTO_GOLPE)
        self.assertEqual(r["classe"], "golpe")
        self.assertGreater(r["prob_golpe"], 0.5)

    def test_previsao_para_mensagem_informativa(self):
        r = classificar_mensagem(TEXTO_LEGITIMO)
        self.assertIn(r["classe"], ("golpe", "legitimo"))
        self.assertTrue(0 <= r["prob_golpe"] <= 1)

    def test_avisa_quando_entrada_fora_do_intervalo(self):
        texto = " ".join(f"http://x{i}.exemplo.top" for i in range(12))
        self.assertTrue(classificar_mensagem(texto)["fora_do_intervalo"])
        self.assertFalse(classificar_mensagem(TEXTO_LEGITIMO)["fora_do_intervalo"])

    def test_conversao_probabilidade_em_certeza(self):
        self.assertEqual(prob_para_cf(0.5), 0.0)
        self.assertEqual(prob_para_cf(1.0), 1.0)
        self.assertEqual(prob_para_cf(0.0), -1.0)
        self.assertAlmostEqual(prob_para_cf(0.75), 0.5)


# ======================================================================
# FASE 2: sistema especialista
# ======================================================================
class TestFatoresDeCerteza(unittest.TestCase):
    def test_combinacao_positiva(self):
        self.assertAlmostEqual(combinar(0.6, 0.4), 0.76)

    def test_combinacao_negativa(self):
        self.assertAlmostEqual(combinar(-0.6, -0.4), -0.76)

    def test_combinacao_mista(self):
        self.assertAlmostEqual(combinar(0.8, -0.4), 0.4 / 0.6)

    def test_combinacao_e_simetrica_e_limitada(self):
        for a in (-0.9, -0.3, 0.2, 0.7, 1.0):
            for b in (-0.8, -0.1, 0.5, 0.95):
                c = combinar(a, b)
                self.assertAlmostEqual(c, combinar(b, a))
                self.assertTrue(-1.0 <= c <= 1.0)

    def test_certezas_opostas_maximas_nao_dividem_por_zero(self):
        self.assertEqual(combinar(1.0, -1.0), 0.0)

    def test_nivel(self):
        self.assertEqual(classificar_nivel(0.7, 10), "ALTO")
        self.assertEqual(classificar_nivel(0.4, 10), "MODERADO")
        self.assertEqual(classificar_nivel(0.39, 10), "BAIXO")
        self.assertEqual(classificar_nivel(0.0, 2), "INCOMPLETO")


class TestCasosPositivos(unittest.TestCase):
    """Golpes típicos: nível alto, tipo correto no topo, ações coerentes."""

    def _checar(self, resp, tipo_esperado):
        d, _ = rodar(resp)
        self.assertEqual(d.nivel, "ALTO")
        self.assertIn(tipo_esperado, d.tipos[0][0])
        return d

    def test_conta_segura(self):
        self._checar(cenario(s_contato_inesperado="sim", s_numero_nao_oficial="sim",
                             s_urgencia="sim", s_cita_compra_suspeita="sim",
                             s_pede_transferencia="sim"), "conta segura")

    def test_motoboy(self):
        self._checar(cenario(s_cita_compra_suspeita="sim", s_pede_entregar_cartao="sim"), "motoboy")

    def test_acesso_remoto(self):
        self._checar(cenario(s_pede_app_remoto="sim"), "acesso remoto")

    def test_roubo_de_codigo(self):
        self._checar(cenario(s_pede_codigo="sim", s_urgencia="sim",
                             s_contato_inesperado="sim"), "código ou senha")

    def test_phishing_por_link(self):
        d, _ = rodar(cenario(s_link="sim", s_numero_nao_oficial="sim", s_urgencia="sim"))
        self.assertIn("link", d.tipos[0][0])

    def test_falsa_oferta(self):
        d, _ = rodar(cenario(s_promessa_beneficio="sim", s_pede_pagar_taxa="sim",
                             s_contato_inesperado="sim"))
        self.assertEqual(d.nivel, "ALTO")
        self.assertIn("oferta", d.tipos[0][0])

    def test_acoes_basicas_sempre_presentes_no_alerta(self):
        d, _ = rodar(cenario(s_pede_senha="sim"))
        texto = " ".join(d.acoes)
        self.assertIn("Encerre o contato", texto)
        self.assertIn("número oficial", texto)
        self.assertIn("denuncie", texto)

    def test_orientacao_sugere_ligar_de_outro_aparelho(self):
        d, _ = rodar(cenario(s_pede_codigo="sim"))
        self.assertIn("outro aparelho", " ".join(d.acoes))


class TestPlanoDeAcaoPersonalizado(unittest.TestCase):
    def test_pix_feito_pede_contestacao(self):
        r = cenario(s_pede_transferencia="sim", s_cita_compra_suspeita="sim")
        r["a_fez_transferencia"] = "sim"
        d, _ = rodar(r)
        texto = " ".join(d.acoes)
        self.assertIn("MED", texto)
        self.assertIn("boletim de ocorrência", texto)
        self.assertTrue(d.acoes[0].startswith("URGENTE"))

    def test_cartao_entregue_pede_bloqueio(self):
        r = cenario(s_pede_entregar_cartao="sim")
        r["a_entregou_cartao"] = "sim"
        self.assertIn("bloqueie o cartão", " ".join(rodar(r)[0].acoes))

    def test_app_instalado_pede_remocao(self):
        r = cenario(s_pede_app_remoto="sim")
        r["a_instalou_app"] = "sim"
        self.assertIn("desinstalar", " ".join(rodar(r)[0].acoes))

    def test_senha_informada_pede_troca(self):
        r = cenario(s_pede_senha="sim")
        r["a_passou_senha"] = "sim"
        self.assertIn("Troque agora as senhas", " ".join(rodar(r)[0].acoes))

    def test_sem_dano_nao_recomenda_medidas_de_dano(self):
        r = cenario(s_pede_codigo="sim")
        for a in ("a_passou_codigo", "a_passou_senha", "a_instalou_app",
                  "a_fez_transferencia", "a_entregou_cartao", "a_clicou_link"):
            r[a] = "nao"
        texto = " ".join(rodar(r)[0].acoes)
        self.assertNotIn("MED", texto)
        self.assertNotIn("boletim", texto)
        self.assertNotIn("URGENTE", texto)


class TestCasosNegativos(unittest.TestCase):
    """Sem sinais de golpe: o sistema não alarma."""

    def test_sms_informativo_legitimo(self):
        d, _ = rodar(cenario(s_contato_inesperado="sim"))
        self.assertEqual(d.nivel, "BAIXO")
        self.assertEqual(d.tipos, [])
        self.assertEqual(d.suspeita, 0.0)

    def test_voce_ligou_para_numero_oficial_sem_pedidos_suspeitos(self):
        d, _ = rodar(cenario(s_voce_iniciou="sim"))
        self.assertEqual(d.nivel, "BAIXO")

    def test_pergunta_danos_mesmo_quando_nao_ha_alerta(self):
        _, motor = rodar(cenario())
        self.assertEqual(len([f for f in motor.perguntadas if f.startswith("a_")]), 6)

    def test_evidencia_negativa_reduz_suspeita(self):
        base = rodar(cenario(s_pede_codigo="sim"))[0].suspeita
        menor = rodar(cenario(s_pede_codigo="sim", s_voce_iniciou="sim"))[0].suspeita
        self.assertLess(menor, base)

    def test_pedido_de_codigo_continua_suspeito_mesmo_se_voce_ligou(self):
        d, _ = rodar(cenario(s_pede_codigo="sim", s_voce_iniciou="sim"))
        self.assertIn(d.nivel, ("MODERADO", "ALTO"))

    def test_compra_suspeita_isolada_e_so_moderada(self):
        d, _ = rodar(cenario(s_cita_compra_suspeita="sim", s_contato_inesperado="sim"))
        self.assertEqual(d.nivel, "MODERADO")


class TestCasosIncompletos(unittest.TestCase):
    def test_usuario_nao_sabe_nada(self):
        d, _ = rodar({})
        self.assertEqual(d.nivel, "INCOMPLETO")
        self.assertIn("insuficientes", d.acoes[0])

    def test_poucos_sinais_sem_alerta_nao_declara_baixo_risco(self):
        d, _ = rodar({"s_urgencia": "nao", "s_link": "nao"})
        self.assertEqual(d.nivel, "INCOMPLETO")

    def test_resposta_invalida_vira_desconhecido(self):
        d, _ = rodar({"s_pede_codigo": "talvez"})
        self.assertEqual(d.nivel, "INCOMPLETO")

    def test_alerta_com_dados_parciais_ainda_orienta(self):
        d, _ = rodar({"s_pede_app_remoto": "sim"})
        self.assertEqual(d.nivel, "ALTO")

    def test_nunca_pergunta_duas_vezes(self):
        _, motor = rodar(cenario(s_pede_codigo="sim"))
        self.assertEqual(len(motor.perguntadas), len(set(motor.perguntadas)))

    def test_texto_vazio_equivale_a_nao_ter_texto(self):
        d1, _ = rodar(cenario(s_pede_codigo="sim"), texto="   ")
        d2, _ = rodar(cenario(s_pede_codigo="sim"), texto=None)
        self.assertIsNone(d1.ml)
        self.assertEqual(d1.suspeita, d2.suspeita)


# ======================================================================
# INTEGRAÇÃO: Fase 1 + Fase 2
# ======================================================================
class TestIntegracaoMLRegras(unittest.TestCase):
    def test_previsao_vira_fato_dinamico_na_memoria(self):
        bc = criar_bc_golpes()
        _, motor = analisar_contato(bc, lambda f, p: None, TEXTO_GOLPE)
        self.assertIn("ml_golpe", motor.mt.fatos)
        self.assertEqual(motor.mt.origem["ml_golpe"], "modelo de ML")

    def test_sem_texto_nao_ha_fato_do_ml(self):
        bc = criar_bc_golpes()
        _, motor = analisar_contato(bc, lambda f, p: None, None)
        self.assertNotIn("ml_golpe", motor.mt.fatos)

    def test_texto_suspeito_aumenta_a_suspeita(self):
        r = cenario(s_pede_codigo="sim")
        sem = rodar(r)[0].suspeita
        com = rodar(r, TEXTO_GOLPE)[0].suspeita
        self.assertGreater(com, sem)

    def test_texto_legitimo_nunca_reduz_a_suspeita(self):
        """O ML só reforça: um texto 'legítimo' não pode baixar a suspeita (evita falsa segurança)."""
        r = cenario(s_pede_codigo="sim")
        sem = rodar(r)[0].suspeita
        motor = MotorInferencia(criar_bc_golpes())
        motor.mt.afirmar("ml_golpe", -1.0, "modelo de ML")
        com = diagnosticar(motor.bc, lambda f,p: r.get(f), motor)[0].suspeita
        self.assertEqual(com, sem)

    def test_ml_sozinho_nao_decide_um_golpe(self):
        """Só o modelo (sem sinais confirmados) gera no máximo um ALERTA FRACO."""
        d, _ = rodar(cenario(), TEXTO_GOLPE)
        self.assertEqual(d.nivel, "ALERTA FRACO")

    def test_regras_dominam_quando_ha_sinal_forte_apesar_do_texto_legitimo(self):
        d, _ = rodar(cenario(s_pede_app_remoto="sim"), TEXTO_LEGITIMO)
        self.assertIn(d.nivel, ("MODERADO", "ALTO"))

    def test_regras_compensam_falso_negativo_do_modelo(self):
        """Golpe sem palavras de urgência: o ML erra, mas o sinal informado pelo usuário salva."""
        motor = MotorInferencia(criar_bc_golpes())
        motor.mt.afirmar("ml_golpe", -1.0, "modelo de ML")  # falso negativo controlado
        r = cenario(s_contato_inesperado="sim", s_pede_entregar_cartao="sim")
        d, _ = diagnosticar(motor.bc, lambda f,p: r.get(f), motor)
        self.assertEqual(d.nivel, "ALTO")                                      # as regras acertam
        self.assertIn("motoboy", d.tipos[0][0])

    def test_resultado_inclui_leitura_do_ml_e_aviso(self):
        d, _ = rodar(cenario(s_pede_codigo="sim"), TEXTO_GOLPE)
        self.assertEqual(d.ml["classe"], "golpe")
        self.assertIn("revisão humana", d.aviso)

    def test_aviso_diferente_quando_fora_do_intervalo(self):
        texto = " ".join(f"http://x{i}.exemplo.top" for i in range(12))
        d, _ = rodar(cenario(s_link="sim"), texto)
        self.assertIn("fora dos intervalos", d.aviso)

    def test_explicacao_cita_leitura_do_modelo(self):
        d, _ = rodar(cenario(s_pede_codigo="sim"), TEXTO_GOLPE)
        self.assertIn("modelo de ML", d.explicacao)
        self.assertIn("M1", d.explicacao)


# ======================================================================
# PROTEÇÃO ÉTICA: o texto sozinho nunca dispara o plano de ação
# ======================================================================
TEXTO_FATURA = "Sua fatura vence hoje. Pague agora pelo aplicativo para evitar juros."


def falso_positivo_controlado(respostas):
    """Simula previsão errada do classificador para testar a política simbólica."""
    bc = criar_bc_golpes()
    motor = MotorInferencia(bc)
    motor.mt.afirmar("ml_golpe", 1.0, "modelo de ML")
    return diagnosticar(bc, lambda f, p: respostas.get(f), motor)


class TestProtecaoEtica(unittest.TestCase):
    def test_fatura_legitima_lida_como_golpe_gera_so_alerta_fraco(self):
        self.assertEqual(falso_positivo_controlado(cenario())[1].mt.fatos["ml_golpe"], 1.0)
        d, _ = falso_positivo_controlado(cenario())
        self.assertEqual(d.nivel, "ALERTA FRACO")                                # mas não vira alarme

    def test_alerta_fraco_nao_manda_encerrar_mas_investiga_danos(self):
        d, motor = falso_positivo_controlado(cenario())
        self.assertNotIn("Encerre o contato", " ".join(d.acoes))
        self.assertEqual(len([f for f in motor.perguntadas if f.startswith("a_")]), 6)
        self.assertEqual(d.tipos, [])

    def test_alerta_fraco_orienta_a_revisar_e_confirmar(self):
        d, _ = falso_positivo_controlado(cenario())
        self.assertIn("Alerta fraco", d.acoes[0])
        self.assertIn("canal oficial", d.acoes[0])

    def test_sem_o_texto_o_mesmo_caso_e_baixo(self):
        d, _ = rodar(cenario(), None)
        self.assertEqual(d.nivel, "BAIXO")

    def test_texto_suspeito_sem_nenhuma_resposta_e_alerta_fraco(self):
        d, _ = rodar({}, TEXTO_GOLPE)
        self.assertEqual(d.nivel, "ALERTA FRACO")

    def test_explicacao_do_alerta_fraco_menciona_o_texto(self):
        d, _ = falso_positivo_controlado(cenario())
        self.assertIn("apenas da leitura do texto", d.explicacao)

    def test_ml_nao_derruba_suspeita_moderada(self):
        """Antes, um texto 'legítimo' derrubava 40% (MODERADO) para 25% (BAIXO)."""
        r = cenario(s_cita_compra_suspeita="sim", s_contato_inesperado="sim")
        sem = rodar(r, None)[0]
        com = rodar(r, "Fale com a gente sobre seu cartão.")[0]
        self.assertEqual(sem.nivel, "MODERADO")
        self.assertEqual(com.nivel, "MODERADO")
        self.assertEqual(com.suspeita, sem.suspeita)

    def test_ml_pode_reforcar_quando_ha_evidencia_confirmada(self):
        r = cenario(s_cita_compra_suspeita="sim", s_contato_inesperado="sim")
        d, _ = rodar(r, TEXTO_GOLPE)
        self.assertEqual(d.nivel, "ALTO")

    def test_nenhuma_regra_do_ml_reduz_a_suspeita(self):
        bc = criar_bc_golpes()
        regras_ml = [r for r in bc.regras if r.fonte == "ML"]
        self.assertTrue(regras_ml)
        self.assertTrue(all(r.cf > 0 for r in regras_ml))
        self.assertNotIn("M2", [r.id for r in bc.regras])


class TestEncadeamentoParaFrente(unittest.TestCase):
    def _forward(self, respostas):
        mt = MemoriaTrabalho()
        motor = MotorInferencia(criar_bc_golpes(), mt)
        for f, r in respostas.items():
            motor.registrar_resposta(f, r)
        motor.encadeamento_frente()
        return mt

    def test_concorda_com_backward(self):
        r = cenario(s_cita_compra_suspeita="sim", s_pede_transferencia="sim",
                    s_urgencia="sim", s_contato_inesperado="sim")
        r["a_fez_transferencia"] = "sim"
        mt = self._forward(r)
        d, motor = rodar(r)
        self.assertAlmostEqual(mt.fatos["suspeita_golpe"], d.suspeita, places=6)
        self.assertAlmostEqual(mt.fatos["t_conta_segura"], motor.mt.fatos["t_conta_segura"], places=6)
        self.assertGreaterEqual(mt.fatos["ac_contestar_pix"], 0.2)

    def test_sem_fatos_nada_dispara(self):
        self.assertEqual(self._forward({}).fatos, {})

    def test_regra_com_premissa_falsa_nao_dispara(self):
        mt = self._forward(cenario())
        self.assertNotIn("t_motoboy", mt.fatos)
        self.assertNotIn("ac_encerrar", mt.fatos)

    def test_dispara_regras_em_cadeia(self):
        mt = self._forward({"s_pede_codigo": "sim"})
        self.assertIn("i_pede_credencial", mt.fatos)
        self.assertIn("suspeita_golpe", mt.fatos)
        self.assertIn("f_alerta", mt.fatos)


class TestExplicacao(unittest.TestCase):
    def test_explica_regras_e_evidencias(self):
        d, _ = rodar(cenario(s_pede_codigo="sim", s_urgencia="sim", s_contato_inesperado="sim"))
        self.assertIn("pedido de código", d.explicacao)
        self.assertIn("S1", d.explicacao)
        self.assertIn("não compartilhe códigos", d.explicacao)

    def test_explicacao_cita_a_fonte_da_regra(self):
        d, _ = rodar(cenario(s_pede_codigo="sim"))
        self.assertIn("[fonte: FEB]", d.explicacao)

    def test_explicacao_usa_rotulos_legiveis_e_agrupa(self):
        r = cenario(s_pede_transferencia="sim", s_cita_compra_suspeita="sim")
        r["a_fez_transferencia"] = "sim"
        d, _ = rodar(r)
        self.assertIn("você fez Pix/transferência", d.explicacao)
        self.assertNotIn("a_fez_transferencia", d.explicacao)
        self.assertIn("D4", d.explicacao)
        self.assertIn("Regras que indicam o tipo de golpe", d.explicacao)
        self.assertNotIn("T1 (aumenta a suspeita", d.explicacao)

    def test_explicacao_mostra_regra_que_reduz(self):
        d, _ = rodar(cenario(s_pede_codigo="sim", s_voce_iniciou="sim"))
        self.assertIn("reduz", d.explicacao)


class TestVerificacaoBC(unittest.TestCase):
    def test_bc_de_golpes_esta_limpa(self):
        rel = criar_bc_golpes().verificar()
        self.assertEqual({k: v for k, v in rel.items() if v}, {})

    def test_toda_regra_tem_fonte_conhecida(self):
        for r in criar_bc_golpes().regras:
            self.assertIn(r.fonte, ("FEB", "BCB", "HEUR", "ML"), r.id)

    def test_regras_de_alerta_tem_justificativa(self):
        for r in criar_bc_golpes().regras:
            if r.conclusao.startswith(("i_pede", "suspeita", "t_")):
                self.assertTrue(r.nota, f"{r.id} sem nota")

    def test_ha_pelo_menos_quatro_regras(self):
        self.assertGreaterEqual(len(criar_bc_golpes().regras), 4)

    def _bc(self, regras, perguntas=None):
        return BaseConhecimento(perguntas or {"a": "?", "b": "?"}, regras, {}, {}, {}, {"z"})

    def test_detecta_duplicada(self):
        r = self._bc([Regra.criar("X1", "a", "z", 0.5), Regra.criar("X2", "a", "z", 0.7),
                      Regra.criar("X3", "b", "z", 0.5)]).verificar()
        self.assertTrue(r["duplicadas"])

    def test_detecta_inalcancavel(self):
        r = self._bc([Regra.criar("X1", "inexistente & a & b", "z", 0.5)]).verificar()
        self.assertTrue(r["inalcancaveis"])

    def test_fato_externo_nao_e_inalcancavel(self):
        bc = BaseConhecimento({"a": "?"}, [Regra.criar("X1", "ml & a", "z", 0.5)],
                              {}, {}, {}, {"z"}, externos=frozenset({"ml"}))
        self.assertFalse(bc.verificar()["inalcancaveis"])

    def test_detecta_ciclo(self):
        r = self._bc([Regra.criar("X1", "p", "q", 0.5), Regra.criar("X2", "q", "p", 0.5),
                      Regra.criar("X3", "a & b", "z", 0.5)]).verificar()
        self.assertTrue(r["ciclos"])

    def test_detecta_cf_invalido(self):
        r = self._bc([Regra.criar("X1", "a & b", "z", 1.5)]).verificar()
        self.assertTrue(r["cf_invalido"])

    def test_detecta_pergunta_sem_uso_e_fato_orfao(self):
        r = self._bc([Regra.criar("X1", "a", "w", 0.5)]).verificar()
        self.assertTrue(any("'b'" in m for m in r["nao_usados"]))
        self.assertTrue(any("'w'" in m for m in r["nao_usados"]))

    def test_backward_nao_entra_em_loop_com_ciclo(self):
        bc = self._bc([Regra.criar("X1", "p", "q", 0.5), Regra.criar("X2", "q", "p", 0.5)])
        cf = MotorInferencia(bc).avaliar("p", lambda f, p: None)
        self.assertIsNone(cf)


class TestVersao2(unittest.TestCase):
    def test_dano_sem_sinais_exige_orientacao_critica(self):
        d, m = rodar({"a_passou_codigo": "sim"})
        self.assertEqual(d.nivel, "CRÍTICO")
        self.assertEqual(d.nivel_suspeita, "INCOMPLETO")
        self.assertEqual(d.comprometimento, "POSSÍVEL EXPOSIÇÃO")
        self.assertIn("Troque agora as senhas", " ".join(d.acoes))
        self.assertIn("D1", d.explicacao)

    def test_dano_com_previsao_legitima(self):
        d, _ = rodar({"a_entregou_cartao": "sim"}, TEXTO_LEGITIMO)
        self.assertEqual(d.nivel, "CRÍTICO")
        self.assertIn("bloqueie o cartão", " ".join(d.acoes))

    def test_pressao_nao_duplica_urgencia(self):
        m = MotorInferencia(criar_bc_golpes())
        for f in ("s_urgencia", "s_contato_inesperado"):
            m.registrar_resposta(f, "sim")
        self.assertAlmostEqual(m.avaliar("i_pressao", lambda f,p: None), .9)
        self.assertIn("I2", m.suprimidas["i_pressao"])
        m.encadeamento_frente()
        self.assertAlmostEqual(m.mt.fatos["i_pressao"], .9)

    def test_dependencia_transitiva_nao_duplica_link(self):
        m = MotorInferencia(criar_bc_golpes())
        m.registrar_resposta("s_link", "sim")
        m.registrar_resposta("s_numero_nao_oficial", "nao")
        self.assertAlmostEqual(m.avaliar("t_phishing_link", lambda f,p: None), .5)

    def test_corrigir_resposta_invalida_derivados(self):
        m = MotorInferencia(criar_bc_golpes())
        m.registrar_resposta("s_pede_codigo", "sim")
        self.assertGreater(m.avaliar("suspeita_golpe", lambda f,p: None), 0)
        m.registrar_resposta("s_pede_codigo", "nao")
        self.assertIsNone(m.avaliar("suspeita_golpe", lambda f,p: None))
        self.assertNotIn("i_pede_credencial", m.mt.fatos)

    def test_corrigir_desconhecido_e_retirar_fato(self):
        m = MotorInferencia(criar_bc_golpes())
        m.registrar_resposta("s_pede_codigo", None)
        m.registrar_resposta("s_pede_codigo", "sim")
        self.assertNotIn("s_pede_codigo", m.mt.desconhecidos)
        m.registrar_resposta("s_pede_codigo", None)
        self.assertNotIn("s_pede_codigo", m.mt.fatos)
        self.assertIn("s_pede_codigo", m.mt.desconhecidos)

    def test_aviso_preventivo_nao_e_pedido(self):
        a = extrair_atributos("Nunca informe sua senha por telefone.")
        self.assertEqual(a["aviso_preventivo"], 1)
        self.assertEqual(a["pedido_credencial"], 0)
        self.assertEqual(extrair_atributos("Informe sua senha")["pedido_credencial"], 1)

    def test_ids_repetidos_e_premissas_contraditorias(self):
        bc = BaseConhecimento({"a": "?"}, [Regra.criar("X", "a & !a", "z", .5),
                             Regra.criar("X", "a", "z", .5)], {}, {}, {}, {"z"})
        self.assertEqual(bc.verificar()["ids_duplicados"], ["X"])
        self.assertEqual(bc.verificar()["premissas_contraditorias"], ["X"])

    def test_fato_dinamico_corresponde_ao_rotulo(self):
        d,m = rodar(cenario(), TEXTO_GOLPE)
        self.assertEqual(m.mt.fatos["ml_golpe"], 1 if d.ml["classe"] == "golpe" else -1)

    def test_sem_comprometimento_confirmado_nao_aciona_acao_urgente(self):
        d, _ = falso_positivo_controlado(cenario())
        self.assertEqual(d.nivel, "ALERTA FRACO")
        self.assertNotIn("URGENTE", " ".join(d.acoes))


if __name__ == "__main__":
    unittest.main(verbosity=2)
