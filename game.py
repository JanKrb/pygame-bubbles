from math import sqrt
from typing import Tuple
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
    bubble_spawn_speed_initial = (1, 4)
    bubble_animation_speed = 1
    bubbles_max_initial = 5

    # Sound settings
    volume = 0.1

    # Fonts
    font_pause = ('arialblack', 64)
    font_points = ('arialblack', 28)

    # Strings
    title_points = "Points: %s"

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
        self.state = 0  # Current image
        self.killed = False

        self.image = self.images[self.state]
        self.image = pygame.transform.scale(self.images[self.state],
                                            (Settings.bubble_radius * 2, Settings.bubble_radius * 2))
        self.rect = self.image.get_rect()
        self.radius = self.rect.width // 2

        self.expansion_rate = random.randint(*game.bubble_spawn_speed)

        self.rect.center = Bubble.generate_next_free_position()

    @staticmethod
    def get_bubble_images() -> list[pygame.Surface]:
        bubble_images = ['bubble1.png', 'bubble2.png', 'bubble3.png', 'bubble4.png', 'bubble5.png', 'bubble6.png',
                         'bubble7.png']
        bubble_images.sort()
        return [pygame.image.load(Settings.create_image_path(img)) for img in bubble_images]

    @staticmethod
    def generate_next_free_position(depth=0) -> tuple[int, int]:
        random_pos = (
            random.randint(0, Settings.window_width - Settings.bubble_radius - 10),
            random.randint(0, Settings.window_height - Settings.bubble_radius - 10)
        )

        if not Bubble._check_if_pos_is_valid(random_pos) and depth <= 50:
            return Bubble.generate_next_free_position(depth=depth + 1)

        return random_pos

    @staticmethod
    def _check_if_pos_is_valid(position):
        bubbles = [(bubble.rect.center, bubble.rect.width) for bubble in game.bubbles.sprites()]

        for b in bubbles:
            b_pos = b[0]
            dist_x = abs(b_pos[0] - position[0])
            dist_y = abs(b_pos[1] - position[1])
            dist = sqrt(dist_x ** 2 + dist_y ** 2)

            if dist <= b[1] // 2 + 10:
                return False

        return True

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
            super().kill()  # Kill after animation is done

    def increase_size(self) -> None:
        center = self.rect.center
        self.image = pygame.transform.scale(self.images[self.state], (
        self.rect.width + self.expansion_rate, self.rect.height + self.expansion_rate))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.radius = self.rect.width // 2

    def is_hovered(self, mouse_pos) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def check_bubble_collision(self):
        # TODO: Game Over
        hits = pygame.sprite.spritecollide(self, game.bubbles, False, pygame.sprite.collide_circle)

        if len(hits) > 1:
            for hit in hits:
                hit.kill(looped_call=False)

    def check_window_collision(self):
        # TODO: Game Over
        left_pos = self.rect.center[0] - self.rect.width // 2
        if left_pos < 0: self.kill(looped_call=False)

        right_pos = self.rect.center[0] + self.rect.width // 2
        if right_pos > Settings.window_width: self.kill(looped_call=False)

        top_pos = self.rect.center[1] - self.rect.height // 2
        if top_pos < 0: self.kill(looped_call=False)

        bottom_pos = self.rect.center[1] + self.rect.height // 2
        if bottom_pos > Settings.window_height: self.kill(looped_call=False)

    def check_collision(self):
        self.check_bubble_collision()
        self.check_window_collision()

    def update(self):
        if self.killed:
            self.kill()
            return

        self.check_collision()


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
        self.bubble_spawn_speed = Settings.bubble_spawn_speed_initial

        self.game_over = False
        self.pause = False
        self.points = 0

        pygame.mixer.music.set_volume(Settings.volume)
        self.sound_pop_bubble = pygame.mixer.Sound(Settings.create_sound_path('pop.mp3'))

    def run(self) -> None:
        while self.running:
            self.clock.tick(Settings.window_fps)
            self.handle_events()

            if not self.pause and not self.game_over:
                self.update()
                self.draw()
            elif self.pause:
                self.draw_pause()
            elif self.game_over:
                self.draw_game_over()

    def handle_keydown_events(self, event) -> None:
        if event.key == pygame.K_ESCAPE:
            self.running = False

    def handle_mouse_events(self, event) -> None:
        if event.button == 1:
            for bubble in self.bubbles:
                if bubble.is_hovered(event.pos):
                    bubble.kill(looped_call=False)
                    self.points += bubble.rect.width // 2  # Points depending on bubble size
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

        self.draw_points()

        pygame.display.flip()

    def draw_pause(self) -> None:
        self.screen.fill((0, 0, 0))
        pygame.display.flip()

    def draw_gameover(self) -> None:
        self.screen.fill((0, 0, 0))
        pygame.display.flip()

    def draw_points(self) -> None:
        font = pygame.font.SysFont(Settings.font_points[0], Settings.font_points[1])
        points_text = font.render(Settings.title_points.replace('%s', str(self.points)), True, (255, 255, 255))
        points_text_rect = points_text.get_rect()
        points_text_rect.top = Settings.window_height - 50
        points_text_rect.left = 25

        self.screen.blit(points_text, points_text_rect)


if __name__ == '__main__':
    game = Game()
    game.run()
