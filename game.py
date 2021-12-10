import pygame
import os

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
    bubble_speed = 1000 / 60 # 60x per second
    bubble_spawn_margin = 10
    bubble_spawn_speed = (1, 4)

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

        self.image = self.images[self.state]
        self.image = pygame.transform.scale(self.images[self.state], (Settings.bubble_radius, Settings.bubble_radius))
        self.rect = self.image.get_rect()

    @staticmethod
    def get_bubble_images() -> list[pygame.Surface]:
        images_in_path = os.listdir(Settings.path_images)
        bubble_images = [img for img in images_in_path if img.startswith('bubble')]
        return [pygame.image.load(Settings.create_image_path(img)) for img in bubble_images]
    
    def kill(self) -> None:
        self.state += 1
        self.image = self.images[self.state]
        self.rect = self.image.get_rect()

        if self.state > len(self.images) - 1:
            super().kill() # Kill after animation is done

    def increase_size(self) -> None:
        center = self.rect.center
        self.image = pygame.transform.scale(self.images[self.state], (self.rect.width + Settings.bubble_speed, self.rect.height + Settings.bubble_speed))
        self.rect = self.image.get_rect()
        self.rect.center = center

    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    def update(self):
        pass

class Game:
    def __init__(self) -> None:
        os.environ['SDL_VIDEO_WINDOW_CENTERED'] = '1'
        pygame.init()
        pygame.display.set_caption(Settings.window_caption)

        self.screen = pygame.display.set_mode(Settings.get_size())
        self.clock = pygame.time.Clock()
        self.running = True

        self.bubble_speed = Settings.bubble_speed

        self.background = Background()
        self.bubbles = pygame.sprite.Group()

        self.bubbles.add(Bubble())

    def run(self) -> None:
        while self.running:
            self.clock.tick(Settings.window_fps)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def respawn_bubbles(self) -> None:
        pass

    def update(self) -> None:
        self.respawn_bubbles()

        self.bubbles.update()

        self.bubble_speed -= 1

        # Increase bubble size
        if self.bubble_speed <= 0:
            self.bubble_speed = Settings.bubble_speed

            for bubble in self.bubbles.sprites():
                bubble.increase_size()

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))

        self.background.draw(self.screen)
        self.bubbles.draw(self.screen)

        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.run()