import pygame
import random
import sys

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
        "grelha_unica": [[0 for _ in range(4)] for _ in range(8)],
        "mensagem_resultado": "",
        "cor_resultado": (240, 240, 240),
        "tempo_inicio": time.time()
    }

# INICIALIZAÇÃO DO PYGAME
pygame.init()
LARGURA, ALTURA = 1200, 720
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("SHERLOGIC - Painel de Investigação")
clock = pygame.time.Clock()

# CARREGAMENTO DAS IMAGENS (LOGOS E SUSPEITOS)
def carregar_imagem(caminho, tamanho):
    if os.path.exists(caminho):
        img = pygame.image.load(caminho).convert_alpha()
        return pygame.transform.smoothscale(img, tamanho)
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

# CORES E FONTES
COR_ESQUERDA = (30, 35, 45)
COR_DIREITA = (20, 22, 28)
COR_LINHA_DIVISORA = (70, 80, 105)
COR_TEXTO = (240, 240, 240)
COR_AMARELO = (240, 200, 80)
COR_BOTAO_PISTA = (50, 120, 180)
COR_BOTAO_ACUSAR = (180, 60, 60)
COR_BOTAO_SAIR = (130, 40, 40)
COR_VERMELHO = (220, 60, 60)
COR_VERDE = (60, 200, 100)
COR_CELULA = (40, 45, 60)
COR_DIVISOR_TABELA = (90, 100, 130)
COR_MODAL_FUNDO = (15, 18, 24)
COR_BOTAO_SETA = (50, 60, 80)
COR_CAMPO_TEXTO = (35, 40, 55)

fonte_titulo = pygame.font.SysFont("arial", 20, bold=True)
fonte_pista = pygame.font.SysFont("arial", 13)
fonte_grelha = pygame.font.SysFont("arial", 13)
fonte_grelha.set_bold(True)

btn_pedir_pista = pygame.Rect(20, 580, 460, 45)
btn_acusar = pygame.Rect(20, 635, 460, 45)

tam_celula = 50
ox = 740
oy = 140

# Inicializa o estado do jogo
estado_jogo = iniciar_novo_jogo()

modal_acusacao_aberto = False
sel_suspeito = 0
sel_arma = 0
sel_local = 0
categoria_foco = 0

estado_jogo = iniciar_novo_jogo()

def desenhar_texto_multilinhas(superficie, texto, x, y, largura_max, fonte, cor):
    palavras = texto.split(' ')
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        test_line = linha_atual + palavra + " "
        if fonte.size(test_line)[0] <= largura_max:
            linha_atual = test_line
        else:
            linhas.append(linha_atual)
            linha_atual = palavra + " "
    linhas.append(linha_atual)

    altura_y = y
    for linha in linhas:
        txt_surface = fonte.render(linha.strip(), True, cor)
        superficie.blit(txt_surface, (x, altura_y))
        altura_y += fonte.get_height() + 2
    return altura_y

# Loop Principal
rodando = True
while rodando:
    
    # TELA DE DIGITAÇÃO DO NOME
    if etapa_atual == "NOME":
        tela.fill(COR_ESQUERDA)
        
        rect_box = pygame.Rect(350, 200, 500, 300)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_box, border_radius=12)
        pygame.draw.rect(tela, COR_AMARELO, rect_box, 2, border_radius=12)
        
        txt_t = fonte_titulo.render("BEM-VINDO AO SHERLOGIC", True, COR_AMARELO)
        tela.blit(txt_t, (380, 230))
        
        txt_sub = fonte_grelha.render("Digite o seu nome de detetive:", True, COR_TEXTO)
        tela.blit(txt_sub, (380, 280))
        
        rect_input = pygame.Rect(380, 320, 440, 45)
        pygame.draw.rect(tela, COR_CAMPO_TEXTO, rect_input, border_radius=6)
        pygame.draw.rect(tela, COR_LINHA_DIVISORA, rect_input, 1, border_radius=6)
        
        txt_nome = fonte_titulo.render(nome_jogador + "|", True, COR_AMARELO)
        tela.blit(txt_nome, (rect_input.x + 15, rect_input.y + 10))
        
        btn_avancar = pygame.Rect(380, 400, 440, 45)
        pygame.draw.rect(tela, COR_VERDE, btn_avancar, border_radius=8)
        txt_av = fonte_titulo.render("CONTINUAR", True, COR_TEXTO)
        tela.blit(txt_av, (btn_avancar.x + 160, btn_avancar.y + 10))

    # TELA DE PERGUNTA DO TUTORIAL
    elif etapa_atual == "PERGUNTA_TUTORIAL":
        tela.fill(COR_ESQUERDA)
        
        rect_box = pygame.Rect(350, 220, 500, 260)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_box, border_radius=12)
        pygame.draw.rect(tela, COR_AMARELO, rect_box, 2, border_radius=12)
        
        txt_t = fonte_titulo.render(f"Olá, Detetive {nome_jogador}!", True, COR_AMARELO)
        tela.blit(txt_t, (380, 250))
        
        txt_q = fonte_grelha.render("Deseja fazer o tutorial interativo?", True, COR_TEXTO)
        tela.blit(txt_q, (380, 290))
        
        btn_sim = pygame.Rect(380, 360, 200, 50)
        pygame.draw.rect(tela, COR_VERDE, btn_sim, border_radius=8)
        txt_s = fonte_titulo.render("SIM", True, COR_TEXTO)
        tela.blit(txt_s, (btn_sim.x + 85, btn_sim.y + 12))
        
        btn_nao = pygame.Rect(620, 360, 200, 50)
        pygame.draw.rect(tela, COR_BOTAO_PISTA, btn_nao, border_radius=8)
        txt_n = fonte_titulo.render("NÃO", True, COR_TEXTO)
        tela.blit(txt_n, (btn_nao.x + 80, btn_nao.y + 12))

    # TELA DE TUTORIAL
    elif etapa_atual == "TUTORIAL":
        tela.fill(COR_ESQUERDA)
        
        rect_tut = pygame.Rect(200, 100, 800, 500)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_tut, border_radius=12)
        pygame.draw.rect(tela, COR_AMARELO, rect_tut, 2, border_radius=12)
        
        txt_tut_t = fonte_titulo.render(f"TUTORIAL - PARTE {passo_tutorial + 1} DE 3", True, COR_AMARELO)
        tela.blit(txt_tut_t, (230, 130))
        
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
                "Ao acertar, o jogo revela a vitória e já carrega um novo enigma."
            ]
            desenhar_linhas_tutorial(tela, linhas_parte_3, 230, 180, fonte_tutorial, COR_TEXTO)

        btn_prox = pygame.Rect(750, 530, 220, 45)
        pygame.draw.rect(tela, COR_VERDE, btn_prox, border_radius=8)
        lbl_btn = "AVANÇAR" if passo_tutorial < 2 else "INICIAR JOGO"
        txt_px = fonte_titulo.render(lbl_btn, True, COR_TEXTO)
        tela.blit(txt_px, (btn_prox.x + 35, btn_prox.y + 10))

    # TELA PRINCIPAL DO JOGO
    elif etapa_atual == "JOGO":
        suspeitos = estado_jogo["suspeitos"]
        armas = estado_jogo["armas"]
        locais = estado_jogo["locais"]
        itens_laterais = armas + locais

    # 1. DESENHAR METADE ESQUERDA (PISTAS E BOTÕES)
    pygame.draw.rect(tela, COR_ESQUERDA, (0, 0, 500, ALTURA))
    
    txt_tit1 = fonte_titulo.render("PISTAS REVELADAS", True, COR_AMARELO)
    tela.blit(txt_tit1, (20, 15))

    # Exibe histórico de pistas
    y_pista = 45
    for i, p in enumerate(estado_jogo["pistas_reveladas"]):
        if y_pista > 520:
            break
        txt_f = fonte_grelha.render(f"Pista {i+1}: {p['formula']}", True, COR_AMARELO)
        tela.blit(txt_f, (20, y_pista))
        y_pista += 18
        
        y_pista = desenhar_texto_multilinhas(tela, f"\"{p['historia']}\"", 20, y_pista, 450, fonte_pista, COR_TEXTO)
        y_pista += 6

    if estado_jogo["mensagem_resultado"]:
        txt_res = fonte_titulo.render(estado_jogo["mensagem_resultado"], True, estado_jogo["cor_resultado"])
        tela.blit(txt_res, (20, 550))

    # Botões Esquerda
    pygame.draw.rect(tela, COR_BOTAO_PISTA, btn_pedir_pista, border_radius=8)
    txt_btn1 = fonte_titulo.render("PEDIR NOVA PISTA [1]", True, COR_TEXTO)
    tela.blit(txt_btn1, (btn_pedir_pista.x + 115, btn_pedir_pista.y + 11))

    pygame.draw.rect(tela, COR_BOTAO_ACUSAR, btn_acusar, border_radius=8)
    txt_btn2 = fonte_titulo.render("FAZER ACUSAÇÃO [2]", True, COR_TEXTO)
    tela.blit(txt_btn2, (btn_acusar.x + 125, btn_acusar.y + 11))

    # 2. DESENHAR DIVISÓRIA CENTRAL
    pygame.draw.line(tela, COR_LINHA_DIVISORA, (500, 0), (500, ALTURA), 4)

    # 3. DESENHAR METADE DIREITA (GRELHA DE DEDUÇÃO)
    pygame.draw.rect(tela, COR_DIREITA, (500, 0, 700, ALTURA))
    
    txt_tit2 = fonte_titulo.render("GRELHA DE DEDUÇÃO", True, COR_AMARELO)
    tela.blit(txt_tit2, (520, 15))

    # Rótulos dos Suspeitos (Topo)
    for col in range(4):
        txt_col = fonte_grelha.render(suspeitos[col][:4], True, COR_AMARELO)
        tela.blit(txt_col, (ox + col * tam_celula + 10, oy - 25))

    # Desenho da Tabela
    for lin in range(8):
        cor_rotulo = COR_AMARELO if lin < 4 else COR_TEXTO
        txt_lin = fonte_grelha.render(itens_laterais[lin][:10], True, cor_rotulo)
        tela.blit(txt_lin, (ox - 140, oy + lin * tam_celula + 16))

        for col in range(4):
            rect = pygame.Rect(ox + col * tam_celula, oy + lin * tam_celula, tam_celula - 2, tam_celula - 2)
            pygame.draw.rect(tela, COR_CELULA, rect, border_radius=4)
            
            val = estado_jogo["grelha_unica"][lin][col]
            if val == 1:
                txt_x = fonte_titulo.render("X", True, COR_VERMELHO)
                tela.blit(txt_x, (rect.x + 17, rect.y + 12))
            elif val == 2:
                txt_v = fonte_titulo.render("V", True, COR_VERDE)
                tela.blit(txt_v, (rect.x + 17, rect.y + 12))

        pygame.draw.line(tela, COR_DIVISOR_TABELA, (ox - 140, oy + 4 * tam_celula - 1), (ox + 4 * tam_celula, oy + 4 * tam_celula - 1), 3)

    # 4. MODAL DE ACUSAÇÃO INTERATIVO (COM POSIÇÕES FIXAS PARA AS SETAS)
    if modal_acusacao_aberto and not estado_jogo["jogo_encerrado"]:
        s_overlay = pygame.Surface((LARGURA, ALTURA))
        s_overlay.set_alpha(200)
        s_overlay.fill((0, 0, 0))
        tela.blit(s_overlay, (0, 0))

        rect_modal = pygame.Rect(350, 150, 500, 400)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_modal, border_radius=12)
        pygame.draw.rect(tela, COR_AMARELO, rect_modal, 2, border_radius=12)

        txt_mod_tit = fonte_titulo.render("MONTE SUA ACUSAÇÃO", True, COR_AMARELO)
        tela.blit(txt_mod_tit, (370, 170))

        # BOTÕES DAS SETAS COM POSIÇÕES FIXAS ABSOLUTAS
        btn_s_esq = pygame.Rect(480, 215, 35, 30)
        btn_s_dir = pygame.Rect(720, 215, 35, 30)
        
        btn_a_esq = pygame.Rect(480, 275, 35, 30)
        btn_a_dir = pygame.Rect(720, 275, 35, 30)
        
        btn_l_esq = pygame.Rect(480, 335, 35, 30)
        btn_l_dir = pygame.Rect(720, 335, 35, 30)

        # Desenhar Botões < e > de Suspeito
        pygame.draw.rect(tela, COR_BOTAO_SETA, btn_s_esq, border_radius=5)
        pygame.draw.rect(tela, COR_BOTAO_SETA, btn_s_dir, border_radius=5)
        tela.blit(fonte_titulo.render("<", True, COR_TEXTO), (btn_s_esq.x + 11, btn_s_esq.y + 3))
        tela.blit(fonte_titulo.render(">", True, COR_TEXTO), (btn_s_dir.x + 11, btn_s_dir.y + 3))

        # Desenhar Botões < e > de Arma
        pygame.draw.rect(tela, COR_BOTAO_SETA, btn_a_esq, border_radius=5)
        pygame.draw.rect(tela, COR_BOTAO_SETA, btn_a_dir, border_radius=5)
        tela.blit(fonte_titulo.render("<", True, COR_TEXTO), (btn_a_esq.x + 11, btn_a_esq.y + 3))
        tela.blit(fonte_titulo.render(">", True, COR_TEXTO), (btn_a_dir.x + 11, btn_a_dir.y + 3))

        # Desenhar Botões < e > de Local
        pygame.draw.rect(tela, COR_BOTAO_SETA, btn_l_esq, border_radius=5)
        pygame.draw.rect(tela, COR_BOTAO_SETA, btn_l_dir, border_radius=5)
        tela.blit(fonte_titulo.render("<", True, COR_TEXTO), (btn_l_esq.x + 11, btn_l_esq.y + 3))
        tela.blit(fonte_titulo.render(">", True, COR_TEXTO), (btn_l_dir.x + 11, btn_l_dir.y + 3))

        # Rótulos e Texto Centralizado
        txt_s_label = fonte_grelha.render("1. Suspeito:", True, COR_TEXTO)
        tela.blit(txt_s_label, (370, 220))
        txt_s_val = fonte_grelha.render(suspeitos[sel_suspeito], True, COR_AMARELO if categoria_foco == 0 else COR_TEXTO)
        tela.blit(txt_s_val, (530, 220))

        txt_a_label = fonte_grelha.render("2. Arma:", True, COR_TEXTO)
        tela.blit(txt_a_label, (370, 280))
        txt_a_val = fonte_grelha.render(armas[sel_arma], True, COR_AMARELO if categoria_foco == 1 else COR_TEXTO)
        tela.blit(txt_a_val, (530, 280))

        txt_l_label = fonte_grelha.render("3. Local:", True, COR_TEXTO)
        tela.blit(txt_l_label, (370, 340))
        txt_l_val = fonte_grelha.render(locais[sel_local], True, COR_AMARELO if categoria_foco == 2 else COR_TEXTO)
        tela.blit(txt_l_val, (530, 340))

        txt_inst = fonte_pista.render("Clique nos botões < > ou use as setas do teclado", True, COR_AMARELO)
        tela.blit(txt_inst, (370, 385))

        btn_confirmar = pygame.Rect(370, 430, 220, 45)
        pygame.draw.rect(tela, COR_VERDE, btn_confirmar, border_radius=8)
        txt_conf = fonte_titulo.render("CONFIRMAR", True, COR_TEXTO)
        tela.blit(txt_conf, (btn_confirmar.x + 50, btn_confirmar.y + 10))

        btn_cancelar = pygame.Rect(610, 430, 220, 45)
        pygame.draw.rect(tela, COR_VERMELHO, btn_cancelar, border_radius=8)
        txt_canc = fonte_titulo.render("CANCELAR", True, COR_TEXTO)
        tela.blit(txt_canc, (btn_cancelar.x + 60, btn_cancelar.y + 10))

    # 5. MODAL DE FIM DE JOGO
    if estado_jogo["jogo_encerrado"]:
        s_overlay = pygame.Surface((LARGURA, ALTURA))
        s_overlay.set_alpha(220)
        s_overlay.fill((0, 0, 0))
        tela.blit(s_overlay, (0, 0))

        rect_box = pygame.Rect(320, 150, 560, 400)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_box, border_radius=12)
        pygame.draw.rect(tela, COR_AMARELO, rect_box, 2, border_radius=12)

        txt_vit = fonte_titulo.render("CASO RESOLVIDO COM SUCESSO!", True, COR_VERDE)
        tela.blit(txt_vit, (350, 220))

        txt_sol = fonte_pista.render(
            f"Culpado: {estado_jogo['culpado']}  |  Arma: {estado_jogo['arma_real']}  |  Local: {estado_jogo['local_real']}",
            True, COR_AMARELO
        )
        tela.blit(txt_sol, (350, 260))

        txt_perg = fonte_titulo.render("Deseja jogar um novo enigma?", True, COR_TEXTO)
        tela.blit(txt_perg, (440, 320))

        btn_reiniciar = pygame.Rect(360, 400, 220, 50)
        pygame.draw.rect(tela, COR_VERDE, btn_reiniciar, border_radius=8)
        txt_re = fonte_titulo.render("JOGAR NOVAMENTE", True, COR_TEXTO)
        tela.blit(txt_re, (btn_reiniciar.x + 18, btn_reiniciar.y + 12))

        btn_sair = pygame.Rect(600, 400, 220, 50)
        pygame.draw.rect(tela, COR_VERMELHO, btn_sair, border_radius=8)
        txt_sa = fonte_titulo.render("SAIR DO JOGO", True, COR_TEXTO)
        tela.blit(txt_sa, (btn_sair.x + 45, btn_sair.y + 12))

    # GERENCIAMENTO DE EVENTOS DE ENTRADA
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            if etapa_atual == "NOME":
                if evento.key == pygame.K_RETURN and nome_jogador.strip():
                    etapa_atual = "PERGUNTA_TUTORIAL"
                elif evento.key == pygame.K_BACKSPACE:
                    nome_jogador = nome_jogador[:-1]
                else:
                    if len(nome_jogador) < 15 and evento.unicode.isprintable():
                        nome_jogador += evento.unicode

            elif modal_acusacao_aberto:
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

            elif etapa_atual == "RANKING_FINAL":
                if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    rodando = False

            else:
                if evento.key == pygame.K_1 and estado_jogo["pista_index"] < len(estado_jogo["pistas"]):
                    estado_jogo["pistas_reveladas"].append(estado_jogo["pistas"][estado_jogo["pista_index"]])
                    estado_jogo["pista_index"] += 1
                elif evento.key == pygame.K_2:
                    modal_acusacao_aberto = True

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            pos_mouse = evento.pos

            if estado_jogo["jogo_encerrado"]:
                btn_reiniciar = pygame.Rect(360, 400, 220, 50)
                btn_sair = pygame.Rect(600, 400, 220, 50)

                if btn_reiniciar.collidepoint(pos_mouse):
                    estado_jogo = iniciar_novo_jogo()
                    modal_acusacao_aberto = False
                elif btn_sair.collidepoint(pos_mouse):
                    rodando = False

            elif modal_acusacao_aberto:
                btn_confirmar = pygame.Rect(370, 430, 220, 45)
                btn_cancelar = pygame.Rect(610, 430, 220, 45)

                # CLIQUES PRECISOS NOS BOTÕES < E > DE SUSPEITO
                if btn_s_esq.collidepoint(pos_mouse):
                    sel_suspeito = (sel_suspeito - 1) % 4
                    categoria_foco = 0
                elif btn_s_dir.collidepoint(pos_mouse):
                    sel_suspeito = (sel_suspeito + 1) % 4
                    categoria_foco = 0

                # CLIQUES PRECISOS NOS BOTÕES < E > DE ARMA
                elif btn_a_esq.collidepoint(pos_mouse):
                    sel_arma = (sel_arma - 1) % 4
                    categoria_foco = 1
                elif btn_a_dir.collidepoint(pos_mouse):
                    sel_arma = (sel_arma + 1) % 4
                    categoria_foco = 1

                # CLIQUES PRECISOS NOS BOTÕES < E > DE LOCAL
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
                        estado_jogo["mensagem_resultado"] = "SOLUÇÃO CORRETA!"
                        estado_jogo["cor_resultado"] = COR_VERDE
                        estado_jogo["jogo_encerrado"] = True

                    elif btn_cancelar.collidepoint(pos_mouse):
                        modal_acusacao_aberto = False
                    
                    else:
                        estado_jogo["mensagem_resultado"] = "ACUSAÇÃO FALSA (F)! Tente novamente."
                        estado_jogo["cor_resultado"] = COR_VERMELHO

            elif etapa_atual == "RANKING_FINAL":
                btn_fechar = pygame.Rect(350, 440, 500, 50)
                if btn_fechar.collidepoint(pos_mouse):
                    rodando = False

            else:
                if btn_pedir_pista.collidepoint(pos_mouse):
                    if estado_jogo["pista_index"] < len(estado_jogo["pistas"]):
                        estado_jogo["pistas_reveladas"].append(estado_jogo["pistas"][estado_jogo["pista_index"]])
                        estado_jogo["pista_index"] += 1

                    elif btn_acusar.collidepoint(pos_mouse):
                        modal_acusacao_aberto = True

                for lin in range(8):
                    for col in range(4):
                        r = pygame.Rect(ox + col * tam_celula, oy + lin * tam_celula, tam_celula, tam_celula)
                        if r.collidepoint(pos_mouse):
                            estado_jogo["grelha_unica"][lin][col] = (estado_jogo["grelha_unica"][lin][col] + 1) % 3

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()