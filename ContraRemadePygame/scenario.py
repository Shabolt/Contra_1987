"""
Cenário pixel-art estilo Contra (Jungle / Stage 1).
Gera uma superfície de fundo estática (desenhada uma vez) e exporta:
  - Cenario.desenhar(tela, camera_x)  → desenha o fundo com parallax
  - Cenario.plataformas              → lista de pygame.Rect para colisão
"""

import random

import pygame
from constants import ALTURA, CHAO_Y, LARGURA

# ──────────────────────── paleta pixel-art ────────────────────────
COR_CEU_TOPO = (10, 5, 30)       # azul escuro / noite
COR_CEU_BASE = (40, 25, 80)      # roxo escuro
COR_ESTRELA = (255, 255, 200)

COR_MONTANHA_1 = (20, 30, 45)    # montanha distante
COR_MONTANHA_2 = (30, 45, 55)    # montanha média

COR_ARVORE_TRONCO = (55, 35, 20)
COR_ARVORE_COPA = (15, 65, 15)
COR_ARVORE_COPA_CLARA = (30, 90, 25)
COR_ARVORE_COPA_ESCURA = (10, 45, 10)

COR_CHAO_TOPO = (50, 100, 30)     # grama
COR_CHAO_TERRA = (80, 55, 30)     # terra
COR_CHAO_TERRA_ESCURA = (60, 40, 20)
COR_CHAO_PEDRA = (90, 85, 75)

COR_PLATAFORMA = (75, 60, 40)
COR_PLATAFORMA_BORDA = (100, 80, 55)

COR_AGUA = (20, 60, 120)
COR_AGUA_BRILHO = (60, 120, 180)

COR_FOLHA = (20, 80, 20)
COR_FOLHA_CLARA = (50, 130, 40)
COR_FLOR = (200, 50, 50)
COR_FLOR2 = (220, 180, 40)

COR_CERCA = (90, 65, 35)
COR_CERCA_ESCURA = (65, 45, 25)


# ───────────────────── helpers de pixel-art ─────────────────────

def _pixel(surf, x, y, cor, tamanho=4):
    """Desenha um 'pixel' grande (bloco 4×4 por padrão)."""
    pygame.draw.rect(surf, cor, (x, y, tamanho, tamanho))


def _gradiente_vertical(surf, rect, cor_topo, cor_base):
    """Preenche um retângulo com gradiente vertical."""
    x, y, w, h = rect
    for fila in range(h):
        t = fila / max(h - 1, 1)
        r = int(cor_topo[0] + (cor_base[0] - cor_topo[0]) * t)
        g = int(cor_topo[1] + (cor_base[1] - cor_topo[1]) * t)
        b = int(cor_topo[2] + (cor_base[2] - cor_topo[2]) * t)
        pygame.draw.line(surf, (r, g, b), (x, y + fila), (x + w - 1, y + fila))


def _desenhar_montanha(surf, base_x, base_y, largura, altura, cor):
    """Montanha triangular com contorno pixel-art."""
    pico_x = base_x + largura // 2
    pontos = [
        (base_x, base_y),
        (pico_x, base_y - altura),
        (base_x + largura, base_y),
    ]
    pygame.draw.polygon(surf, cor, pontos)
    # neve no pico
    neve_h = altura // 5
    pontos_neve = [
        (pico_x - largura // 8, base_y - altura + neve_h),
        (pico_x, base_y - altura),
        (pico_x + largura // 8, base_y - altura + neve_h),
    ]
    cor_neve = tuple(min(c + 80, 255) for c in cor)
    pygame.draw.polygon(surf, cor_neve, pontos_neve)


def _desenhar_arvore(surf, x, base_y, escala=1.0, seed=0):
    """Árvore de selva com tronco e copa estilo pixel-art."""
    rng = random.Random(seed)
    h_tronco = int(rng.randint(80, 140) * escala)
    w_tronco = int(rng.randint(14, 22) * escala)
    y_tronco = base_y - h_tronco

    # tronco
    pygame.draw.rect(surf, COR_ARVORE_TRONCO, (x - w_tronco // 2, y_tronco, w_tronco, h_tronco))
    # textura no tronco
    for i in range(3):
        ty = y_tronco + rng.randint(10, h_tronco - 10)
        tw = rng.randint(4, w_tronco - 4)
        tx = x - tw // 2
        pygame.draw.rect(surf, (40, 25, 15), (tx, ty, tw, 3))

    # copa (vários círculos sobrepostos)
    r_copa = int(rng.randint(40, 70) * escala)
    centros = [
        (x, y_tronco - r_copa // 2),
        (x - r_copa // 2, y_tronco + 5),
        (x + r_copa // 2, y_tronco + 5),
        (x, y_tronco - r_copa),
        (x - r_copa // 3, y_tronco - r_copa * 2 // 3),
        (x + r_copa // 3, y_tronco - r_copa * 2 // 3),
    ]
    for cx, cy in centros:
        cor = rng.choice([COR_ARVORE_COPA, COR_ARVORE_COPA_CLARA, COR_ARVORE_COPA_ESCURA])
        raio = rng.randint(int(r_copa * 0.5), int(r_copa * 0.8))
        pygame.draw.circle(surf, cor, (cx, cy), raio)

    # detalhes de folhas (pixels soltos na copa)
    for _ in range(int(12 * escala)):
        fx = x + rng.randint(-r_copa, r_copa)
        fy = y_tronco - rng.randint(0, int(r_copa * 1.6))
        cor_f = rng.choice([COR_FOLHA, COR_FOLHA_CLARA])
        _pixel(surf, fx, fy, cor_f, 4)


def _desenhar_arbusto(surf, x, base_y, seed=0):
    """Arbusto/moita decorativa."""
    rng = random.Random(seed)
    w = rng.randint(30, 55)
    h = rng.randint(18, 30)
    for i in range(5):
        cx = x + rng.randint(-w // 2, w // 2)
        cy = base_y - rng.randint(h // 3, h)
        raio = rng.randint(10, 20)
        cor = rng.choice([COR_ARVORE_COPA, COR_ARVORE_COPA_ESCURA, COR_FOLHA])
        pygame.draw.circle(surf, cor, (cx, cy), raio)
    # florzinha eventual
    if rng.random() < 0.4:
        cor = rng.choice([COR_FLOR, COR_FLOR2])
        _pixel(surf, x + rng.randint(-8, 8), base_y - h + 4, cor, 5)


def _desenhar_cerca(surf, x, base_y, comprimento, seed=0):
    """Cerca de madeira decorativa, encostada no chão."""
    rng = random.Random(seed)
    h_estaca = rng.randint(35, 50)
    espaco = 22
    n_estacas = comprimento // espaco

    # barra horizontal
    pygame.draw.rect(surf, COR_CERCA, (x, base_y - h_estaca + 10, comprimento, 6))
    pygame.draw.rect(surf, COR_CERCA, (x, base_y - h_estaca // 2, comprimento, 6))

    for i in range(n_estacas + 1):
        ex = x + i * espaco
        # ponta triangular
        pontos = [
            (ex, base_y - h_estaca - 8),
            (ex - 5, base_y - h_estaca),
            (ex + 5, base_y - h_estaca),
        ]
        pygame.draw.polygon(surf, COR_CERCA, pontos)
        pygame.draw.rect(surf, COR_CERCA, (ex - 5, base_y - h_estaca, 10, h_estaca))
        # sombra
        pygame.draw.rect(surf, COR_CERCA_ESCURA, (ex - 5, base_y - h_estaca, 2, h_estaca))


def _desenhar_agua(surf, x, y, w, h, seed=0):
    """Poça/rio decorativo."""
    rng = random.Random(seed)
    pygame.draw.rect(surf, COR_AGUA, (x, y, w, h))
    # brilhos
    for _ in range(w // 12):
        bx = x + rng.randint(4, w - 8)
        by = y + rng.randint(2, max(3, h - 6))
        bw = rng.randint(8, 20)
        pygame.draw.rect(surf, COR_AGUA_BRILHO, (bx, by, bw, 2))


def _desenhar_pedras(surf, base_y, largura_total, seed=0):
    """Pedras espalhadas pelo chão."""
    rng = random.Random(seed)
    for _ in range(largura_total // 100):
        px = rng.randint(0, largura_total)
        py = base_y + rng.randint(5, 40)
        pw = rng.randint(10, 25)
        ph = rng.randint(6, 14)
        cor = rng.choice([COR_CHAO_PEDRA, (110, 105, 95), (70, 65, 55)])
        pygame.draw.ellipse(surf, cor, (px, py, pw, ph))


# ═══════════════════════ classe principal ═══════════════════════

class Cenario:
    """Cenário Jungle pixel-art para Contra."""

    def __init__(self, seed=42):
        self.rng = random.Random(seed)

        # Largura total do nível (pode ser > LARGURA para scrolling futuro)
        self.largura_total = LARGURA

        # ─── superfícies pré-renderizadas ───
        self.camada_ceu = self._criar_ceu()
        self.camada_montanhas = self._criar_montanhas()
        self.camada_cenario = self._criar_cenario()
        self.camada_frente = self._criar_frente()

        # ─── plataformas colidíveis ───
        self.plataformas = self._criar_plataformas()

    # ────────── camada 0: céu + estrelas ──────────
    def _criar_ceu(self):
        surf = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        _gradiente_vertical(surf, (0, 0, LARGURA, CHAO_Y), COR_CEU_TOPO, COR_CEU_BASE)

        # estrelas
        for _ in range(80):
            sx = self.rng.randint(0, LARGURA)
            sy = self.rng.randint(0, CHAO_Y // 2)
            tamanho = self.rng.choice([2, 2, 2, 3, 4])
            brilho = self.rng.randint(150, 255)
            cor = (brilho, brilho, self.rng.randint(180, 255))
            _pixel(surf, sx, sy, cor, tamanho)

        # lua
        lua_x, lua_y = LARGURA - 180, 80
        pygame.draw.circle(surf, (220, 215, 180), (lua_x, lua_y), 35)
        pygame.draw.circle(surf, COR_CEU_TOPO, (lua_x + 12, lua_y - 8), 30)  # sombra
        return surf

    # ────────── camada 1: montanhas distantes ──────────
    def _criar_montanhas(self):
        surf = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        base = CHAO_Y - 20

        # camada traseira
        posicoes = [(-80, 320), (150, 260), (400, 340), (650, 280),
                    (850, 310), (1050, 290)]
        for px, alt in posicoes:
            larg = self.rng.randint(250, 400)
            _desenhar_montanha(surf, px, base, larg, alt, COR_MONTANHA_1)

        # camada frontal (mais claras)
        for px, alt in [(50, 200), (350, 180), (700, 220), (950, 190)]:
            larg = self.rng.randint(200, 350)
            _desenhar_montanha(surf, px, base, larg, alt, COR_MONTANHA_2)

        return surf

    # ────────── camada 2: cenário principal (árvores, chão) ──────────
    def _criar_cenario(self):
        surf = pygame.Surface((self.largura_total, ALTURA), pygame.SRCALPHA)

        # ── chão (grama + terra) ──
        # faixa de grama
        _gradiente_vertical(surf, (0, CHAO_Y - 6, self.largura_total, 10),
                            COR_CHAO_TOPO, COR_CHAO_TERRA)
        # terra principal
        _gradiente_vertical(surf, (0, CHAO_Y + 4, self.largura_total, ALTURA - CHAO_Y - 4),
                            COR_CHAO_TERRA, COR_CHAO_TERRA_ESCURA)

        # textura de grama (pixelinhos no topo do chão)
        for gx in range(0, self.largura_total, 6):
            gh = self.rng.randint(3, 12)
            cor = self.rng.choice([COR_CHAO_TOPO, COR_FOLHA, COR_ARVORE_COPA_ESCURA])
            pygame.draw.rect(surf, cor, (gx, CHAO_Y - gh, 3, gh))

        # pedras no chão
        _desenhar_pedras(surf, CHAO_Y, self.largura_total, seed=100)

        # ── árvores de fundo (atrás de tudo) ──
        posicoes_arvores = [60, 220, 420, 580, 750, 950, 1120]
        for i, ax in enumerate(posicoes_arvores):
            escala = self.rng.uniform(0.7, 1.3)
            _desenhar_arvore(surf, ax, CHAO_Y, escala, seed=i * 7 + 3)

        # ── cercas decorativas ──
        _desenhar_cerca(surf, 80, CHAO_Y, 120, seed=50)
        _desenhar_cerca(surf, 700, CHAO_Y, 90, seed=51)

        # ── arbustos ──
        for i, bx in enumerate([150, 340, 510, 660, 870, 1050]):
            _desenhar_arbusto(surf, bx, CHAO_Y, seed=200 + i)

        # ── poça de água decorativa ──
        _desenhar_agua(surf, 450, CHAO_Y + 2, 100, 10, seed=300)

        return surf

    # ────────── camada 3: vegetação na frente (overlay) ──────────
    def _criar_frente(self):
        surf = pygame.Surface((self.largura_total, ALTURA), pygame.SRCALPHA)

        # folhas pendentes no topo da tela (copa densa)
        for i in range(25):
            fx = self.rng.randint(0, self.largura_total)
            fy = self.rng.randint(0, 60)
            raio = self.rng.randint(20, 50)
            alpha = self.rng.randint(60, 120)
            cor = list(self.rng.choice([COR_ARVORE_COPA, COR_ARVORE_COPA_ESCURA, COR_FOLHA]))
            cor.append(alpha)
            pygame.draw.circle(surf, cor, (fx, fy), raio)

        # cipós caindo do topo
        for _ in range(8):
            cx = self.rng.randint(0, self.largura_total)
            cy = 0
            comprimento = self.rng.randint(80, 200)
            for seg in range(comprimento // 6):
                cor_cipo = (30 + self.rng.randint(-5, 5),
                            60 + self.rng.randint(-10, 10),
                            15)
                cx += self.rng.randint(-3, 3)
                pygame.draw.rect(surf, cor_cipo, (cx, cy + seg * 6, 3, 7))
            # folhinha na ponta
            _pixel(surf, cx - 3, cy + comprimento, COR_FOLHA_CLARA, 6)
            _pixel(surf, cx + 3, cy + comprimento + 2, COR_FOLHA, 5)

        # pequenos insetos / vagalumes (partículas brilhantes)
        for _ in range(10):
            vx = self.rng.randint(0, self.largura_total)
            vy = self.rng.randint(100, CHAO_Y - 50)
            cor_vaga = (180, 220, 80, self.rng.randint(100, 180))
            _pixel(surf, vx, vy, cor_vaga, 3)

        return surf

    # ────────── plataformas ──────────
    def _criar_plataformas(self):
        """Cria retângulos de plataformas elevadas para colisão."""
        plats = [
            pygame.Rect(200, CHAO_Y - 160, 140, 20),
            pygame.Rect(500, CHAO_Y - 240, 160, 20),
            pygame.Rect(800, CHAO_Y - 180, 130, 20),
            pygame.Rect(1020, CHAO_Y - 300, 150, 20),
            pygame.Rect(350, CHAO_Y - 100, 100, 20),
        ]
        return plats

    def _desenhar_plataforma(self, tela, rect):
        """Desenha uma plataforma pixel-art."""
        # corpo
        pygame.draw.rect(tela, COR_PLATAFORMA, rect)
        # borda superior mais clara
        pygame.draw.rect(tela, COR_PLATAFORMA_BORDA, (rect.x, rect.y, rect.width, 5))
        # textura
        for tx in range(rect.x + 8, rect.x + rect.width - 8, 16):
            pygame.draw.rect(tela, COR_CHAO_TERRA_ESCURA, (tx, rect.y + 7, 8, 3))
        # suportes inferiores
        sw = 8
        pygame.draw.rect(tela, COR_CERCA_ESCURA, (rect.x + 10, rect.bottom, sw, 14))
        pygame.draw.rect(tela, COR_CERCA_ESCURA,
                         (rect.x + rect.width - 18, rect.bottom, sw, 14))

    # ────────── desenho principal ──────────
    def desenhar(self, tela, camera_x=0):
        """
        Desenha todas as camadas do cenário.
        camera_x: deslocamento horizontal (para scrolling futuro).
        """
        # Camada 0 — céu (fixo, sem parallax)
        tela.blit(self.camada_ceu, (0, 0))

        # Camada 1 — montanhas (parallax lento)
        offset_mont = int(camera_x * 0.2)
        tela.blit(self.camada_montanhas, (-offset_mont, 0))

        # Camada 2 — cenário principal
        tela.blit(self.camada_cenario, (-camera_x, 0))

        # Plataformas (desenhadas por cima do cenário)
        for plat in self.plataformas:
            r = plat.move(-camera_x, 0)
            self._desenhar_plataforma(tela, r)

        # Camada 3 — vegetação frontal (overlay)
        tela.blit(self.camada_frente, (-camera_x, 0))
