import os

import pygame
from constants import ALTURA, DEBUG, LARGURA, VERDE


class Stage_1:
    def __init__(self):
        diretorio_atual = os.path.dirname(__file__)
        caminho_bg = os.path.join(diretorio_atual, "assets", "backgrounds", "stage1_bg.png") 

        imagem_original = pygame.image.load(caminho_bg).convert()
        orig_w = imagem_original.get_width()
        orig_h = imagem_original.get_height()   

        nova_altura = ALTURA
        nova_largura = int(orig_w * (nova_altura / orig_h)) 
        
        # Carrega a imagem de fundo
        self.background = pygame.transform.scale(imagem_original, (nova_largura, nova_altura))  
        self.largura_bg = self.background.get_width()
        self.altura_bg = self.background.get_height()

        # Fator de escala caso os retângulos precisem ser proporcionais ao tamanho original
        self.escala_x = nova_largura / orig_w
        self.escala_y = nova_altura / orig_h

        # Posição de spawn do player (X, Y) na proporção da tela
        self.spawn_pos = (200, 700)

        # Definição das plataformas do stage 1
        self.plataformas = [
            #Template chunk de grama
            #pygame.Rect(x, y, 33, 1)
            
            #água
            pygame.Rect(1, 217, 1720, 1),

            #Seção 1 (pré-ponte 1)
            pygame.Rect(32, 100, 730, 1),
            pygame.Rect(159, 131, 95, 1),
            pygame.Rect(416, 131, 63, 1),
            pygame.Rect(640, 145, 95, 1),
            pygame.Rect(255, 163, 33, 1),
            pygame.Rect(351, 163, 33, 1),
            pygame.Rect(288, 193, 63, 1),
            pygame.Rect(608, 198, 63, 1),

            #Ponte 1 (liga a plataforma (32, 100) com a (1184, 100); estavam na mesma altura
            #e faltava o trecho no meio: ajuste o x/largura se a ponte do cenário for diferente)
            pygame.Rect(762, 100, 422, 1),

            #Seção 2 (pós-ponte 2)
            pygame.Rect(1376, 68, 512, 1),
            pygame.Rect(2047, 68, 161, 1), 
            pygame.Rect(1184, 100, 256, 1),
            pygame.Rect(1856, 100, 223, 1),
            pygame.Rect(2240, 100, 64, 1),
            pygame.Rect(1600, 132, 223, 1),
            pygame.Rect(2176, 132, 95, 1),
            pygame.Rect(1503, 149, 63, 1),
            pygame.Rect(2111, 149, 33, 1),
            pygame.Rect(1920, 164, 64, 1),
            pygame.Rect(2016, 164, 64, 1),
            pygame.Rect(1408, 197, 95, 1),
            pygame.Rect(1728, 197, 190, 1),

            #Seção 3 (precipícios)
            pygame.Rect(2624, 67, 64, 1),
            pygame.Rect(2369, 100, 64, 1),
            pygame.Rect(2593, 100, 64, 1),
            pygame.Rect(2721, 100, 64, 1),
            pygame.Rect(2337, 130, 64, 1),
            pygame.Rect(2464, 130, 64, 1),
            pygame.Rect(2753, 130, 161, 1),
            pygame.Rect(2658, 146, 33, 1),
            pygame.Rect(2498, 160, 95, 1),
            pygame.Rect(2462, 195, 33, 1),
            pygame.Rect(2626, 195, 33, 1),
            pygame.Rect(2848, 195, 95, 1),
            pygame.Rect(2979, 164, 64, 1),

            #Seção 4 (portão)
            pygame.Rect(3137, 100, 131, 1),
            pygame.Rect(3072, 130, 64, 1),
            pygame.Rect(3264, 130, 33, 1),
            pygame.Rect(3169, 149, 95, 1),
            pygame.Rect(3297, 164, 33, 1),
            pygame.Rect(3137, 195, 231, 1),

        ]

        # Pontos de spawn dos inimigos, fixos nas plataformas (como no jogo original).
        # Formato: (x, y do topo da plataforma, tipo)  -> mesmas coordenadas das plataformas
        # Dispara quando a borda direita da câmera chega no x do ponto.
        #   "soldado"  (vermelho): só nas plataformas SUPERIORES. Corre, não atira.
        #   "atirador" (laranja):  só nas plataformas INFERIORES. Fica parado e atira.
        self.spawns = [
            # --- Soldados: plataformas superiores ---
            (700, 100, "soldado"),    # plataforma (32, 100)
            (1300, 100, "soldado"),   # plataforma (1184, 100)
            (1700, 68, "soldado"),    # plataforma (1376, 68)
            (2150, 68, "soldado"),    # plataforma (2047, 68)
            (2660, 67, "soldado"),    # plataforma (2624, 67)
            (2740, 100, "soldado"),   # plataforma (2721, 100)
            (3200, 100, "soldado"),   # plataforma (3137, 100)

            # --- Atiradores: plataformas inferiores ---
            (320, 193, "atirador"),   # plataforma (288, 193)
            (640, 198, "atirador"),   # plataforma (608, 198)
            (1250, 217, "atirador"),  # nível da água
            (1440, 197, "atirador"),  # plataforma (1408, 197)
            (1800, 197, "atirador"),  # plataforma (1728, 197)
            (2880, 195, "atirador"),  # plataforma (2848, 195)
            (3250, 195, "atirador"),  # plataforma (3137, 195)
        ]

        # Caixas prateadas das torretas: (x do centro, y da base) em coordenadas do cenário.
        # A torreta é gerada automaticamente, na frente da caixa, quando o jogador chega a
        # 700px dela (GerenciadorInimigos.DISTANCIA_SPAWN_TORRETA). Uma entrada por caixa.
        # Dica: com DEBUG ligado o HUD mostra a coordenada do mouse; passe o mouse no
        # centro da caixa e some metade do tamanho_caixa no y pra achar a base.
        self.tamanho_caixa = 16
        self.caixas_torreta = [
            (334, 150),
            (1584, 140),
            (2287, 173),
            (2216, 174)
        ]

    # Desenha o cenário, player e inimigos na tela, ajustando 
    # pela posição da câmera
    def desenhar(self, tela, camera_x, jogador, inimigos):
        if camera_x < 0:
            camera_x = 0
        elif camera_x > self.largura_bg - LARGURA:
            camera_x = self.largura_bg - LARGURA

        # 1. Desenha o fundo com o recorte da câmera
        area_recorte = pygame.Rect(camera_x, 0, LARGURA, ALTURA)
        tela.blit(self.background, (0, 0), area_recorte)
        if DEBUG:
            # Plataformas em vermelho, spawns em verde e caixas das torretas em ciano
            for p in self.obter_plataformas_tela(camera_x):
                pygame.draw.rect(tela, (255, 0, 0), p)
            for x, y, _tipo in self.obter_spawns():
                pygame.draw.line(tela, VERDE, (x - camera_x, y - 80), (x - camera_x, y), 3)
            for caixa in self.obter_caixas_torreta():
                pygame.draw.rect(tela, (0, 255, 255), caixa.move(-camera_x, 0), 2)

        # 2. Desenha o player ajustado pela câmera
        jogador.desenhar(tela, camera_x)

        # 3. Desenha os inimigos ajustados pela câmera
        inimigos.desenhar(tela, camera_x)

    # Retorna uma lista de retângulos das plataformas ajustadas
    # para a tela, considerando a posição da câmera
    def obter_plataformas_tela(self, camera_x):
        plataformas_ajustadas = []
        for p in self.plataformas:
            rect_tela = pygame.Rect(
                p.x * self.escala_x - camera_x,
                p.y * self.escala_y,
                p.width * self.escala_x,
                p.height * self.escala_y
            )
            plataformas_ajustadas.append(rect_tela)
        return plataformas_ajustadas

    # Pontos de spawn em coordenadas de mundo (já escaladas): (x, y_topo, tipo)
    def obter_spawns(self):
        return [(int(x * self.escala_x), int(y * self.escala_y), tipo)
                for x, y, tipo in self.spawns]

    # Retângulos das caixas das torretas em coordenadas de mundo (já escaladas)
    def obter_caixas_torreta(self):
        t = self.tamanho_caixa
        return [pygame.Rect(int((x - t / 2) * self.escala_x), int((y - t) * self.escala_y),
                            int(t * self.escala_x), int(t * self.escala_y))
                for x, y in self.caixas_torreta]