import random

# Elementos do jogo
suspeitos = ["Mordomo", "Cozinheira", "Jardineiro", "Motorista"]
armas = ["Veneno", "Pistola", "Faca", "Corda"]
locais = ["Biblioteca", "Cozinha", "Jardim", "Sala"]

# Sorteio aleatório do crime real
culpado = random.choice(suspeitos)
arma_real = random.choice(armas)
local_real = random.choice(locais)

# Elementos falsos para criar as pistas
s_falsos = [s for s in suspeitos if s != culpado]
a_falsas = [a for a in armas if a != arma_real]
l_falsos = [l for l in locais if l != local_real]

# Pistas imersivas com contexto narrativo + fórmula lógica
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
pista_index = 0

print("========================================")
print("             SHERLÓGICA                 ")
print("  O Enigma da Lógica Proposicional     ")
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