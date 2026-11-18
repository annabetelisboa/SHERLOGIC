import pygame
import random
import sys
import os
import time
import ctypes

# Ativa nitidez nativa no Windows (evita zoom borrado de DPI)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


# FUNÇÃO PARA REINICIAR O JOGO
def iniciar_novo_jogo():
    suspeitos = ["Mordomo", "Cozinheira", "Jardineiro", "Motorista"]
    armas = ["Veneno", "Pistola", "Faca", "Corda"]
    locais = ["Biblioteca", "Cozinha", "Jardim", "Sala"]

    culpado = random.choice(suspeitos)
    arma_real = random.choice(armas)
    local_real = random.choice(locais)

    s_falsos = [s for s in suspeitos if s != culpado]
    a_falsas = [a for a in armas if a != arma_real]
    l_falsos = [l for l in locais if l != local_real]

    pistas = [
        {
            "historia": f"Um vizinho confirmou que viu {s_falsos[0]} longe da mansão no horário do crime.",
            "formula": f"¬{s_falsos[0]}"
        },
        {
            "historia": f"A perícia analisou a cena: Se o culpado for {culpado}, a arma NÃO pode ser {a_falsas[0]}.",
            "formula": f"{culpado} -> ¬{a_falsas[0]}"
        },
        {
            "historia": f"Um bilhete anônimo revela uma ligação direta entre o autor do crime e a arma usada.",
            "formula": f"{culpado} <-> {arma_real}"
        },
        {
            "historia": f"O mordomo jurou que {s_falsos[1]} e {s_falsos[2]} estavam jogando cartas juntos na hora do crime.",
            "formula": f"¬({s_falsos[1]} v {s_falsos[2]})"
        },
        {
            "historia": f"Um rastro de sangue indica que o uso de {arma_real} leva diretamente ao local do crime.",
            "formula": f"{arma_real} -> {local_real}"
        },
        {
            "historia": f"As câmeras de segurança descartam completamente a presença de qualquer pessoa na {l_falsos[0]}.",
            "formula": f"¬{l_falsos[0]}"
        },
        {
            "historia": f"Fios de cabelo encontrados mostram que quem usou {a_falsas[1]} não tem o perfil do culpado.",
            "formula": f"¬{a_falsas[1]}"
        },
        {
            "historia": f"Os registros de limpeza confirmam que o cômodo {l_falsos[1]} estava trancado o dia todo.",
            "formula": f"¬{l_falsos[1]}"
        },
        {
            "historia": f"A testemunha ocular garante que o crime não ocorreu na {l_falsos[2]}.",
            "formula": f"¬{l_falsos[2]}"
        },
        {
            "historia": f"Uma análise forense provou que {a_falsas[2]} é apenas uma réplica de decoração.",
            "formula": f"¬{a_falsas[2]}"
        }
    ]
    random.shuffle(pistas)
    if nivel_atual >= 3:
        pistas.extend([
            {
                "historia": f"A perícia concluiu: se {arma_real} foi usada, então o crime ocorreu na {local_real}; além disso, a arma ligada ao culpado foi encontrada na cena.",
                "formula": f"({arma_real} -> {local_real}) ^ ({culpado} <-> {arma_real})"
            },
            {
                "historia": f"Dois registros coincidem: {culpado} é o autor se, e somente se, {arma_real} foi usada; sem {arma_real}, o crime não poderia ter ocorrido na {local_real}.",
                "formula": f"({culpado} <-> {arma_real}) ^ (¬{arma_real} -> ¬{local_real})"
            }
        ])
        random.shuffle(pistas)

    return {
        "suspeitos": suspeitos,
        "armas": armas,
        "locais": locais,
        "culpado": culpado,
        "arma_real": arma_real,
        "local_real": local_real,
        "pistas": pistas,
        "pistas_reveladas": [],
        "pista_index": 0,
        "tentativas_acusacao": 0,
        "grelha_unica": [[0 for _ in range(4)] for _ in range(8)],
        "mensagem_resultado": "",
        "cor_resultado": (240, 240, 240),
        "tempo_inicio": time.time(),
        "tempo_limite": tempo_limite_fase(nivel_atual),
        "jogo_encerrado": False
    }


def limite_pistas_fase(fase):
    """Reduz as pistas disponíveis gradualmente, sem alterar as regras do caso."""
    return 10 if fase == 1 else max(5, 10 - (fase - 1))


def tempo_limite_fase(fase):
    """Começa em 1 minuto e meio (90s) e reduz 10s por fase até o mínimo de 30s."""
    return max(30, 90 - (fase - 1) * 10)


# INICIALIZAÇÃO DO PYGAME EM TELA CHEIA COM ESCALA NATIVA NÍTIDA
pygame.init()
info_monitor = pygame.display.Info()
LARGURA = info_monitor.current_w
ALTURA = info_monitor.current_h

ESCALA = min(LARGURA / 1200.0, ALTURA / 720.0)
MARGEM_X = (LARGURA - 1200 * ESCALA) / 2.0
MARGEM_Y = (ALTURA - 720 * ESCALA) / 2.0


def sx(x):
    return int(round(MARGEM_X + x * ESCALA))


def sy(y):
    return int(round(MARGEM_Y + y * ESCALA))


def sw(w):
    return int(round(w * ESCALA))


def sh(h):
    return int(round(h * ESCALA))


def srect(x, y, w, h):
    return pygame.Rect(sx(x), sy(y), sw(w), sh(h))


tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("SHERLOGIC - Painel de Investigação")
clock = pygame.time.Clock()


def carregar_imagem(caminho, tamanho):
    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    nome_base = os.path.splitext(caminho)[0]
    tamanho_escalado = (max(1, sw(tamanho[0])), max(1, sh(tamanho[1])))
    for extensao in (".jpeg", ".jpg", ".png", ".JPEG", ".JPG", ".PNG"):
        caminho_completo = os.path.join(diretorio_base, nome_base + extensao)
        if os.path.exists(caminho_completo):
            try:
                img = pygame.image.load(caminho_completo).convert_alpha()
                return pygame.transform.smoothscale(img, tamanho_escalado)
            except pygame.error:
                return None
    return None


logo_img = carregar_imagem("logosherlogic.jpeg", (240, 70))
if not logo_img:
    logo_img = carregar_imagem("sóalupalogo.jpeg", (70, 70))

imgs_suspeitos = {
    "Mordomo": carregar_imagem("mordomo.jpg", (45, 45)),
    "Cozinheira": carregar_imagem("cozinheira.jpg", (45, 45)),
    "Jardineiro": carregar_imagem("jardineiro.jpg", (45, 45)),
    "Motorista": carregar_imagem("motorista.jpg", (45, 45))
}
imgs_suspeitos_modal = {
    "Mordomo": carregar_imagem("mordomo.jpg", (90, 90)),
    "Cozinheira": carregar_imagem("cozinheira.jpg", (90, 90)),
    "Jardineiro": carregar_imagem("jardineiro.jpg", (90, 90)),
    "Motorista": carregar_imagem("motorista.jpg", (90, 90))
}
img_fim_de_jogo = carregar_imagem("fim_de_jogo.jpg", (400, 225))

# Paleta de arquivo policial com alto contraste para leitura nítida
COR_ESQUERDA = (32, 40, 45)
COR_DIREITA = (24, 31, 36)
COR_LINHA_DIVISORA = (89, 104, 105)
COR_TEXTO = (255, 255, 255)
COR_AMARELO = (235, 192, 108)
COR_BOTAO_PISTA = (56, 105, 117)
COR_BOTAO_ACUSAR = (151, 69, 57)
COR_BOTAO_SAIR = (94, 49, 45)
COR_VERMELHO = (212, 88, 74)
COR_VERDE = (86, 156, 114)
COR_CELULA = (39, 50, 54)
COR_DIVISOR_TABELA = (93, 111, 109)
COR_MODAL_FUNDO = (26, 34, 38)
COR_BOTAO_SETA = (57, 73, 78)
COR_CAMPO_TEXTO = (39, 50, 54)
COR_CARTAO = (22, 29, 33)

# Fontes renderizadas diretamente na resolução nativa do monitor (nitidez 100%)
fonte_titulo = pygame.font.SysFont("segoeui,arial", max(14, int(21 * ESCALA)), bold=True)
fonte_pista = pygame.font.SysFont("segoeui,calibri,arial", max(12, int(16 * ESCALA)))
fonte_formula = pygame.font.SysFont("consolas,segoeui,arial", max(11, int(15 * ESCALA)), bold=True)
fonte_grelha = pygame.font.SysFont("segoeui,arial", max(11, int(14 * ESCALA)), bold=True)
fonte_tutorial = pygame.font.SysFont("segoeui,arial", max(12, int(16 * ESCALA)))

# Botões Painel Esquerdo (coordenadas lógicas 1200x720)
btn_pedir_pista = srect(20, 560, 460, 38)
btn_acusar = srect(20, 605, 460, 38)
btn_sair_jogo = srect(20, 650, 460, 35)

tam_celula = 50
ox = 740
oy = 140

# Dados Globais do Jogador
nome_jogador = ""
pontuacao_total = 0
casos_resolvidos = 0
nivel_atual = 1

# Etapas do Jogo: "NOME", "PERGUNTA_TUTORIAL", "TUTORIAL", "JOGO", "RANKING_FINAL"
etapa_atual = "NOME"
passo_tutorial = 0

# Modais e Animações do Jogo
modal_acusacao_aberto = False
sel_suspeito = 0
sel_arma = 0
sel_local = 0
categoria_foco = 0

pistas_scroll = 0.0
alvo_scroll = 0.0
animacao_nova_pista_y = 0.0
altura_total_pistas = 0

estado_jogo = iniciar_novo_jogo()


def desenhar_texto_multilinhas(superficie, texto, x_logico, y_logico, largura_max_logica, fonte, cor, desenhar=True):
    palavras = texto.split(' ')
    linhas = []
    linha_atual = ""
    largura_max_real = sw(largura_max_logica)

    for palavra in palavras:
        test_line = linha_atual + palavra + " "
        if fonte.size(test_line)[0] <= largura_max_real:
            linha_atual = test_line
        else:
            linhas.append(linha_atual)
            linha_atual = palavra + " "
    linhas.append(linha_atual)

    altura_y = y_logico
    passo_linha = (fonte.get_height() / ESCALA) + 5
    for linha in linhas:
        if desenhar:
            txt_surface = fonte.render(linha.strip(), True, cor)
            superficie.blit(txt_surface, (sx(x_logico), sy(altura_y)))
        altura_y += passo_linha
    return altura_y


def desenhar_linhas_tutorial(superficie, linhas_texto, x_logico, y_logico, fonte, cor):
    altura_y = y_logico
    passo_linha = (fonte.get_height() / ESCALA) + 12
    for linha in linhas_texto:
        txt_surface = fonte.render(linha, True, cor)
        superficie.blit(txt_surface, (sx(x_logico), sy(altura_y)))
        altura_y += passo_linha


# Loop Principal
rodando = True
while rodando:
    # TELA DE DIGITAÇÃO DO NOME
    if etapa_atual == "NOME":
        tela.fill(COR_ESQUERDA)

        rect_box = srect(350, 200, 500, 300)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_box, border_radius=sw(12))
        pygame.draw.rect(tela, COR_AMARELO, rect_box, max(1, sw(2)), border_radius=sw(12))

        txt_t = fonte_titulo.render("BEM-VINDO AO SHERLOGIC", True, COR_AMARELO)
        tela.blit(txt_t, (sx(380), sy(230)))

        txt_sub = fonte_grelha.render("Digite o seu nome de detetive:", True, COR_TEXTO)
        tela.blit(txt_sub, (sx(380), sy(280)))

        rect_input = srect(380, 320, 440, 45)
        pygame.draw.rect(tela, COR_CAMPO_TEXTO, rect_input, border_radius=sw(6))
        pygame.draw.rect(tela, COR_LINHA_DIVISORA, rect_input, 1, border_radius=sw(6))

        txt_nome = fonte_titulo.render(nome_jogador + "|", True, COR_AMARELO)
        tela.blit(txt_nome, (rect_input.x + sw(15), rect_input.y + sh(10)))

        btn_avancar = srect(380, 400, 440, 45)
        pygame.draw.rect(tela, COR_VERDE, btn_avancar, border_radius=sw(8))
        txt_av = fonte_titulo.render("CONTINUAR", True, COR_TEXTO)
        tela.blit(txt_av, (btn_avancar.x + sw(160), btn_avancar.y + sh(10)))

    # TELA DE PERGUNTA DO TUTORIAL
    elif etapa_atual == "PERGUNTA_TUTORIAL":
        tela.fill(COR_ESQUERDA)

        rect_box = srect(350, 220, 500, 260)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_box, border_radius=sw(12))
        pygame.draw.rect(tela, COR_AMARELO, rect_box, max(1, sw(2)), border_radius=sw(12))

        txt_t = fonte_titulo.render(f"Olá, Detetive {nome_jogador}!", True, COR_AMARELO)
        tela.blit(txt_t, (sx(380), sy(250)))

        txt_q = fonte_grelha.render("Deseja fazer o tutorial?", True, COR_TEXTO)
        tela.blit(txt_q, (sx(380), sy(290)))

        btn_sim = srect(380, 360, 200, 50)
        pygame.draw.rect(tela, COR_VERDE, btn_sim, border_radius=sw(8))
        txt_s = fonte_titulo.render("SIM", True, COR_TEXTO)
        tela.blit(txt_s, (btn_sim.x + sw(85), btn_sim.y + sh(12)))

        btn_nao = srect(620, 360, 200, 50)
        pygame.draw.rect(tela, COR_BOTAO_PISTA, btn_nao, border_radius=sw(8))
        txt_n = fonte_titulo.render("NÃO", True, COR_TEXTO)
        tela.blit(txt_n, (btn_nao.x + sw(80), btn_nao.y + sh(12)))

    # TELA DE TUTORIAL
    elif etapa_atual == "TUTORIAL":
        tela.fill(COR_ESQUERDA)

        rect_tut = srect(200, 100, 800, 500)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_tut, border_radius=sw(12))
        pygame.draw.rect(tela, COR_AMARELO, rect_tut, max(1, sw(2)), border_radius=sw(12))

        txt_tut_t = fonte_titulo.render(f"TUTORIAL - PARTE {passo_tutorial + 1} DE 3", True, COR_AMARELO)
        tela.blit(txt_tut_t, (sx(230), sy(130)))

        if passo_tutorial == 0:
            linhas_parte_1 = [
                "1. PISTAS LÓGICAS:",
                "O jogo fornece depoimentos acompanhados de fórmulas lógicas.",
                "",
                "Símbolos importantes:",
                "¬ (Negação): Significa 'NÃO'. Ex: ¬Mordomo -> O Mordomo não é o culpado.",
                "-> (Condicional): Se a primeira parte for verdade, a segunda também é.",
                "<-> (Bicondicional): Elementos diretamente ligados."
            ]
            desenhar_linhas_tutorial(tela, linhas_parte_1, 230, 180, fonte_tutorial, COR_TEXTO)

        elif passo_tutorial == 1:
            linhas_parte_2 = [
                "2. GRELHA DE DEDUÇÃO:",
                "No lado direito fica o seu mapa de anotações.",
                "",
                "Ao clicar em uma célula da grelha:",
                "1º Clique: Adiciona 'X' (Vermelho), descartando a opção.",
                "2º Clique: Adiciona 'V' (Verde), confirmando a opção.",
                "3º Clique: Limpa a célula de volta para o estado vazio."
            ]
            desenhar_linhas_tutorial(tela, linhas_parte_2, 230, 180, fonte_tutorial, COR_TEXTO)

        elif passo_tutorial == 2:
            linhas_parte_3 = [
                "3. PONTUAÇÃO E OBJETIVO:",
                "Esta partida de treino NÃO contabiliza pontos nem tempo.",
                "",
                "Nas partidas reais:",
                "Quanto MENOS tempo e MENOS pistas utilizadas, MAIOR será sua pontuação!",
                "Acusações falsas geram alertas mas você pode continuar tentando.",
                "Ao acertar, o jogo revela a vitória e permite jogar um novo enigma."
            ]
            desenhar_linhas_tutorial(tela, linhas_parte_3, 230, 180, fonte_tutorial, COR_TEXTO)

        btn_prox = srect(750, 530, 220, 45)
        pygame.draw.rect(tela, COR_VERDE, btn_prox, border_radius=sw(8))
        lbl_btn = "AVANÇAR" if passo_tutorial < 2 else "INICIAR JOGO"
        txt_px = fonte_titulo.render(lbl_btn, True, COR_TEXTO)
        tela.blit(txt_px, (btn_prox.x + sw(35), btn_prox.y + sh(10)))

    # TELA PRINCIPAL DO JOGO
    elif etapa_atual == "JOGO":
        if not estado_jogo["jogo_encerrado"]:
            tempo_restante = max(0, int(estado_jogo["tempo_limite"] - (time.time() - estado_jogo["tempo_inicio"])))
            if tempo_restante == 0:
                estado_jogo["jogo_encerrado"] = True
                estado_jogo["mensagem_resultado"] = "TEMPO ESGOTADO!"
                estado_jogo["cor_resultado"] = COR_VERMELHO
                modal_acusacao_aberto = False
        else:
            tempo_restante = 0

        # Atualização suave da animação das pistas subindo (Ease-Out)
        pistas_scroll += (alvo_scroll - pistas_scroll) * 0.12
        if animacao_nova_pista_y > 0:
            animacao_nova_pista_y -= max(2.0, animacao_nova_pista_y * 0.08)
            if animacao_nova_pista_y < 1:
                animacao_nova_pista_y = 0.0

        suspeitos = estado_jogo["suspeitos"]
        armas = estado_jogo["armas"]
        locais = estado_jogo["locais"]
        itens_laterais = armas + locais

        # 1. METADE ESQUERDA (PISTAS E BOTÕES)
        pygame.draw.rect(tela, COR_ESQUERDA, (0, 0, sx(500), ALTURA))
        pygame.draw.rect(tela, COR_LINHA_DIVISORA, (0, 0, sx(500), max(2, sh(5))))

        txt_tit1 = fonte_titulo.render("ARQUIVO DO CASO", True, COR_AMARELO)
        tela.blit(txt_tit1, (sx(20), sy(15)))

        txt_p_info = fonte_grelha.render(
            f"FASE {nivel_atual}  |  Detetive: {nome_jogador}  |  {pontuacao_total} pts",
            True, COR_AMARELO
        )
        tela.blit(txt_p_info, (sx(20), sy(40)))

        pygame.draw.line(tela, COR_LINHA_DIVISORA, (sx(20), sy(62)), (sx(480), sy(62)), 1)
        txt_contagem = fonte_grelha.render(
            f"PISTAS: {estado_jogo['pista_index']}/{limite_pistas_fase(nivel_atual)}   •   CASOS: {casos_resolvidos}",
            True, COR_TEXTO)
        tela.blit(txt_contagem, (sx(20), sy(70)))
        txt_tentativas = fonte_grelha.render(
            f"TENTATIVAS DE ACUSAÇÃO: {3 - estado_jogo['tentativas_acusacao']}/3",
            True, COR_TEXTO
        )
        tela.blit(txt_tentativas, (sx(20), sy(88)))
        cor_tempo = COR_VERMELHO if tempo_restante <= 10 else COR_AMARELO
        txt_tempo = fonte_grelha.render(f"TEMPO: {tempo_restante // 60:02d}:{tempo_restante % 60:02d}", True, cor_tempo)
        tela.blit(txt_tempo, (sx(350), sy(70)))

        area_pistas = srect(10, 114, 480, 401)
        tela.set_clip(area_pistas)
        y_base = 114 - pistas_scroll
        altura_acumulada = 0

        for i, p in enumerate(estado_jogo["pistas_reveladas"]):
            y_atual = y_base + altura_acumulada
            if i == len(estado_jogo["pistas_reveladas"]) - 1:
                y_atual += animacao_nova_pista_y

            historia = f'"{p["historia"]}"'
            altura_texto = desenhar_texto_multilinhas(
                tela, historia, 28, y_atual + 28, 440, fonte_pista, COR_TEXTO, desenhar=False
            )
            altura_card = max(60, altura_texto - y_atual + 8)
            pygame.draw.rect(tela, COR_CARTAO, srect(14, y_atual - 3, 472, altura_card), border_radius=sw(8))
            pygame.draw.rect(tela, COR_AMARELO, srect(14, y_atual - 3, 4, altura_card), border_radius=sw(3))
            txt_f = fonte_formula.render(f"EVIDÊNCIA {i+1}  ·  {p['formula']}", True, COR_AMARELO)
            tela.blit(txt_f, (sx(28), sy(y_atual + 3)))
            desenhar_texto_multilinhas(tela, historia, 28, y_atual + 28, 440, fonte_pista, COR_TEXTO, desenhar=True)
            altura_acumulada += altura_card + 12

        altura_total_pistas = altura_acumulada
        tela.set_clip(None)

        if estado_jogo["mensagem_resultado"]:
            txt_res = fonte_grelha.render(estado_jogo["mensagem_resultado"], True, estado_jogo["cor_resultado"])
            tela.blit(txt_res, (sx(20), sy(530)))

        # Botões Esquerda
        pygame.draw.rect(tela, COR_BOTAO_PISTA, btn_pedir_pista, border_radius=sw(8))
        txt_btn1 = fonte_titulo.render("PEDIR NOVA PISTA [1]", True, COR_TEXTO)
        tela.blit(txt_btn1, (btn_pedir_pista.x + sw(115), btn_pedir_pista.y + sh(8)))

        pygame.draw.rect(tela, COR_BOTAO_ACUSAR, btn_acusar, border_radius=sw(8))
        txt_btn2 = fonte_titulo.render("FAZER ACUSAÇÃO [2]", True, COR_TEXTO)
        tela.blit(txt_btn2, (btn_acusar.x + sw(125), btn_acusar.y + sh(8)))

        pygame.draw.rect(tela, COR_BOTAO_SAIR, btn_sair_jogo, border_radius=sw(8))
        txt_btn3 = fonte_titulo.render("SAIR DO JOGO [ESC]", True, COR_TEXTO)
        tela.blit(txt_btn3, (btn_sair_jogo.x + sw(130), btn_sair_jogo.y + sh(6)))

        # 2. METADE DIREITA (GRELHA DE DEDUÇÃO)
        pygame.draw.rect(tela, COR_DIREITA, (sx(500), 0, LARGURA - sx(500), ALTURA))
        pygame.draw.line(tela, COR_LINHA_DIVISORA, (sx(500), 0), (sx(500), ALTURA), max(2, sw(4)))

        txt_tit2 = fonte_titulo.render("QUADRO DE DEDUÇÕES", True, COR_AMARELO)
        tela.blit(txt_tit2, (sx(520), sy(15)))
        pygame.draw.line(tela, COR_LINHA_DIVISORA, (sx(520), sy(49)), (sx(710), sy(49)), max(1, sw(2)))
        txt_fase = fonte_pista.render(f"FASE {nivel_atual}  ·  DIFICULDADE {min(nivel_atual, 7)}/7", True, COR_TEXTO)
        tela.blit(txt_fase, (sx(520), sy(57)))

        if logo_img:
            tela.blit(logo_img, (LARGURA - logo_img.get_width() - sw(20), sy(10)))

        # Rótulos e fotos dos Suspeitos (Topo)
        for col in range(4):
            nome_s = suspeitos[col]
            img_s = imgs_suspeitos.get(nome_s)
            if img_s:
                tela.blit(img_s, (sx(ox + col * tam_celula + 2), sy(oy - 75)))
            txt_col = fonte_grelha.render(nome_s[:4], True, COR_AMARELO)
            tela.blit(txt_col, (sx(ox + col * tam_celula + 10), sy(oy - 25)))

        # Desenho da Tabela
        for lin in range(8):
            cor_rotulo = COR_AMARELO if lin < 4 else COR_TEXTO
            txt_lin = fonte_grelha.render(itens_laterais[lin][:10], True, cor_rotulo)
            tela.blit(txt_lin, (sx(ox - 140), sy(oy + lin * tam_celula + 16)))

            for col in range(4):
                rect = srect(ox + col * tam_celula, oy + lin * tam_celula, tam_celula - 2, tam_celula - 2)
                pygame.draw.rect(tela, COR_CELULA, rect, border_radius=sw(7))
                pygame.draw.rect(tela, (61, 76, 78), rect, 1, border_radius=sw(7))

                val = estado_jogo["grelha_unica"][lin][col]
                if val == 1:
                    txt_x = fonte_titulo.render("X", True, COR_VERMELHO)
                    tela.blit(txt_x, (rect.x + sw(17), rect.y + sh(12)))
                elif val == 2:
                    txt_v = fonte_titulo.render("V", True, COR_VERDE)
                    tela.blit(txt_v, (rect.x + sw(17), rect.y + sh(12)))

        pygame.draw.line(
            tela,
            COR_DIVISOR_TABELA,
            (sx(ox - 140), sy(oy + 4 * tam_celula - 1)),
            (sx(ox + 4 * tam_celula), sy(oy + 4 * tam_celula - 1)),
            max(2, sw(3))
        )

        # 4. MODAL DE ACUSAÇÃO
        if modal_acusacao_aberto and not estado_jogo["jogo_encerrado"]:
            s_overlay = pygame.Surface((LARGURA, ALTURA))
            s_overlay.set_alpha(200)
            s_overlay.fill((0, 0, 0))
            tela.blit(s_overlay, (0, 0))

            rect_modal = srect(350, 150, 500, 400)
            pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_modal, border_radius=sw(12))
            pygame.draw.rect(tela, COR_AMARELO, rect_modal, max(1, sw(2)), border_radius=sw(12))

            txt_mod_tit = fonte_titulo.render("MONTE SUA ACUSAÇÃO", True, COR_AMARELO)
            tela.blit(txt_mod_tit, (sx(370), sy(170)))

            btn_s_esq = srect(480, 215, 35, 30)
            btn_s_dir = srect(720, 215, 35, 30)
            btn_a_esq = srect(480, 275, 35, 30)
            btn_a_dir = srect(720, 275, 35, 30)
            btn_l_esq = srect(480, 335, 35, 30)
            btn_l_dir = srect(720, 335, 35, 30)

            pygame.draw.rect(tela, COR_BOTAO_SETA, btn_s_esq, border_radius=sw(5))
            pygame.draw.rect(tela, COR_BOTAO_SETA, btn_s_dir, border_radius=sw(5))
            tela.blit(fonte_titulo.render("<", True, COR_TEXTO), (btn_s_esq.x + sw(11), btn_s_esq.y + sh(3)))
            tela.blit(fonte_titulo.render(">", True, COR_TEXTO), (btn_s_dir.x + sw(11), btn_s_dir.y + sh(3)))

            pygame.draw.rect(tela, COR_BOTAO_SETA, btn_a_esq, border_radius=sw(5))
            pygame.draw.rect(tela, COR_BOTAO_SETA, btn_a_dir, border_radius=sw(5))
            tela.blit(fonte_titulo.render("<", True, COR_TEXTO), (btn_a_esq.x + sw(11), btn_a_esq.y + sh(3)))
            tela.blit(fonte_titulo.render(">", True, COR_TEXTO), (btn_a_dir.x + sw(11), btn_a_dir.y + sh(3)))

            pygame.draw.rect(tela, COR_BOTAO_SETA, btn_l_esq, border_radius=sw(5))
            pygame.draw.rect(tela, COR_BOTAO_SETA, btn_l_dir, border_radius=sw(5))
            tela.blit(fonte_titulo.render("<", True, COR_TEXTO), (btn_l_esq.x + sw(11), btn_l_esq.y + sh(3)))
            tela.blit(fonte_titulo.render(">", True, COR_TEXTO), (btn_l_dir.x + sw(11), btn_l_dir.y + sh(3)))

            txt_s_label = fonte_grelha.render("1. Suspeito:", True, COR_TEXTO)
            tela.blit(txt_s_label, (sx(370), sy(220)))
            txt_s_val = fonte_grelha.render(suspeitos[sel_suspeito], True, COR_AMARELO if categoria_foco == 0 else COR_TEXTO)
            tela.blit(txt_s_val, (sx(530), sy(220)))

            txt_a_label = fonte_grelha.render("2. Arma:", True, COR_TEXTO)
            tela.blit(txt_a_label, (sx(370), sy(280)))
            txt_a_val = fonte_grelha.render(armas[sel_arma], True, COR_AMARELO if categoria_foco == 1 else COR_TEXTO)
            tela.blit(txt_a_val, (sx(530), sy(280)))

            txt_l_label = fonte_grelha.render("3. Local:", True, COR_TEXTO)
            tela.blit(txt_l_label, (sx(370), sy(340)))
            txt_l_val = fonte_grelha.render(locais[sel_local], True, COR_AMARELO if categoria_foco == 2 else COR_TEXTO)
            tela.blit(txt_l_val, (sx(530), sy(340)))

            txt_inst = fonte_pista.render("Clique nos botões < > ou use as setas do teclado", True, COR_AMARELO)
            tela.blit(txt_inst, (sx(370), sy(385)))

            btn_confirmar = srect(370, 430, 220, 45)
            pygame.draw.rect(tela, COR_VERDE, btn_confirmar, border_radius=sw(8))
            txt_conf = fonte_titulo.render("CONFIRMAR", True, COR_TEXTO)
            tela.blit(txt_conf, (btn_confirmar.x + sw(50), btn_confirmar.y + sh(10)))

            btn_cancelar = srect(610, 430, 220, 45)
            pygame.draw.rect(tela, COR_VERMELHO, btn_cancelar, border_radius=sw(8))
            txt_canc = fonte_titulo.render("CANCELAR", True, COR_TEXTO)
            tela.blit(txt_canc, (btn_cancelar.x + sw(60), btn_cancelar.y + sh(10)))

        # 5. MODAL DE FIM DE JOGO (CASO RESOLVIDO)
        if estado_jogo["jogo_encerrado"]:
            s_overlay = pygame.Surface((LARGURA, ALTURA))
            s_overlay.set_alpha(220)
            s_overlay.fill((0, 0, 0))
            tela.blit(s_overlay, (0, 0))

            tempo_esgotado = estado_jogo["mensagem_resultado"].startswith(("TEMPO ESGOTADO", "ACABARAM AS TENTATIVAS"))
            rect_box = srect(320, 85, 560, 550) if tempo_esgotado else srect(320, 150, 560, 400)
            pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_box, border_radius=sw(12))
            pygame.draw.rect(tela, COR_AMARELO, rect_box, max(1, sw(2)), border_radius=sw(12))

            if tempo_esgotado:
                if img_fim_de_jogo:
                    tela.blit(img_fim_de_jogo, (sx(400), sy(110)))
                else:
                    tela.blit(fonte_titulo.render("FIM DE JOGO", True, COR_VERMELHO), (sx(515), sy(125)))
                mensagem_fim = "ACABARAM AS TENTATIVAS!" if estado_jogo["mensagem_resultado"].startswith("ACABARAM AS TENTATIVAS") else "TEMPO ESGOTADO!"
                tela.blit(fonte_titulo.render(mensagem_fim, True, COR_VERMELHO), (sx(500), sy(350)))
                tela.blit(fonte_titulo.render("Deseja jogar novamente?", True, COR_TEXTO), (sx(460), sy(390)))
                btn_reiniciar = srect(360, 470, 220, 50)
                btn_sair = srect(600, 470, 220, 50)
                pygame.draw.rect(tela, COR_VERDE, btn_reiniciar, border_radius=sw(8))
                pygame.draw.rect(tela, COR_VERMELHO, btn_sair, border_radius=sw(8))
                tela.blit(fonte_titulo.render("JOGAR NOVAMENTE", True, COR_TEXTO), (btn_reiniciar.x + sw(14), btn_reiniciar.y + sh(12)))
                tela.blit(fonte_titulo.render("SAIR DO JOGO", True, COR_TEXTO), (btn_sair.x + sw(35), btn_sair.y + sh(12)))
            else:
                txt_vit = fonte_titulo.render("CASO RESOLVIDO COM SUCESSO!", True, COR_VERDE)
                tela.blit(txt_vit, (sx(350), sy(200)))
                img_culpado = imgs_suspeitos_modal.get(estado_jogo["culpado"])
                if img_culpado:
                    tela.blit(img_culpado, (sx(555), sy(240)))
                txt_sol = fonte_pista.render(
                    f"Culpado: {estado_jogo['culpado']}  |  Arma: {estado_jogo['arma_real']}  |  Local: {estado_jogo['local_real']}",
                    True, COR_AMARELO
                )
                tela.blit(txt_sol, (sx(350), sy(345)))
                tela.blit(fonte_titulo.render("Deseja jogar um novo enigma?", True, COR_TEXTO), (sx(440), sy(380)))
                btn_reiniciar = srect(360, 430, 220, 50)
                pygame.draw.rect(tela, COR_VERDE, btn_reiniciar, border_radius=sw(8))
                tela.blit(fonte_titulo.render("PRÓXIMA FASE", True, COR_TEXTO), (btn_reiniciar.x + sw(48), btn_reiniciar.y + sh(12)))
                tela.blit(fonte_pista.render(f"O próximo caso será a fase {nivel_atual + 1}.", True, COR_AMARELO), (sx(440), sy(410)))
                btn_sair = srect(600, 430, 220, 50)
                pygame.draw.rect(tela, COR_VERMELHO, btn_sair, border_radius=sw(8))
                tela.blit(fonte_titulo.render("SAIR", True, COR_TEXTO), (btn_sair.x + sw(18), btn_sair.y + sh(12)))

    # TELA DE RANKING FINAL
    elif etapa_atual == "RANKING_FINAL":
        tela.fill(COR_ESQUERDA)

        rect_box = srect(320, 150, 560, 400)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_box, border_radius=sw(12))
        pygame.draw.rect(tela, COR_AMARELO, rect_box, max(1, sw(2)), border_radius=sw(12))

        txt_t = fonte_titulo.render("RANKING FINAL DO INVESTIGADOR", True, COR_AMARELO)
        tela.blit(txt_t, (sx(350), sy(180)))

        txt_p = fonte_grelha.render(f"Detetive: {nome_jogador}", True, COR_TEXTO)
        tela.blit(txt_p, (sx(350), sy(230)))

        txt_c = fonte_grelha.render(f"Casos Resolvidos: {casos_resolvidos}", True, COR_TEXTO)
        tela.blit(txt_c, (sx(350), sy(260)))

        txt_pts = fonte_titulo.render(f"Pontuação Total: {pontuacao_total} pts", True, COR_VERDE)
        tela.blit(txt_pts, (sx(350), sy(300)))

        txt_msg = fonte_pista.render("Obrigado por jogar SHERLOGIC!", True, COR_TEXTO)
        tela.blit(txt_msg, (sx(350), sy(360)))

        btn_fechar = srect(350, 440, 500, 50)
        pygame.draw.rect(tela, COR_VERMELHO, btn_fechar, border_radius=sw(8))
        txt_fc = fonte_titulo.render("FECHAR JOGO", True, COR_TEXTO)
        tela.blit(txt_fc, (btn_fechar.x + sw(190), btn_fechar.y + sh(12)))

    # GERENCIAMENTO DE EVENTOS DE ENTRADA
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.MOUSEWHEEL and etapa_atual == "JOGO":
            max_scroll = max(0.0, float(altura_total_pistas - 401))
            alvo_scroll = max(0.0, min(max_scroll, alvo_scroll - evento.y * 35))

        elif evento.type == pygame.KEYDOWN:
            if etapa_atual == "NOME":
                if evento.key == pygame.K_RETURN and nome_jogador.strip():
                    etapa_atual = "PERGUNTA_TUTORIAL"
                elif evento.key == pygame.K_BACKSPACE:
                    nome_jogador = nome_jogador[:-1]
                else:
                    if len(nome_jogador) < 15 and evento.unicode.isprintable():
                        nome_jogador += evento.unicode

            elif etapa_atual == "JOGO" and not estado_jogo["jogo_encerrado"]:
                if modal_acusacao_aberto:
                    if evento.key == pygame.K_ESCAPE:
                        modal_acusacao_aberto = False
                    elif evento.key == pygame.K_UP:
                        categoria_foco = (categoria_foco - 1) % 3
                    elif evento.key == pygame.K_DOWN:
                        categoria_foco = (categoria_foco + 1) % 3
                    elif evento.key == pygame.K_LEFT:
                        if categoria_foco == 0:
                            sel_suspeito = (sel_suspeito - 1) % 4
                        elif categoria_foco == 1:
                            sel_arma = (sel_arma - 1) % 4
                        elif categoria_foco == 2:
                            sel_local = (sel_local - 1) % 4
                    elif evento.key == pygame.K_RIGHT:
                        if categoria_foco == 0:
                            sel_suspeito = (sel_suspeito + 1) % 4
                        elif categoria_foco == 1:
                            sel_arma = (sel_arma + 1) % 4
                        elif categoria_foco == 2:
                            sel_local = (sel_local + 1) % 4
                else:
                    if evento.key == pygame.K_ESCAPE:
                        etapa_atual = "RANKING_FINAL"
                    elif evento.key == pygame.K_1:
                        if estado_jogo["pista_index"] < min(len(estado_jogo["pistas"]), limite_pistas_fase(nivel_atual)):
                            estado_jogo["pistas_reveladas"].append(estado_jogo["pistas"][estado_jogo["pista_index"]])
                            estado_jogo["pista_index"] += 1
                            animacao_nova_pista_y = 380.0
                            alvo_scroll = max(0.0, float(altura_total_pistas + 100 - 401))
                        else:
                            estado_jogo["mensagem_resultado"] = "LIMITE DE PISTAS DESTA FASE ATINGIDO."
                            estado_jogo["cor_resultado"] = COR_AMARELO
                    elif evento.key == pygame.K_2:
                        modal_acusacao_aberto = True

            elif etapa_atual == "RANKING_FINAL":
                if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    rodando = False

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            pos_mouse = evento.pos

            if etapa_atual == "NOME":
                btn_avancar = srect(380, 400, 440, 45)
                if btn_avancar.collidepoint(pos_mouse) and nome_jogador.strip():
                    etapa_atual = "PERGUNTA_TUTORIAL"

            elif etapa_atual == "PERGUNTA_TUTORIAL":
                btn_sim = srect(380, 360, 200, 50)
                btn_nao = srect(620, 360, 200, 50)

                if btn_sim.collidepoint(pos_mouse):
                    etapa_atual = "TUTORIAL"
                    passo_tutorial = 0
                elif btn_nao.collidepoint(pos_mouse):
                    etapa_atual = "JOGO"
                    estado_jogo = iniciar_novo_jogo()
                    pistas_scroll = 0.0
                    alvo_scroll = 0.0

            elif etapa_atual == "TUTORIAL":
                btn_prox = srect(750, 530, 220, 45)
                if btn_prox.collidepoint(pos_mouse):
                    if passo_tutorial < 2:
                        passo_tutorial += 1
                    else:
                        etapa_atual = "JOGO"
                        estado_jogo = iniciar_novo_jogo()
                        pistas_scroll = 0.0
                        alvo_scroll = 0.0

            elif etapa_atual == "JOGO":
                if estado_jogo["jogo_encerrado"]:
                    tempo_esgotado = estado_jogo["mensagem_resultado"].startswith(("TEMPO ESGOTADO", "ACABARAM AS TENTATIVAS"))
                    y_botoes = 470 if tempo_esgotado else 430
                    btn_reiniciar = srect(360, y_botoes, 220, 50)
                    btn_sair = srect(600, y_botoes, 220, 50)

                    if btn_reiniciar.collidepoint(pos_mouse):
                        if not tempo_esgotado:
                            nivel_atual += 1
                        else:
                            nivel_atual = 1
                        estado_jogo = iniciar_novo_jogo()
                        pistas_scroll = 0.0
                        alvo_scroll = 0.0
                        modal_acusacao_aberto = False
                    elif btn_sair.collidepoint(pos_mouse):
                        etapa_atual = "RANKING_FINAL"

                elif modal_acusacao_aberto:
                    btn_s_esq = srect(480, 215, 35, 30)
                    btn_s_dir = srect(720, 215, 35, 30)
                    btn_a_esq = srect(480, 275, 35, 30)
                    btn_a_dir = srect(720, 275, 35, 30)
                    btn_l_esq = srect(480, 335, 35, 30)
                    btn_l_dir = srect(720, 335, 35, 30)
                    btn_confirmar = srect(370, 430, 220, 45)
                    btn_cancelar = srect(610, 430, 220, 45)

                    if btn_s_esq.collidepoint(pos_mouse):
                        sel_suspeito = (sel_suspeito - 1) % 4
                        categoria_foco = 0
                    elif btn_s_dir.collidepoint(pos_mouse):
                        sel_suspeito = (sel_suspeito + 1) % 4
                        categoria_foco = 0

                    elif btn_a_esq.collidepoint(pos_mouse):
                        sel_arma = (sel_arma - 1) % 4
                        categoria_foco = 1
                    elif btn_a_dir.collidepoint(pos_mouse):
                        sel_arma = (sel_arma + 1) % 4
                        categoria_foco = 1

                    elif btn_l_esq.collidepoint(pos_mouse):
                        sel_local = (sel_local - 1) % 4
                        categoria_foco = 2
                    elif btn_l_dir.collidepoint(pos_mouse):
                        sel_local = (sel_local + 1) % 4
                        categoria_foco = 2

                    elif btn_confirmar.collidepoint(pos_mouse):
                        modal_acusacao_aberto = False
                        s_palpite = suspeitos[sel_suspeito]
                        a_palpite = armas[sel_arma]
                        l_palpite = locais[sel_local]

                        if s_palpite == estado_jogo["culpado"] and a_palpite == estado_jogo["arma_real"] and l_palpite == estado_jogo["local_real"]:
                            tempo_gasto = int(time.time() - estado_jogo["tempo_inicio"])
                            pistas_usadas = len(estado_jogo["pistas_reveladas"])

                            pontos_rodada = max(100, 1000 - (tempo_gasto * 5) - (pistas_usadas * 100))
                            pontuacao_total += pontos_rodada
                            casos_resolvidos += 1

                            estado_jogo["mensagem_resultado"] = f"SOLUÇÃO CORRETA! (+{pontos_rodada} pts)"
                            estado_jogo["cor_resultado"] = COR_VERDE
                            estado_jogo["jogo_encerrado"] = True
                        else:
                            estado_jogo["tentativas_acusacao"] += 1
                            estado_jogo["cor_resultado"] = COR_VERMELHO
                            if estado_jogo["tentativas_acusacao"] >= 3:
                                estado_jogo["mensagem_resultado"] = "ACABARAM AS TENTATIVAS! O caso foi encerrado."
                                estado_jogo["jogo_encerrado"] = True
                            else:
                                restantes = 3 - estado_jogo["tentativas_acusacao"]
                                estado_jogo["mensagem_resultado"] = f"ACUSAÇÃO FALSA! Restam {restantes} tentativas."

                    elif btn_cancelar.collidepoint(pos_mouse):
                        modal_acusacao_aberto = False

                else:
                    if btn_pedir_pista.collidepoint(pos_mouse):
                        if estado_jogo["pista_index"] < min(len(estado_jogo["pistas"]), limite_pistas_fase(nivel_atual)):
                            estado_jogo["pistas_reveladas"].append(estado_jogo["pistas"][estado_jogo["pista_index"]])
                            estado_jogo["pista_index"] += 1
                            animacao_nova_pista_y = 380.0
                            alvo_scroll = max(0.0, float(altura_total_pistas + 100 - 401))
                        else:
                            estado_jogo["mensagem_resultado"] = "LIMITE DE PISTAS DESTA FASE ATINGIDO."
                            estado_jogo["cor_resultado"] = COR_AMARELO

                    elif btn_acusar.collidepoint(pos_mouse):
                        modal_acusacao_aberto = True

                    elif btn_sair_jogo.collidepoint(pos_mouse):
                        etapa_atual = "RANKING_FINAL"

                    for lin in range(8):
                        for col in range(4):
                            r = srect(ox + col * tam_celula, oy + lin * tam_celula, tam_celula, tam_celula)
                            if r.collidepoint(pos_mouse):
                                estado_jogo["grelha_unica"][lin][col] = (estado_jogo["grelha_unica"][lin][col] + 1) % 3

            elif etapa_atual == "RANKING_FINAL":
                btn_fechar = srect(350, 440, 500, 50)
                if btn_fechar.collidepoint(pos_mouse):
                    rodando = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()