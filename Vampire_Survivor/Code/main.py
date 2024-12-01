
#Importacion de librerias necesarias
from settings import *                    #Configuracion de la ventana
from Player import Player                 #Jugador
from sprites import *                     #Sprites

from groups import AllSprites             #Grupos de sprites
from Interfaces import *                  #Interfaz del jugador

#Clase principal del juego
class Game:
    def __init__(self):
        #setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vampire Survivor")
        self.clock = pygame.time.Clock()
        self.running = True
        
        #Interface inicial
        self.show_start_screen()

        #Grupos
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        #Gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 150

        #Enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event,350)

        #Enemy speed event
        self.enemy_speed_event = pygame.event.custom_type()
        self.intervalo_score = 50
        self.next_score = self.intervalo_score
        
        #Boss Event
        self.boss_event = pygame.event.custom_type()
        self.boss_score = 250
        self.next_boss_score = self.boss_score

        #Posiciones de los enemigos y bosses
        self.spawn_positions = []
        self.boss_spawn_positions = []

        #Audio
        self.shoot_sound = pygame.mixer.Sound(join('Assets','audio','shoot.wav'))
        self.shoot_sound.set_volume(0.15)
        self.impact_sound = pygame.mixer.Sound(join('Assets','audio','impact.ogg'))
        self.music = pygame.mixer.Sound(join('Assets','audio','main.mp3'))
        
        self.music.set_volume(0.5)
        self.hurt_sound = pygame.mixer.Sound(join('Assets','audio','classic_hurt.mp3'))
        self.hurt_sound.set_volume(0.7)
        
        self.game_over_music = pygame.mixer.Sound(join('Assets','audio','game_over.mp3'))
        self.game_over_music.set_volume(0.3)

        #Se cargan las imágenes
        self.load_images()
        self.setup()

#Metodo que muestra la pantalla de inicio
    def show_start_screen(self):
        start_screen = StartScreen(self.display_surface) #Se crea una instancia de la pantalla de inicio
        start_screen.run()

#Metodo que elimina todos los sprites cuando pierdes
    def kill_entities(self):
            self.all_sprites.empty()

#Metodo que muestra la pantalla de Game Over
    def game_over(self):
        # Mostrar la pantalla de Game Over
        self.kill_entities()                    #Se eliminan todos los sprites
        self.music.stop()                       #Se detiene el sonido de la musica
        game_over_screen = GameOverScreen(self.display_surface)     #Se crea una instancia de la pantalla de Game Over
        self.game_over_music.play(loops=-1)     #Se reproduce la musica de Game Over
        game_over_screen.run()                  #Se muestra la pantalla de Game Over

        # Reiniciar el juego después de la pantalla de Game Over
        self.setup()
        self.running = True
        self.game_over_music.stop()

#Metodo que carga los sprites de los enemigos y bosses
    def load_images(self):
        self.enemy_frames = {}                  #Se crea un diccionario para guardar los frames de los enemigos
        self.boss_frames = []                   #Se crea una lista para guardar los frames de los bosses
        
        #Se carga el sprite de la bala
        self.bullet_surf = pygame.image.load(join('Assets','images','gun','bullet.png')).convert_alpha() 

        #Se recorren los directorios de los enemigos y se cargan los sprites
        enemy_folders = list(walk(join('Assets','images','enemies')))[0][1]

        for folder in enemy_folders:            #Se recorren los directorios de los enemigos
            for folder_path, _, file_names in walk(join('Assets', 'images', 'enemies', folder)): 
                self.enemy_frames[folder] = []      #Adentro del diccionario se crea un arreglo para las direcciones de los frames
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):    #Se ordenan los frames por el numero de la imagen
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    #Se escala el frame
                    scaled_surf = pygame.transform.scale(surf, (surf.get_width() // 1.5, surf.get_height() // 1.5))
                    self.enemy_frames[folder].append(scaled_surf)
        
        # Cargar jefe (boss)
        boss_folder_path = join('Assets', 'images','boss')  # Ruta directa a la carpeta de boss
        for file_name in sorted(listdir(boss_folder_path), key=lambda name: int(name.split('.')[0])):
            full_path = join(boss_folder_path, file_name)
            surf = pygame.image.load(full_path).convert_alpha()

            # Escalar para el jefe (puedes ajustar el tamaño si es necesario)
            scaled_surf = pygame.transform.scale(surf, (surf.get_width() // 1.2, surf.get_height() // 1.2))
            self.boss_frames.append(scaled_surf)

#Metodo que configura el juego y carga el mapa
    def setup(self):
        self.music.play(loops=-1)
        #Se obtiene el mapa creado en Tiled
        map = load_pygame(join('Assets','data','maps','Map.tmx'))
        
        #Se importan todas las capas del mapa por separado
        #La capa ground
        for x,y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites))
        #La capa High
        for x,y, image in map.get_layer_by_name('High').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites))
        #La capa Objects
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x,obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        #La capa Collisions
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x,obj.y), pygame.Surface((obj.width,obj.height)), (self.collision_sprites))
        #La capa Entities
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':        #Entidad del jugador
                self.player = Player((obj.x,obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            elif obj.name == 'Enemy':       #Entidad del enemigo
                self.spawn_positions.append((obj.x,obj.y))
            else:                           #Entidad del boss
                self.boss_spawn_positions.append((obj.x,obj.y))
            self.player_interface = PlayerInterface(self.player, self.display_surface)

#Metodos que obtiene la accion de disparar del mouse
    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:    #Si esta precionado el click izquierdo
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            #Se crea una bala
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

#Metodo timer del arma, para controlar la velocidad de disparo
    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

#Metodo para detectar las colisiones de las balas con los enemigos
    def bulllet_collision(self):
        if self.bullet_sprites:   #Si hay balas
            for bullet in self.bullet_sprites:   #Se recorren las balas
                #Se verifica si existe una colision
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:   #Si existe una colision
                    self.impact_sound.play()    
                    bullet.kill()
                    for sprite in collision_sprites:        #Se recorren las colisiones
                        if isinstance(sprite, Enemy):       #Si es un enemigo se elimina
                            sprite.kill()
                        if isinstance(sprite, Boss):        #Si es un boss se baja una vida al boss
                            sprite.health -= 1
                            if sprite.health <= 0:
                                sprite.kill()
                        self.player.score += 1              #Se incrementa el puntaje del jugador

#Metodo para detectar las colisiones del jugador con los enemigos
    def player_collision(self):
        #Se verifica si hay colisiones
        collision_sprite = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
        if collision_sprite:    #Si hay colisiones
            self.player.lifes -= 1    #Se baja una vida al jugador
            for enemy in collision_sprite:    #Se recorren las colisiones
                enemy.kill()                  #Se eliminan los enemigos
            self.hurt_sound.play()
            if self.player.lifes <= 0:        #Si las vidas del jugador se bajan a 0
                self.game_over()              #Se muestra la pantalla de Game Over

#Eventos

#Metodo que verifica el puntaje del jugador para activar eventos
    def check_score(self):
        #Evento de aumento de velocidad de los enemigos
        if self.player.score >= self.next_score:
            pygame.event.post(pygame.event.Event(self.enemy_speed_event))  # Publicar evento
            self.next_score += self.intervalo_score  # Configurar el siguiente umbral
        
        # Evento de aparición del jefe
        if self.player.score >= self.next_boss_score:
            pygame.event.post(pygame.event.Event(self.boss_event))  # Publicar evento para boss
            self.next_boss_score += self.boss_score# Configurar el siguiente umbral para el boss

#Metodo que aumenta la velocidad de los enemigos
    def increase_enemy_speed(self):
        for enemy in self.enemy_sprites:
            enemy.speed *= 1.05  # Incremento del 5%

#Metodo que crea un boss
    def spawn_boss(self):
        boss_position = choice(self.boss_spawn_positions)  # Posición inicial del boss
        Boss(
            boss_position,
            self.boss_frames,  # Usa los sprites del jefe cargados
            (self.all_sprites, self.enemy_sprites),  # El boss pertenece a los mismos grupos que los enemigos
            self.player,
            self.collision_sprites
        )

#Metodo run principal del juego
    def run(self):
        while self.running:
            #Delta time
            dt = self.clock.tick(240) / 1000
            #Eventos del juego
            for event in pygame.event.get():
                if event.type == pygame.QUIT:       #Se detecta el evento de salir
                    self.running = False
                if event.type == self.enemy_event:  #Se detecta el evento de crear un enemigo
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
                if event.type == self.enemy_speed_event:    #Se detecta el evento de aumento de velocidad de los enemigos
                    self.increase_enemy_speed()
                if event.type == self.boss_event:           #Se detecta el evento de crear un boss
                    self.spawn_boss()
            #update
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bulllet_collision()
            self.player_collision()
            self.check_score()
            
            #render
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            self.player_interface.update()
            pygame.display.update()
            
        
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()