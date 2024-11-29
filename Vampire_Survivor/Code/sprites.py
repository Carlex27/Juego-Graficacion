from settings import *
from math import atan2, degrees

#Clase para los tiles y objetos del mapa
class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos,surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

#Clase para las colisiones entre sprites
class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

#Clase para el arma del jugador
class Gun(pygame.sprite.Sprite):
    #Metodo constructor
    def __init__(self, player ,groups):
        self.player = player            #Conexion con el jugador
        self.distance = 60              #Distancia entre el arma y el jugador
        self.player_direction = pygame.Vector2(1,0)     #Guarda la direccion del jugador

        #Sprite setup
        super().__init__(groups)
        #Se carga el sprite del arma
        self.gun_surf = pygame.image.load(join('Assets','images','gun','gun1.png')).convert_alpha()
        self.image = self.gun_surf      #Sprite del arma
        self.rect = self.image.get_frect(center = self.player.rect.center + self.player_direction * self.distance)   #Rect del arma

    #Metodo para rotar el arma dependiendo del eje X del jugador
    def rotate_gun(self):
        #Se obtiene el angulo de rotacion del arma
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90

        #Se rota el sprite del arma
        if self.player_direction.x > 0:         #Si se apunta hacia la derecha
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:                                   #Si se apunta hacia la izquierda
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    #Se obtiene la direccion del arma conforme al movimiento del mouse
    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()

    #Metodo que actualiza el sprite del arma
    def update(self, _):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance
        

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000

        self.direction = direction
        self.speed = 1200

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self,pos,frames,groups,player,collision_sprites):
        super().__init__(groups)
        self.player = player
        #image
        self.frames, self.frame_index = frames,0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6

        #Rect
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-20,-40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 300

        #Timer
        self.death_time = 0
        self.death_duration = 200

        self.spawn_time = pygame.time.get_ticks()

    def animate(self,dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def move(self,dt):
        #Get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()
        #Update the rect position
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    
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

    def destroy(self):
        #Start a timer
        self.death_time = pygame.time.get_ticks()
        #Change the image
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf
    
    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time > self.death_duration:
            self.kill()

    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()