import random

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
    f"As pegadas de lama registradas na entrada descartam a presença de {s_falsos[0]}.",
    f"O alibi de {s_falsos[0]} foi confirmado pela polícia local durante o depoimento."
]

opcoes_condicional = [
    f"A perícia analisou a cena: Se o culpado for {culpado}, a arma NÃO pode ser {a_falsas[0]}.",
    f"Um laudo médico indica: Se a autoria é de {culpado}, fica descartado o uso de {a_falsas[0]}.",
    f"A investigação concluiu: Caso {culpado} seja o autor, o uso de {a_falsas[0]} é impossível."
]

opcoes_bicondicional = [
    f"Um bilhete anônimo revela uma ligação direta entre o autor do crime e a arma usada.",
    f"Marcas digitais no cabo mostram a conexão inseparável entre o criminoso e o objeto do crime.",
    f"Uma confissão parcial sugere que o verdadeiro culpado operou exclusivamente essa arma."
]

opcoes_demorgan = [
    f"O mordomo jurou que {s_falsos[1]} e {s_falsos[2]} estavam jogando cartas juntos longe da cena.",
    f"Imagens de câmeras externas mostram {s_falsos[1]} e {s_falsos[2]} juntos no cinema da cidade.",
    f"Testemunhas afirmam que {s_falsos[1]} e {s_falsos[2]} participavam de um jantar bem longe daqui."
]

opcoes_rastro = [
    f"Um rastro de sangue indica que o uso de {arma_real} leva diretamente ao local do crime.",
    f"Resíduos encontrados confirmam que {arma_real} só poderia ter sido empregada no(a) {local_real}.",
    f"A análise forense provou que o impacto de {arma_real} ocorreu exclusivamente no(a) {local_real}."
]

opcoes_local = [
    f"As câmeras de segurança descartam completamente a presença de qualquer pessoa na {l_falsos[0]}.",
    f"A porta do(a) {l_falsos[0]} estava trancada por dentro e sem nenhum sinal de intrusão.",
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
pista_index = 0

print("========================================")
print("              SHERLÓGICA                ")
print("   O Enigma da Lógica Proposicional     ")
print("========================================")
print("Use a sua grelha em papel para deduzir o crime!\n")

while True:
    opcao = input("\nDigite [1] para Pedir Pista | [2] para Acusar: ").strip()
    if opcao == "1":
        if pista_index < len(pistas):
            p = pistas[pista_index]
            print(f"\n CASO SHERLÓGICA - PISTA {pista_index + 1}")
            print(f"Depoimento: \"{p['historia']}\"")
            print(f"Fórmula Lógica: {p['formula']}")
            pista_index += 1
        else:
            print("\nTodas as pistas já foram reveladas!")
    elif opcao == "2":
        s = input("Suspeito (ex: Mordomo): ").strip().capitalize()
        a = input("Arma (ex: Veneno): ").strip().capitalize()
        l = input("Local (ex: Biblioteca): ").strip().capitalize()
        if s == culpado and a == arma_real and l == local_real:
            print(f"\n PARABÉNS, ELEMENTAR! ({s} ∧ {a} ∧ {l}) é VERDADEIRO! Caso resolvido!")
            break
        else:
            print("\n ACUSAÇÃO FALSA (F)! Essa combinação gera contradição lógica.")
