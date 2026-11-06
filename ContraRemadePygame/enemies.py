import math
import random

import pygame
from constants import ALTURA, BRANCO, CINZA, LARANJA, LARGURA, VERMELHO


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

    def fora_da_tela(self, camera_x):
        # Verifica se saiu da área visível (coordenadas de mundo → tela)
        tela_x = self.x - camera_x
        return tela_x < -50 or tela_x > LARGURA + 50 or self.y < -50 or self.y > ALTURA + 50

    def desenhar(self, tela, camera_x):
        # Subtrai o camera_x para desenhar na posição correta da tela
        pos_x_tela = self.x - camera_x
        pygame.draw.circle(tela, BRANCO, (int(pos_x_tela), int(self.y)), self.raio)
        pygame.draw.circle(tela, VERMELHO, (int(pos_x_tela), int(self.y)), self.raio - 2)


class Inimigo:
    """Classe base: todo inimigo novo deve herdar dela e sobrescrever atualizar()."""

    dano_contato = True  # encostar no inimigo machuca o jogador?

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
        # Física (usada por quem anda em plataformas)
        self.vel_y = 0
        self.gravidade = 0.5
        self.no_chao = False
        self.camera_x = 0  # o gerenciador atualiza todo frame (pra saber se está visível)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def levar_dano(self, dano=1):
        self.vida -= dano
        if self.vida <= 0:
            self.vivo = False

    def _aplicar_gravidade(self, plataformas):
        """Gravidade + pouso em cima das plataformas (mesma lógica do jogador)."""
        y_antes = self.y + self.altura
        self.vel_y += self.gravidade
        self.y += self.vel_y
        self.no_chao = False

        if self.vel_y < 0:
            return
        for p in plataformas:
            if (y_antes <= p.top
                    and self.y + self.altura >= p.top
                    and self.x + self.largura > p.left
                    and self.x < p.right):
                self.y = p.top - self.altura
                self.vel_y = 0
                self.no_chao = True
                break

    def fora_da_tela(self, camera_x):
        return False

    def atualizar(self, jogador, balas_inimigas, plataformas):
        pass

    def desenhar(self, tela, camera_x):
        # Subtrai o camera_x para desenhar na posição correta da tela
        pos_x_tela = self.x - camera_x
        pygame.draw.rect(tela, self.cor, (pos_x_tela, self.y, self.largura, self.altura))
        # "arma" só pra indicar pra onde o inimigo está olhando
        arma_x = pos_x_tela + self.largura if self.direcao == 1 else pos_x_tela - 12
        pygame.draw.rect(tela, CINZA, (arma_x, self.y + 20, 12, 6))


class Soldado(Inimigo):
    """Soldado vermelho: nasce na borda direita da tela, numa plataforma SUPERIOR,
    e corre pra esquerda. Cai das bordas das plataformas e pula de vez em quando.
    Só se move: NÃO atira."""

    def __init__(self, x, y_chao, direcao=-1):
        super().__init__(x, y_chao - 60, 40, 60, vida=1, cor=VERMELHO, pontos=100)
        self.direcao = direcao
        self.velocidade = 3

    def atualizar(self, jogador, balas_inimigas, plataformas):
        self.x += self.velocidade * self.direcao

        # Pulo aleatório
        if self.no_chao and random.random() < 0.004:
            self.vel_y = -10
            self.no_chao = False

        self._aplicar_gravidade(plataformas)

    def fora_da_tela(self, camera_x):
        # Saiu da área visível por uma margem grande (ou despencou da fase)
        tela_x = self.x - camera_x
        return tela_x < -200 or tela_x > LARGURA + 200 or self.y > ALTURA + 100


class Atirador(Inimigo):
    """Atirador laranja: fica PARADO numa plataforma INFERIOR. Não anda, só vira pro
    jogador e atira mirando nele (apenas enquanto está visível na tela)."""

    def __init__(self, x, y_chao):
        super().__init__(x, y_chao - 60, 40, 60, vida=2, cor=LARANJA, pontos=200)
        self.cooldown = random.randint(40, 90)

    def atualizar(self, jogador, balas_inimigas, plataformas):
        self._aplicar_gravidade(plataformas)  # só assenta na plataforma, não anda

        self.direcao = 1 if jogador.x > self.x else -1

        # Fora da tela ele não atira
        tela_x = self.x - self.camera_x
        if tela_x < 0 or tela_x + self.largura > LARGURA:
            return

        self.cooldown -= 1
        if self.cooldown <= 0:
            origem_x = self.x + self.largura // 2 + self.direcao * (self.largura // 2 + 6)
            origem_y = self.y + 23
            alvo_x = jogador.x + jogador.largura / 2
            alvo_y = jogador.y + jogador.altura / 2
            balas_inimigas.append(BalaInimiga(origem_x, origem_y, alvo_x, alvo_y))
            self.cooldown = random.randint(80, 140)

    def fora_da_tela(self, camera_x):
        tela_x = self.x - camera_x
        return tela_x < -400 or tela_x > LARGURA + 400 or self.y > ALTURA + 100


class Torreta(Inimigo):
    """Torreta que é gerada na frente de uma caixa prateada do cenário quando o jogador
    se aproxima (a distância é controlada pelo GerenciadorInimigos). Ela sai de dentro da
    caixa (desenhada por cima dela), fica vulnerável e passa a atirar mirando no jogador."""

    dano_contato = False
    TEMPO_ABERTURA = 30   # frames pra torreta sair de dentro da caixa
    COMPRIMENTO_CANO = 0.85  # em múltiplos do tamanho da caixa

    def __init__(self, caixa):
        super().__init__(caixa.x, caixa.y, caixa.width, caixa.height,
                         vida=5, cor=CINZA, pontos=500)
        self.estado = "abrindo"  # abrindo -> aberta
        self.timer_abertura = 0
        self.angulo = math.pi
        self.cooldown = 60

    @property
    def centro(self):
        return self.x + self.largura / 2, self.y + self.altura / 2

    def levar_dano(self, dano=1):
        # Enquanto está saindo da caixa ela é invulnerável
        if self.estado == "aberta":
            super().levar_dano(dano)

    def atualizar(self, jogador, balas_inimigas, plataformas):
        cx, cy = self.centro
        alvo_x = jogador.x + jogador.largura / 2
        alvo_y = jogador.y + jogador.altura / 2
        self.angulo = math.atan2(alvo_y - cy, alvo_x - cx)  # o cano segue o jogador

        if self.estado == "abrindo":
            self.timer_abertura += 1
            if self.timer_abertura >= self.TEMPO_ABERTURA:
                self.estado = "aberta"
            return

        # Aberta: só atira enquanto está visível na tela
        tela_x = self.x - self.camera_x
        if tela_x + self.largura < 0 or tela_x > LARGURA:
            return
        self.cooldown -= 1
        if self.cooldown <= 0:
            comp = self.largura * self.COMPRIMENTO_CANO
            ponta_x = cx + math.cos(self.angulo) * comp
            ponta_y = cy + math.sin(self.angulo) * comp
            balas_inimigas.append(BalaInimiga(ponta_x, ponta_y, alvo_x, alvo_y))
            self.cooldown = random.randint(70, 110)

    def desenhar(self, tela, camera_x):
        # A torreta é desenhada POR CIMA do background, na frente da caixa
        lado = self.largura
        cx, cy = self.centro
        cx = int(cx - camera_x)
        cy = int(cy)
        # 0 -> 1 enquanto ela sai da caixa
        prog = 1.0 if self.estado == "aberta" else self.timer_abertura / self.TEMPO_ABERTURA

        escuro = (25, 25, 25)

        # Base: placa que sobe da caixa, cobrindo o painel da frente
        base_w = int(lado * 0.8)
        base_h = max(2, int(lado * 0.7 * prog))
        base = pygame.Rect(0, 0, base_w, base_h)
        base.midbottom = (cx, cy + int(lado * 0.35))
        pygame.draw.rect(tela, (70, 70, 75), base)
        pygame.draw.rect(tela, escuro, base, 3)

        # Cúpula
        raio = max(2, int(lado * 0.32 * prog))
        pygame.draw.circle(tela, CINZA, (cx, cy), raio)
        pygame.draw.circle(tela, escuro, (cx, cy), raio, 3)

        if self.estado == "aberta":
            # Cano apontando pro jogador (sai pra fora da caixa)
            comp = lado * self.COMPRIMENTO_CANO
            ponta = (cx + math.cos(self.angulo) * comp, cy + math.sin(self.angulo) * comp)
            pygame.draw.line(tela, escuro, (cx, cy), ponta, 12)
            pygame.draw.line(tela, (200, 200, 205), (cx, cy), ponta, 7)
            # "Olho" vermelho da cúpula
            pygame.draw.circle(tela, VERMELHO, (cx, cy), max(3, raio // 3))


class GerenciadorInimigos:
    """Cuida de spawn, atualização, colisões e desenho de inimigos e balas inimigas.

    Spawn igual ao do jogo original: nada de spawn aleatório. Cada ponto de spawn é
    fixo numa plataforma e dispara quando a borda direita da câmera chega nele.
    Soldados (vermelhos) saem das plataformas superiores; atiradores (laranjas) ficam
    parados nas inferiores (a posição de cada um é definida em scenario.py).
    As torretas só são geradas quando o jogador chega perto de uma caixa do cenário."""

    DISTANCIA_SPAWN_TORRETA = 700  # px entre o jogador e a caixa pra torreta ser gerada

    def __init__(self, spawns, caixas):
        """spawns: lista de (x, y_topo_da_plataforma, tipo) em coordenadas de mundo.
        caixas: lista de pygame.Rect (em coordenadas de mundo) das caixas das torretas."""
        self.inimigos = []
        # Cada caixa gera a sua torreta uma única vez
        self.caixas = [{"rect": c, "gerada": False} for c in caixas]
        self.balas = []
        self.pontos = 0
        self.camera_x = 0
        self.plataformas = []
        # "armado" = o ponto está fora da tela à direita, esperando a câmera chegar
        self.spawns = [{"x": x, "y": y, "tipo": tipo, "armado": False} for x, y, tipo in spawns]

    def _spawnar(self, spawn):
        x, y = spawn["x"], spawn["y"]
        if spawn["tipo"] == "atirador":
            self.inimigos.append(Atirador(x, y))
        else:
            self.inimigos.append(Soldado(x, y, direcao=-1))

    def _checar_spawns(self, camera_x):
        borda_direita = camera_x + LARGURA
        for s in self.spawns:
            if not s["armado"]:
                # Rearma quando o ponto volta pra fora da tela (ex: jogador voltou)
                if s["x"] > borda_direita + 60:
                    s["armado"] = True
            elif s["x"] <= borda_direita + 5:
                self._spawnar(s)
                s["armado"] = False

    def _checar_torretas(self, jogador):
        jx = jogador.x + jogador.largura / 2
        jy = jogador.y + jogador.altura / 2
        for c in self.caixas:
            if c["gerada"]:
                continue
            caixa = c["rect"]
            if math.hypot(caixa.centerx - jx, caixa.centery - jy) <= self.DISTANCIA_SPAWN_TORRETA:
                self.inimigos.append(Torreta(caixa))
                c["gerada"] = True

    def atualizar(self, jogador, camera_x=0, plataformas=()):
        self.camera_x = camera_x
        self.plataformas = plataformas

        self._checar_spawns(camera_x)
        self._checar_torretas(jogador)

        # Atualiza inimigos e balas
        for inimigo in self.inimigos:
            inimigo.camera_x = camera_x
            inimigo.atualizar(jogador, self.balas, plataformas)
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
            if inimigo.dano_contato and inimigo.vivo and inimigo.rect.colliderect(jogador.rect):
                jogador.levar_dano()

        for bala in self.balas[:]:
            if bala.rect.colliderect(jogador.rect):
                jogador.levar_dano()
                self.balas.remove(bala)

        # Limpeza
        self.inimigos = [i for i in self.inimigos if i.vivo and not i.fora_da_tela(camera_x)]
        self.balas = [b for b in self.balas if not b.fora_da_tela(camera_x)]

    def desenhar(self, tela, camera_x):
        for inimigo in self.inimigos:
            inimigo.desenhar(tela, camera_x)
        for bala in self.balas:
            bala.desenhar(tela, camera_x)