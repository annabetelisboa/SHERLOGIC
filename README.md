# SHERLOGIC — O Enigma da Lógica Proposicional

**SherLogic** é um jogo de dedução digital desenvolvido em Python com a biblioteca **Pygame CE**.

Você é um detetive que precisa resolver um crime numa mansão. Para isso, lê pistas escritas em linguagem natural **e** em fórmulas de lógica proposicional, anota suas deduções num quadro e, no fim, acusa a combinação correta de **Culpado**, **Arma** e **Local**. Cada caso resolvido leva a uma fase mais difícil.

---

##  Sobre o Jogo

Existem 4 opções para cada categoria: 
* **4 Suspeitos:** Mordomo, Cozinheira, Jardineiro, Motorista
* **4 Armas:** Veneno, Pistola, Faca, Corda
* **4 Locais:** Biblioteca, Cozinha, Jardim, Sala

No início de cada partida, o programa sorteia a combinação correta. O objetivo é descobri-la antes que o tempo ou as tentativas acabem.

---


## Sumário

- [Acusação e tentativas](#acusação-e-tentativas)
- [Fases e dificuldade](#fases-e-dificuldade)
- [Pontuação e ranking](#pontuação-e-ranking)
- [Controles](#controles)
- [Como executar](#como-executar)

---

## Fluxo do jogo

1. **Nome do detetive**: o jogador digita um nome de até 15 caracteres e confirma com `Enter` ou com o botão **CONTINUAR**.
2. **Tutorial (opcional)**: o jogo pergunta se você quer fazer o tutorial. Ele tem três telas curtas que explicam os símbolos lógicos, o quadro de deduções e a pontuação. Ao final, ou se você respondeu **NÃO** inicialmente, começa a Fase 1.
3. **Investigação**: você pede pistas, anota deduções e faz acusações (detalhes abaixo).
4. **Fim do caso**:
   - **Acertou**: aparece a tela "CASO RESOLVIDO COM SUCESSO!" com a foto do culpado e a solução. Você pode seguir para a **PRÓXIMA FASE** ou **SAIR**.
   - **Perdeu** (tempo esgotado ou três acusações erradas): aparece a tela de **FIM DE JOGO**. Você pode **JOGAR NOVAMENTE**, voltando para a Fase 1, ou **SAIR DO JOGO**.
5. **Ranking final**: ao sair, o jogo mostra o nome do detetive, quantos casos foram resolvidos e a pontuação total acumulada.

---

## A tela de investigação

A tela é dividida em duas metades.

**Painel esquerdo, "ARQUIVO DO CASO"**
- Fase atual, nome do detetive e pontuação total.
- Contador de pistas usadas em relação ao limite da fase (ex.: `PISTAS: 3/10`) e número de casos resolvidos.
- Tentativas de acusação restantes (`3/3`, `2/3`...).
- Cronômetro regressivo.
- Lista das pistas reveladas, cada uma como um cartão "EVIDÊNCIA N · fórmula" com a história embaixo. (A lista rola com a roda do mouse.)
- Botões **PEDIR NOVA PISTA [1]**, **FAZER ACUSAÇÃO [2]** e **SAIR DO JOGO [ESC]**.

**Painel direito, "QUADRO DE DEDUÇÕES"**
- Fase e nível de dificuldade (de 1/5 a 5/5).
- A grade de anotações, com as fotos dos suspeitos no topo.

---

## As pistas e a lógica por trás delas

As pistas são geradas a partir da solução sorteada, então **todas são verdadeiras**. A cada partida elas são embaralhadas, e cada clique em "Pedir nova pista" revela a próxima da fila.

Em todas as fases existe um conjunto base de 10 pistas. "Falso" abaixo quer dizer um elemento que **não** faz parte da solução:

| # | Tipo | Fórmula | O que o detetive conclui |
| :-: | :--- | :--- | :--- |
| 1 | Negação | `¬SuspeitoFalso` | Esse suspeito está descartado. |
| 2 | Condicional | `Culpado -> ¬ArmaFalsa` | Se você descobrir quem é o culpado, por **Modus Ponens** essa arma é descartada. |
| 3 | Bicondicional | `Culpado <-> ArmaReal` | Culpado e arma andam juntos: descobrir um revela o outro. |
| 4 | De Morgan | `¬(SuspeitoFalso v SuspeitoFalso)` | Equivale a `¬P ^ ¬Q`: descarta **dois** suspeitos de uma vez. |
| 5 | Condicional | `ArmaReal -> LocalReal` | Ao confirmar a arma, por **Modus Ponens** você descobre o local. |
| 6 | Negação | `¬LocalFalso` | Esse local está descartado. |
| 7 | Negação | `¬LocalFalso` | Outro local descartado. |
| 8 | Negação | `¬LocalFalso` | Mais um local descartado. |
| 9 | Negação | `¬ArmaFalsa` | Essa arma está descartada. |
| 10 | Negação | `¬ArmaFalsa` | Outra arma descartada. |

A partir da **Fase 3**, entram mais duas pistas compostas, que juntam várias proposições numa só fórmula (o `^` é o **E** lógico):

| Fórmula | Leitura |
| :--- | :--- |
| `(ArmaReal -> LocalReal) ^ (Culpado <-> ArmaReal)` | Junta as pistas 3 e 5 numa conjunção. É preciso separar as partes (**Simplificação**) e aplicar cada uma. |
| `(Culpado <-> ArmaReal) ^ (¬ArmaReal -> ¬LocalReal)` | A segunda parte é a **contrapositiva** de `LocalReal -> ArmaReal`, então pede raciocínio com equivalências lógicas. |

### Símbolos usados

| Símbolo | Nome | Significado |
| :-: | :--- | :--- |
| `¬` | Negação | "não" |
| `v` | Disjunção | "ou" |
| `^` | Conjunção | "e" |
| `->` | Condicional | "se... então..." |
| `<->` | Bicondicional | "se, e somente se" |

---

## Quadro de deduções

A grade tem **8 linhas × 4 colunas**:

- **Colunas**: os quatro suspeitos, com foto e as quatro primeiras letras do nome.
- **Linhas de cima (em amarelo)**: as quatro armas.
- **Linhas de baixo**: os quatro locais, separados das armas por uma linha mais grossa.

Cada clique numa célula alterna entre três estados:

| Clique | Estado | Uso sugerido |
| :-: | :--- | :--- |
| 1º | **X** vermelho | Combinação descartada |
| 2º | **V** verde | Combinação confirmada |
| 3º | Vazio | Limpa a anotação |

*O quadro serve só de anotação: o jogo não verifica o que você marca. A resposta conta apenas na acusação.*

---

## Acusação e tentativas

Ao clicar em **FAZER ACUSAÇÃO** (ou apertar `2`), abre uma janela para montar o palpite:

- Escolha **Suspeito**, **Arma** e **Local** com os botões `<` `>` ou com as setas do teclado (`↑` `↓` trocam a categoria e `←` `→` trocam a opção).
- **CONFIRMAR** envia a acusação. **CANCELAR** ou `ESC` fecham a janela.

Você tem **3 tentativas por caso**:
- **Acusação correta**: o caso é resolvido e a pontuação da rodada é somada.
- **Acusação falsa**: aparece "ACUSAÇÃO FALSA! Restam N tentativas." e o jogo continua.
- **Terceiro erro**: "ACABARAM AS TENTATIVAS!" e o caso é encerrado (fim de jogo).

---

## Fases e dificuldade

A cada caso resolvido você sobe uma fase. Duas coisas apertam: o **tempo** e o **número de pistas** que podem ser pedidas.

| Fase | Tempo limite | Pistas disponíveis | Pistas compostas | Dificuldade exibida |
| :-: | :-: | :-: | :-: | :-: |
| 1 | 60 s | 10 | Não | 1/5 |
| 2 | 50 s | 9 | Não | 2/5 |
| 3 | 40 s | 8 | Sim | 3/5 |
| 4 | 30 s | 7 | Sim | 4/5 |
| 5 | 20 s | 6 | Sim | 5/5 |
| 6+ | 10 s | 5 | Sim | 5/5 |

- Quando o cronômetro chega a zero, aparece **"TEMPO ESGOTADO!"** e o caso termina.
- Ao atingir o limite de pistas, o jogo avisa "LIMITE DE PISTAS DESTA FASE ATINGIDO."
- Como as pistas vêm embaralhadas, nas fases com menos pistas pode ser que você não receba todas as informações. Aí é preciso aproveitar ao máximo as condicionais e bicondicionais, ou arriscar um palpite usando as tentativas.
- Depois de uma derrota, "JOGAR NOVAMENTE" volta para a Fase 1.

---

## Pontuação e ranking

Cada caso resolvido vale:

```
pontos = max(100, 1000 − 5 × segundos_gastos − 100 × pistas_usadas)
```

- Quanto **mais rápido** e com **menos pistas**, mais pontos. Cada segundo custa 5 pontos e cada pista custa 100.
- Todo caso resolvido vale no mínimo **100 pontos**.
- Acusações erradas não tiram pontos diretamente, mas o tempo continua correndo.
- A pontuação total e o número de casos resolvidos aparecem no **Ranking Final** quando você sai do jogo.

---

## Como executar

### 1. Pré-requisitos
Tenha o **Python 3.x** instalado.

### 2. Instalar o Pygame CE
```bash
python -m pip install pygame-ce
```

### 3. Rodar o jogo
Na pasta do projeto:
```bash
python main.py
```

O jogo abre em **tela cheia** (resolução base 1200×720, ajustada à tela). Para sair a qualquer momento, use **SAIR DO JOGO** / `ESC` e depois **FECHAR JOGO**.

---

## Tecnologias Utilizadas

- **Linguagem:** Python 3
- **Biblioteca gráfica:** `pygame-ce` (Pygame Community Edition)
