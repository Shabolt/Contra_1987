import pygame
from constants import ALTURA, BRANCO, CHAO_Y, FPS, LARGURA, PRETO, VERDE
from enemies import GerenciadorInimigos
from player import Player
from scenario import Stage_1

pygame.init()





 quit...
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Contra")

clock = pygame.time.Clock()
fonte = pygame.font.Font(None, 36)
fonte_grande = pygame.font.Font(None, 96)

stage1 = Stage_1()
jogador = Player(stage1.spawn_pos[0], stage1.spawn_pos[1])
inimigos = GerenciadorInimigos()
game_over = False
camera_x = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Reinicia o jogo apertando R na tela de game over
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
            jogador = Player(stage1.spawn_pos[0], stage1.spawn_pos[1])
            inimigos = GerenciadorInimigos()
            game_over = False

    teclas = pygame.key.get_pressed()

    if not game_over:
        plataformas_atuais = stage1.obter_plataformas_tela(camera_x)
        jogador.atualizar(teclas, plataformas_atuais)
        inimigos.atualizar(jogador, camera_x)
        if jogador.vidas <= 0:
            game_over = True

        # Câmera segue o jogador (1/3 da tela), com clamping nos limites do cenário
        camera_x = jogador.rect.centerx - LARGURA // 3
        if camera_x < 0:
            camera_x = 0
        elif camera_x > stage1.largura_bg - LARGURA:
            camera_x = stage1.largura_bg - LARGURA

    screen.fill(PRETO)
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
