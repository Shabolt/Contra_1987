import os
import pygame

class SpriteManager:
    carregado = False

    img_player = None
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

    torretas_sprites = {}

    @classmethod
    def carregar_tudo(cls):
        if cls.carregado:
            return
        cls.carregado = True

        pastas_candidatas = [
            os.path.join("assets", "sprites"),
            os.path.join("sprites"),
            os.path.join("animation"),
            os.path.join("animations"),
            os.path.join("assets"),
            "."
        ]

        def carregar_img(nome):
            for pasta in pastas_candidatas:
                for ext in [".png", ".jpg", ".jpeg", ""]:
                    caminho = os.path.join(pasta, nome + ext)
                    if os.path.exists(caminho):
                        try:
                            return pygame.image.load(caminho).convert_alpha()
                        except Exception:
                            pass
            return None

        # Carregar explo1 para o tiro dos inimigos
        img_explo1 = carregar_img("explo1")
        if img_explo1:
            cls.frames_tiro_inimigo = [img_explo1]

        # Carregar explo2 para o tiro do Bill
        img_explo2 = carregar_img("explo2")
        if img_explo2:
            cls.frames_tiro_bill = [img_explo2]

        # Carregar explosões adicionais (explo1 a explo4)
        explo = []
        for i in range(1, 5):
            img = carregar_img(f"explo{i}")
            if img:
                explo.append(img)
        cls.frames_explosao = explo
        if not cls.frames_tiro_inimigo and explo:
            cls.frames_tiro_inimigo = [explo[0]]
        if not cls.frames_tiro_bill and len(explo) > 1:
            cls.frames_tiro_bill = [explo[1]]
        elif not cls.frames_tiro_bill and explo:
            cls.frames_tiro_bill = [explo[0]]

        # Torretas
        nomes_torretas = [
            "torret_B", "torret_C", "torret_D", "torret_DB", "torret_DB2", 
            "torret_DC", "torret_DC2", "torret_E", "torret_EB", "torret_EB2", 
            "torret_EC", "torret_EC2"
        ]
        for nome in nomes_torretas:
            img_t = carregar_img(nome)
            if img_t:
                cls.torretas_sprites[nome] = img_t

        if not cls.torretas_sprites:
            img_gen = carregar_img("torret_B") or carregar_img("turret")
            if img_gen:
                cls.torretas_sprites["torret_B"] = img_gen

        # Jogador Parado
        img_p = carregar_img("and_1") or carregar_img("Player") or carregar_img("player") or carregar_img("bill")
        if img_p:
            cls.img_player = img_p
            cls.frames_jogador_parado_d = [img_p]
            cls.frames_jogador_parado_e = [pygame.transform.flip(img_p, True, False)]

        andando_direita = []
        for i in range(1, 6):
            img = carregar_img(f"and_{i}")
            if img:
                andando_direita.append(img)
        if not andando_direita and img_p:
            andando_direita = [img_p]

        cls.frames_andando_d = andando_direita
        cls.frames_andando_e = [pygame.transform.flip(f, True, False) for f in andando_direita]

        seq_cd = []
        for i in range(1, 5):
            img = carregar_img(f"And_CD{i}")
            if img:
                seq_cd.append(img)
        if not seq_cd:
            seq_cd = andando_direita
        cls.frames_and_cd = seq_cd

        seq_ce = []
        for i in range(1, 5):
            img = carregar_img(f"And_CE{i}")
            if img:
                seq_ce.append(img)
        if not seq_ce:
            seq_ce = [pygame.transform.flip(f, True, False) for f in seq_cd]
        cls.frames_and_ce = seq_ce

        def carregar_sequencia(prefixo, qtd=5):
            lista = []
            for i in range(1, qtd + 1):
                img = carregar_img(f"{prefixo}{i}")
                if img:
                    lista.append(img)
            return lista

        cls.frames_and_ccd = carregar_sequencia("And_CCD")
        cls.frames_and_cce = carregar_sequencia("And_CCE")
        cls.frames_and_bd = carregar_sequencia("And_BD")
        cls.frames_and_be = carregar_sequencia("And_BE")

        pulos_d = []
        for i in range(1, 5):
            img = carregar_img(f"CBD_{i}")
            if img:
                pulos_d.append(img)
        if not pulos_d:
            pulos_d = andando_direita
        cls.frames_pulo_d = pulos_d

        pulos_e = []
        for i in range(1, 5):
            img = carregar_img(f"CBE_{i}")
            if img:
                pulos_e.append(img)
        if not pulos_e:
            pulos_e = [pygame.transform.flip(f, True, False) for f in pulos_d]
        cls.frames_pulo_e = pulos_e

        img_cima = carregar_img("aim_up") or carregar_img("up") or img_p
        cls.frames_mira_cima_d = [img_cima]
        cls.frames_mira_cima_e = [pygame.transform.flip(img_cima, True, False)]

        img_deit = carregar_img("down") or carregar_img("deitado") or carregar_img("crouch") or img_p
        cls.frames_deitado_d = [img_deit]
        cls.frames_deitado_e = [pygame.transform.flip(img_deit, True, False)]

        soldados = []
        for i in range(1, 10):
            img = carregar_img(f"Enemy1D_{i}") or carregar_img(f"enemy_{i}")
            if img:
                soldados.append(img)
        if not soldados:
            soldados = [img_p]
        cls.frames_soldado_d = soldados
        cls.frames_soldado_e = [pygame.transform.flip(f, True, False) for f in soldados]

        e2d = carregar_img("Enemy2D")
        e2e = carregar_img("Enemy2E")
        if e2d:
            cls.frames_atirador_pe_d = [e2d]
        if e2e:
            cls.frames_atirador_pe_e = [e2e]

        e2bd = carregar_img("Enemy2BD")
        e2be = carregar_img("Enemy2BE")
        if e2bd:
            cls.frames_atirador_agachado_d = [e2bd]
        if e2be:
            cls.frames_atirador_agachado_e = [e2be]

        e2cd = carregar_img("Enemy2CD")
        e2ce = carregar_img("Enemy2CE")
        if e2cd:
            cls.frames_atirador_cima_d = [e2cd]
        if e2ce:
            cls.frames_atirador_cima_e = [e2ce]

        if not cls.frames_atirador_pe_d:
            cls.frames_atirador_pe_d = soldados
        if not cls.frames_atirador_pe_e:
            cls.frames_atirador_pe_e = [pygame.transform.flip(f, True, False) for f in soldados]
        if not cls.frames_atirador_agachado_d:
            cls.frames_atirador_agachado_d = cls.frames_atirador_pe_d
        if not cls.frames_atirador_agachado_e:
            cls.frames_atirador_agachado_e = cls.frames_atirador_pe_e
        if not cls.frames_atirador_cima_d:
            cls.frames_atirador_cima_d = cls.frames_atirador_pe_d
        if not cls.frames_atirador_cima_e:
            cls.frames_atirador_cima_e = cls.frames_atirador_pe_e
