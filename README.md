# KOF 2002 UM - Hitbox Viewer & Frame Data Tool

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Game](https://img.shields.io/badge/Game-KOF2002UM%20(Steam%20x64)-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

Uma ferramenta avançada de overlay (sobreposição) desenvolvida em Python para **The King of Fighters 2002 Unlimited Match (versão Steam x64)**.

Este projeto permite visualizar hitboxes, hurtboxes, áreas de throw e, principalmente, **Frame Data em tempo real** com cálculo de vantagem (advantage) na tela. É a ferramenta ideal para laboratório (training mode), descoberta de setups e entendimento profundo das mecânicas do jogo.

## 📸 Preview
![Preview](active.png)
![Preview](active2.png)
![Preview](active3.png)
![Preview](frame_advantage.png)
![Preview](narnia.png)

## ✨ Funcionalidades

- **Visualização de Caixas:**
  - 🟥 **Hitboxes:** Áreas ativas de ataque (vermelho).
  - 🟦 **Hurtboxes:** Áreas vulneráveis do corpo (azul).
  - 🟩 **Pushbox:** Colisão física entre personagens (verde).
  - 🟨 **Normal e Command Throws:** Alcance de agarrões de comando (com detecção de conexão).
- **Indicador visual de proximidade de golpes** Linha guia que mostra a distancia necessária para ativar um ataque de perto.
- **Frame Data Bar:** Barra visual que mostra a linha do tempo do golpe (Startup, Active, Recovery e Hitstun).
- **Advantage Calculator:** Exibe automaticamente a vantagem de quadros (`+` ou `-`) ao final da animação.
- **Modo Narnia:** Permite deixar os personagens invisíveis/visíveis para testar e visualizar golpes de perto.
- **Controle Total:** Pause o jogo, avance frame-por-frame para visualizar cada detalhe do golpe.

## ⚙️ Pré-requisitos

- **Jogo:** King of Fighters 2002 Unlimited Match (Steam Version) 64 bits.
- **Sistema:** Windows 10 ou 11 (x64).
- **Python 3** (desenvolvedores).

## 🚀 Instalação e Uso

### Opção 1: Usuários
1. Vá até a aba [Releases](../../releases) deste repositório.
2. Baixe o arquivo `.exe` mais recente.
3. Abra o jogo, entre no Training Mode.
4. Execute a ferramenta.

### Opção 2: Desenvolvedores
1. Clone o repositório
2. Instale as dependências:
   - pip install pymem pygame pywin32
3. Execute o script:
   - python hitbox.py

## ⚠️ Atenção
Para garantir que o overlay funcione perfeitamente, configure o jogo para rodar em modo Janela (Windowed).

## ⌨️ Comandos e Hotkeys
Teclas de atalho para ativar funções.

### ⚙️ Sistema e Controle de Jogo
| Tecla | Função | Descrição |
| :--- | :--- | :--- |
| **F7** | **Pause / Resume** | Congela ou descongela a engine do jogo. |
| **F8** | **Frame Step** | Avança exatamente 1 frame (apenas quando pausado). |
| **F9** | **Frame Data Bar** | Liga/Desliga a barra de contagem de frames. |
| **F10** | **Master Toggle** | Liga/Desliga o desenho de todas as hitboxes na tela. |
| **Ctrl + Esc** | **Sair** | Encerra a ferramenta imediatamente. |

### 🔴 Player 1 (Configurações)
| Tecla | Função | Descrição |
| :--- | :--- | :--- |
| **F1** | **Prox. Range** | Alterna visualização do alcance de ativação de botões (Close A, B, C, D). |
| **F2** | **Atk. Boxes** | Liga/Desliga visualização de Normal e Command Throws. |
| **F3** | **Throwable Box** | Liga/Desliga a caixa branca que mostra onde o P1 pode ser agarrado. |
| **Numpad 1** | **Narnia P1** | Torna o Player 1 invisível/visível (útil para visualizar golpes de perto). |

### 🔵 Player 2 (Configurações)
| Tecla | Função | Descrição |
| :--- | :--- | :--- |
| **F4** | **Prox. Range** | Alterna visualização do alcance de ativação de botões (Close A, B, C, D). |
| **F5** | **Atk. Boxes** | Liga/Desliga visualização de Normal e Command Throws. |
| **F6** | **Throwable Box** | Liga/Desliga a caixa branca que mostra onde o P2 pode ser agarrado. |
| **Numpad 2** | **Narnia P2** | Torna o Player 2 invisível/visível (útil para visualizar golpes de perto). |

## ⚠️ Disclaimer
Este software é uma ferramenta de estudo e deve ser usada somente este fim.
A ferramenta ainda não está completa e pode ocorrer alguns bugs ou inconsistências nos dados apresentados.

## 🤝 Contribuição
Sinta-se à vontade para abrir Issues ou enviar Pull Requests com melhorias de código ou novos endereços de memória.
