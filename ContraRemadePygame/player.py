import math
import pygame
from constants import (ALTURA, BRANCO, COOLDOWN_TIRO_H, COOLDOWN_TIRO_NORMAL, LARGURA,
                       S_ALCANCE, S_ANGULOS, VERMELHO)
from animations import SpriteManager
from sound import SoundManager

class Tiro:
    def __init__(self, x, y, direcao_x, direcao_y=0, alcance=None):
        self.x = x
        self.y = y
        self.velocidade = 12
        self.alcance = alcance  # None = sem limite; número = distância máxima em px
        self.percorrido = 0.0
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
        self.percorrido += self.velocidade
        self.frame_anim += 0.3

    def fora_da_tela(self, camera_x):
        if self.alcance is not None and self.percorrido >= self.alcance:
            return True
        return self.x < -10000 or self.x > 20000 or self.y < -2000 or self.y > ALTURA + 2000

    def desenhar(self, tela, camera_x):
        pos_x_tela = self.x - camera_x
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
        self.largura_normal = 40
        self.altura_normal = 60
        self.largura = self.largura_normal
        self.altura = self.altura_normal
        self.vel_x = 0
        self.vel_y = 0
        self.gravidade = 0.50  
        self.no_chao = False
        self.vidas = 3
        self.direcao = 1  # 1 para direita, -1 para esquerda
        self.deitado = False
        self.descendo = 0
        self.invencivel = 0
        self.pulando = False

        # Power-ups coletados nas caixas
        self.cadencia_rapida = False   # H
        self.tiro_espalhado = False    # S

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
        if self.invencivel > 0:
            return
        self.vidas -= 1
        self.invencivel = 120
        SoundManager.parar_passos()

    def pegar_powerup(self, tipo):
        if tipo == "H":
            self.cadencia_rapida = True
        elif tipo == "S":
            self.tiro_espalhado = True
        SoundManager.tocar_powerup()

    def atirar(self, teclas):
        # Enquanto estiver no ar / ação de pular executada, não pode atirar
        if self.cooldown_tiro > 0 or not self.no_chao or self.pulando:
            return

        cima = teclas[pygame.K_UP] or teclas[pygame.K_w]
        baixo = teclas[pygame.K_DOWN] or teclas[pygame.K_s]
        esquerda = teclas[pygame.K_LEFT] or teclas[pygame.K_a]
        direita = teclas[pygame.K_RIGHT] or teclas[pygame.K_d]

        dir_h = 0
        if direita and not esquerda:
            dir_h = 1
        elif esquerda and not direita:
            dir_h = -1

        dir_v = 0
        if cima and not baixo:
            dir_v = -1
        elif baixo and not cima:
            dir_v = 1

        fator_diag = 0.7071
        dx = float(self.direcao)
        dy = 0.0

        if self.deitado:
            # Agachado / deitado: tiro sempre horizontal para a frente, sem mudar de direção
            dx = float(self.direcao)
            dy = 0.0
        elif dir_v == -1:  # Mirando para cima (W)
            if dir_h != 0:
                # Diagonal para cima (Ctrl + W + D ou Ctrl + W + A)
                dx = dir_h * fator_diag
                dy = -fator_diag
                self.direcao = dir_h
            else:
                # Apenas para cima (Ctrl + W)
                dx = 0.0
                dy = -1.0
        elif dir_v == 1:  # Mirando para baixo (S)
            if dir_h != 0:
                # Diagonal para baixo apenas se pressionar Ctrl + S + D ou Ctrl + S + A
                dx = dir_h * fator_diag
                dy = fator_diag
                self.direcao = dir_h
            elif not self.no_chao:
                # No ar sem A/D: atira reto para baixo
                dx = 0.0
                dy = 1.0
            else:
                # No chão com S sem A/D: atira horizontalmente para a frente (NUNCA diagonal)
                dx = float(self.direcao)
                dy = 0.0
        else:  # Sem W e sem S
            if dir_h != 0:
                dx = float(dir_h)
                dy = 0.0
                self.direcao = dir_h
            else:
                dx = float(self.direcao)
                dy = 0.0

        if self.deitado:
            origem_x = self.x + self.largura if self.direcao == 1 else self.x
            origem_y = self.y + self.altura - 12
        else:
            origem_x = self.x + self.largura // 2 + (dx * 22)
            origem_y = self.y + self.altura // 2 + (dy * 22)

        if self.tiro_espalhado:
            # Power-up S: 5 projéteis abertos em leque, com alcance curto
            for ang in S_ANGULOS:
                rad = math.radians(ang)
                c, sn = math.cos(rad), math.sin(rad)
                self.tiros.append(Tiro(origem_x, origem_y, dx * c - dy * sn, dx * sn + dy * c, alcance=S_ALCANCE))
        else:
            self.tiros.append(Tiro(origem_x, origem_y, dx, dy))

        SoundManager.tocar_tiro_player()

        # Power-up H: só acelera a cadência
        self.cooldown_tiro = COOLDOWN_TIRO_H if self.cadencia_rapida else COOLDOWN_TIRO_NORMAL

    def atualizar(self, teclas, plataformas):
        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= 1

        if self.invencivel > 0:
            self.invencivel -= 1

        if self.descendo > 0:
            self.descendo -= 1

        alt_pressionado = teclas[pygame.K_LALT] or teclas[pygame.K_RALT]
        baixo_pressionado = teclas[pygame.K_DOWN] or teclas[pygame.K_s]
        velocidade_movimento = 4.2

        # 1. Descer da plataforma com Alt + S
        if alt_pressionado and baixo_pressionado and self.no_chao:
            self.descendo = 15
            self.no_chao = False
            self.pulando = False
            self.vel_x = 0
            self.y += 6
            self.vel_y = 2.0
            if self.deitado:
                self.deitado = False
                self.altura = self.altura_normal
                self.largura = self.largura_normal

        # 2. Agachar / Deitar com Alt (sem estar descendo)
        elif alt_pressionado and self.no_chao:
            if not self.deitado:
                self.deitado = True
                self.altura = 30
                self.largura = 70
                self.y += (self.altura_normal - self.altura)  # Desce 30px mantendo pés na plataforma
        else:
            if self.deitado:
                self.deitado = False
                self.y -= (self.altura_normal - self.altura)  # Sobe 30px restaurando altura normal
                self.altura = self.altura_normal
                self.largura = self.largura_normal

        # 3. Pulo com Barra de Espaço
        # Ao pular, o personagem avança para frente sem parar, como no jogo original
        if teclas[pygame.K_SPACE] and self.no_chao:
            if self.deitado:
                self.deitado = False
                self.y -= (self.altura_normal - self.altura)
                self.altura = self.altura_normal
                self.largura = self.largura_normal

            # Define a direção do pulo (se pressionar A/D no chão, atualiza a direção antes de saltar)
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                self.direcao = -1
            elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                self.direcao = 1

            # Impulso do salto para frente
            self.vel_x = self.direcao * velocidade_movimento
            self.vel_y = -16.5
            self.no_chao = False
            self.pulando = True
            self.pulo_frame_idx = 0.0

        # 4. Movimento Horizontal
        if self.no_chao:
            self.pulando = False
            self.movendo_flag = False
            self.vel_x = 0

            if not self.deitado:
                if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                    self.vel_x = -velocidade_movimento
                    self.direcao = -1
                    self.movendo_flag = True
                elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                    self.vel_x = velocidade_movimento
                    self.direcao = 1
                    self.movendo_flag = True
            else:
                # Enquanto estiver agachado, NÃO pode mudar a direção do personagem nem andar
                pass
        else:
            # No ar (ação de pular executada): continua indo para frente sem parar
            # As teclas de direção não alteram a direção nem cancelam o impulso do pulo no ar
            pass

        self.x += self.vel_x
        if self.x < 0:
            self.x = 0

        # 5. Tiro (Ctrl / Z / X)
        # Enquanto estiver no ar / pulando, NÃO é possível atirar
        atirando_pressionado = (teclas[pygame.K_z] or teclas[pygame.K_x] or teclas[pygame.K_RCTRL] or teclas[pygame.K_LCTRL])
        if atirando_pressionado and self.no_chao and not self.pulando:
            self.atirar(teclas)

        # 6. Gravidade e colisão com plataformas
        y_antes = self.y + self.altura
        self.vel_y += self.gravidade
        self.y += self.vel_y
        self.no_chao = False

        if self.vel_y >= 0 and self.descendo == 0:
            for p in plataformas:
                if (y_antes <= p.top + 6
                        and self.y + self.altura >= p.top
                        and self.x + self.largura > p.left + 5
                        and self.x < p.right - 5):
                    self.y = p.top - self.altura
                    self.vel_y = 0
                    self.no_chao = True
                    self.pulando = False
                    break

        # 7. Avanço dos frames de animação
        if not self.no_chao:
            self.pulo_frame_idx += 0.25
        else:
            self.pulo_frame_idx = 0.0

        if self.movendo_flag or (atirando_pressionado and self.no_chao):
            self.frame_idx += 0.25
        else:
            self.frame_idx = 0.0

        # Efeito sonoro de passos ao andar no chão
        if self.no_chao and self.vel_x != 0 and not self.deitado:
            SoundManager.iniciar_passos()
        else:
            SoundManager.parar_passos()

        # 8. Atualização dos tiros
        for tiro in self.tiros[:]:
            tiro.atualizar()
            if tiro.fora_da_tela(0):
                self.tiros.remove(tiro)

    def desenhar(self, tela, camera_x):
        pos_x_tela = self.x - camera_x
        teclas = pygame.key.get_pressed()

        # Invencibilidade piscando
        if self.invencivel > 0 and (self.invencivel // 5) % 2 == 1:
            for tiro in self.tiros:
                tiro.desenhar(tela, camera_x)
            return

        atirando = (self.cooldown_tiro > 0 or teclas[pygame.K_z] or teclas[pygame.K_x] or teclas[pygame.K_RCTRL] or teclas[pygame.K_LCTRL])
        lista = None

        if not self.no_chao:
            lista = SpriteManager.frames_pulo_d if self.direcao == 1 else SpriteManager.frames_pulo_e
        elif self.deitado:
            lista = SpriteManager.frames_deitado_d if self.direcao == 1 else SpriteManager.frames_deitado_e
        else:
            cima = teclas[pygame.K_UP] or teclas[pygame.K_w]
            baixo = teclas[pygame.K_DOWN] or teclas[pygame.K_s]
            esquerda = teclas[pygame.K_LEFT] or teclas[pygame.K_a]
            direita = teclas[pygame.K_RIGHT] or teclas[pygame.K_d]

            dir_h = 1 if (direita and not esquerda) else (-1 if (esquerda and not direita) else 0)

            if cima and not baixo:
                if dir_h != 0 or atirando:
                    lista = SpriteManager.frames_and_ccd if self.direcao == 1 else SpriteManager.frames_and_cce
                else:
                    lista = SpriteManager.frames_mira_cima_d if self.direcao == 1 else SpriteManager.frames_mira_cima_e
            elif baixo and not cima and dir_h != 0:
                # Diagonal para baixo ao correr/mirar com S + D ou S + A
                lista = SpriteManager.frames_and_bd if self.direcao == 1 else SpriteManager.frames_and_be
            else:
                if atirando:
                    lista = SpriteManager.frames_and_cd if self.direcao == 1 else SpriteManager.frames_and_ce
                elif self.vel_x != 0:
                    lista = SpriteManager.frames_andando_d if self.direcao == 1 else SpriteManager.frames_andando_e
                else:
                    lista = SpriteManager.frames_jogador_parado_d if self.direcao == 1 else SpriteManager.frames_jogador_parado_e

        if lista:
            idx = int(self.pulo_frame_idx) if not self.no_chao else int(self.frame_idx)
            img = lista[idx % len(lista)]
            rect_sprite = img.get_rect()
            if not self.no_chao:
                rect_sprite.center = (int(pos_x_tela + self.largura // 2), int(self.y + self.altura // 2))
            else:
                rect_sprite.midbottom = (int(pos_x_tela + self.largura // 2), int(self.y + self.altura))
            tela.blit(img, rect_sprite)
        else:
            pygame.draw.rect(tela, VERMELHO, (pos_x_tela, self.y, self.largura, self.altura))

        for tiro in self.tiros:
            tiro.desenhar(tela, camera_x)