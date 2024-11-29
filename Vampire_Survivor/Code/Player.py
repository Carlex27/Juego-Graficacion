from settings import *

#Clase del jugador
class Player(pygame.sprite.Sprite):
    #Metodo constructor
    def __init__(self, pos ,groups, collision_sprites):
        super().__init__(groups)
        self.score = 0      #Puntos
        self.lifes = 5      #Vidas
        self.load_images()  #Cargar sprites

        #Estado del jugador e indice del sprite
        self.state, self.frame_index = 'down', 0
        self.image = pygame.image.load(join("Assets","images","player","down","0.png"))
        #Rect del jugador
        self.rect = self.image.get_frect(center = pos)
        #Rect del jugador con el cuerpo
        self.hitbox_rect = self.rect.inflate(0, -30)

        #Movimiento del jugador
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites #Sprites en los que puede colisionar

    #Se cargan los sprites del jugador
    def load_images(self):
        #Estados que tiene el jugador
        self.frames = {'left': [], 'right': [], 'down': [], 'up': []}
        #Se recorren los estados y se cargan los sprites
        for state in self.frames.keys():
            for folder_path, _, file_names in walk(join('Assets', 'images', 'player', state)):
                if file_names:
                    #Se ordenan los sprites por el numero de la imagen
                    for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])): #Se separa el nombre de la imagen
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    #Controles del jugador
    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction

    #Movimiento del jugador
    def move(self,dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    #Colisiones del jugador
    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    #Verifica si el movimiento es hacia la derecha 
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    #Verifica si el movimiento es hacia la izquierda
                    elif self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                elif direction == 'vertical':
                    #Verifica si el movimiento es hacia abajo
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                    #Verifica si el movimiento es hacia arriba
                    elif self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom

    #Animacion del jugador
    def animate(self,dt):
        #Get state
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        elif self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        #Animate
        self.frame_index = self.frame_index + 5 * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]
    
    #Se actualiza el sprite del jugador
    def update(self,dt):
        self.input()
        self.move(dt)
        self.animate(dt)
