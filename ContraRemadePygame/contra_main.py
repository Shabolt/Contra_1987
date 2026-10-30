import pygame
from constants import ALTURA, BRANCO, CHAO_Y, FPS, LARGURA, PRETO
from enemies import GerenciadorInimigos
from player import Player
from scenario import Cenario

pygame.init()
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Contra")

clock = pygame.time.Clock()
fonte = pygame.font.Font(None, 36)
fonte_grande = pygame.font.Font(None, 96)

cenario = Cenario()
jogador = Player(100, 300)
jogador.plataformas = cenario.plataformas
inimigos = GerenciadorInimigos()
game_over = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Reinicia o jogo apertando R na tela de game over
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
            jogador = Player(100, 300)
            jogador.plataformas = cenario.plataformas
            inimigos = GerenciadorInimigos()
            game_over = False

    keys = pygame.key.get_pressed()

    if not game_over:
        jogador.atualizar(keys)
        inimigos.atualizar(jogador)
        if jogador.vidas <= 0:
            game_over = True

    # Desenha o cenário (substitui o fundo preto + chão antigo)
    cenario.desenhar(screen)
    inimigos.desenhar(screen)
    jogador.desenhar(screen)

    # HUD
    hud = fonte.render(f"VIDAS: {max(jogador.vidas, 0)}    PONTOS: {inimigos.pontos}", True, BRANCO)
    screen.blit(hud, (20, 20))

    if game_over:
        texto = fonte_grande.render("GAME OVER", True, BRANCO)
        dica = fonte.render("Pressione R para reiniciar", True, BRANCO)
        screen.blit(texto, texto.get_rect(center=(LARGURA // 2, ALTURA // 2 - 40)))
        screen.blit(dica, dica.get_rect(center=(LARGURA // 2, ALTURA // 2 + 30)))

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
