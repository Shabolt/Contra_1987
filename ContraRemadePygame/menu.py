import os
import pygame
from constants import ALTURA, BRANCO, LARGURA, PRETO


class Menu:
    def __init__(self):
        diretorio_atual = os.path.dirname(__file__)
        bg_path = os.path.join(diretorio_atual, "assets", "backgrounds", "title_bg.png")
        cursor_path = os.path.join(diretorio_atual, "assets", "backgrounds", "title_cursor.png")

        self.background = None
        self.cursor = None

        if os.path.exists(bg_path):
            imagem_bg = pygame.image.load(bg_path).convert()
            self.escala = ALTURA / float(imagem_bg.get_height())
            novo_w = int(imagem_bg.get_width() * self.escala)
            novo_h = int(imagem_bg.get_height() * self.escala)
            self.background = pygame.transform.scale(imagem_bg, (novo_w, novo_h))
            self.pos_x = (LARGURA - novo_w) // 2
            self.pos_y = (ALTURA - novo_h) // 2
        else:
            self.escala = 2.3
            self.pos_x = 0
            self.pos_y = 0

        if os.path.exists(cursor_path):
            img_c = pygame.image.load(cursor_path).convert_alpha()
            cw = int(img_c.get_width() * self.escala)
            ch = int(img_c.get_height() * self.escala)
            self.cursor = pygame.transform.scale(img_c, (cw, ch))
            self.cursor_x = self.pos_x + int(25 * self.escala)
            self.cursor_y = self.pos_y + int(271 * self.escala)
        else:
            self.cursor_x = LARGURA // 2 - 120
            self.cursor_y = ALTURA // 2

        self.fonte = pygame.font.Font(None, 40)
        self.iniciando = False
        self.timer_inicio = 0

    def atualizar(self, eventos, teclas):
        """Retorna True quando o jogador confirma o início do jogo."""
        if self.iniciando:
            self.timer_inicio -= 1
            if self.timer_inicio <= 0:
                self.iniciando = False
                return True
            return False

        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z, pygame.K_x, pygame.K_LCTRL, pygame.K_RCTRL):
                    self.iniciar()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.iniciar()

        return False

    def iniciar(self):
        self.iniciando = True
        self.timer_inicio = 24  # Pisca o cursor na confirmação antes de carregar a fase

    def desenhar(self, tela):
        tela.fill((20, 16, 22))

        if self.background:
            tela.blit(self.background, (self.pos_x, self.pos_y))
        else:
            # Fallback caso a imagem não esteja acessível
            titulo = pygame.font.Font(None, 100).render("CONTRA", True, (255, 100, 0))
            opcao = self.fonte.render("1 PLAYER", True, BRANCO)
            tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, ALTURA // 3)))
            tela.blit(opcao, opcao.get_rect(center=(LARGURA // 2, ALTURA // 2)))

        # Efeito de piscar o cursor ao confirmar início (estilo arcade/NES)
        mostrar_cursor = True
        if self.iniciando:
            mostrar_cursor = (self.timer_inicio // 4) % 2 == 0

        if mostrar_cursor:
            if self.cursor:
                tela.blit(self.cursor, (self.cursor_x, self.cursor_y))
            else:
                # Indicador de cursor fallback
                pygame.draw.polygon(tela, (255, 200, 0), [
                    (self.cursor_x, self.cursor_y),
                    (self.cursor_x + 20, self.cursor_y + 10),
                    (self.cursor_x, self.cursor_y + 20)
                ])
