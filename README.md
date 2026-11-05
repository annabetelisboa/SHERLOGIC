# SHERLOGIC — O Enigma da Lógica Proposicional

**SherLogic** é um jogo de dedução digital desenvolvido em Python com a biblioteca **Pygame CE** para a disciplina de Lógica Proposicional.

O jogo coloca os participantes no papel de detetives que precisam de solucionar um mistério utilizando **regras de inferência, equivalências lógicas e tabelas-verdade** para descobrir a combinação secreta de **Culpado**, **Arma** e **Local**.

---

##  Sobre o Jogo

O crime possui uma matriz $4 \times 4 \times 4$ de elementos:
* **4 Suspeitos:** Mordomo, Cozinheira, Jardineiro, Motorista
* **4 Armas:** Veneno, Pistola, Faca, Corda
* **4 Locais:** Biblioteca, Cozinha, Jardim, Sala

No início de cada partida, o programa sorteia a combinação correta ($S \land A \land L$). O jogador analisa as pistas reveladas no painel esquerdo e faz o registo das suas deduções diretamente na **Grelha de Dedução Digital** interativa no painel direito.

---

##  Lógica Proposicional Explícita

A mecânica do jogo utiliza os conceitos fundamentais da Lógica Proposicional diretamente na tomada de decisão:

| Conectivo / Regra | Exemplo no Jogo | Raciocínio & Ação na Grelha Digital |
| :--- | :--- | :--- |
| **Negação ($\neg$)** | `¬Motorista` | Elimina o Motorista (clique na célula correspondente para marcar `X`). |
| **Condicional ($\rightarrow$)** | `Mordomo -> ¬Veneno` | Se o culpado for o Mordomo, por *Modus Ponens*, a arma não foi o Veneno. |
| **Bicondicional ($\leftrightarrow$)** | `Mordomo <-> Veneno` | O culpado e a arma têm obrigatoriamente o mesmo valor-verdade. |
| **Lei de De Morgan ($\neg(P \lor Q)$)** | `¬(Jardineiro v Motorista)` | Equivale a $\neg P \land \neg Q$. Elimina o Jardineiro **E** o Motorista de uma só vez. |

---

##  Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Biblioteca Gráfica:** `pygame-ce` (Pygame Community Edition)

---

##  Como Executar o Projeto

### 1. Pré-requisitos
Certifique-se de ter o **Python 3.x** instalado no seu computador.

### 2. Instalar o Pygame CE
No terminal do seu editor (ou prompt de comando), execute:

```bash
python -m pip install pygame-ce
```
## Controles e Jogabilidade
Pedir Pista: Clique no botão PEDIR NOVA PISTA [1] ou pressione a tecla 1.

**Preencher Grelha Digital:** Clique diretamente nas células da tabela no painel direito para alternar os estados (Vazio → X → V).

**Fazer Acusação:** Clique no botão FAZER ACUSAÇÃO [2] ou pressione a tecla 2.

**Navegar no Modal de Acusação:** Use as setas do teclado (↑↓←→) ou clique nos botões < e > na tela.

**Confirmar / Cancelar:** Selecione as opções na tela ou pressione a tecla ESC para fechar modais.
