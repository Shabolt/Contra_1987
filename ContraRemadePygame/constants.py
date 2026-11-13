# Resolução da tela e taxa de frames
LARGURA = 1240
ALTURA = 920
FPS = 60

# Altura do chão (temporário, até existir um mapa/fase)
CHAO_Y = 1000

# Modo debug: desenha plataformas, pontos de spawn e caixas das torretas,
# e mostra no HUD a coordenada do mouse (no mesmo sistema de coordenadas do scenario.py)
DEBUG = True

# Cor = (R, G, B)
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AZUL = (0, 100, 255)
VERMELHO = (220, 50, 50)
LARANJA = (255, 140, 0)
VERDE = (0, 200, 80)
CINZA = (160, 160, 160)
ROXO = (160, 32, 240)
# ---------------------------------------------------------------
# Power-ups (caixas)
CHANCE_POWERUP_CAIXA = 1.0      # chance (0 a 1) de a caixa soltar um power-up ao explodir
COOLDOWN_TIRO_NORMAL = 12       # frames entre um tiro e outro (padrão)
COOLDOWN_TIRO_H = 5             # power-up H: cadência bem mais rápida
S_ANGULOS = (-24, -12, 0, 12, 24)  # power-up S: 5 projéteis (graus em relação à mira)
S_ALCANCE = 420                 # power-up S: distância máxima do projétil (px)
# ---------------------------------------------------------------
# Variáveis a serem adicionadas