import pygame
from constants import LARGURA, ALTURA, FPS, PRETO
from player import Player

pygame.init()
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Contra")

clock = pygame.time.Clock()
jogador = Player(100, 300)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    jogador.atualizar(keys)

    screen.fill(PRETO)
    jogador.desenhar(screen)
    pygame.display.flip()
    
    clock.tick(FPS)

pygame.quit()