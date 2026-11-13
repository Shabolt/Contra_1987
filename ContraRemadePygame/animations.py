import os
import pygame

# ---------------------------------------------------------------------------
# Configuração dos sprites do player
# ---------------------------------------------------------------------------
# Altura (em pixels) do sprite do player PARADO. Todos os outros frames usam
# a mesma escala, então o personagem tem o mesmo "tamanho de pixel" em todas
# as poses. Use None para manter o tamanho original dos arquivos.
PLAYER_ALTURA = None

# Remove as bordas transparentes de cada frame antes de uniformizar. Evita que
# o player "pule" na tela por causa de margens diferentes entre as imagens.
RECORTAR_TRANSPARENCIA = True

EXTENSOES = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")


def _espelhar(frames):
    return [pygame.transform.flip(f, True, False) for f in frames]


def _placeholder(cor=(255, 0, 255), tamanho=(32, 48)):
    """Sprite provisório visível (evita crash quando falta imagem)."""
    surf = pygame.Surface(tamanho, pygame.SRCALPHA)
    surf.fill((*cor, 255))
    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
    return surf


def _recortar(img):
    """Corta a área transparente em volta do sprite."""
    rect = img.get_bounding_rect()
    if rect.width == 0 or rect.height == 0 or rect.size == img.get_size():
        return img
    return img.subsurface(rect).copy()


class SpriteManager:
    carregado = False

    img_player = None
    # Tamanho (largura, altura) comum a TODOS os frames do player.
    # Os frames ficam alinhados pelos pés (embaixo) e centralizados na horizontal,
    # então desenhe o player usando midbottom como âncora.
    player_tamanho = (0, 0)

    frames_jogador_parado_d = []
    frames_jogador_parado_e = []
    frames_andando_d = []
    frames_andando_e = []

    frames_and_cd = []
    frames_and_ce = []
    frames_and_ccd = []
    frames_and_cce = []
    frames_and_bd = []
    frames_and_be = []

    frames_pulo_d = []
    frames_pulo_e = []

    frames_mira_cima_d = []
    frames_mira_cima_e = []
    frames_mira_diag_cima_d = []
    frames_mira_diag_cima_e = []
    frames_deitado_d = []
    frames_deitado_e = []

    frames_atirador_pe_d = []
    frames_atirador_pe_e = []
    frames_atirador_agachado_d = []
    frames_atirador_agachado_e = []
    frames_atirador_cima_d = []
    frames_atirador_cima_e = []

    frames_soldado_d = []
    frames_soldado_e = []
    frames_explosao = []
    frames_tiro_inimigo = []
    frames_tiro_bill = []

    # Power-ups: explosão das caixas (explo6, explo7) e ícones H (power1) e S (power2)
    frames_explosao_caixa = []
    sprite_power_h = None
    sprite_power_s = None

    torretas_sprites = {}

    # Boss
    sprite_boss_canhao1 = None
    sprite_boss_canhao2 = None
    sprite_boss_dest = None
    frames_explosao_boss = []

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    @staticmethod
    def _indexar_imagens():
        """Mapeia nome (sem extensão, minúsculo) -> caminho do arquivo.

        Assim 'And_CD1' encontra 'and_cd1.png' também no Linux/Mac, onde o
        sistema de arquivos diferencia maiúsculas de minúsculas. A primeira
        pasta da lista de prioridade que tiver o arquivo vence.
        """
        bases = []
        for base in (os.path.dirname(os.path.abspath(__file__)), os.getcwd()):
            if base not in bases:
                bases.append(base)

        subpastas = [
            os.path.join("assets", "sprites"),
            "sprites",
            "animation",
            "animations",
            "assets",
            ".",
        ]

        indice = {}
        for base in bases:
            for sub in subpastas:
                pasta = os.path.normpath(os.path.join(base, sub))
                if not os.path.isdir(pasta):
                    continue
                for arq in sorted(os.listdir(pasta)):
                    caminho = os.path.join(pasta, arq)
                    if not os.path.isfile(caminho):
                        continue
                    nome, ext = os.path.splitext(arq)
                    if ext.lower() not in EXTENSOES:
                        continue
                    indice.setdefault(nome.lower(), caminho)
        return indice

    @staticmethod
    def _carregar_arquivo(caminho):
        try:
            img = pygame.image.load(caminho)
            # convert_alpha exige uma janela criada (set_mode); sem ela
            # o código antigo falhava em silêncio e nenhum sprite carregava.
            if pygame.display.get_surface() is not None:
                img = img.convert_alpha()
            return img
        except Exception as e:
            print(f"[SpriteManager] Erro ao carregar '{caminho}': {e}")
            return None

    @staticmethod
    def _preparar_frames(frames, largura_alvo, altura_alvo, base_w=None, base_h=None, modo="bottom"):
        """Prepara e uniformiza frames para dimensões específicas, mantendo tamanho compatível com inimigos."""
        saida = []
        for f in frames:
            if f is None:
                continue
            rec = _recortar(f) if RECORTAR_TRANSPARENCIA else f
            if modo == "stretch":
                scaled = pygame.transform.scale(rec, (largura_alvo, altura_alvo))
                saida.append(scaled)
            elif modo == "bottom":
                bw = base_w or rec.get_width()
                bh = base_h or rec.get_height()
                scale_x = largura_alvo / float(bw) if bw else 1.0
                scale_y = altura_alvo / float(bh) if bh else 1.0
                nw = min(largura_alvo, round(rec.get_width() * scale_x))
                nh = min(altura_alvo, round(rec.get_height() * scale_y))
                scaled = pygame.transform.scale(rec, (max(1, nw), max(1, nh)))
                canvas = pygame.Surface((largura_alvo, altura_alvo), pygame.SRCALPHA)
                canvas.blit(scaled, ((largura_alvo - nw) // 2, altura_alvo - nh))
                saida.append(canvas)
            else:
                saida.append(pygame.transform.scale(rec, (largura_alvo, altura_alvo)))
        return saida

    @staticmethod
    def _uniformizar_player(raw, ref):
        ref_p = _recortar(ref) if RECORTAR_TRANSPARENCIA else ref
        ref_h = ref_p.get_height()
        escala = PLAYER_ALTURA / ref_h if (PLAYER_ALTURA and ref_h) else 1.0

        preparados = {}
        for nome, frames in raw.items():
            lista = []
            for f in frames:
                if RECORTAR_TRANSPARENCIA:
                    f = _recortar(f)
                if escala != 1.0:
                    novo = (max(1, round(f.get_width() * escala)),
                            max(1, round(f.get_height() * escala)))
                    f = pygame.transform.scale(f, novo)
                lista.append(f)
            preparados[nome] = lista

        todos = [f for lista in preparados.values() for f in lista]
        largura = max(f.get_width() for f in todos)
        altura = max(f.get_height() for f in todos)

        saida = {}
        for nome, lista in preparados.items():
            novos = []
            for f in lista:
                canvas = pygame.Surface((largura, altura), pygame.SRCALPHA)
                canvas.blit(f, ((largura - f.get_width()) // 2,
                                altura - f.get_height()))
                novos.append(canvas)
            saida[nome] = novos
        return saida, (largura, altura)

    # ------------------------------------------------------------------
    # Carregamento principal
    # ------------------------------------------------------------------
    @classmethod
    def carregar_tudo(cls):
        if cls.carregado:
            return

        indice = cls._indexar_imagens()
        cache = {}

        def carregar_img(*nomes):
            """Tenta cada nome em ordem e devolve a primeira imagem achada."""
            for nome in nomes:
                chave = nome.lower()
                if chave not in cache:
                    caminho = indice.get(chave)
                    cache[chave] = cls._carregar_arquivo(caminho) if caminho else None
                if cache[chave] is not None:
                    return cache[chave]
            return None

        def sequencia(prefixo, qtd):
            frames = []
            for i in range(1, qtd + 1):
                img = carregar_img(f"{prefixo}{i}")
                if img is not None:
                    frames.append(img)
            return frames

        # ---------------- Tiros e explosões ----------------
        img_explo1 = carregar_img("explo1")
        img_explo2 = carregar_img("explo2")
        explo = sequencia("explo", 4)
        cls.frames_explosao = explo

        if img_explo1 is not None:
            cls.frames_tiro_inimigo = [img_explo1]
        elif explo:
            cls.frames_tiro_inimigo = [explo[0]]

        if img_explo2 is not None:
            cls.frames_tiro_bill = [img_explo2]
        elif explo:
            cls.frames_tiro_bill = [explo[1] if len(explo) > 1 else explo[0]]

        # ---------------- Power-ups e explosão das caixas ----------------
        cls.frames_explosao_caixa = [
            img for img in (carregar_img("explo6"), carregar_img("explo7")) if img is not None
        ]
        cls.sprite_power_h = carregar_img("power1")
        cls.sprite_power_s = carregar_img("power2")

        # ---------------- Torretas ----------------
        nomes_torretas = [
            "torret_B", "torret_C", "torret_D", "torret_DB", "torret_DB2",
            "torret_DC", "torret_DC2", "torret_E", "torret_EB", "torret_EB2",
            "torret_EC", "torret_EC2",
        ]
        cls.torretas_sprites = {}
        for nome in nomes_torretas:
            img_t = carregar_img(nome)
            if img_t is not None:
                cls.torretas_sprites[nome] = img_t

        if not cls.torretas_sprites:
            img_gen = carregar_img("turret")
            if img_gen is not None:
                cls.torretas_sprites["torret_B"] = img_gen

        # ---------------- Player (carrega os frames crus) ----------------
        base = carregar_img("and_1", "Player", "player", "bill")
        if base is None:
            print("[SpriteManager] Sprite do player não encontrado; usando placeholder.")
            base = _placeholder()

        andando = sequencia("and_", 5) or [base]
        cd = sequencia("And_CD", 4) or andando
        ce = sequencia("And_CE", 4)                 # vazio -> espelha cd depois
        ccd = sequencia("And_CCD", 5)
        cce = sequencia("And_CCE", 5)
        bd = sequencia("And_BD", 5)
        be = sequencia("And_BE", 5)
        pulo_d = sequencia("CBD_", 4) or andando
        pulo_e = sequencia("CBE_", 4)               # vazio -> espelha pulo_d depois
        img_cima = carregar_img("aim_up", "up") or (ccd[0] if ccd else base)
        img_deit = carregar_img("deit", "down", "deitado", "crouch") or base
        img_diag = carregar_img("aim_diag_up", "diag_up")

        # ---------------- Player (uniformiza em tamanhos equivalentes aos inimigos) ----------------
        # Inimigos Soldado e Atirador usam largura=40 e altura=60.
        cls.player_tamanho = (40, 60)

        # 1. Parado e Andando: largura 40, altura 60 (mesmo tamanho dos inimigos)
        norm_parado = cls._preparar_frames([base], 40, 60, base_w=18, base_h=36)
        cls.img_player = norm_parado[0]
        cls.frames_jogador_parado_d = norm_parado
        cls.frames_jogador_parado_e = _espelhar(norm_parado)

        norm_andando = cls._preparar_frames(andando, 40, 60, base_w=18, base_h=36)
        cls.frames_andando_d = norm_andando
        cls.frames_andando_e = _espelhar(norm_andando)

        # 2. Tiro Reto: largura 40, altura 60
        norm_cd = cls._preparar_frames(cd, 40, 60, base_w=18, base_h=35)
        cls.frames_and_cd = norm_cd
        cls.frames_and_ce = cls._preparar_frames(ce, 40, 60, base_w=18, base_h=35) if ce else _espelhar(norm_cd)

        # 3. Tiro Diagonal Baixo: largura 40, altura 60
        norm_bd = cls._preparar_frames(bd, 40, 60, base_w=20, base_h=35)
        cls.frames_and_bd = norm_bd
        cls.frames_and_be = cls._preparar_frames(be, 40, 60, base_w=20, base_h=35) if be else _espelhar(norm_bd)

        # 4. Tiro Diagonal Cima: largura 40, altura 75 (cano da arma estendido para cima)
        norm_ccd = cls._preparar_frames(ccd, 40, 75, base_w=18, base_h=45)
        cls.frames_and_ccd = norm_ccd
        cls.frames_and_cce = cls._preparar_frames(cce, 40, 75, base_w=18, base_h=45) if cce else _espelhar(norm_ccd)

        # 5. Mira reta para cima: largura 40, altura 75
        norm_cima = cls._preparar_frames([img_cima], 40, 75, base_w=18, base_h=45)
        cls.frames_mira_cima_d = norm_cima
        cls.frames_mira_cima_e = _espelhar(norm_cima)

        diag_d = norm_ccd[:1] or norm_cima
        cls.frames_mira_diag_cima_d = diag_d
        cls.frames_mira_diag_cima_e = _espelhar(diag_d)

        # 6. Pulo (cambalhota): largura 40, altura 40
        norm_pulo_d = cls._preparar_frames(pulo_d, 40, 40, modo="stretch")
        cls.frames_pulo_d = norm_pulo_d
        cls.frames_pulo_e = cls._preparar_frames(pulo_e, 40, 40, modo="stretch") if pulo_e else _espelhar(norm_pulo_d)

        # 7. Deitado / Agachado: largura 70, altura 30
        norm_deit = cls._preparar_frames([img_deit], 70, 30, modo="stretch")
        cls.frames_deitado_d = norm_deit
        cls.frames_deitado_e = _espelhar(norm_deit)

        # ---------------- Inimigos ----------------
        soldados = []
        for i in range(1, 10):
            img = carregar_img(f"Enemy1D_{i}", f"enemy_{i}")
            if img is not None:
                soldados.append(img)
        if not soldados:
            print("[SpriteManager] Sprites do soldado não encontrados; usando placeholder.")
            soldados = [_placeholder((255, 0, 0))]
        cls.frames_soldado_d = soldados
        cls.frames_soldado_e = _espelhar(soldados)

        def par(nome_d, nome_e, fallback_d, fallback_e):
            d = carregar_img(nome_d)
            e = carregar_img(nome_e)
            d = [d] if d is not None else None
            e = [e] if e is not None else None
            if d is None and e is not None:
                d = _espelhar(e)
            if e is None and d is not None:
                e = _espelhar(d)
            return (d or fallback_d), (e or fallback_e)

        cls.frames_atirador_pe_d, cls.frames_atirador_pe_e = par(
            "Enemy2D", "Enemy2E", cls.frames_soldado_d, cls.frames_soldado_e)
        cls.frames_atirador_agachado_d, cls.frames_atirador_agachado_e = par(
            "Enemy2BD", "Enemy2BE", cls.frames_atirador_pe_d, cls.frames_atirador_pe_e)
        cls.frames_atirador_cima_d, cls.frames_atirador_cima_e = par(
            "Enemy2CD", "Enemy2CE", cls.frames_atirador_pe_d, cls.frames_atirador_pe_e)

        # ---------------- Boss ----------------
        cls.sprite_boss_canhao1 = carregar_img("boss_canhao1")
        cls.sprite_boss_canhao2 = carregar_img("boss_canhao2")
        cls.sprite_boss_dest = carregar_img("boss_dest")
        cls.frames_explosao_boss = [
            img for img in (carregar_img("explo5"), carregar_img("explo6"), carregar_img("explo7"),
                            carregar_img("Exp_1"), carregar_img("Exp_2"))
            if img is not None
        ]
        if not cls.frames_explosao_boss and cls.frames_explosao:
            cls.frames_explosao_boss = cls.frames_explosao

        # Só marca como carregado no fim, para que uma falha no meio
        # não deixe o gerenciador "meio carregado" para sempre.
        cls.carregado = True