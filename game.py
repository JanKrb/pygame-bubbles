import pygame
import os
import random

class Settings:
    # Window settings
    window_height = 750
    window_width = 1200
    window_fps = 60
    window_caption = "Bubbles"

    @staticmethod
    def get_size() -> tuple[int, int]:
        return Settings.window_width, Settings.window_height
    
    # Paths
    path_working_directory = os.path.dirname(os.path.abspath(__file__))
    path_assets = os.path.join(path_working_directory, 'assets')
    path_images = os.path.join(path_assets, 'images')
    path_sounds = os.path.join(path_assets, 'sounds')

    @staticmethod
    def create_image_path(image_name) -> str:
        return os.path.join(Settings.path_images, image_name)
    
    @staticmethod
    def create_sound_path(sound_name) -> str:
        return os.path.join(Settings.path_sounds, sound_name)
    
    # Bubble settings
    bubble_radius = 5
    bubble_speed = 20
    bubble_spawn_margin = 10
    bubble_spawn_speed = (1, 4)
    bubble_animation_speed = 1
    bubbles_max_initial = 5

    # Sound settings
    volume = 0.1

class Background(pygame.sprite.Sprite):
    def __init__(self, image_name='background.jpg') -> None:
        super().__init__()

        self.image = pygame.image.load(Settings.create_image_path(image_name))
        self.image = pygame.transform.scale(self.image, Settings.get_size())
    
    def draw(self, screen):
        screen.blit(self.image, (0, 0))

class Bubble(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

        self.images = Bubble.get_bubble_images()
        self.state = 0 # Current image
        self.killed = False

        self.image = self.images[self.state]
        self.image = pygame.transform.scale(self.images[self.state], (Settings.bubble_radius, Settings.bubble_radius))
        self.rect = self.image.get_rect()

        self.expansion_rate = random.randint(*Settings.bubble_spawn_speed)

        self.rect.center = (
            random.randint(Settings.bubble_radius + Settings.bubble_spawn_margin, Settings.window_width - (Settings.bubble_radius + Settings.bubble_spawn_margin)),
            random.randint(Settings.bubble_radius + Settings.bubble_spawn_margin, Settings.window_height - (Settings.bubble_radius + Settings.bubble_spawn_margin))
        )

    @staticmethod
    def get_bubble_images() -> list[pygame.Surface]:
        bubble_images = ['bubble1.png', 'bubble2.png', 'bubble3.png', 'bubble4.png', 'bubble5.png', 'bubble6.png', 'bubble7.png']
        bubble_images.sort()
        return [pygame.image.load(Settings.create_image_path(img)) for img in bubble_images]
    
    def kill(self, looped_call=True) -> None:
        self.killed = True

        if not looped_call:
            pygame.mixer.Sound.play(game.sound_pop_bubble)

        if game.bubble_animation_frames <= Settings.bubble_animation_speed:
            game.bubble_animation_frames += 1
            return
        else:
            game.bubble_animation_frames = 0

        self.state += 1
        old_center = self.rect.center
        old_size = self.rect.size

        self.image = self.images[self.state]
        self.image = pygame.transform.scale(self.image, old_size)
        self.rect = self.image.get_rect()
        self.rect.center = old_center


        if self.state > len(self.images) - 2:
            super().kill() # Kill after animation is done

    def increase_size(self) -> None:
        center = self.rect.center
        self.image = pygame.transform.scale(self.images[self.state], (self.rect.width + self.expansion_rate, self.rect.height + self.expansion_rate))
        self.rect = self.image.get_rect()
        self.rect.center = center

    def is_hovered(self, mouse_pos) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    def update(self):
        if self.killed:
            self.kill()
            return            

class Game:
    def __init__(self) -> None:
        os.environ['SDL_VIDEO_WINDOW_CENTERED'] = '1'
        pygame.init()
        pygame.display.set_caption(Settings.window_caption)
        pygame.mouse.set_cursor(*pygame.cursors.diamond)

        self.screen = pygame.display.set_mode(Settings.get_size())
        self.clock = pygame.time.Clock()
        self.running = True

        self.bubble_speed = Settings.bubble_speed

        self.background = Background()
        self.bubbles = pygame.sprite.Group()
        self.bubble_animation_frames = 0
        self.bubbles_limit = Settings.bubbles_max_initial

        pygame.mixer.music.set_volume(Settings.volume) 
        self.sound_pop_bubble = pygame.mixer.Sound(Settings.create_sound_path('pop.mp3'))

    def run(self) -> None:
        while self.running:
            self.clock.tick(Settings.window_fps)
            self.handle_events()
            self.update()
            self.draw()

    def handle_keydown_events(self, event) -> None:
        if event.key == pygame.K_ESCAPE:
            self.running = False

    def handle_mouse_events(self, event) -> None:
        if event.button == 1:
            for bubble in self.bubbles:
                if bubble.is_hovered(event.pos):
                    bubble.kill(looped_call=False)
                    break

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown_events(event)    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_events(event)

    def respawn_bubbles(self) -> None:
        if len(self.bubbles.sprites()) <= self.bubbles_limit:
            self.bubbles.add(Bubble())

    def update(self) -> None:
        self.respawn_bubbles()

        self.bubbles.update()

        self.bubble_speed -= 1

        if self.bubble_speed <= 0:
            self.bubble_speed = Settings.bubble_speed
            for bubble in self.bubbles.sprites():
                bubble.increase_size()

        any_bubble_hovered = False
        for bubble in self.bubbles.sprites():
            if bubble.is_hovered(pygame.mouse.get_pos()):
                any_bubble_hovered = True

            pygame.mouse.set_cursor(*pygame.cursors.broken_x if any_bubble_hovered else pygame.cursors.diamond)

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))

        self.background.draw(self.screen)
        self.bubbles.draw(self.screen)

        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.run()