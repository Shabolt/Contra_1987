import math
import random
import pygame
from constants import ALTURA, BRANCO, CINZA, LARANJA, LARGURA, VERMELHO
from animations import SpriteManager

class BalaInimiga:
    def __init__(self, x, y, alvo_x, alvo_y):
        self.x = x
        self.y = y
        self.raio = 7
        velocidade = 3.2  # Velocidade clássica dos tiros inimigos no NES
        dx = alvo_x - x
        dy = alvo_y - y
        distancia = math.hypot(dx, dy) or 1
        self.vel_x = dx / distancia * velocidade
        self.vel_y = dy / distancia * velocidade
        self.frame_anim = 0.0

    @property
    def rect(self):
        return pygame.Rect(self.x - self.raio, self.y - self.raio, self.raio * 2, self.raio * 2)

    def atualizar(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.frame_anim += 0.2

    def fora_da_tela(self, camera_x):
        tela_x = self.x - camera_x
        return tela_x < -100 or tela_x > LARGURA + 100 or self.y < -100 or self.y > ALTURA + 100

    def desenhar(self, tela, camera_x):
        pos_x_tela = self.x - camera_x
        # Usa explo1 (frames_tiro_inimigo) para o tiro dos inimigos (conforme solicitado nas imagens)
        imgs = SpriteManager.frames_tiro_inimigo if hasattr(SpriteManager, 'frames_tiro_inimigo') and SpriteManager.frames_tiro_inimigo else []
        if imgs:
            img = imgs[int(self.frame_anim) % len(imgs)]
            tam = 18
            tela.blit(pygame.transform.scale(img, (tam, tam)), (int(pos_x_tela - tam//2), int(self.y - tam//2)))
        else:
            pygame.draw.circle(tela, BRANCO, (int(pos_x_tela), int(self.y)), self.raio)
            pygame.draw.circle(tela, VERMELHO, (int(pos_x_tela), int(self.y)), self.raio - 2)


class Inimigo:
    dano_contato = True

    def __init__(self, x, y, largura, altura, vida, cor, pontos):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.vida = vida
        self.cor = cor
        self.pontos = pontos
        self.direcao = -1
        self.vivo = True
        self.vel_y = 0
        self.gravidade = 0.55
        self.no_chao = False
        self.camera_x = 0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def levar_dano(self, dano=1):
        self.vida -= dano
        if self.vida <= 0:
            self.vivo = False

    def _aplicar_gravidade(self, plataformas):
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
        pos_x_tela = self.x - camera_x
        pygame.draw.rect(tela, self.cor, (pos_x_tela, self.y, self.largura, self.altura))


class Soldado(Inimigo):
    def __init__(self, x, y_chao, direcao=-1):
        super().__init__(x, y_chao - 60, 40, 60, vida=1, cor=VERMELHO, pontos=100)
        self.direcao = direcao
        self.velocidade = 2.2
        self.frame_idx = 0.0
        SpriteManager.carregar_tudo()

    def atualizar(self, jogador, balas_inimigas, plataformas):
        self.x += self.velocidade * self.direcao
        self.frame_idx += 0.12
        if self.no_chao and random.random() < 0.003:
            self.vel_y = -9.5
            self.no_chao = False
        self._aplicar_gravidade(plataformas)

    def fora_da_tela(self, camera_x):
        tela_x = self.x - camera_x
        return tela_x < -200 or tela_x > LARGURA + 200 or self.y > ALTURA + 100

    def desenhar(self, tela, camera_x):
        pos_x_tela = self.x - camera_x
        lista = SpriteManager.frames_soldado_d if self.direcao == 1 else SpriteManager.frames_soldado_e
        if lista:
            img = lista[int(self.frame_idx) % len(lista)]
            tela.blit(pygame.transform.scale(img, (self.largura, self.altura)), (pos_x_tela, self.y))
        else:
            pygame.draw.rect(tela, self.cor, (pos_x_tela, self.y, self.largura, self.altura))


class Atirador(Inimigo):
    def __init__(self, x, y_chao):
        super().__init__(x, y_chao - 60, 40, 60, vida=2, cor=LARANJA, pontos=200)
        self.cooldown = random.randint(80, 140)
        self.estado_pose = "pe"
        self.timer_pose = 0
        SpriteManager.carregar_tudo()

    def atualizar(self, jogador, balas_inimigas, plataformas):
        self._aplicar_gravidade(plataformas)
        self.direcao = 1 if jogador.x > self.x else -1

        self.timer_pose -= 1
        if self.timer_pose <= 0:
            escolha = random.choice(["pe", "agachado", "cima"])
            self.estado_pose = escolha
            self.timer_pose = random.randint(60, 110)

        self.cooldown -= 1
        if self.cooldown <= 0:
            origem_x = self.x + self.largura // 2 + self.direcao * 20
            origem_y = self.y + 25 if self.estado_pose != "cima" else self.y + 5
            alvo_x = jogador.x + jogador.largura / 2
            alvo_y = jogador.y + jogador.altura / 2
            balas_inimigas.append(BalaInimiga(origem_x, origem_y, alvo_x, alvo_y))
            self.cooldown = random.randint(90, 150)

    def fora_da_tela(self, camera_x):
        tela_x = self.x - camera_x
        return tela_x < -400 or tela_x > LARGURA + 400 or self.y > ALTURA + 100

    def desenhar(self, tela, camera_x):
        pos_x_tela = self.x - camera_x
        
        if self.estado_pose == "agachado":
            lista = SpriteManager.frames_atirador_agachado_d if self.direcao == 1 else SpriteManager.frames_atirador_agachado_e
        elif self.estado_pose == "cima":
            lista = SpriteManager.frames_atirador_cima_d if self.direcao == 1 else SpriteManager.frames_atirador_cima_e
        else:
            lista = SpriteManager.frames_atirador_pe_d if self.direcao == 1 else SpriteManager.frames_atirador_pe_e

        if lista:
            img = lista[0]
            tela.blit(pygame.transform.scale(img, (self.largura, self.altura)), (pos_x_tela, self.y))
        else:
            pygame.draw.rect(tela, self.cor, (pos_x_tela, self.y, self.largura, self.altura))


class Torreta(Inimigo):
    dano_contato = False
    COMPRIMENTO_CANO = 0.85

    def __init__(self, caixa):
        super().__init__(caixa.x, caixa.y, caixa.width, caixa.height, vida=5, cor=CINZA, pontos=500)
        self.angulo = math.pi
        self.cooldown = 70
        self.anim_timer = 0.0
        SpriteManager.carregar_tudo()

    @property
    def centro(self):
        return self.x + self.largura / 2, self.y + self.altura / 2

    def levar_dano(self, dano=1):
        super().levar_dano(dano)

    def atualizar(self, jogador, balas_inimigas, plataformas):
        cx, cy = self.centro
        alvo_x = jogador.x + jogador.largura / 2
        alvo_y = jogador.y + jogador.altura / 2
        self.angulo = math.atan2(alvo_y - cy, alvo_x - cx)

        self.cooldown -= 1
        if self.cooldown <= 0:
            comp = self.largura * self.COMPRIMENTO_CANO
            ponta_x = cx + math.cos(self.angulo) * comp
            ponta_y = cy + math.sin(self.angulo) * comp
            balas_inimigas.append(BalaInimiga(ponta_x, ponta_y, alvo_x, alvo_y))
            self.cooldown = random.randint(70, 110)
            self.anim_timer = 12

        if self.anim_timer > 0:
            self.anim_timer -= 1

    def desenhar(self, tela, camera_x):
        lado = self.largura
        cx, cy = self.centro
        px = int(cx - camera_x - lado // 2)
        py = int(cy - lado // 2)

        deg = math.degrees(self.angulo)
        is_firing = self.anim_timer > 0
        
        if -90 <= deg <= 90:
            if deg < -30:
                nome_sprite = "torret_DB2" if is_firing else "torret_DB"
            elif deg > 30:
                nome_sprite = "torret_DC2" if is_firing else "torret_DC"
            else:
                nome_sprite = "torret_C" if is_firing else "torret_B"
        else:
            if -150 <= deg < -90:
                nome_sprite = "torret_EB2" if is_firing else "torret_EB"
            elif 90 < deg <= 150:
                nome_sprite = "torret_EC2" if is_firing else "torret_EC"
            else:
                nome_sprite = "torret_EC2" if is_firing else "torret_EB"

        sprite_dict = SpriteManager.torretas_sprites
        img_t = sprite_dict.get(nome_sprite) or sprite_dict.get("torret_B") or (list(sprite_dict.values())[0] if sprite_dict else None)

        if img_t:
            tela.blit(pygame.transform.scale(img_t, (lado, lado)), (px, py))
        else:
            pygame.draw.rect(tela, self.cor, (px, py, lado, lado))


class GerenciadorInimigos:
    DISTANCIA_SPAWN_TORRETA = 900

    def __init__(self, spawns, caixas):
        self.inimigos = []
        self.caixas = [{"rect": c, "gerada": False} for c in caixas]
        self.balas = []
        self.pontos = 0
        self.camera_x = 0
        self.plataformas = []
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
                if s["x"] > borda_direita + 100:
                    s["armado"] = True
            elif s["x"] <= borda_direita + 20:
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

        for inimigo in self.inimigos:
            inimigo.camera_x = camera_x
            inimigo.atualizar(jogador, self.balas, plataformas)
        for bala in self.balas:
            bala.atualizar()

        for tiro in jogador.tiros[:]:
            for inimigo in self.inimigos:
                if inimigo.vivo and tiro.rect.colliderect(inimigo.rect):
                    inimigo.levar_dano()
                    if tiro in jogador.tiros:
                        jogador.tiros.remove(tiro)
                    if not inimigo.vivo:
                        self.pontos += inimigo.pontos
                    break

        for inimigo in self.inimigos:
            if inimigo.dano_contato and inimigo.vivo and inimigo.rect.colliderect(jogador.rect):
                jogador.levar_dano()

        for bala in self.balas[:]:
            if bala.rect.colliderect(jogador.rect):
                jogador.levar_dano()
                if bala in self.balas:
                    self.balas.remove(bala)

        self.inimigos = [i for i in self.inimigos if i.vivo and not i.fora_da_tela(camera_x)]
        self.balas = [b for b in self.balas if not b.fora_da_tela(camera_x)]

    def desenhar(self, tela, camera_x):
        for inimigo in self.inimigos:
            inimigo.desenhar(tela, camera_x)
        for bala in self.balas:
            bala.desenhar(tela, camera_x)
