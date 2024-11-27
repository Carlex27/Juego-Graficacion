from settings import *


class PlayerInterface(pygame.sprite.Sprite):
    def __init__(self, player, display_surface):
        super().__init__()
        self.display_surface = display_surface
        self.player = player
        self.life_icon = pygame.image.load(join('Assets','images','heart.gif')).convert_alpha()
        self.life_icon = pygame.transform.scale(self.life_icon, (50,50))
    
    def draw_life_counter(self):
        self.display_surface.blit(self.life_icon, (30,30))

        font = pygame.font.Font(None, 40)
        life_text = font.render(f"x{self.player.lifes}", True, (255,255,255))

        self.display_surface.blit(life_text, (80,40))

    def draw_score(self):
        font = pygame.font.Font(None, 40)  # Cambia el tamaño si es necesario
        score_text = font.render(f"Score: {self.player.score}", True, (255, 255, 255))  # Texto blanco
        self.display_surface.blit(score_text, (20, 80))  # Ajusta la posición según sea necesario

    def update(self):
        self.draw_life_counter()
        self.draw_score()