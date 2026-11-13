import pygame
from constants import ALTURA, BRANCO, DEBUG, FPS, LARGURA, PRETO
from enemies import GerenciadorInimigos
from menu import Menu
from player import Player
from powerups import GerenciadorPowerUps
from scenario import Stage_1
from sound import SoundManager

pygame.init()
SoundManager.inicializar()
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Contra")

clock = pygame.time.Clock()
fonte = pygame.font.Font(None, 36)
fonte_grande = pygame.font.Font(None, 96)

menu = Menu()
stage1 = Stage_1()
jogador = Player(stage1.spawn_pos[0], stage1.spawn_pos[1])
boss = stage1.criar_boss()
inimigos = GerenciadorInimigos(stage1.obter_spawns(), stage1.obter_caixas_torreta(), boss)
powerups = GerenciadorPowerUps(stage1.obter_caixas_powerup(), stage1.escala_x)
estado = "MENU"
camera_x = 0

if DEBUG:
    print("DEBUG: o HUD mostra a coordenada do mouse; use pra preencher self.caixas_torreta (scenario.py).")

running = True
while running:
    eventos = pygame.event.get()
    for event in eventos:
        if event.type == pygame.QUIT:
            running = False

        if estado == "GAME_OVER":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    jogador = Player(stage1.spawn_pos[0], stage1.spawn_pos[1])
                    boss = stage1.criar_boss()
                    inimigos = GerenciadorInimigos(stage1.obter_spawns(), stage1.obter_caixas_torreta(), boss)
                    powerups = GerenciadorPowerUps(stage1.obter_caixas_powerup(), stage1.escala_x)
                    camera_x = 0
                    SoundManager.tocar_musica()
                    estado = "JOGO"
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    SoundManager.parar_musica()
                    SoundManager.parar_passos()
                    estado = "MENU"

        elif estado == "VITORIA":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    jogador = Player(stage1.spawn_pos[0], stage1.spawn_pos[1])
                    boss = stage1.criar_boss()
                    inimigos = GerenciadorInimigos(stage1.obter_spawns(), stage1.obter_caixas_torreta(), boss)
                    powerups = GerenciadorPowerUps(stage1.obter_caixas_powerup(), stage1.escala_x)
                    camera_x = 0
                    SoundManager.tocar_musica()
                    estado = "JOGO"
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    SoundManager.parar_musica()
                    SoundManager.parar_passos()
                    estado = "MENU"

        elif estado == "JOGO":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                SoundManager.parar_musica()
                SoundManager.parar_passos()
                estado = "MENU"

    teclas = pygame.key.get_pressed()

    if estado == "MENU":
        if menu.atualizar(eventos, teclas):
            stage1 = Stage_1()
            jogador = Player(stage1.spawn_pos[0], stage1.spawn_pos[1])
            boss = stage1.criar_boss()
            inimigos = GerenciadorInimigos(stage1.obter_spawns(), stage1.obter_caixas_torreta(), boss)
            powerups = GerenciadorPowerUps(stage1.obter_caixas_powerup(), stage1.escala_x)
            camera_x = 0
            SoundManager.tocar_musica()
            estado = "JOGO"

        menu.desenhar(screen)

    elif estado == "JOGO":
        SoundManager.tocar_musica()
        plataformas_atuais = stage1.obter_plataformas_tela(0)
        jogador.atualizar(teclas, plataformas_atuais)

        # Para desligar os inimigos, comente a linha abaixo
        inimigos.atualizar(jogador, camera_x, plataformas_atuais)
        powerups.atualizar(jogador, camera_x, plataformas_atuais)

        if jogador.y > ALTURA + 100 or jogador.vidas <= 0:
            SoundManager.parar_musica()
            SoundManager.parar_passos()
            estado = "GAME_OVER"

        # Vitória ao derrotar os canhões
        if inimigos.vitoria:
            SoundManager.parar_passos()
            estado = "VITORIA"

        # Câmera segue o jogador (1/3 da tela), com clamping nos limites do cenário
        camera_x = jogador.rect.centerx - LARGURA // 3
        if camera_x < 0:
            camera_x = 0
        elif camera_x > stage1.largura_bg - LARGURA:
            camera_x = stage1.largura_bg - LARGURA

        screen.fill(PRETO)
        stage1.desenhar(screen, camera_x, jogador, inimigos, powerups)

        # HUD
        hud = fonte.render(f"VIDAS: {max(jogador.vidas, 0)}    PONTOS: {inimigos.pontos}", True, BRANCO)
        screen.blit(hud, (20, 20))

        if DEBUG:
            # Coordenada do mouse no sistema do scenario.py (pra posicionar caixas/spawns)
            mx, my = pygame.mouse.get_pos()
            coord = fonte.render(
                f"MOUSE x: {int((mx + camera_x) / stage1.escala_x)}  y: {int(my / stage1.escala_y)}",
                True, BRANCO)
            screen.blit(coord, (20, 55))

    elif estado == "GAME_OVER":
        screen.fill(PRETO)
        stage1.desenhar(screen, camera_x, jogador, inimigos, powerups)

        texto = fonte_grande.render("GAME OVER", True, BRANCO)
        dica1 = fonte.render("Pressione R para reiniciar", True, BRANCO)
        dica2 = fonte.render("Pressione ESC para o Menu", True, BRANCO)
        screen.blit(texto, texto.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50)))
        screen.blit(dica1, dica1.get_rect(center=(LARGURA // 2, ALTURA // 2 + 20)))
        screen.blit(dica2, dica2.get_rect(center=(LARGURA // 2, ALTURA // 2 + 65)))

    elif estado == "VITORIA":
        screen.fill(PRETO)
        stage1.desenhar(screen, camera_x, jogador, inimigos, powerups)

        texto_v = fonte_grande.render("STAGE CLEAR!", True, (0, 255, 0))
        pontos_txt = fonte.render(f"PONTOS: {inimigos.pontos}", True, BRANCO)
        dica1_v = fonte.render("Pressione R para jogar novamente", True, BRANCO)
        dica2_v = fonte.render("Pressione ESC para o Menu", True, BRANCO)
        screen.blit(texto_v, texto_v.get_rect(center=(LARGURA // 2, ALTURA // 2 - 60)))
        screen.blit(pontos_txt, pontos_txt.get_rect(center=(LARGURA // 2, ALTURA // 2 + 10)))
        screen.blit(dica1_v, dica1_v.get_rect(center=(LARGURA // 2, ALTURA // 2 + 60)))
        screen.blit(dica2_v, dica2_v.get_rect(center=(LARGURA // 2, ALTURA // 2 + 100)))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()