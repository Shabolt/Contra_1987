import math
import random

import pygame
from constants import ALTURA, BRANCO, CHAO_Y, CINZA, LARANJA, LARGURA, VERMELHO


class BalaInimiga:
    """Tiro inimigo: sai em direção a um alvo (posição do jogador no momento do disparo)."""

    def __init__(self, x, y, alvo_x, alvo_y):
        self.x = x
        self.y = y
        self.raio = 5
        velocidade = 5

        dx = alvo_x - x
        dy = alvo_y - y
        distancia = math.hypot(dx, dy) or 1  # evita divisão por zero
        self.vel_x = dx / distancia * velocidade
        self.vel_y = dy / distancia * velocidade

    @property
    def rect(self):
        return pygame.Rect(self.x - self.raio, self.y - self.raio, self.raio * 2, self.raio * 2)

    def atualizar(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def fora_da_tela(self):
        return self.x < -20 or self.x > LARGURA + 20 or self.y < -20 or self.y > ALTURA + 20

    def desenhar(self, tela, camera_x):
        # Subtrai o camera_x para desenhar na posição correta da tela
        pos_x_tela = self.x - camera_x
        pygame.draw.circle(tela, BRANCO, (int(pos_x_tela), int(self.y)), self.raio)
        pygame.draw.circle(tela, VERMELHO, (int(pos_x_tela), int(self.y)), self.raio - 2)


class Inimigo:
    """Classe base: todo inimigo novo deve herdar dela e sobrescrever atualizar()."""

    def __init__(self, x, y, largura, altura, vida, cor, pontos):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.vida = vida
        self.cor = cor
        self.pontos = pontos
        self.direcao = -1  # 1 = olhando pra direita, -1 = esquerda
        self.vivo = True

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def levar_dano(self, dano=1):
        self.vida -= dano
        if self.vida <= 0:
            self.vivo = False

    def fora_da_tela(self):
        return False

    def atualizar(self, jogador, balas_inimigas):
        pass

    def desenhar(self, tela, camera_x):
        # Subtrai o camera_x para desenhar na posição correta da tela
        pos_x_tela = self.x - camera_x
        pygame.draw.rect(tela, self.cor, (pos_x_tela, self.y, self.largura, self.altura))
        # "arma" só pra indicar pra onde o inimigo está olhando
        arma_x = pos_x_tela + self.largura if self.direcao == 1 else pos_x_tela - 12
        pygame.draw.rect(tela, CINZA, (arma_x, self.y + 20, 12, 6))


class Soldado(Inimigo):
    """Soldado corredor: atravessa a tela correndo e pula de vez em quando."""

    def __init__(self, x, direcao):
        super().__init__(x, CHAO_Y - 60, 40, 60, vida=1, cor=VERMELHO, pontos=100)
        self.direcao = direcao
        self.velocidade = 3
        self.vel_y = 0
        self.gravidade = 0.5
        self.no_chao = True

    def atualizar(self, jogador, balas_inimigas):
        self.x += self.velocidade * self.direcao

        # Pulo aleatório
        if self.no_chao and random.random() < 0.004:
            self.vel_y = -10
            self.no_chao = False

        self.vel_y += self.gravidade
        self.y += self.vel_y

        if self.y + self.altura >= CHAO_Y:
            self.y = CHAO_Y - self.altura
            self.vel_y = 0
            self.no_chao = True

    def fora_da_tela(self):
        return self.x < -100 or self.x > LARGURA + 100


class Atirador(Inimigo):
    """Entra pela lateral, para numa posição e atira mirando no jogador."""

    def __init__(self, x, alvo_x):
        super().__init__(x, CHAO_Y - 60, 40, 60, vida=2, cor=LARANJA, pontos=200)
        self.alvo_x = alvo_x
        self.velocidade = 3
        self.cooldown = random.randint(40, 90)

    def atualizar(self, jogador, balas_inimigas):
        # Fase 1: caminha até a posição escolhida (sem atirar)
        if abs(self.x - self.alvo_x) > self.velocidade:
            self.direcao = 1 if self.alvo_x > self.x else -1
            self.x += self.velocidade * self.direcao
            return

        # Fase 2: parado, olhando pro jogador e atirando
        self.direcao = 1 if jogador.x > self.x else -1
        self.cooldown -= 1
        if self.cooldown <= 0:
            origem_x = self.x + self.largura // 2 + self.direcao * (self.largura // 2 + 6)
            origem_y = self.y + 23
            alvo_x = jogador.x + jogador.largura / 2
            alvo_y = jogador.y + jogador.altura / 2
            balas_inimigas.append(BalaInimiga(origem_x, origem_y, alvo_x, alvo_y))
            self.cooldown = random.randint(80, 140)


class GerenciadorInimigos:
    """Cuida de spawn, atualização, colisões e desenho de inimigos e balas inimigas."""

    def __init__(self):
        self.inimigos = []
        self.balas = []
        self.pontos = 0
        self.timer_spawn = 60
        self.intervalo_spawn = 90   # frames entre spawns (varia +-30)
        self.max_inimigos = 6

    def _spawnar(self, jogador):
        lado_esquerdo = random.choice([True, False])
        x_spawn = -50 if lado_esquerdo else LARGURA + 10

        if random.random() < 0.65:
            direcao = 1 if lado_esquerdo else -1
            self.inimigos.append(Soldado(x_spawn, direcao))
        else:
            # Escolhe uma posição que não seja em cima do jogador
            alvo_x = random.randint(100, LARGURA - 140)
            for _ in range(10):
                if abs(alvo_x - jogador.x) > 300:
                    break
                alvo_x = random.randint(100, LARGURA - 140)
            self.inimigos.append(Atirador(x_spawn, alvo_x))

    def atualizar(self, jogador):
        # Spawn
        self.timer_spawn -= 1
        if self.timer_spawn <= 0 and len(self.inimigos) < self.max_inimigos:
            self._spawnar(jogador)
            self.timer_spawn = random.randint(self.intervalo_spawn - 30, self.intervalo_spawn + 30)

        # Atualiza inimigos e balas
        for inimigo in self.inimigos:
            inimigo.atualizar(jogador, self.balas)
        for bala in self.balas:
            bala.atualizar()

        # Tiros do jogador x inimigos
        for tiro in jogador.tiros[:]:
            for inimigo in self.inimigos:
                if inimigo.vivo and tiro.rect.colliderect(inimigo.rect):
                    inimigo.levar_dano()
                    jogador.tiros.remove(tiro)
                    if not inimigo.vivo:
                        self.pontos += inimigo.pontos
                    break

        # Inimigos e balas inimigas x jogador
        for inimigo in self.inimigos:
            if inimigo.vivo and inimigo.rect.colliderect(jogador.rect):
                jogador.levar_dano()

        for bala in self.balas[:]:
            if bala.rect.colliderect(jogador.rect):
                jogador.levar_dano()
                self.balas.remove(bala)

        # Limpeza
        self.inimigos = [i for i in self.inimigos if i.vivo and not i.fora_da_tela()]
        self.balas = [b for b in self.balas if not b.fora_da_tela()]

    def desenhar(self, tela, camera_x):
        for inimigo in self.inimigos:
            inimigo.desenhar(tela, camera_x)
        for bala in self.balas:
            bala.desenhar(tela, camera_x)