import os

import pygame
from constants import ALTURA, LARGURA


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
        self.spawn_pos = (150, 450)

        # Definição das plataformas do stage 1
        self.plataformas = [
              
        ]

    def desenhar(self, tela, camera_x, jogador, inimigos):
        if camera_x < 0:
            camera_x = 0
        elif camera_x > self.largura_bg - LARGURA:
            camera_x = self.largura_bg - LARGURA

        # 1. Desenha o fundo com o recorte da câmera
        area_recorte = pygame.Rect(camera_x, 0, LARGURA, ALTURA)
        tela.blit(self.background, (0, 0), area_recorte)

        # 2. Desenha o player ajustado pela câmera
        jogador.desenhar(tela, camera_x)

        # 3. Desenha os inimigos ajustados pela câmera
        inimigos.desenhar(tela, camera_x)

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