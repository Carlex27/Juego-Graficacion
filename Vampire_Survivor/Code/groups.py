from settings import *

#Clase que contiene un grupo personalizado de sprites
class AllSprites(pygame.sprite.Group):
    #Metodo constructor
    def __init__(self):
        super().__init__()
        #Ventana
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        
    #Metodo que dibuja los sprites en la ventana
    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)

        #Se obtiene los sprites de los tiles y los objetos
        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'ground')]
        object_sprites = [sprite for sprite in self if not hasattr(sprite, 'ground')]

        #Cargar los tiles y los objetos en el mapa
        for layer in [ground_sprites, object_sprites]:
            for sprite in sorted(layer, key=lambda sprite: sprite.rect.centery):
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
