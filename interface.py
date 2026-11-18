import pygame
import random
import sys
import os
import time

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

    opcoes_negacao = [
        f"Um vizinho confirmou que viu {s_falsos[0]} longe da mansão no horário do crime.",
        f"As pegadas registradas na entrada descartam totalmente {s_falsos[0]}.",
        f"O alibi de {s_falsos[0]} foi confirmado pela polícia local na hora do crime."
    ]
    opcoes_condicional = [
        f"A perícia analisou a cena: Se o culpado for {culpado}, a arma NÃO pode ser {a_falsas[0]}.",
        f"Laudo médico: Se o autor é {culpado}, fica descartado o uso de {a_falsas[0]}.",
        f"A investigação concluiu: Se {culpado} for culpado, {a_falsas[0]} não foi usada."
    ]
    opcoes_bicondicional = [
        f"Um bilhete anônimo revela uma ligação direta entre o autor e a arma usada.",
        f"Marcas digitais no cabo mostram conexão inseparável entre o autor e a arma.",
        f"Uma confissão parcial sugere que o culpado usou exclusivamente esta arma."
    ]
    opcoes_demorgan = [
        f"O mordomo jurou que {s_falsos[1]} e {s_falsos[2]} estavam jogando cartas longe da cena.",
        f"Imagens de câmeras mostram {s_falsos[1]} e {s_falsos[2]} juntos no cinema da cidade.",
        f"Testemunhas afirmam que {s_falsos[1]} e {s_falsos[2]} estavam num jantar bem longe dali."
    ]
    opcoes_rastro = [
        f"Um rastro de sangue indica que o uso de {arma_real} leva diretamente ao {local_real}.",
        f"Resíduos encontrados confirmam que {arma_real} foi empregada no(a) {local_real}.",
        f"A análise forense provou que o impacto de {arma_real} ocorreu no(a) {local_real}."
    ]
    opcoes_local = [
        f"As câmeras de segurança descartam qualquer pessoa na {l_falsos[0]}.",
        f"A porta do(a) {l_falsos[0]} estava trancada sem sinal de intrusão.",
        f"A perícia varreu o(a) {l_falsos[0]} e confirmou que o local permaneceu intacto."
    ]

    pistas = [
        {"historia": random.choice(opcoes_negacao), "formula": f"¬{s_falsos[0]}"},
        {"historia": random.choice(opcoes_condicional), "formula": f"{culpado} -> ¬{a_falsas[0]}"},
        {"historia": random.choice(opcoes_bicondicional), "formula": f"{culpado} <-> {arma_real}"},
        {"historia": random.choice(opcoes_demorgan), "formula": f"¬({s_falsos[1]} v {s_falsos[2]})"},
        {"historia": random.choice(opcoes_rastro), "formula": f"{arma_real} -> {local_real}"},
        {"historia": random.choice(opcoes_local), "formula": f"¬{l_falsos[0]}"}
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
        "tentativas_acusacao": 0,
        "grelha_unica": [[0 for _ in range(4)] for _ in range(8)],
        "mensagem_resultado": "",
        "cor_resultado": (236, 232, 216),
        "tempo_inicio": time.time(),
        "tempo_limite": 90, 
        "jogo_encerrado": False
    }

# INICIALIZAÇÃO DO PYGAME
pygame.init()
LARGURA, ALTURA = 1200, 720
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("SHERLOGIC - Painel de Investigação")
clock = pygame.time.Clock()

def carregar_imagem(caminho, tamanho):
    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    nome_base = os.path.splitext(caminho)[0]
    for extensao in (".jpeg", ".jpg", ".png", ".JPEG", ".JPG", ".PNG"):
        caminho_completo = os.path.join(diretorio_base, nome_base + extensao)
        if os.path.exists(caminho_completo):
            try:
                img = pygame.image.load(caminho_completo).convert_alpha()
                return pygame.transform.smoothscale(img, tamanho)
            except pygame.error:
                return None
    return None

# Carregamento de Ativos de Imagem
logo_img = carregar_imagem("logosherlogic.jpeg", (180, 50))
img_relogio = carregar_imagem("relogio.png", (22, 22))

imgs_suspeitos = {
    "Mordomo": carregar_imagem("mordomo.jpg", (50, 50)),
    "Cozinheira": carregar_imagem("cozinheira.jpg", (50, 50)),
    "Jardineiro": carregar_imagem("jardineiro.jpg", (50, 50)),
    "Motorista": carregar_imagem("motorista.jpg", (50, 50))
}

# PALETA DE CORES TEMA BORDÔ
COR_ESQUERDA = (38, 18, 24)         # Fundo esquerdo em bordô bem escuro
COR_DIREITA = (20, 10, 14)          # Fundo direito quase preto, com um toque quente
COR_BORDAS = (212, 163, 115)        # Dourado/Cobre elegante para contrastar
COR_TEXTO = (235, 225, 215)         # Creme/Marfim claro
COR_FOCO = (220, 180, 110)          # Dourado de destaque
COR_VERMELHO_FORTE = (210, 50, 60)  
COR_VERDE = (60, 150, 90)           
COR_CELULA = (50, 24, 32)           # Células da tabela em bordô
COR_BOTAO_PADRAO = (75, 32, 45)     # Botão pedir pista
COR_BOTAO_ACUSAR = (140, 35, 45)    # Botão de acusar mais intenso
COR_BOTAO_SAIR = (45, 20, 26)       # Botão de sair discreto
COR_CARD = (48, 22, 30)             # Fundo dos cartões de pista
COR_BORDA_CELULA = (90, 45, 55)     # Contorno das células da grelha

# Fontes
fonte_titulo = pygame.font.SysFont("georgia", 20, bold=True)
fonte_pista = pygame.font.SysFont("georgia", 14)
fonte_formula = pygame.font.SysFont("courier new", 14, bold=True)
fonte_grelha = pygame.font.SysFont("georgia", 13, bold=True)

# Definição dos Retângulos
btn_pedir_pista = pygame.Rect(20, 560, 460, 42)
btn_acusar = pygame.Rect(20, 615, 460, 42)
btn_sair_jogo = pygame.Rect(20, 670, 460, 35)

tam_celula = 52
ox = 740
oy = 150

nome_jogador = "Isabela"
pontuacao_total = 0
casos_resolvidos = 0
nivel_atual = 1

# VARIÁVEIS DE ANIMAÇÃO 
pistas_scroll = 0.0          # Scroll atual
alvo_scroll = 0.0            # Scroll destino (para onde a tela vai rolar suavemente)
animacao_nova_pista_y = 0.0  # Deslocamento Y da última pista para o efeito "subindo"

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
        altura_y += fonte.get_height() + 3
    return altura_y

estado_jogo = iniciar_novo_jogo()

# LOOP PRINCIPAL
rodando = True
while rodando:
    tempo_atual = time.time()
    
    if not estado_jogo["jogo_encerrado"]:
        tempo_restante = max(0, int(estado_jogo["tempo_limite"] - (time.time() - estado_jogo["tempo_inicio"])))
    else:
        tempo_restante = 0

    # ==================================================
    # LÓGICA DE ATUALIZAÇÃO DA ANIMAÇÃO (EASE-OUT)
    # ==================================================
    # Interpolação do scroll para descer suavemente
    pistas_scroll += (alvo_scroll - pistas_scroll) * 0.15 
    
    # Faz a pista subir suavemente até a posição 0 (reduzindo a distância)
    if animacao_nova_pista_y > 0:
        animacao_nova_pista_y -= max(1.0, animacao_nova_pista_y * 0.15)
        if animacao_nova_pista_y < 1:
            animacao_nova_pista_y = 0

    tela.fill(COR_DIREITA)
    suspeitos = estado_jogo["suspeitos"]
    armas = estado_jogo["armas"]
    locais = estado_jogo["locais"]
    itens_laterais = armas + locais

    # ==================================================
    # Painel Esquerdo (Pistas e Controles)
    # ==================================================
    pygame.draw.rect(tela, COR_ESQUERDA, (0, 0, 500, ALTURA))
    pygame.draw.line(tela, COR_BORDAS, (500, 0), (500, ALTURA), 4)

    txt_tit1 = fonte_titulo.render("ARQUIVO DO CASO", True, COR_FOCO)
    tela.blit(txt_tit1, (20, 15))

    txt_p_info = fonte_grelha.render(f"FASE {nivel_atual}  |  Detetive: {nome_jogador}  |  {pontuacao_total} pts", True, COR_TEXTO)
    tela.blit(txt_p_info, (20, 42))

    pygame.draw.line(tela, COR_BORDAS, (20, 65), (480, 65), 1)

    txt_contagem = fonte_pista.render(f"PISTAS: {estado_jogo['pista_index']}/6   •   CASOS: {casos_resolvidos}", True, COR_TEXTO)
    tela.blit(txt_contagem, (20, 75))

    txt_tentativas = fonte_pista.render(f"TENTATIVAS DE ACUSAÇÃO: {3 - estado_jogo['tentativas_acusacao']}/3", True, COR_TEXTO)
    tela.blit(txt_tentativas, (20, 92))

    if img_relogio:
        tela.blit(img_relogio, (350, 75))
    cor_tempo = COR_VERMELHO_FORTE if tempo_restante <= 15 else COR_FOCO
    txt_tempo = fonte_grelha.render(f"TEMPO: {tempo_restante // 60:02d}:{tempo_restante % 60:02d}", True, cor_tempo)
    tela.blit(txt_tempo, (380, 75))

    # ==================================================
    # Renderização dos Cards das Pistas (Com Máscara de Corte)
    # ==================================================
    area_pistas = pygame.Rect(10, 115, 480, 430)
    tela.set_clip(area_pistas)
    y_pista = area_pistas.top - pistas_scroll
    
    for i, p in enumerate(estado_jogo["pistas_reveladas"]):
        y_atual = y_pista
        
        # Se for o último card inserido, aplica o deslocamento para ele "subir"
        if i == len(estado_jogo["pistas_reveladas"]) - 1:
            y_atual += animacao_nova_pista_y

        card_rect = pygame.Rect(14, y_atual, 452, 68)
        # Usando a nova cor para o card e para a borda
        pygame.draw.rect(tela, COR_CARD, card_rect, border_radius=6)
        pygame.draw.rect(tela, COR_BORDAS, card_rect, 1, border_radius=6)
        pygame.draw.rect(tela, COR_FOCO, (14, y_atual, 4, 68), border_radius=2) 

        txt_f = fonte_formula.render(f"EVIDÊNCIA {i+1} · {p['formula']}", True, COR_FOCO)
        tela.blit(txt_f, (26, y_atual + 6))

        desenhar_texto_multilinhas(tela, f'"{p["historia"]}"', 26, y_atual + 24, 425, fonte_pista, COR_TEXTO)
        
        y_pista += 76
        
    tela.set_clip(None)

    # Botões do Painel Esquerdo
    pygame.draw.rect(tela, COR_BOTAO_PADRAO, btn_pedir_pista, border_radius=8)
    pygame.draw.rect(tela, COR_BORDAS, btn_pedir_pista, 1, border_radius=8)
    txt_btn1 = fonte_titulo.render("PEDIR NOVA PISTA [1]", True, COR_TEXTO)
    tela.blit(txt_btn1, (btn_pedir_pista.x + (460 - txt_btn1.get_width())//2, btn_pedir_pista.y + 10))

    pygame.draw.rect(tela, COR_BOTAO_ACUSAR, btn_acusar, border_radius=8)
    pygame.draw.rect(tela, COR_BORDAS, btn_acusar, 1, border_radius=8)
    txt_btn2 = fonte_titulo.render("FAZER ACUSAÇÃO [2]", True, COR_TEXTO)
    tela.blit(txt_btn2, (btn_acusar.x + (460 - txt_btn2.get_width())//2, btn_acusar.y + 10))

    pygame.draw.rect(tela, COR_BOTAO_SAIR, btn_sair_jogo, border_radius=8)
    pygame.draw.rect(tela, COR_BORDAS, btn_sair_jogo, 1, border_radius=8)
    txt_btn3 = fonte_titulo.render("SAIR DO JOGO [ESC]", True, COR_TEXTO)
    tela.blit(txt_btn3, (btn_sair_jogo.x + (460 - txt_btn3.get_width())//2, btn_sair_jogo.y + 7))

    # ==================================================
    # Painel Direito (Quadro de Deduções)
    # ==================================================
    txt_tit2 = fonte_titulo.render("QUADRO DE DEDUÇÕES", True, COR_FOCO)
    tela.blit(txt_tit2, (520, 15))
    pygame.draw.line(tela, COR_BORDAS, (520, 42), (710, 42), 2)
    txt_fase = fonte_pista.render(f"FASE {nivel_atual}  ·  DIFICULDADE {min(nivel_atual, 7)}/7", True, COR_TEXTO)
    tela.blit(txt_fase, (520, 50))

    if logo_img:
        tela.blit(logo_img, (LARGURA - logo_img.get_width() - 20, 12))

    # Fotos e rótulos dos Suspeitos
    for col in range(4):
        nome_s = suspeitos[col]
        img_s = imgs_suspeitos.get(nome_s)
        
        pos_x = ox + col * tam_celula + 2
        pos_y = oy - 78
        if img_s:
            pygame.draw.circle(tela, COR_BORDAS, (pos_x + 22, pos_y + 22), 26, 2)
            tela.blit(img_s, (pos_x, pos_y))
            
        txt_col = fonte_grelha.render(nome_s[:4].upper(), True, COR_FOCO)
        tela.blit(txt_col, (ox + col * tam_celula + 8, oy - 22))

    # Desenho da Grelha
    for lin in range(8):
        cor_rotulo = COR_FOCO if lin < 4 else COR_TEXTO
        txt_lin = fonte_grelha.render(itens_laterais[lin], True, cor_rotulo)
        tela.blit(txt_lin, (ox - 140, oy + lin * tam_celula + 18))

        for col in range(4):
            rect = pygame.Rect(ox + col * tam_celula, oy + lin * tam_celula, tam_celula - 2, tam_celula - 2)
            
            # Usando a nova cor para as células da tabela
            pygame.draw.rect(tela, COR_CELULA, rect, border_radius=6)
            pygame.draw.rect(tela, COR_BORDA_CELULA, rect, 1, border_radius=6)

            val = estado_jogo["grelha_unica"][lin][col]
            if val == 1:
                txt_x = fonte_titulo.render("X", True, COR_VERMELHO_FORTE)
                tela.blit(txt_x, (rect.x + (tam_celula - txt_x.get_width())//2, rect.y + 11))
            elif val == 2:
                txt_v = fonte_titulo.render("V", True, COR_VERDE)
                tela.blit(txt_v, (rect.x + (tam_celula - txt_v.get_width())//2, rect.y + 11))

    pygame.draw.line(tela, COR_BORDAS, (ox - 140, oy + 4 * tam_celula - 1), (ox + 4 * tam_celula, oy + 4 * tam_celula - 1), 3)

    # EVENTOS DE ENTRADA
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        
        elif evento.type == pygame.MOUSEWHEEL:
            max_scroll = max(0, len(estado_jogo["pistas_reveladas"]) * 76 - 430)
            alvo_scroll = max(0, min(max_scroll, alvo_scroll - evento.y * 30))
            
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                rodando = False
            elif evento.key == pygame.K_1:
                # Dispara a lógica de revelação e a animação
                if estado_jogo["pista_index"] < len(estado_jogo["pistas"]):
                    estado_jogo["pistas_reveladas"].append(estado_jogo["pistas"][estado_jogo["pista_index"]])
                    estado_jogo["pista_index"] += 1
                    
                    animacao_nova_pista_y = 120 # O quão abaixo ela começa antes de subir
                    alvo_scroll = max(0, len(estado_jogo["pistas_reveladas"]) * 76 - 430) # Força o scroll para a pista nova
                    
            elif evento.key == pygame.K_2:
                print("Lógica de Acusação")
                
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            pos_mouse = evento.pos
            
            if btn_pedir_pista.collidepoint(pos_mouse):
                # Dispara a lógica de revelação e a animação pelo botão do mouse
                if estado_jogo["pista_index"] < len(estado_jogo["pistas"]):
                    estado_jogo["pistas_reveladas"].append(estado_jogo["pistas"][estado_jogo["pista_index"]])
                    estado_jogo["pista_index"] += 1
                    
                    animacao_nova_pista_y = 120 
                    alvo_scroll = max(0, len(estado_jogo["pistas_reveladas"]) * 76 - 430) 
                    
            elif btn_acusar.collidepoint(pos_mouse):
                print("Lógica de Acusação")
                
            elif btn_sair_jogo.collidepoint(pos_mouse):
                rodando = False
                
            # Clique na Grelha
            for lin in range(8):
                for col in range(4):
                    r = pygame.Rect(ox + col * tam_celula, oy + lin * tam_celula, tam_celula, tam_celula)
                    if r.collidepoint(pos_mouse):
                        estado_jogo["grelha_unica"][lin][col] = (estado_jogo["grelha_unica"][lin][col] + 1) % 3

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()