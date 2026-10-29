import math

import pygame
from constants import ALTURA, AZUL, CHAO_Y, LARGURA


class Bullet:
    def __init__(self, x, y, dir_x, dir_y):
        self.x = x
        self.y = y
        self.velocidade = 10
        
        # Se for diagonal, normalizamos o vetor para manter a velocidade constante
        if dir_x != 0 and dir_y != 0:
            fator = 1 / math.sqrt(2)
            self.vel_x = self.velocidade * dir_x * fator
            self.vel_y = self.velocidade * dir_y * fator
            self.largura = 8
            self.altura = 8
        else:
            self.vel_x = self.velocidade * dir_x
            self.vel_y = self.velocidade * dir_y
            self.largura = 5 if dir_x == 0 else 10
            self.altura = 10 if dir_x == 0 else 5

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def atualizar(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def desenhar(self, tela):
        pygame.draw.rect(tela, (255, 255, 0), (self.x, self.y, self.largura, self.altura))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largura = 40
        self.altura = 60
        self.velocidade = 5
        self.vel_y = 0
        self.gravidade = 0.5
        self.forca_pulo = -12
        self.no_chao = False
        self.direcao = 1  # 1 para direita, -1 para esquerda
        self.tiros = []
        self.cooldown_tiro = 0
        self.largura_normal = 40
        self.altura_normal = 60
        self.deitado = False
        self.vidas = 3
        self.invencivel = 0  # frames de invencibilidade após levar dano

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def levar_dano(self):
        # Enquanto estiver invencível, ignora o dano
        if self.invencivel > 0:
            return

        self.vidas -= 1
        self.invencivel = 120  # 2 segundos a 60 FPS

        # Reaparece caindo do topo, em pé
        self.deitado = False
        self.largura = self.largura_normal
        self.altura = self.altura_normal
        self.x = 100
        self.y = 0
        self.vel_y = 0
        self.no_chao = False

    def atualizar(self, teclas):
        # Movimento horizontal para a esquerda
        if teclas[pygame.K_a]:
            self.x -= self.velocidade
            self.direcao = -1

        # Movimento horizontal para a direita
        if teclas[pygame.K_d]:
            self.x += self.velocidade
            self.direcao = 1

        # Pulo (Espaço ou Seta para Cima)
        if teclas[pygame.K_SPACE] and self.no_chao:
            self.vel_y = self.forca_pulo
            self.no_chao = False

        # Se deitar + reduz o hitbox
        if teclas[pygame.K_LALT] and self.no_chao:
            if not self.deitado:
                self.deitado = True
                self.altura = 30  # Altura reduzida
                self.largura = 70 # Largura maior (esticado)
                self.y += 30  # Empurra para baixo para compensar a perda de altura
        else:
            if self.deitado:
                # Levanta e ajusta o Y para não afundar no chão
                self.y -= (60 - 30)
                self.altura = self.altura_normal
                self.largura = self.largura_normal
                self.deitado = False

        # Tiro (Left Control) com suporte a mirar para cima (W)
        if teclas[pygame.K_LCTRL] and self.cooldown_tiro == 0:
            apontando_cima = teclas[pygame.K_w] and not self.deitado
            apontando_baixo = (teclas[pygame.K_s] or teclas[pygame.K_DOWN]) and not self.deitado
            movendo_horizontal = teclas[pygame.K_a] or teclas[pygame.K_d] or teclas[pygame.K_LEFT] or teclas[pygame.K_RIGHT]
            
            direcao_x = self.direcao
            direcao_y = 0

            if apontando_cima and movendo_horizontal:
                # Diagonal superior
                direcao_x = self.direcao
                direcao_y = -1
                tiro_x = self.x + self.largura if self.direcao == 1 else self.x - 10
                tiro_y = self.y - 10
            elif apontando_cima:
                # Apenas para cima
                direcao_x = 0
                direcao_y = -1
                tiro_x = self.x + self.largura // 2 - 2
                tiro_y = self.y - 10
            elif apontando_baixo and movendo_horizontal:
                # Diagonal inferior
                direcao_x = self.direcao
                direcao_y = 1
                tiro_x = self.x + self.largura if self.direcao == 1 else self.x - 10
                tiro_y = self.y + self.altura
            elif apontando_baixo:
                # Apenas para baixo
                direcao_x = 0
                direcao_y = 1
                tiro_x = self.x + self.largura // 2 - 2
                tiro_y = self.y + self.altura
            else:
                # Tiro normal para frente (forçado se estiver deitado)
                direcao_x = self.direcao
                direcao_y = 0
                tiro_x = self.x + self.largura if self.direcao == 1 else self.x - 10
                offset_y = 15 if self.deitado else self.altura // 2 - 2
                tiro_y = self.y + offset_y

            self.tiros.append(Bullet(tiro_x, tiro_y, direcao_x, direcao_y))
            self.cooldown_tiro = 15

        # Aplica gravidade
        self.vel_y += self.gravidade
        self.y += self.vel_y

        # Limite temporário do chão
        if self.y + self.altura >= CHAO_Y:
            self.y = CHAO_Y - self.altura
            self.vel_y = 0
            self.no_chao = True

        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= 1

        if self.invencivel > 0:
            self.invencivel -= 1

        # Remove tiros que saíram da tela (horizontal e vertical)
        for tiro in self.tiros[:]:
            tiro.atualizar()
            if tiro.x < 0 or tiro.x > LARGURA or tiro.y < 0 or tiro.y > ALTURA:
                self.tiros.remove(tiro)

    def desenhar(self, tela):
        # Pisca enquanto está invencível
        piscando = self.invencivel > 0 and (self.invencivel // 5) % 2 == 0
        if not piscando:
            pygame.draw.rect(tela, AZUL, (self.x, self.y, self.largura, self.altura))
        for tiro in self.tiros:
            tiro.desenhar(tela)