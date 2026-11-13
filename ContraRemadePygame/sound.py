import os
import pygame


class SoundManager:
    inicializado = False

    snd_tiro_player = None
    snd_tiro_inimigo = None
    snd_destruicao = None
    snd_passos = None
    snd_powerup = None
    canal_passos = None
    caminho_ost = None

    @classmethod
    def inicializar(cls):
        if cls.inicializado:
            return

        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"[SoundManager] Falha ao inicializar mixer: {e}")
                return

        pygame.mixer.set_num_channels(32)
        # Reserva o canal 0 para o loop de passos do player
        cls.canal_passos = pygame.mixer.Channel(0)

        diretorio = os.path.dirname(os.path.abspath(__file__))
        pasta_sounds = os.path.join(diretorio, "assets", "sounds")

        def carregar(nome):
            caminho = os.path.join(pasta_sounds, nome)
            if os.path.isfile(caminho):
                try:
                    return pygame.mixer.Sound(caminho)
                except Exception as e:
                    print(f"[SoundManager] Erro ao carregar '{nome}': {e}")
            return None

        # Tiro do player e tiro inimigo (mesmo som, volumes diferentes)
        cls.snd_tiro_player = carregar("tiro-sfx.wav")
        if cls.snd_tiro_player:
            cls.snd_tiro_player.set_volume(0.6)

        cls.snd_tiro_inimigo = carregar("tiro-sfx.wav")
        if cls.snd_tiro_inimigo:
            cls.snd_tiro_inimigo.set_volume(0.2)

        # Destruição (torretas e caixas)
        cls.snd_destruicao = carregar("destruicao-sfx.wav")
        if cls.snd_destruicao:
            cls.snd_destruicao.set_volume(0.65)

        # Passos (loop contínuo enquanto anda)
        cls.snd_passos = carregar("passos-sfx.wav")
        if cls.snd_passos:
            cls.snd_passos.set_volume(0.25)

        # Coleta de power-up
        cls.snd_powerup = carregar("powerup-sfx.wav")
        if cls.snd_powerup:
            cls.snd_powerup.set_volume(0.7)

        # OST principal
        caminho_ost = os.path.join(pasta_sounds, "ost-principal.mp3")
        if os.path.isfile(caminho_ost):
            cls.caminho_ost = caminho_ost

        cls.inicializado = True

    @classmethod
    def tocar_musica(cls):
        cls.inicializar()
        if cls.caminho_ost and pygame.mixer.get_init():
            try:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(cls.caminho_ost)
                    pygame.mixer.music.set_volume(0.45)
                    pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"[SoundManager] Erro ao tocar música: {e}")

    @classmethod
    def parar_musica(cls):
        if pygame.mixer.get_init():
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    @classmethod
    def tocar_tiro_player(cls):
        cls.inicializar()
        if cls.snd_tiro_player:
            cls.snd_tiro_player.play()

    @classmethod
    def tocar_tiro_inimigo(cls):
        cls.inicializar()
        if cls.snd_tiro_inimigo:
            cls.snd_tiro_inimigo.play()

    @classmethod
    def tocar_destruicao(cls):
        cls.inicializar()
        if cls.snd_destruicao:
            cls.snd_destruicao.play()

    @classmethod
    def tocar_powerup(cls):
        cls.inicializar()
        if cls.snd_powerup:
            cls.snd_powerup.play()

    @classmethod
    def iniciar_passos(cls):
        cls.inicializar()
        if cls.canal_passos and cls.snd_passos:
            if not cls.canal_passos.get_busy():
                cls.canal_passos.play(cls.snd_passos, loops=-1)

    @classmethod
    def parar_passos(cls):
        if cls.canal_passos:
            if cls.canal_passos.get_busy():
                cls.canal_passos.stop()
