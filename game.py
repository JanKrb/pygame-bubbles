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

class Background(pygame.sprite.Sprite):
    def __init__(self, image_name='background.jpg') -> None:
        super().__init__()

        self.image = pygame.image.load(Settings.create_image_path(image_name))
        self.image = pygame.transform.scale(self.image, Settings.get_size())
    
    def draw(self, screen):
        screen.blit(self.image, (0, 0))

class Game:
    def __init__(self) -> None:
        os.environ['SDL_VIDEO_WINDOW_CENTERED'] = '1'
        pygame.init()
        pygame.display.set_caption(Settings.window_caption)

        self.screen = pygame.display.set_mode(Settings.get_size())
        self.clock = pygame.time.Clock()
        self.running = True

        self.background = Background()

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

    def update(self) -> None:
        pass

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))

        self.background.draw(self.screen)

        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.run()