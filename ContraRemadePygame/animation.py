import os
import pygame
from pygame.locals import *

pygame.init()

screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Contra Style - Animação")

# Descobre o diretório exato onde este script está guardado
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprites = []
        
        # EXEMPLO: Se você tiver 8 imagens na pasta, mude o final do range para 9 (range vai de 1 até 8)
        total_frames = 5
        for i in range(1, total_frames + 1):
            caminho_img = os.path.join(DIRETORIO_ATUAL, 'assets', 'sprites', f'and_{i}.png')
            self.sprites.append(pygame.image.load(caminho_img).convert_alpha())
            
        self.atual = 0
        self.image = self.sprites[self.atual]
        self.rect = self.image.get_rect()
        self.rect.topleft = [100, 100]  # Posição inicial na tela
        
        # Controla a velocidade da troca de frames (quanto menor, mais devagar a animação roda)
        self.velocidade_animacao = 0.25

    def update(self):
        # Avança o frame atual gradualmente
        self.atual += self.velocidade_animacao
        
        # Se passar do último frame disponível, o ciclo reinicia no primeiro (0)
        if self.atual >= len(self.sprites):
            self.atual = 0
            
        # Atualiza a imagem atual da sprite convertendo o índice para número inteiro
        self.image = self.sprites[int(self.atual)]

# Nome do grupo padronizado
todas_as_sprites = pygame.sprite.Group()
player = Player()  
todas_as_sprites.add(player)

relogio = pygame.time.Clock()
Running = True

while Running:
    for event in pygame.event.get():
        if event.type == QUIT:
            Running = False

    # 1. Primeiro limpa a tela pintando o fundo de verde
    screen.fill((0, 255, 0))

    # 2. Atualiza a lógica das sprites e desenha-as na tela
    todas_as_sprites.update()
    todas_as_sprites.draw(screen)

    # 3. Atualiza o ecrã
    pygame.display.flip()
    relogio.tick(30)  # Limita a 30 quadros por segundo

pygame.quit()