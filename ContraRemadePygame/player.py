import pygame
from constants import ALTURA, BRANCO, LARGURA, VERMELHO
from animations import SpriteManager

class Tiro:
    def __init__(self, x, y, direcao_x, direcao_y=0):
        self.x = x
        self.y = y
        self.velocidade = 12
        self.direcao_x = direcao_x
        self.direcao_y = direcao_y
        self.raio = 8
        self.frame_anim = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.raio), int(self.y - self.raio), self.raio * 2, self.raio * 2)

    def atualizar(self):
        self.x += self.velocidade * self.direcao_x
        self.y += self.velocidade * self.direcao_y
        self.frame_anim += 0.3

    def fora_da_tela(self, camera_x):
        return self.x < -10000 or self.x > 20000 or self.y < -2000 or self.y > ALTURA + 2000

    def desenhar(self, tela, camera_x):
        pos_x_tela = self.x - camera_x
        # Usa explo2 para o tiro do Bill (conforme solicitado nas imagens)
        imgs = SpriteManager.frames_tiro_bill if hasattr(SpriteManager, 'frames_tiro_bill') and SpriteManager.frames_tiro_bill else []
        if imgs:
            img = imgs[int(self.frame_anim) % len(imgs)]
            tam = 20
            tela.blit(pygame.transform.scale(img, (tam, tam)), (int(pos_x_tela - tam//2), int(self.y - tam//2)))
        else:
            pygame.draw.circle(tela, BRANCO, (int(pos_x_tela), int(self.y)), self.raio)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largura = 40
        self.altura = 60
        self.vel_x = 0
        self.vel_y = 0
        self.gravidade = 0.50  
        self.no_chao = False
        self.vidas = 3
        self.direcao = 1  # 1 para direita, -1 para esquerda

        self.tiros = []
        self.cooldown_tiro = 0
        self.frame_idx = 0.0
        self.pulo_frame_idx = 0.0
        self.movendo_flag = False

        SpriteManager.carregar_tudo()

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def levar_dano(self):
        self.vidas -= 1

    def atirar(self, teclas):
        if self.cooldown_tiro > 0:
            return

        cima = teclas[pygame.K_UP] or teclas[pygame.K_w]
        baixo = teclas[pygame.K_DOWN] or teclas[pygame.K_s]
        esquerda = teclas[pygame.K_LEFT] or teclas[pygame.K_a]
        direita = teclas[pygame.K_RIGHT] or teclas[pygame.K_d]

        dx = float(self.direcao)
        dy = 0.0
        fator_diag = 0.7071

        if cima:
            if esquerda:
                dx, dy = -fator_diag, -fator_diag
            elif direita:
                dx, dy = fator_diag, -fator_diag
            else:
                dx, dy = 0.0, -1.0
        elif baixo and self.no_chao:
            dx, dy = float(self.direcao), 0.0
        elif baixo and not self.no_chao:
            if esquerda:
                dx, dy = -fator_diag, fator_diag
            elif direita:
                dx, dy = fator_diag, fator_diag
            else:
                dx, dy = 0.0, 1.0
        else:
            if esquerda:
                dx, dy = -1.0, 0.0
            elif direita:
                dx, dy = 1.0, 0.0
            else:
                dx, dy = float(self.direcao), 0.0

        origem_x = self.x + self.largura // 2 + (dx * 20)
        origem_y = self.y + self.altura // 2 + (dy * 20)
        
        self.tiros.append(Tiro(origem_x, origem_y, dx, dy))
        self.cooldown_tiro = 12

    def atualizar(self, teclas, plataformas):
        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= 1

        atirando_pressionado = (teclas[pygame.K_z] or teclas[pygame.K_x] or teclas[pygame.K_RCTRL] or teclas[pygame.K_LCTRL])
        if atirando_pressionado:
            self.atirar(teclas)

        velocidade_movimento = 4.2
        self.movendo_flag = False
        self.vel_x = 0

        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x = -velocidade_movimento
            self.direcao = -1
            self.movendo_flag = True
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x = velocidade_movimento
            self.direcao = 1
            self.movendo_flag = True

        self.x += self.vel_x

        if teclas[pygame.K_SPACE] and self.no_chao:
            self.vel_y = -16.5
            self.no_chao = False
            self.pulo_frame_idx = 0.0

        y_antes = self.y + self.altura
        self.vel_y += self.gravidade
        self.y += self.vel_y
        self.no_chao = False

        if self.vel_y >= 0:
            for p in plataformas:
                if (y_antes <= p.top + 5
                        and self.y + self.altura >= p.top
                        and self.x + self.largura > p.left + 5
                        and self.x < p.right - 5):
                    self.y = p.top - self.altura
                    self.vel_y = 0
                    self.no_chao = True
                    break

        if not self.no_chao:
            self.pulo_frame_idx += 0.25
        else:
            self.pulo_frame_idx = 0.0

        if self.movendo_flag or atirando_pressionado:
            self.frame_idx += 0.25
        else:
            self.frame_idx = 0.0

        for tiro in self.tiros[:]:
            tiro.atualizar()
            if tiro.fora_da_tela(0):
                self.tiros.remove(tiro)

    def desenhar(self, tela, camera_x):
        pos_x_tela = self.x - camera_x
        teclas = pygame.key.get_pressed()

        atirando = (self.cooldown_tiro > 0 or teclas[pygame.K_z] or teclas[pygame.K_x] or teclas[pygame.K_RCTRL] or teclas[pygame.K_LCTRL])
        lista = None

        if not self.no_chao:
            if self.direcao == 1:
                lista = SpriteManager.frames_pulo_d
            else:
                lista = SpriteManager.frames_pulo_e
        else:
            mirando_cima = teclas[pygame.K_UP] or teclas[pygame.K_w]
            mirando_baixo = teclas[pygame.K_DOWN] or teclas[pygame.K_s]

            if mirando_cima:
                if getattr(self, 'movendo_flag', False) or atirando:
                    if self.direcao == 1:
                        lista = SpriteManager.frames_and_ccd if SpriteManager.frames_and_ccd else SpriteManager.frames_mira_cima_d
                    else:
                        lista = SpriteManager.frames_and_cce if SpriteManager.frames_and_cce else SpriteManager.frames_mira_cima_e
                else:
                    if self.direcao == 1:
                        lista = SpriteManager.frames_mira_cima_d
                    else:
                        lista = SpriteManager.frames_mira_cima_e
            elif mirando_baixo and self.no_chao:
                if self.direcao == 1:
                    lista = SpriteManager.frames_and_bd if SpriteManager.frames_and_bd else SpriteManager.frames_deitado_d
                else:
                    lista = SpriteManager.frames_and_be if SpriteManager.frames_and_be else SpriteManager.frames_deitado_e
            else:
                if atirando:
                    if self.direcao == 1:
                        lista = SpriteManager.frames_and_cd
                    else:
                        lista = SpriteManager.frames_and_ce
                elif self.vel_x != 0:
                    if self.direcao == 1:
                        lista = SpriteManager.frames_andando_d
                    else:
                        lista = SpriteManager.frames_andando_e
                else:
                    if self.direcao == 1:
                        lista = SpriteManager.frames_jogador_parado_d
                    else:
                        lista = SpriteManager.frames_jogador_parado_e

        if lista:
            idx = int(self.pulo_frame_idx) if not self.no_chao else int(self.frame_idx)
            img = lista[idx % len(lista)]
            tela.blit(pygame.transform.scale(img, (self.largura, self.altura)), (pos_x_tela, self.y))
        else:
            pygame.draw.rect(tela, VERMELHO, (pos_x_tela, self.y, self.largura, self.altura))

        for tiro in self.tiros:
            tiro.desenhar(tela, camera_x)
