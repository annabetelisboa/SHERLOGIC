import pygame
import random
import sys

# lógica e gerador de pistas
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
        "historia": f"A pericia analisou a cena: Se o culpado for {culpado}, a arma NÃO pode ser {a_falsas[0]}.",
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
    }
]

random.shuffle(pistas)

# estrutura visual e interativa (pygames)

pygame.init()
LARGURA, ALTURA = 1200, 700
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("SHERLOGIC - Painel de Investigação")

# paleta de cores
COR_ESQUERDA = (30, 35, 45)
COR_DIREITA = (20, 22, 28)
COR_LINHA_DIVISORA = (70, 80, 105)
COR_TEXTO = (240, 240, 240)
COR_AMARELO = (240, 200, 80)
COR_BOTAO_PISTA = (50, 120, 180)
COR_BOTAO_ACUSAR = (180, 60, 60)
COR_VERMELHO = (220, 60, 60)
COR_VERDE = (60, 200, 100)
COR_CELULA = (40, 45, 60)
COR_DIVISOR_TABELA = (90, 100, 130)
COR_MODAL_FUNDO = (15, 18, 24)

# configuração de Fontes
fonte_titulo = pygame.font.SysFont("arial", 20)
fonte_titulo.set_bold(True)
fonte_pista = pygame.font.SysFont("arial", 13)
fonte_grelha = pygame.font.SysFont("arial", 13)
fonte_grelha.set_bold(True)

# controle de Pistas e Interface
pistas_reveladas = []
pista_index = 0

btn_pedir_pista = pygame.Rect(20, 580, 460, 45)
btn_acusar = pygame.Rect(20, 635, 460, 45)

# grelha de Dedução (8x4) com armas e locais x suspeitos
itens_laterais = armas + locais
grelha_unica = [[0 for _ in range(4)] for _ in range(8)]
tam_celula = 50
ox = 740
oy = 100

# estados de Modal de Acusação
modal_acusacao_aberto = False
sel_suspeito = 0
sel_arma = 0
sel_local = 0
mensagem_resultado = ""
cor_resultado = COR_TEXTO

def desenhar_texto_multilinhas(superficie, texto, x, y, largura_max, fonte, cor):
    """Quebra automaticamente o texto longo em várias linhas sem truncar."""
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

# loop Principal
rodando = True
while rodando:
    # 1. DESENHAR METADE ESQUERDA (PISTAS E BOTÕES)
    pygame.draw.rect(tela, COR_ESQUERDA, (0, 0, 500, ALTURA))
    
    txt_tit1 = fonte_titulo.render("🔍 PISTAS REVELADAS", True, COR_AMARELO)
    tela.blit(txt_tit1, (20, 15))

    # exibe histórico de pistas com texto completo
    y_pista = 45
    for i, p in enumerate(pistas_reveladas):
        if y_pista > 520:
            break
        txt_f = fonte_grelha.render(f"Pista {i+1}: {p['formula']}", True, COR_AMARELO)
        tela.blit(txt_f, (20, y_pista))
        y_pista += 18

        # pra suportar texto com mais de 1 linha
        y_pista = desenhar_texto_multilinhas(tela, f"\"{p['historia']}\"", 20, y_pista, 450, fonte_pista, COR_TEXTO)
        y_pista += 6

    # exibe resultado da acusação se houver
    if mensagem_resultado:
        txt_res = fonte_titulo.render(mensagem_resultado, True, cor_resultado)
        tela.blit(txt_res, (20, 550))

    # botões Esquerda
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
    
    txt_tit2 = fonte_titulo.render("📝 GRELHA DE DEDUÇÃO", True, COR_AMARELO)
    tela.blit(txt_tit2, (520, 15))

    # rótulos dos suspeitos
    for col in range(4):
        txt_col = fonte_grelha.render(suspeitos[col][:4], True, COR_AMARELO)
        tela.blit(txt_col, (ox + col * tam_celula + 10, oy - 25))

    # tabela
    for lin in range(8):
        cor_rotulo = COR_AMARELO if lin < 4 else COR_TEXTO
        txt_lin = fonte_grelha.render(itens_laterais[lin][:10], True, cor_rotulo)
        tela.blit(txt_lin, (ox - 140, oy + lin * tam_celula + 16))

        for col in range(4):
            rect = pygame.Rect(ox + col * tam_celula, oy + lin * tam_celula, tam_celula - 2, tam_celula - 2)
            pygame.draw.rect(tela, COR_CELULA, rect, border_radius=4)
            
            val = grelha_unica[lin][col]
            if val == 1:
                txt_x = fonte_titulo.render("X", True, COR_VERMELHO)
                tela.blit(txt_x, (rect.x + 17, rect.y + 12))
            elif val == 2:
                txt_v = fonte_titulo.render("V", True, COR_VERDE)
                tela.blit(txt_v, (rect.x + 17, rect.y + 12))

    # Linha divisória entre Armas e Locais
    pygame.draw.line(tela, COR_DIVISOR_TABELA, (ox - 140, oy + 4 * tam_celula - 1), (ox + 4 * tam_celula, oy + 4 * tam_celula - 1), 3)

    # 4. MODAL/TELA FLUTUANTE DE ACUSAÇÃO (VISUAL E INTERATIVO)
    if modal_acusacao_aberto:
        # Fundo escuro transparente
        s_overlay = pygame.Surface((LARGURA, ALTURA))
        s_overlay.set_alpha(200)
        s_overlay.fill((0, 0, 0))
        tela.blit(s_overlay, (0, 0))

        # Caixinha do Modal
        rect_modal = pygame.Rect(350, 150, 500, 400)
        pygame.draw.rect(tela, COR_MODAL_FUNDO, rect_modal, border_radius=12)
        pygame.draw.rect(tela, COR_AMARELO, rect_modal, 2, border_radius=12)

        txt_mod_tit = fonte_titulo.render("⚖️ MONTE SUA ACUSAÇÃO", True, COR_AMARELO)
        tela.blit(txt_mod_tit, (370, 170))

        # Seletores de Suspeito, Arma e Local
        txt_s = fonte_grelha.render(f"1. Suspeito: < {suspeitos[sel_suspeito]} >", True, COR_TEXTO)
        tela.blit(txt_s, (380, 220))

        txt_a = fonte_grelha.render(f"2. Arma:     < {armas[sel_arma]} >", True, COR_TEXTO)
        tela.blit(txt_a, (380, 280))

        txt_l = fonte_grelha.render(f"3. Local:    < {locais[sel_local]} >", True, COR_TEXTO)
        tela.blit(txt_l, (380, 340))

        txt_inst = fonte_pista.render("(Use as setas para alternar ou clique nos botões abaixo)", True, COR_AMARELO)
        tela.blit(txt_inst, (380, 380))

        # botão confirmar acusação
        btn_confirmar = pygame.Rect(380, 430, 210, 45)
        pygame.draw.rect(tela, COR_VERDE, btn_confirmar, border_radius=8)
        txt_conf = fonte_titulo.render("CONFIRMAR", True, COR_TEXTO)
        tela.blit(txt_conf, (btn_confirmar.x + 45, btn_confirmar.y + 10))

        # botão cancelar
        btn_cancelar = pygame.Rect(610, 430, 210, 45)
        pygame.draw.rect(tela, COR_VERMELHO, btn_cancelar, border_radius=8)
        txt_canc = fonte_titulo.render("CANCELAR", True, COR_TEXTO)
        tela.blit(txt_canc, (btn_cancelar.x + 55, btn_cancelar.y + 10))

    # 5. TRATAMENTO DE EVENTOS
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            if modal_acusacao_aberto:
                if evento.key == pygame.K_UP:
                    sel_suspeito = (sel_suspeito + 1) % 4
                elif evento.key == pygame.K_DOWN:
                    sel_arma = (sel_arma + 1) % 4
                elif evento.key == pygame.K_RIGHT:
                    sel_local = (sel_local + 1) % 4
                elif evento.key == pygame.K_ESCAPE:
                    modal_acusacao_aberto = False
            else:
                if evento.key == pygame.K_1 and pista_index < len(pistas):
                    pistas_reveladas.append(pistas[pista_index])
                    pista_index += 1
                elif evento.key == pygame.K_2:
                    modal_acusacao_aberto = True

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            pos_mouse = evento.pos

            if modal_acusacao_aberto:
                btn_confirmar = pygame.Rect(380, 430, 210, 45)
                btn_cancelar = pygame.Rect(610, 430, 210, 45)
                
                # zonas de clique para alternar elementos no modal
                if pygame.Rect(380, 215, 300, 35).collidepoint(pos_mouse):
                    sel_suspeito = (sel_suspeito + 1) % 4
                elif pygame.Rect(380, 275, 300, 35).collidepoint(pos_mouse):
                    sel_arma = (sel_arma + 1) % 4
                elif pygame.Rect(380, 335, 300, 35).collidepoint(pos_mouse):
                    sel_local = (sel_local + 1) % 4

                elif btn_confirmar.collidepoint(pos_mouse):
                    modal_acusacao_aberto = False
                    s_palpite = suspeitos[sel_suspeito]
                    a_palpite = armas[sel_arma]
                    l_palpite = locais[sel_local]

                    if s_palpite == culpado and a_palpite == arma_real and l_palpite == local_real:
                        mensagem_resultado = "SOLUÇÃO CORRETA! CASO RESOLVIDO!"
                        cor_resultado = COR_VERDE
                    else:
                        mensagem_resultado = "ACUSAÇÃO FALSA (F)! Tente novamente."
                        cor_resultado = COR_VERMELHO

                elif btn_cancelar.collidepoint(pos_mouse):
                    modal_acusacao_aberto = False

            else:
                # clique no Botão 1 pra pistas
                if btn_pedir_pista.collidepoint(pos_mouse):
                    if pista_index < len(pistas):
                        pistas_reveladas.append(pistas[pista_index])
                        pista_index += 1

                # clique no botão 2 pra acusar (com mouse ou teclado)
                elif btn_acusar.collidepoint(pos_mouse):
                    modal_acusacao_aberto = True

                # clique na grelha
                for lin in range(8):
                    for col in range(4):
                        r = pygame.Rect(ox + col * tam_celula, oy + lin * tam_celula, tam_celula, tam_celula)
                        if r.collidepoint(pos_mouse):
                            grelha_unica[lin][col] = (grelha_unica[lin][col] + 1) % 3

    pygame.display.flip()

pygame.quit()
sys.exit()
# obs: se for rodar no vs code, precisa instalar pygame ou pygame-e
