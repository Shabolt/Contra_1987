import random
import pygame
from constants import ALTURA, CHANCE_POWERUP_CAIXA, DEBUG, LARGURA
from animations import SpriteManager
from sound import SoundManager


def _escalar(img, escala):
    """Escala o sprite pelo mesmo fator do cenário (pixel art, sem suavizar)."""
    w = max(1, round(img.get_width() * escala))
    h = max(1, round(img.get_height() * escala))
    return pygame.transform.scale(img, (w, h))


def _sprite_fallback(tipo, escala):
    """Ícone provisório caso power1.png / power2.png não sejam encontrados."""
    surf = pygame.Surface((round(22 * escala), round(20 * escala)))
    surf.fill((255, 140, 0) if tipo == "H" else (0, 200, 80))
    pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 3)
    letra = pygame.font.Font(None, int(surf.get_height() * 0.9)).render(tipo, True, (255, 255, 255))
    surf.blit(letra, letra.get_rect(center=surf.get_rect().center))
    return surf


class CaixaPowerUp:
    """Caixa do cenário: ao ser acertada explode e pode soltar um power-up."""
    FRAMES_POR_SPRITE = 8  # quanto tempo cada frame da explosão fica na tela

    def __init__(self, rect, escala):
        SpriteManager.carregar_tudo()
        self.rect = rect
        self.vida = 1
        self.ativa = True        # ainda não foi destruída
        self.timer = 0
        self.frames = [_escalar(f, escala) for f in SpriteManager.frames_explosao_caixa]
        self.duracao = max(1, len(self.frames)) * self.FRAMES_POR_SPRITE

    @property
    def terminou(self):
        return not self.ativa and self.timer >= self.duracao

    def levar_dano(self):
        """Retorna True no tiro que destrói a caixa."""
        if not self.ativa:
            return False
        self.vida -= 1
        if self.vida <= 0:
            self.ativa = False
            self.timer = 0
            SoundManager.tocar_destruicao()
            return True
        return False

    def atualizar(self):
        if not self.ativa:
            self.timer += 1

    def desenhar(self, tela, camera_x):
        if self.ativa:
            if DEBUG:
                pygame.draw.rect(tela, (255, 0, 255), self.rect.move(-camera_x, 0), 2)
            return
        centro = (self.rect.centerx - camera_x, self.rect.centery)
        if self.frames:
            idx = min(self.timer // self.FRAMES_POR_SPRITE, len(self.frames) - 1)
            img = self.frames[idx]
            tela.blit(img, img.get_rect(center=centro))
        else:
            raio = int(self.rect.width * (0.5 + self.timer / self.duracao))
            pygame.draw.circle(tela, (255, 140, 0), centro, raio)


class ItemPowerUp:
    """Ícone H ou S que pula da caixa, cai nas plataformas e é coletado ao encostar."""

    def __init__(self, centro_x, centro_y, tipo, escala):
        SpriteManager.carregar_tudo()
        self.tipo = tipo
        img = SpriteManager.sprite_power_h if tipo == "H" else SpriteManager.sprite_power_s
        self.img = _escalar(img, escala) if img is not None else _sprite_fallback(tipo, escala)
        self.largura = self.img.get_width()
        self.altura = self.img.get_height()
        self.x = centro_x - self.largura / 2
        self.y = centro_y - self.altura / 2
        self.vel_y = -9.0   # pulinho ao sair da caixa
        self.gravidade = 0.5
        self.no_chao = False
        self.vivo = True

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def atualizar(self, plataformas):
        y_antes = self.y + self.altura
        self.vel_y += self.gravidade
        self.y += self.vel_y
        self.no_chao = False

        if self.vel_y >= 0:
            for p in plataformas:
                if (y_antes <= p.top
                        and self.y + self.altura >= p.top
                        and self.x + self.largura > p.left
                        and self.x < p.right):
                    self.y = p.top - self.altura
                    self.vel_y = 0
                    self.no_chao = True
                    break

        if self.y > ALTURA + 100:
            self.vivo = False

    def desenhar(self, tela, camera_x):
        tela.blit(self.img, (int(self.x - camera_x), int(self.y)))


class GerenciadorPowerUps:
    TIPOS = ("H", "S")

    def __init__(self, caixas, escala=1.0):
        self.escala = escala
        self.caixas = [CaixaPowerUp(c, escala) for c in caixas]
        self.itens = []

    def _soltar_item(self, caixa):
        if random.random() <= CHANCE_POWERUP_CAIXA:
            tipo = random.choice(self.TIPOS)
            self.itens.append(ItemPowerUp(caixa.rect.centerx, caixa.rect.centery, tipo, self.escala))

    def atualizar(self, jogador, camera_x, plataformas):
        for caixa in self.caixas:
            caixa.atualizar()

        # Tiros do jogador x caixas (só vale se a caixa estiver visível na tela)
        for tiro in jogador.tiros[:]:
            for caixa in self.caixas:
                if not caixa.ativa:
                    continue
                if caixa.rect.right < camera_x or caixa.rect.left > camera_x + LARGURA:
                    continue
                if tiro.rect.colliderect(caixa.rect):
                    if tiro in jogador.tiros:
                        jogador.tiros.remove(tiro)
                    if caixa.levar_dano():
                        self._soltar_item(caixa)
                    break

        # Itens caindo / sendo coletados
        for item in self.itens:
            item.atualizar(plataformas)
            if item.vivo and item.rect.colliderect(jogador.rect):
                jogador.pegar_powerup(item.tipo)
                item.vivo = False

        self.caixas = [c for c in self.caixas if not c.terminou]
        self.itens = [i for i in self.itens if i.vivo]

    def desenhar(self, tela, camera_x):
        for caixa in self.caixas:
            caixa.desenhar(tela, camera_x)
        for item in self.itens:
            item.desenhar(tela, camera_x)
