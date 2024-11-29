from settings import *
from Player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from random import choice
from groups import AllSprites
from Interfaces import PlayerInterface

class Game:
    def __init__(self):
        #setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vampire Survivor")
        self.clock = pygame.time.Clock()
        self.running = True
        

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
        self.spawn_positions = []

        #Audio
        self.shoot_sound = pygame.mixer.Sound(join('Assets','audio','shoot.wav'))
        self.shoot_sound.set_volume(0.35)
        self.impact_sound = pygame.mixer.Sound(join('Assets','audio','impact.ogg'))
        self.music = pygame.mixer.Sound(join('Assets','audio','music.wav'))
        self.music.play(loops=-1)
        self.music.set_volume(0.3)
        self.hurt_sound = pygame.mixer.Sound(join('Assets','audio','classic_hurt.mp3'))
        self.hurt_sound.set_volume(0.4)

        #Interface
        
        
        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('Assets','images','gun','bullet.png')).convert_alpha()

        folders = list(walk(join('Assets','images','enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('Assets', 'images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()

                    scaled_surf = pygame.transform.scale(surf, (surf.get_width() // 1.5, surf.get_height() // 1.5))
                    self.enemy_frames[folder].append(scaled_surf)
        

    def setup(self):
        map = load_pygame(join('Assets','data','maps','world.tmx'))
        
        for x,y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites))

        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x,obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x,obj.y), pygame.Surface((obj.width,obj.height)), (self.collision_sprites))

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x,obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x,obj.y))
            self.player_interface = PlayerInterface(self.player, self.display_surface)
    

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

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
                        sprite.destroy()
                        self.player.score += 1

    def player_collision(self):
        collision_sprite = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
        if collision_sprite:
            self.player.lifes -= 1
            for enemy in collision_sprite:
                if isinstance(enemy, Enemy) and enemy.is_invulnerable():
                    continue
                enemy.kill()
            if self.player.lifes <= 0:
                self.running = False
            self.hurt_sound.play()

    def run(self):
        while self.running:
            #dtd
            dt = self.clock.tick(120) / 1000
            #event loopa
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
            #update
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bulllet_collision()
            self.player_collision()
            
            #render
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            self.player_interface.update()
            pygame.display.update()
            
        
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()