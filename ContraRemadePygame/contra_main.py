import pygame
from scenario import Stage_1
from constants import ALTURA, BRANCO, CHAO_Y, FPS, LARGURA, PRETO, VERDE
from enemies import GerenciadorInimigos
from player import Player

camera_x = 0  

pygame.init()
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Contra")

clock = pygame.time.Clock()
fonte = pygame.font.Font(None, 36)
fonte_grande = pygame.font.Font(None, 96)

jogador = Player(100, 300)
inimigos = GerenciadorInimigos()
game_over = False

stage1 = Stage_1()
player = Player(stage1.spawn_pos[0], stage1.spawn_pos[1])

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Reinicia o jogo apertando R na tela de game over
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
            jogador = Player(100, 300)
            inimigos = GerenciadorInimigos()
            game_over = False

    teclas = pygame.key.get_pressed()

    if not game_over:
        camera_x = jogador.rect.centerx - LARGURA // 3
        plataformas_atuais = stage1.obter_plataformas_tela(camera_x)
        jogador.atualizar(teclas, plataformas_atuais)
        inimigos.atualizar(jogador)
        if jogador.vidas <= 0:
            game_over = True

    screen.fill(PRETO)
    inimigos.desenhar(screen, camera_x)
    jogador.desenhar(screen, camera_x)
    stage1.desenhar(screen, camera_x, jogador, inimigos)

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