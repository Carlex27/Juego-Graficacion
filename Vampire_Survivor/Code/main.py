from settings import *
from Player import Player
from sprites import *

from groups import AllSprites
from Interfaces import *

class Game:
    def __init__(self):
        #setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vampire Survivor")
        self.clock = pygame.time.Clock()
        self.running = True
        
        #Interface inicial
        self. show_start_screen()

        #groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        #Gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 150

        #Enemy timer a
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

        self.load_images()
        self.setup()

    def show_start_screen(self):
        start_screen = StartScreen(self.display_surface)
        start_screen.run()

    def kill_entities(self):
            self.all_sprites.empty()

    def game_over(self):
        # Mostrar la pantalla de Game Over
        self.kill_entities()
        self.music.stop()
        game_over_screen = GameOverScreen(self.display_surface)
        self.game_over_music.play(loops=-1)
        game_over_screen.run()

        # Reiniciar el juego después de la pantalla de Game Over
        self.setup()
        self.running = True
        self.game_over_music.stop()

    def load_images(self):
        self.enemy_frames = {}
        self.boss_frames = []
        
        self.bullet_surf = pygame.image.load(join('Assets','images','gun','bullet.png')).convert_alpha()

        enemy_folders = list(walk(join('Assets','images','enemies')))[0][1]
        for folder in enemy_folders:
            for folder_path, _, file_names in walk(join('Assets', 'images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()

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

    def setup(self):
        self.music.play(loops=-1)
        map = load_pygame(join('Assets','data','maps','Map.tmx'))
        
        for x,y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites))

        for x,y, image in map.get_layer_by_name('High').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites))

        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x,obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x,obj.y), pygame.Surface((obj.width,obj.height)), (self.collision_sprites))

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x,obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            elif obj.name == 'Enemy':
                self.spawn_positions.append((obj.x,obj.y))
            else:
                self.boss_spawn_positions.append((obj.x,obj.y))
            self.player_interface = PlayerInterface(self.player, self.display_surface)
    
    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

#Metodos de colisiones
    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def bulllet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    bullet.kill()
                    for sprite in collision_sprites:
                        if isinstance(sprite, Enemy):
                            sprite.kill()
                        if isinstance(sprite, Boss):
                            sprite.health -= 1
                            if sprite.health <= 0:
                                sprite.kill()
                        self.player.score += 1

    def player_collision(self):
        collision_sprite = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
        if collision_sprite:
            self.player.lifes -= 1

            for enemy in collision_sprite:
                enemy.kill()

            self.hurt_sound.play()

            if self.player.lifes <= 0:
                self.game_over()

#Eventos
    def check_score(self):
        if self.player.score >= self.next_score:
            pygame.event.post(pygame.event.Event(self.enemy_speed_event))  # Publicar evento
            self.next_score += self.intervalo_score  # Configurar el siguiente umbral
        
        # Evento de aparición del jefe
        if self.player.score >= self.next_boss_score:
            pygame.event.post(pygame.event.Event(self.boss_event))  # Publicar evento para boss
            self.next_boss_score += self.boss_score# Configurar el siguiente umbral para el boss

    def increase_enemy_speed(self):
        for enemy in self.enemy_sprites:
            enemy.speed *= 1.05  # Incremento del 5%

    def spawn_boss(self):
        boss_position = choice(self.boss_spawn_positions)  # Posición inicial del boss
        Boss(
            boss_position,
            self.boss_frames,  # Usa los sprites del jefe cargados
            (self.all_sprites, self.enemy_sprites),  # El boss pertenece a los mismos grupos que los enemigos
            self.player,
            self.collision_sprites
        )

    def run(self):
        while self.running:
            #dtd
            dt = self.clock.tick(240) / 1000
            #event loopa
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
                if event.type == self.enemy_speed_event:
                    self.increase_enemy_speed()
                if event.type == self.boss_event:
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