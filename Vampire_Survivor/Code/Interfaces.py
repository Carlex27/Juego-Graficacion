from settings import *

#La interfaz del jugador durante el juego
class PlayerInterface(pygame.sprite.Sprite):
    def __init__(self, player, display_surface):
        super().__init__()
        self.display_surface = display_surface  #Se asigna el display original de la aplicacion
        self.player = player                    #Se asigna el jugador
        #Se importa el icono de corazones
        self.life_icon = pygame.image.load(join('Assets','images','heart.gif')).convert_alpha()
        #Se escala el icono 
        self.life_icon = pygame.transform.scale(self.life_icon, (50,50))
    
    def draw_life_counter(self):
        #Se dibuja en pantalla el life_icon
        self.display_surface.blit(self.life_icon, (30,30))

        #Se declara el font de las letras
        font = pygame.font.Font(None, 40)
        life_text = font.render(f"x{self.player.lifes}", True, (255,255,255)) #Se se crea el texto de las vidas del jugador

        #Se dibuja en pantalla el texto de las vidas
        self.display_surface.blit(life_text, (80,40))

    #Se dibuja el contador de puntos del jugador5
    def draw_score(self):
        font = pygame.font.Font(None, 40)  # Cambia el tamaño si es necesario
        score_text = font.render(f"Score: {self.player.score}", True, (255, 255, 255))  # Texto blanco
        self.display_surface.blit(score_text, (20, 80))  # Ajusta la posición según sea necesario

    def update(self):
        self.draw_life_counter()
        self.draw_score()

class StartScreen:
    def __init__(self, display_surface):
        self.display_surface = display_surface #Se asigna el display original de la aplicacion
        self.running = True                    #Se asigna que el juego no se ha finalizado

        # Cargar imagen de fondo
        self.background = pygame.image.load(join('Assets', 'images', 'start_screen', 'background.jpg')).convert()
        self.background = pygame.transform.scale(self.background, self.display_surface.get_size())

        # Configuración del botón
        self.button_font = pygame.font.Font(None, 60)
        self.button_text = self.button_font.render("Iniciar", True, (255, 255, 255))
        self.button_rect = pygame.Rect(0, 0, 200, 80)  # Tamaño del botón
        self.button_rect.center = (self.display_surface.get_width() // 2, self.display_surface.get_height() // 2)

    def draw(self):
        # Dibujar el fondo
        self.display_surface.blit(self.background, (0, 0))

        # Dibujar el botón
        pygame.draw.rect(self.display_surface, (50, 150, 50), self.button_rect)  # Rectángulo verde
        pygame.draw.rect(self.display_surface, (255, 255, 255), self.button_rect, 3)  # Borde blanco
        #Se dibuja el texto del botón en el centro del botón
        self.display_surface.blit(self.button_text, (self.button_rect.centerx - self.button_text.get_width() // 2,
                                                     self.button_rect.centery - self.button_text.get_height() // 2))

    #Metodo para manejar los eventos del juego
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       #Se detecta el evento de salir
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:    #Se detecta el evento de pulsar el botón 
                if self.button_rect.collidepoint(event.pos):  # Detectar clic en el botón
                    self.running = False  # Salir de la pantalla de inicio

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.update()

class GameOverScreen:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.running = True

        # Cargar imagen de fondo
        self.background = pygame.image.load(join('Assets', 'images', 'game_over', 'background.jpg')).convert()
        self.background = pygame.transform.scale(self.background, self.display_surface.get_size())

        # Configuración del botón "Reiniciar"
        self.button_font = pygame.font.Font(None, 60)
        self.restart_text = self.button_font.render("Reiniciar", True, (255, 255, 255))
        self.restart_rect = pygame.Rect(0, 0, 250, 80)  # Tamaño del botón
        self.restart_rect.center = (self.display_surface.get_width() // 2, self.display_surface.get_height() // 2)

        # Texto de "Game Over"
        self.title_font = pygame.font.Font(None, 100)
        self.game_over_text = self.title_font.render("GAME OVER", True, (255, 0, 0))
        self.game_over_text_rect = self.game_over_text.get_rect(center=(self.display_surface.get_width() // 2, 150))

    def draw(self):
        # Dibujar el fondo
        self.display_surface.blit(self.background, (0, 0))

        # Dibujar el texto de Game Over
        self.display_surface.blit(self.game_over_text, self.game_over_text_rect)

        # Dibujar el botón "Reiniciar"
        pygame.draw.rect(self.display_surface, (50, 50, 150), self.restart_rect)  # Botón azul
        pygame.draw.rect(self.display_surface, (255, 255, 255), self.restart_rect, 3)  # Borde blanco
        #Se dibuja el texto del botón en el centro del botón
        self.display_surface.blit(self.restart_text, (self.restart_rect.centerx - self.restart_text.get_width() // 2,
                                                      self.restart_rect.centery - self.restart_text.get_height() // 2))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.restart_rect.collidepoint(event.pos):  # Detectar clic en "Reiniciar"
                    self.running = False  # Salir de la pantalla de Game Over

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.update()


