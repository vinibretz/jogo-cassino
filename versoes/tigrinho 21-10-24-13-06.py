import random
import pygame
import pygame_gui
import time

# Inicializando o Pygame e o pygame_gui
pygame.init()
pygame.display.set_caption("Simulador Cassino")
manager = pygame_gui.UIManager((800, 800))

# Dimensões da tela
screen_width, screen_height = 800, 800
screen = pygame.display.set_mode((screen_width, screen_height))

# Carregar a imagem de background
background_image = pygame.image.load(r'.\img\background.png')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Carregar a fonte Ubuntu Regular para uso no jogo
pygame.font.init()

# Formatar todas as fontes com a fonte Ubuntu do Google Fontes na pasta fontes
fonte_grande = pygame.font.Font(r'.\fontes\Ubuntu-Regular.ttf', 24)
fonte_pequena = pygame.font.Font(r'.\fontes\Ubuntu-Regular.ttf', 18)
fonte_bold = pygame.font.Font(r'.\fontes\Ubuntu-Bold.ttf', 24)

# Cores
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)


# Variáveis de Jogo
saldo_inicial = 0.00  # Saldo inicial
aposta = 5.00  # Valor da aposta
mensagem = ""   # Mensagem de resultado
mensagem_cor = WHITE  # Cor da mensagem que será atualizada conforme o resultado
mensagem_motivo = ""  # Motivo do ganho ou da perda
multiplicador = 1
RTP = 0.95  # Retorno ao Jogador ajustado para 95%
ganhos_totais = 0.00  # Soma dos ganhos
perdas_totais = 0.00  # Soma das perdas
depositos = 0.00  # Soma dos depósitos adicionais
rtp_acumulado = 0.00  # RTP acumulado
total_apostas = 0.00  # Total de apostas feitas
total_ganhos = 0.00  # Total de ganhos acumulados

# Símbolos e layout
coluna_largura = 150
coluna_altura = 150
num_colunas = 3
num_linhas = 3

# Definindo os multiplicadores dos símbolos
símbolos_multiplicadores = {
    'laranjas': 1.5,
    'sinos': 3,
    'envelopes': 4.5,
    'moedas': 6,
    'jade': 12,
    'enfeite_dourado': 30,
    'wild': 75  # Wild paga mais, mas é mais raro
}

# Frequência ajustada para cada símbolo (probabilidades mais realistas)
símbolos_probabilidades = {
    'laranjas': 0.45,  # Aumenta a frequência dos símbolos com ganhos menores
    'sinos': 0.25,
    'envelopes': 0.12,
    'moedas': 0.08,
    'jade': 0.06,
    'enfeite_dourado': 0.03,
    'wild': 0.01  # Wild extremamente raro
}

# Definindo um símbolo especial com multiplicador
SIMBOLO_WILD = 'wild'

# Carregar imagens dos símbolos (substituir pelos seus próprios arquivos de símbolo)
laranjas = pygame.image.load(r'./img/laranjas.png')
sinos = pygame.image.load(r'./img/sinos.png')
envelopes = pygame.image.load(r'./img/envelopes.png')
moedas = pygame.image.load(r'./img/moedas.png')
jade = pygame.image.load(r'./img/jade.png')
enfeite_dourado = pygame.image.load(r'./img/enfeite_dourado.png')
wild = pygame.image.load(r'./img/wild.png')

# Ajustar o tamanho dos símbolos
símbolos = {
    'laranjas': pygame.transform.scale(laranjas, (100, 100)),
    'sinos': pygame.transform.scale(sinos, (100, 100)),
    'envelopes': pygame.transform.scale(envelopes, (100, 100)),
    'moedas': pygame.transform.scale(moedas, (100, 100)),
    'jade': pygame.transform.scale(jade, (100, 100)),
    'enfeite_dourado': pygame.transform.scale(enfeite_dourado, (100, 100)),
    'wild': pygame.transform.scale(wild, (100, 100))
}

def animar_roleta(time_delta):
    for _ in range(20):  # Número de iterações da animação
        resultados = rodar_jogo()
        screen.blit(background_image, (0, 0))
        desenhar_roleta(resultados)
        desenhar_saldo_aposta(calcular_banca(), aposta)
        desenhar_mensagem(mensagem, mensagem_cor, mensagem_motivo, multiplicador)
        desenhar_rtp_acumulado(rtp_acumulado)
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()
        time.sleep(0.1)  # Pequena pausa para criar o efeito de rotação

def animar_roleta_simulacao(time_delta, duracao):
    start_time = time.time()
    while time.time() - start_time < duracao:
        resultados = rodar_jogo()
        screen.blit(background_image, (0, 0))
        desenhar_roleta(resultados)
        desenhar_saldo_aposta(calcular_banca(), aposta)
        desenhar_mensagem(mensagem, mensagem_cor, mensagem_motivo, multiplicador)
        desenhar_rtp_acumulado(rtp_acumulado)
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()
        time.sleep(0.1)  # Pequena pausa para criar o efeito de rotação

# Função para escolher símbolos com base nas probabilidades ajustadas
def escolher_simbolo():
    return random.choices(
        population=list(símbolos_probabilidades.keys()),
        weights=list(símbolos_probabilidades.values()),
        k=1
    )[0]

# Função para rodar os símbolos
def rodar_jogo():
    return [[escolher_simbolo() for _ in range(num_colunas)] for _ in range(num_linhas)]

# Função para verificar as linhas de pagamento
def verificar_pagamento(resultado):
    global multiplicador, rtp_acumulado, total_apostas, total_ganhos
    multiplicador = 1
    vitoria = False
    linhas_vencedoras = []
    motivo = ""

    # Verificar linhas horizontais
    for lin in range(num_linhas):
        if resultado[lin][0] == resultado[lin][1] == resultado[lin][2]:
            linhas_vencedoras.append(resultado[lin][0])
            motivo = f"Você ganhou por obter 3 {resultado[lin][0]} na linha {lin + 1}."
            vitoria = True

    # Verificar diagonais
    if resultado[0][0] == resultado[1][1] == resultado[2][2]:  # Diagonal principal
        linhas_vencedoras.append(resultado[0][0])
        motivo = f"Você ganhou por obter 3 {resultado[0][0]} na diagonal principal."
        vitoria = True
    if resultado[0][2] == resultado[1][1] == resultado[2][0]:  # Diagonal inversa
        linhas_vencedoras.append(resultado[0][2])
        motivo = f"Você ganhou por obter 3 {resultado[0][2]} na diagonal inversa."
        vitoria = True

    # Multiplicador de 10x só se o grid inteiro tiver o mesmo símbolo
    if all(resultado[i][j] == resultado[0][0] for i in range(num_linhas) for j in range(num_colunas)):
        multiplicador = 10
        motivo = "Você ganhou com multiplicador 10x! Grid completo com o mesmo símbolo."
        vitoria = True

    total_apostas += aposta  # Atualizar o total de apostas feitas

    if vitoria:
        ganho = calcular_ganho(linhas_vencedoras)
        total_ganhos += ganho  # Atualizar o total de ganhos acumulados
        rtp_acumulado = total_ganhos / total_apostas  # Calcular o RTP acumulado
        return linhas_vencedoras, motivo
    else:
        rtp_acumulado = total_ganhos / total_apostas  # Calcular o RTP acumulado mesmo em caso de perda
        return [], "Você perdeu porque não houve combinações vencedoras."

# Função para calcular o valor ganho com base no RTP
def calcular_ganho(linhas_vencedoras):
    ganho_total = 0
    for simbolo in linhas_vencedoras:
        ganho_total += aposta * símbolos_multiplicadores[simbolo] * multiplicador
    return ganho_total * RTP  # Ajuste do valor ganho com base no RTP

# Função para desenhar os símbolos na roleta
def desenhar_roleta(resultados):
    for lin in range(num_linhas):
        for col in range(num_colunas):
            screen.blit(símbolos[resultados[lin][col]], (col * coluna_largura + 200, lin * coluna_altura + 80))

# Função para desenhar o saldo e aposta
def desenhar_saldo_aposta(banca, aposta):
    saldo_texto = fonte_bold.render(f"Banca: R$ {banca:.2f}", True, BLACK)
    aposta_texto = fonte_bold.render(f"Aposta: R$ {aposta:.2f}", True, BLACK)
    screen.blit(saldo_texto, (90, 18))
    screen.blit(aposta_texto, (545, 18))

# Função para desenhar a mensagem de resultado (com multiplicador se vencer)
def desenhar_mensagem(mensagem, cor, motivo, multiplicador=1):
    if multiplicador > 1:
        mensagem = f"{mensagem} - Multiplicador: {multiplicador}x!"  # Mostrando o multiplicador na mensagem de vitória
    mensagem_texto = fonte_grande.render(mensagem, True, cor)
    mensagem_rect = mensagem_texto.get_rect(center=(screen_width // 2, 535))
    screen.blit(mensagem_texto, mensagem_rect)
    
    motivo_texto = fonte_pequena.render(motivo, True, BLACK)
    motivo_rect = motivo_texto.get_rect(center=(screen_width // 2, 560))
    screen.blit(motivo_texto, motivo_rect)

# Função para desenhar o RTP acumulado na tela
def desenhar_rtp_acumulado(rtp_acumulado):
    rtp_texto = fonte_pequena.render(f"RTP Acumulado: {rtp_acumulado * 100:.2f}%", True, WHITE)
    screen.blit(rtp_texto, (10, 600))

def simular_apostas(quantidade, time_delta):
    global ganhos_totais, perdas_totais, mensagem, mensagem_cor, mensagem_motivo
    relatorio = []

    if calcular_banca() < aposta * quantidade:
        mensagem = "SALDO INSUFICIENTE PARA SIMULAÇÃO!"
        mensagem_cor = RED
        return

    animar_roleta_simulacao(time_delta, 2)  # Animação de 2 segundos antes de iniciar as simulações

    for i in range(quantidade):
        resultado = rodar_jogo()
        linhas_vencedoras, motivo = verificar_pagamento(resultado)

        if calcular_banca() >= aposta:
            perdas_totais += aposta
            if linhas_vencedoras:
                ganho = calcular_ganho(linhas_vencedoras)
                ganhos_totais += ganho
                relatorio.append(f"Rodada {i+1}: Ganhou R$ {ganho:.2f} - {motivo}")
            else:
                relatorio.append(f"Rodada {i+1}: Perdeu - {motivo}")
        else:
            mensagem = "SALDO INSUFICIENTE!"
            mensagem_cor = RED
            mensagem_motivo = ""
            relatorio.append(f"Rodada {i+1}: Saldo insuficiente!")
            break

    # Exibir resumo do relatório ao final
    total_ganhos = ganhos_totais
    total_perdas = perdas_totais
    total = total_ganhos - total_perdas
    mensagem = f"{quantidade} Giros: Ganhou R$ {total_ganhos:.2f} | Perdeu R$ {total_perdas:.2f} | Total R$ {total:.2f}"
    mensagem_cor = GREEN if total >= 0 else RED

    for linha in relatorio:
        print(linha)

# Função para calcular a banca atual
def calcular_banca():
    return saldo_inicial + depositos + ganhos_totais - perdas_totais

# Função para calcular o saldo real
def calcular_saldo_real():
    return ganhos_totais - perdas_totais

# Função para resetar o jogo
def resetar_jogo():
    global ganhos_totais, perdas_totais, depositos, rtp_acumulado, total_apostas, total_ganhos
    ganhos_totais = 0.00  # Reseta os ganhos totais
    perdas_totais = 0.00  # Reseta as perdas totais
    depositos = 0.00  # Reseta os depósitos
    rtp_acumulado = 0.00  # Reseta o RTP acumulado
    total_apostas = 0.00  # Reseta o total de apostas feitas
    total_ganhos = 0.00  # Reseta o total de ganhos acumulados

def jogo():
    global mensagem, mensagem_cor, mensagem_motivo, multiplicador, ganhos_totais, perdas_totais, depositos
    rodando = True
    resultado = rodar_jogo()  # Primeira rotação de exemplo
    while rodando:
        time_delta = pygame.time.Clock().tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if girar_button.collidepoint(mouse_pos):
                    mensagem = ""  # Limpar mensagem anterior
                    mensagem_motivo = ""  # Limpar motivo anterior
                    if calcular_banca() >= aposta:
                        perdas_totais += aposta
                        animar_roleta(time_delta)  # Passar time_delta para a função de animação
                        resultado = rodar_jogo()
                        linhas_vencedoras, mensagem_motivo = verificar_pagamento(resultado)
                        if linhas_vencedoras:
                            ganho = calcular_ganho(linhas_vencedoras)
                            ganhos_totais += ganho
                            mensagem = f"VOCÊ GANHOU R$ {ganho:.2f}"
                            mensagem_cor = GREEN
                        else:
                            mensagem = "VOCÊ PERDEU!"
                            mensagem_cor = RED
                    else:
                        mensagem = "SALDO INSUFICIENTE!"
                        mensagem_cor = RED
                        mensagem_motivo = ""

            # Verificar se o botão de simular foi pressionado
            if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                mensagem = ""  # Limpar mensagem anterior
                mensagem_motivo = ""  # Limpar motivo anterior
                if event.ui_element == simular_button:
                    try:
                        quantidade = int(simulacoes_input.get_text())
                        if quantidade <= 0:
                            raise ValueError
                        simular_apostas(quantidade, time_delta)  # Passar time_delta para a função de simulação
                    except ValueError:
                        mensagem = "Por favor, insira um número válido de simulações"
                        mensagem_cor = RED

                # Verificar se o botão de depósito foi pressionado
                if event.ui_element == depositar_button:
                    depositos += 100.00  # Adiciona R$ 100 aos depósitos

                # Verificar se o botão de reset foi pressionado
                if event.ui_element == resetar_button:
                    resetar_jogo()  # Reseta o jogo

            manager.process_events(event)

        # Desenhar a imagem de background
        screen.blit(background_image, (0, 0))

        desenhar_roleta(resultado)
        desenhar_saldo_aposta(calcular_banca(), aposta)
        desenhar_mensagem(mensagem, mensagem_cor, mensagem_motivo, multiplicador)
        desenhar_rtp_acumulado(rtp_acumulado)  # Desenhar o RTP acumulado

        # Atualizar e desenhar a interface do pygame_gui
        manager.update(time_delta)
        manager.draw_ui(screen)

        # Desenhar o botão manual de "Girar"
        pygame.draw.rect(screen, GREEN, girar_button)
        girar_texto = fonte_bold.render("GIRAR", True, WHITE)
        screen.blit(girar_texto, (363, 610))

        # Desenhar o resumo dos ganhos e perdas
        resumo_texto = fonte_pequena.render(f"Ganhos Totais: R$ {ganhos_totais:.2f}", True, WHITE)
        screen.blit(resumo_texto, (10, 650))
        perdas_texto = fonte_pequena.render(f"Perdas Totais: R$ {perdas_totais:.2f}", True, WHITE)
        screen.blit(perdas_texto, (10, 680))

        # Desenhar os depósitos
        depositos_texto = fonte_pequena.render(f"Depósitos: R$ {depositos:.2f}", True, WHITE)
        screen.blit(depositos_texto, (10, 730))

        # Calcular e desenhar o saldo real
        saldo_real = calcular_saldo_real()
        saldo_real_texto = fonte_pequena.render(f"Saldo Real: R$ {saldo_real:.2f}", True, WHITE)
        screen.blit(saldo_real_texto, (10, 760))

        pygame.display.flip()

# Criando interface com pygame_gui para o recurso extra de simulação, depósito e reset
girar_button = pygame.Rect(325, 600, 150, 50)  # Botão de girar original

simular_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((660, 670), (125, 50)),  # Colocado abaixo do botão "Girar"
    text="GIROS",
    manager=manager
)

depositar_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((550, 730), (150, 50)),  # Botão de depósito abaixo do "Simular"
    text="Depositar",
    manager=manager
)

resetar_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((705, 730), (90, 50)),  # Botão de reset abaixo do "Depositar"
    text="Resetar",
    manager=manager
)

simulacoes_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((555, 680), (100, 30)),  # Mantido conforme solicitado
    manager=manager
)

# Iniciar o jogo
jogo()