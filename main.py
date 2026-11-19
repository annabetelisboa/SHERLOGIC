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


def arredondar_imagem(superficie, raio):
    """Aplica máscara com cantos arredondados a uma superfície Pygame."""
    larg, alt = superficie.get_size()
    mascara = pygame.Surface((larg, alt), pygame.SRCALPHA)
    mascara.fill((0, 0, 0, 0))
    pygame.draw.rect(mascara, (255, 255, 255, 255), (0, 0, larg, alt), border_radius=raio)
    resultado = superficie.copy().convert_alpha()
    resultado.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return resultado


def carregar_imagem(caminho, tamanho, raio_borda=0, usar_escala=True):
    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    nome_base = os.path.splitext(caminho)[0]
    if usar_escala:
        tamanho_escalado = (max(1, sw(tamanho[0])), max(1, sh(tamanho[1])))
    else:
        tamanho_escalado = (max(1, int(tamanho[0])), max(1, int(tamanho[1])))
    for extensao in (".png", ".jpeg", ".jpg", ".PNG", ".JPEG", ".JPG"):
        caminho_completo = os.path.join(diretorio_base, nome_base + extensao)
        if os.path.exists(caminho_completo):
            try:
                img = pygame.image.load(caminho_completo).convert_alpha()
                img = pygame.transform.smoothscale(img, tamanho_escalado)
                if raio_borda > 0:
                    img = arredondar_imagem(img, max(2, sw(raio_borda)))
                return img
            except pygame.error:
                return None
    return None


# Ícone do relógio de bolso transparente ao lado do tempo
img_relogio = carregar_imagem("relogio_transparente.png", (30, 30))
if not img_relogio:
    img_relogio = carregar_imagem("relogio.png", (30, 30))

# Fundo de cena do crime em tela cheia para as telas de abertura, tutorial e ranking
fundo_cena_crime = carregar_imagem("cena_crime.jpg", (LARGURA, ALTURA), raio_borda=0, usar_escala=False)

# Logo grande para a tela inicial (acima do formulário)
logo_inicio_img = carregar_imagem("logosherlogic.jpeg", (520, 175), raio_borda=16)
if not logo_inicio_img:
    logo_inicio_img = carregar_imagem("sóalupalogo.jpeg", (150, 150), raio_borda=16)

# Logo do painel do jogo (canto superior direito)
logo_img = carregar_imagem("logosherlogic.jpeg", (230, 96), raio_borda=14)
if not logo_img:
    logo_img = carregar_imagem("sóalupalogo.jpeg", (80, 80), raio_borda=14)

# Fotos maiores dos personagens acima das colunas ampliadas
imgs_suspeitos = {
    "Mordomo": carregar_imagem("mordomo.jpg", (58, 58), raio_borda=6),
    "Cozinheira": carregar_imagem("cozinheira.jpg", (58, 58), raio_borda=6),
    "Jardineiro": carregar_imagem("jardineiro.jpg", (58, 58), raio_borda=6),
    "Motorista": carregar_imagem("motorista.jpg", (58, 58), raio_borda=6)
}
imgs_suspeitos_modal = {
    "Mordomo": carregar_imagem("mordomo.jpg", (90, 90), raio_borda=8),
    "Cozinheira": carregar_imagem("cozinheira.jpg", (90, 90), raio_borda=8),
    "Jardineiro": carregar_imagem("jardineiro.jpg", (90, 90), raio_borda=8),
    "Motorista": carregar_imagem("motorista.jpg", (90, 90), raio_borda=8)
}
img_fim_de_jogo = carregar_imagem("fim_de_jogo.jpg", (400, 225), raio_borda=10)

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
fonte_botao = pygame.font.SysFont("georgia,bookantiqua,timesnewroman,serif", max(14, int(20 * ESCALA)), bold=True)
fonte_pista = pygame.font.SysFont("segoeui,calibri,arial", max(12, int(16 * ESCALA)))
fonte_formula = pygame.font.SysFont("consolas,segoeui,arial", max(11, int(15 * ESCALA)), bold=True)
fonte_grelha = pygame.font.SysFont("segoeui,arial", max(12, int(15 * ESCALA)), bold=True)
fonte_tutorial = pygame.font.SysFont("segoeui,arial", max(12, int(16 * ESCALA)))
fonte_celula = pygame.font.SysFont("segoeui,arial", max(16, int(25 * ESCALA)), bold=True)

# Botões Painel Esquerdo (coordenadas lógicas 1200x720)
btn_pedir_pista = srect(20, 560, 460, 38)
btn_acusar = srect(20, 605, 460, 38)
btn_sair_jogo = srect(20, 650, 460, 35)

# Células mais largas (96px) para comportar os nomes completos dos suspeitos
larg_celula = 96
alt_celula = 58
ox = 675
oy = 205

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


def desenhar_fundo_inicial(superficie):
    """Desenha a cena do crime no fundo com leve vinheta escura para leitura nítida."""
    if fundo_cena_crime:
        superficie.blit(fundo_cena_crime, (0, 0))
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((12, 16, 19, 95))
        superficie.blit(overlay, (0, 0))
    else:
        superficie.fill(COR_ESQUERDA)


def desenhar_logo_topo_central(superficie, y_logico=65):
    """Desenha a logo grande do Sherlogic com moldura dourada acima da caixa central."""
    if logo_inicio_img:
        pos_x = (LARGURA - logo_inicio_img.get_width()) // 2
        pos_y = sy(y_logico)
        superficie.blit(logo_inicio_img, (pos_x, pos_y))
        rect_externo = pygame.Rect(
            pos_x - sw(4),
            pos_y - sh(4),
            logo_inicio_img.get_width() + sw(8),
            logo_inicio_img.get_height() + sh(8)
        )
        rect_interno = pygame.Rect(
            pos_x + sw(3),
            pos_y + sh(3),
            logo_inicio_img.get_width() - sw(6),
            logo_inicio_img.get_height() - sh(6)
        )
        pygame.draw.rect(superficie, COR_AMARELO, rect_externo, max(2, sw(3)), border_radius=max(4, sw(18)))
        pygame.draw.rect(superficie, COR_AMARELO, rect_interno, max(1, sw(1)), border_radius=max(3, sw(14)))


def desenhar_botao(superficie, rect, cor_fundo, texto, fonte=fonte_botao, cor_texto=COR_TEXTO, raio=8):
    pygame.draw.rect(superficie, cor_fundo, rect, border_radius=sw(raio))
    fonte_uso = fonte
    largura_max_texto = rect.width - sw(20)
    if fonte_uso.size(texto)[0] > largura_max_texto:
        tam_base = max(12, int(20 * ESCALA))
        while tam_base > 10:
            fonte_teste = pygame.font.SysFont("georgia,bookantiqua,timesnewroman,serif", tam_base, bold=True)
            if fonte_teste.size(texto)[0] <= largura_max_texto:
                fonte_uso = fonte_teste
                break
            tam_base -= 1
    txt_surf = fonte_uso.render(texto, True, cor_texto)
    pos_x = rect.x + (rect.width - txt_surf.get_width()) // 2
    pos_y = rect.y + (rect.height - txt_surf.get_height()) // 2
    superficie.blit(txt_surf, (pos_x, pos_y))


def desenhar_texto_centralizado(superficie, texto, centro_x_logico, y_logico, fonte, cor):
    txt_surf = fonte.render(texto, True, cor)
    pos_x = sx(centro_x_logico) - txt_surf.get_width() // 2
    superficie.blit(txt_surf, (pos_x, sy(y_logico)))


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
        desenhar_fundo_inicial(tela)
        desenhar_logo_topo_central(tela, y_logico=70)

        rect_box = srect(350, 275, 500, 285)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_box, border_radius=sw(12))
        pygame.draw.rect(tela, COR_AMARELO, rect_box, max(1, sw(2)), border_radius=sw(12))

        txt_t = fonte_titulo.render("BEM-VINDO AO SHERLOGIC", True, COR_AMARELO)
        tela.blit(txt_t, (sx(380), sy(305)))

        txt_sub = fonte_grelha.render("Digite o seu nome de detetive:", True, COR_TEXTO)
        tela.blit(txt_sub, (sx(380), sy(350)))

        rect_input = srect(380, 390, 440, 45)
        pygame.draw.rect(tela, COR_CAMPO_TEXTO, rect_input, border_radius=sw(6))
        pygame.draw.rect(tela, COR_LINHA_DIVISORA, rect_input, 1, border_radius=sw(6))

        txt_nome = fonte_titulo.render(nome_jogador + "|", True, COR_AMARELO)
        tela.blit(txt_nome, (rect_input.x + sw(15), rect_input.y + sh(10)))

        btn_avancar = srect(380, 468, 440, 48)
        desenhar_botao(tela, btn_avancar, COR_VERDE, "CONTINUAR", raio=8)

    # TELA DE PERGUNTA DO TUTORIAL
    elif etapa_atual == "PERGUNTA_TUTORIAL":
        desenhar_fundo_inicial(tela)
        desenhar_logo_topo_central(tela, y_logico=70)

        rect_box = srect(350, 285, 500, 250)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_box, border_radius=sw(12))
        pygame.draw.rect(tela, COR_AMARELO, rect_box, max(1, sw(2)), border_radius=sw(12))

        txt_t = fonte_titulo.render(f"Olá, Detetive {nome_jogador}!", True, COR_AMARELO)
        tela.blit(txt_t, (sx(380), sy(315)))

        txt_q = fonte_grelha.render("Deseja fazer o tutorial?", True, COR_TEXTO)
        tela.blit(txt_q, (sx(380), sy(355)))

        btn_sim = srect(380, 420, 200, 50)
        desenhar_botao(tela, btn_sim, COR_VERDE, "SIM", raio=8)

        btn_nao = srect(620, 420, 200, 50)
        desenhar_botao(tela, btn_nao, COR_BOTAO_PISTA, "NÃO", raio=8)

    # TELA DE TUTORIAL
    elif etapa_atual == "TUTORIAL":
        desenhar_fundo_inicial(tela)

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
        lbl_btn = "AVANÇAR" if passo_tutorial < 2 else "INICIAR JOGO"
        desenhar_botao(tela, btn_prox, COR_VERDE, lbl_btn, raio=8)

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

        # Relógio de bolso transparente ao lado do TEMPO
        cor_tempo = COR_VERMELHO if tempo_restante <= 10 else COR_AMARELO
        txt_tempo = fonte_grelha.render(f"TEMPO: {tempo_restante // 60:02d}:{tempo_restante % 60:02d}", True, cor_tempo)
        pos_tempo_x = sx(480) - txt_tempo.get_width()
        pos_tempo_y = sy(70)
        tela.blit(txt_tempo, (pos_tempo_x, pos_tempo_y))
        if img_relogio:
            pos_rel_x = pos_tempo_x - img_relogio.get_width() - sw(6)
            pos_rel_y = pos_tempo_y + (txt_tempo.get_height() - img_relogio.get_height()) // 2
            tela.blit(img_relogio, (pos_rel_x, pos_rel_y))

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

        # Botões Esquerda com a mesma tipografia serifada clássica da logo
        desenhar_botao(tela, btn_pedir_pista, COR_BOTAO_PISTA, "PEDIR NOVA PISTA [1]", raio=8)
        desenhar_botao(tela, btn_acusar, COR_BOTAO_ACUSAR, "FAZER ACUSAÇÃO [2]", raio=8)
        desenhar_botao(tela, btn_sair_jogo, COR_BOTAO_SAIR, "SAIR DO JOGO [ESC]", raio=8)

        # 2. METADE DIREITA (GRELHA DE DEDUÇÃO COM COLUNAS LARGAS)
        pygame.draw.rect(tela, COR_DIREITA, (sx(500), 0, LARGURA - sx(500), ALTURA))
        pygame.draw.line(tela, COR_LINHA_DIVISORA, (sx(500), 0), (sx(500), ALTURA), max(2, sw(4)))

        txt_tit2 = fonte_titulo.render("QUADRO DE DEDUÇÕES", True, COR_AMARELO)
        tela.blit(txt_tit2, (sx(520), sy(15)))
        pygame.draw.line(tela, COR_LINHA_DIVISORA, (sx(520), sy(49)), (sx(710), sy(49)), max(1, sw(2)))
        txt_fase = fonte_pista.render(f"FASE {nivel_atual}  ·  DIFICULDADE {min(nivel_atual, 7)}/7", True, COR_TEXTO)
        tela.blit(txt_fase, (sx(520), sy(57)))

        if logo_img:
            pos_logo_x = LARGURA - logo_img.get_width() - sw(20)
            pos_logo_y = sy(12)
            tela.blit(logo_img, (pos_logo_x, pos_logo_y))
            pygame.draw.rect(
                tela,
                COR_AMARELO,
                (pos_logo_x - 1, pos_logo_y - 1, logo_img.get_width() + 2, logo_img.get_height() + 2),
                max(1, sw(2)),
                border_radius=max(2, sw(14))
            )

        # Rótulos completos e fotos dos Suspeitos centralizados nas colunas largas
        for col in range(4):
            nome_s = suspeitos[col]
            img_s = imgs_suspeitos.get(nome_s)
            if img_s:
                pos_foto_x = sx(ox + col * larg_celula + (larg_celula - 58) // 2)
                pos_foto_y = sy(oy - 85)
                tela.blit(img_s, (pos_foto_x, pos_foto_y))
                pygame.draw.rect(
                    tela,
                    COR_AMARELO,
                    (pos_foto_x - 1, pos_foto_y - 1, img_s.get_width() + 2, img_s.get_height() + 2),
                    1,
                    border_radius=sw(6)
                )
            txt_col = fonte_grelha.render(nome_s, True, COR_AMARELO)
            pos_texto_x = sx(ox + col * larg_celula) + (sw(larg_celula) - txt_col.get_width()) // 2
            tela.blit(txt_col, (pos_texto_x, sy(oy - 23)))

        # Desenho da Tabela com Células Mais Largas
        for lin in range(8):
            cor_rotulo = COR_AMARELO if lin < 4 else COR_TEXTO
            txt_lin = fonte_grelha.render(itens_laterais[lin][:10], True, cor_rotulo)
            pos_rotulo_y = sy(oy + lin * alt_celula) + (sh(alt_celula) - txt_lin.get_height()) // 2
            tela.blit(txt_lin, (sx(ox - 125), pos_rotulo_y))

            for col in range(4):
                rect = srect(ox + col * larg_celula, oy + lin * alt_celula, larg_celula - 4, alt_celula - 3)
                pygame.draw.rect(tela, COR_CELULA, rect, border_radius=sw(8))
                pygame.draw.rect(tela, (61, 76, 78), rect, 1, border_radius=sw(8))

                val = estado_jogo["grelha_unica"][lin][col]
                if val == 1:
                    txt_x = fonte_celula.render("X", True, COR_VERMELHO)
                    tela.blit(txt_x, (rect.x + (rect.width - txt_x.get_width()) // 2, rect.y + (rect.height - txt_x.get_height()) // 2))
                elif val == 2:
                    txt_v = fonte_celula.render("V", True, COR_VERDE)
                    tela.blit(txt_v, (rect.x + (rect.width - txt_v.get_width()) // 2, rect.y + (rect.height - txt_v.get_height()) // 2))

        pygame.draw.line(
            tela,
            COR_DIVISOR_TABELA,
            (sx(ox - 125), sy(oy + 4 * alt_celula - 2)),
            (sx(ox + 4 * larg_celula), sy(oy + 4 * alt_celula - 2)),
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

            desenhar_botao(tela, btn_s_esq, COR_BOTAO_SETA, "<", raio=5)
            desenhar_botao(tela, btn_s_dir, COR_BOTAO_SETA, ">", raio=5)
            desenhar_botao(tela, btn_a_esq, COR_BOTAO_SETA, "<", raio=5)
            desenhar_botao(tela, btn_a_dir, COR_BOTAO_SETA, ">", raio=5)
            desenhar_botao(tela, btn_l_esq, COR_BOTAO_SETA, "<", raio=5)
            desenhar_botao(tela, btn_l_dir, COR_BOTAO_SETA, ">", raio=5)

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
            desenhar_botao(tela, btn_confirmar, COR_VERDE, "CONFIRMAR", raio=8)

            btn_cancelar = srect(610, 430, 220, 45)
            desenhar_botao(tela, btn_cancelar, COR_VERMELHO, "CANCELAR", raio=8)

        # 5. MODAL DE FIM DE JOGO (CENTRALIZADO)
        if estado_jogo["jogo_encerrado"]:
            s_overlay = pygame.Surface((LARGURA, ALTURA))
            s_overlay.set_alpha(220)
            s_overlay.fill((0, 0, 0))
            tela.blit(s_overlay, (0, 0))

            tempo_esgotado = estado_jogo["mensagem_resultado"].startswith(("TEMPO ESGOTADO", "ACABARAM AS TENTATIVAS"))
            rect_box = srect(320, 85, 560, 550) if tempo_esgotado else srect(320, 150, 560, 400)
            pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_box, border_radius=sw(12))
            pygame.draw.rect(tela, COR_AMARELO, rect_box, max(1, sw(2)), border_radius=sw(12))

            centro_modal_x = 600  # 320 + 560 / 2

            if tempo_esgotado:
                if img_fim_de_jogo:
                    tela.blit(img_fim_de_jogo, (sx(centro_modal_x - 200), sy(110)))
                else:
                    desenhar_texto_centralizado(tela, "FIM DE JOGO", centro_modal_x, 125, fonte_titulo, COR_VERMELHO)

                mensagem_fim = "ACABARAM AS TENTATIVAS!" if estado_jogo["mensagem_resultado"].startswith("ACABARAM AS TENTATIVAS") else "TEMPO ESGOTADO!"
                desenhar_texto_centralizado(tela, mensagem_fim, centro_modal_x, 355, fonte_titulo, COR_VERMELHO)
                desenhar_texto_centralizado(tela, "Deseja jogar novamente?", centro_modal_x, 398, fonte_titulo, COR_TEXTO)

                btn_reiniciar = srect(355, 470, 230, 52)
                btn_sair = srect(615, 470, 230, 52)
                desenhar_botao(tela, btn_reiniciar, COR_VERDE, "JOGAR NOVAMENTE", raio=8)
                desenhar_botao(tela, btn_sair, COR_VERMELHO, "SAIR DO JOGO", raio=8)
            else:
                desenhar_texto_centralizado(tela, "CASO RESOLVIDO COM SUCESSO!", centro_modal_x, 185, fonte_titulo, COR_VERDE)
                img_culpado = imgs_suspeitos_modal.get(estado_jogo["culpado"])
                if img_culpado:
                    tela.blit(img_culpado, (sx(centro_modal_x - 45), sy(225)))

                desenhar_texto_centralizado(
                    tela,
                    f"Culpado: {estado_jogo['culpado']}  |  Arma: {estado_jogo['arma_real']}  |  Local: {estado_jogo['local_real']}",
                    centro_modal_x, 330, fonte_pista, COR_AMARELO
                )
                desenhar_texto_centralizado(tela, "Deseja jogar um novo enigma?", centro_modal_x, 365, fonte_titulo, COR_TEXTO)
                desenhar_texto_centralizado(
                    tela,
                    f"O próximo caso será a fase {nivel_atual + 1}.",
                    centro_modal_x, 400, fonte_pista, COR_AMARELO
                )

                btn_reiniciar = srect(355, 445, 230, 52)
                btn_sair = srect(615, 445, 230, 52)
                desenhar_botao(tela, btn_reiniciar, COR_VERDE, "PRÓXIMA FASE", raio=8)
                desenhar_botao(tela, btn_sair, COR_VERMELHO, "SAIR", raio=8)

    # TELA DE RANKING FINAL (COM O FUNDO DA CENA DO CRIME)
    elif etapa_atual == "RANKING_FINAL":
        desenhar_fundo_inicial(tela)

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
        desenhar_botao(tela, btn_fechar, COR_VERMELHO, "FECHAR JOGO", raio=8)

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
                btn_avancar = srect(380, 468, 440, 48)
                if btn_avancar.collidepoint(pos_mouse) and nome_jogador.strip():
                    etapa_atual = "PERGUNTA_TUTORIAL"

            elif etapa_atual == "PERGUNTA_TUTORIAL":
                btn_sim = srect(380, 420, 200, 50)
                btn_nao = srect(620, 420, 200, 50)

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
                    y_botoes = 470 if tempo_esgotado else 445
                    btn_reiniciar = srect(355, y_botoes, 230, 52)
                    btn_sair = srect(615, y_botoes, 230, 52)

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
                            r = srect(ox + col * larg_celula, oy + lin * alt_celula, larg_celula, alt_celula)
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