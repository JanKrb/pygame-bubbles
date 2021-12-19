# https://pylint.pycqa.org/en/latest/technical_reference/features.html
# pylint: disable=E1101
# pylint: disable=C0115
# pylint: disable=C0114
# pylint: disable=R0902
# pylint: disable=R0902
# pylint: disable=W0511
# pylint: disable=E1136

import os
import random
from math import sqrt
import pygame

class Settings:
    # Window settings
    window_height = 750
    window_width = 1200
    window_fps = 60
    window_caption = "Bubbles"

    @staticmethod
    def get_size() -> tuple[int, int]:
        """
        Returns the window size as a tuple
        """
        return Settings.window_width, Settings.window_height

    # Paths
    path_working_directory = os.path.dirname(os.path.abspath(__file__))
    path_assets = os.path.join(path_working_directory, 'assets')
    path_images = os.path.join(path_assets, 'images')
    path_sounds = os.path.join(path_assets, 'sounds')

    @staticmethod
    def create_image_path(image_name) -> str:
        """
        Generate absolute path to image
        """
        return os.path.join(Settings.path_images, image_name)

    @staticmethod
    def create_sound_path(sound_name) -> str:
        """
        Generate absolute path to sound
        """
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
    font_gameover = ('arialblack', 64)
    font_score = ('arialblack', 48)
    font_highscore = ('arialblack', 48)
    font_restart = ('arialblack', 32)
    font_points = ('arialblack', 28)

    # Strings
    title_points = "Points: %s"
    title_highscore = "Highscore: %s"


class Background(pygame.sprite.Sprite):
    def __init__(self, image_name='background.jpg') -> None:
        super().__init__()

        self.image = pygame.image.load(Settings.create_image_path(image_name))
        self.image = pygame.transform.scale(self.image, Settings.get_size())

    def draw(self, screen):
        """
        Draw sprite on screen at position 0/0
        """
        screen.blit(self.image, (0, 0))

    def update(self):
        """
        Update sprite every [fps] frames
        """

class Cursor(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

        self.cursors = [
            pygame.image.load(Settings.create_image_path('cursor1.png')),
            pygame.image.load(Settings.create_image_path('cursor2.png'))
        ]

        self.image = self.cursors[0]
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()

    def select_cursor(self, cursor_number):
        """
        Select cursor from index
        """

        old_rect = self.rect
        self.image = self.cursors[cursor_number]
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = old_rect

    def draw(self, screen):
        """
        Draw sprite on screen at position 0/0
        """

        screen.blit(self.image, self.rect)

    def update(self, pos):
        """
        Update cursor position
        """

        self.rect.topleft = pos

class Bubble(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

        self.images = Bubble.get_bubble_images()
        self.state = 0  # Current image
        self.killed = False

        self.image = self.images[self.state]
        self.image = pygame.transform.scale(
            self.images[self.state], (Settings.bubble_radius * 2, Settings.bubble_radius * 2))
        self.rect = self.image.get_rect()
        self.radius = self.rect.width // 2

        self.expansion_rate = random.randint(*game.bubble_spawn_speed)

        self.rect.center = Bubble.generate_next_free_position()

    @staticmethod
    def get_bubble_images() -> list[pygame.Surface]:
        """
        Get all images used in the animation
        """

        bubble_images = sorted(['bubble1.png',
                                'bubble2.png',
                                'bubble3.png',
                                'bubble4.png',
                                'bubble5.png',
                                'bubble6.png',
                                'bubble7.png'])
        return [pygame.image.load(Settings.create_image_path(img))
                for img in bubble_images]

    @staticmethod
    def generate_next_free_position(depth=0) -> tuple[int, int]:
        """
        Generate random position on the screen and check if valid
        """

        random_pos = (
            random.randint(
                0,
                Settings.window_width -
                Settings.bubble_radius -
                10),
            random.randint(
                0,
                Settings.window_height -
                Settings.bubble_radius -
                10))

        if not Bubble._check_if_pos_is_valid(random_pos) and depth <= 50:
            return Bubble.generate_next_free_position(depth=depth + 1)

        return random_pos

    @staticmethod
    def _check_if_pos_is_valid(position):
        """
        Check if chosen position is far enough away from another bubble
        """

        bubbles = [(bubble.rect.center, bubble.rect.width)
                   for bubble in game.bubbles.sprites()]

        for bubble in bubbles:
            bubble_pos = bubble[0]
            dist_x = abs(bubble_pos[0] - position[0])
            dist_y = abs(bubble_pos[1] - position[1])
            dist = sqrt(dist_x ** 2 + dist_y ** 2)

            if dist <= bubble[1] // 2 + 10:
                return False

        return True

    def kill(self, looped_call=True) -> None:
        """
        Overload the kill method, to play the animation first.
        Initiate the animation if looped_call=False
        """

        self.killed = True

        if not looped_call:
            pygame.mixer.Sound.play(game.sound_pop_bubble)

        if game.bubble_animation_frames <= Settings.bubble_animation_speed:
            game.bubble_animation_frames += 1
            return

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
        """
        Increase the size of the bubble by it's expansion rate
        """

        center = self.rect.center
        self.image = pygame.transform.scale(self.images[self.state], (
            self.rect.width + self.expansion_rate, self.rect.height + self.expansion_rate))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.radius = self.rect.width // 2

    def is_hovered(self, mouse_pos) -> bool:
        """
        Check if bubble is hovered by cursor
        """

        return self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """
        Draw sprite on screen
        """

        screen.blit(self.image, self.rect)

    def check_bubble_collision(self):
        """
        Check if sprite collides with another sprite/bubble
        """

        hits = pygame.sprite.spritecollide(
            self, game.bubbles, False, pygame.sprite.collide_circle)

        if len(hits) > 1:
            game.game_over = True

    def check_window_collision(self):
        """
        Check if sprite collides with edge
        """

        left_pos = self.rect.center[0] - self.rect.width // 2
        if left_pos < 0:
            game.game_over = True

        right_pos = self.rect.center[0] + self.rect.width // 2
        if right_pos > Settings.window_width:
            game.game_over = True

        top_pos = self.rect.center[1] - self.rect.height // 2
        if top_pos < 0:
            game.game_over = True

        bottom_pos = self.rect.center[1] + self.rect.height // 2
        if bottom_pos > Settings.window_height:
            game.game_over = True

    def check_collision(self):
        """
        Central collision check, splitting into edge & sprite collision
        """

        self.check_bubble_collision()
        self.check_window_collision()

    def update(self):
        """
        Update sprite every [fps] frames
        """

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
        self.cursor = Cursor()

        self.bubble_speed = Settings.bubble_speed

        self.background = Background()
        self.bubbles = pygame.sprite.Group()
        self.bubble_animation_frames = 0
        self.bubbles_limit = Settings.bubbles_max_initial
        self.bubble_spawn_speed = Settings.bubble_spawn_speed_initial

        self.game_over = False
        self.pause = False
        self.points = 0

        pygame.mouse.set_visible(False)
        pygame.mixer.music.set_volume(Settings.volume)
        self.sound_pop_bubble = pygame.mixer.Sound(
            Settings.create_sound_path('pop.mp3'))

        # Game Over Button (Precreated to use collision in events)
        self.restart_surface = pygame.Surface((200, 50))
        self.restart_surface.fill((255, 255, 255))
        self.restart_surface_rect = self.restart_surface.get_rect()
        self.restart_surface_rect.center = (
            Settings.window_width // 2, Settings.window_height // 2 + 250)

    def run(self) -> None:
        """
        Main loop
        """

        while self.running:
            self.clock.tick(Settings.window_fps)
            self.handle_events()

            self.draw()
            self.cursor.update(pygame.mouse.get_pos())

            if self.pause:
                pygame.mixer.pause()
            else:
                pygame.mixer.unpause()

            if not self.pause and not self.game_over:
                self.update()

    def handle_keydown_events(self, event) -> None:
        """
        Event handler for keydown events (key pressed)
        """

        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_p:
            self.pause = not self.pause

    def handle_mouse_events(self, event) -> None:
        """
        Event handler for mouse events
        """

        if event.button == 1:
            if self.game_over:
                self.click_restart_btn_handler(event.pos)
                return

            for bubble in self.bubbles:
                if bubble.is_hovered(event.pos):
                    bubble.kill(looped_call=False)
                    self.points += bubble.rect.width // 2  # Points depending on bubble size
                    break

    def handle_events(self) -> None:
        """
        Central event listener, splitting into keyboard and mouse handler
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_events(event)

    def respawn_bubbles(self) -> None:
        """
        Respawning bubbles
        TODO: Add delay
        """

        if len(self.bubbles.sprites()) <= self.bubbles_limit:
            self.bubbles.add(Bubble())

    def update(self) -> None:
        """
        Update loop every [fps] frames
        """

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

            self.cursor.select_cursor(
                1 if any_bubble_hovered else 0)

    def draw(self) -> None:
        """
        Draw all game objects if not pause or gameover
        """

        self.screen.fill((0, 0, 0))

        self.background.draw(self.screen)
        self.bubbles.draw(self.screen)

        self.draw_points()

        if self.pause:
            self.draw_pause()
        if self.game_over:
            self.draw_gameover()

        self.cursor.draw(self.screen)

        pygame.display.flip()

    def draw_pause(self) -> None:
        """
        Draw the pause screen
        """

        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont(
            Settings.font_pause[0],
            Settings.font_pause[1])
        pause_text = font.render(
            'PAUSE', True, (255, 255, 255))
        pause_text_rect = pause_text.get_rect()
        pause_text_rect.center = (
            Settings.window_width // 2, Settings.window_height // 2)

        self.screen.blit(pause_text, pause_text_rect)

    def draw_gameover(self) -> None:
        """
        Draw the game over screen
        """

        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont(
            Settings.font_gameover[0],
            Settings.font_gameover[1])
        gameover_text = font.render(
            'GAME OVER', True, (255, 255, 255))
        gameover_text_rect = gameover_text.get_rect()
        gameover_text_rect.center = (
            Settings.window_width // 2, Settings.window_height // 2 - 20)

        self.screen.blit(gameover_text, gameover_text_rect)

        font = pygame.font.SysFont(
            Settings.font_score[0],
            Settings.font_score[1])
        points_text = font.render(
            Settings.title_points.replace(
                '%s', str(
                    self.points)), True, (255, 255, 255))
        points_text_rect = points_text.get_rect()
        points_text_rect.center = (
            Settings.window_width // 2, Settings.window_height // 2 + 50)

        self.screen.blit(points_text, points_text_rect)

        # TODO: Add highscore
        font = pygame.font.SysFont(
            Settings.font_highscore[0],
            Settings.font_highscore[1])
        highscore_text = font.render(
            Settings.title_highscore.replace(
                '%s', str(
                    self.points)), True, (255, 255, 255))
        highscore_text_rect = highscore_text.get_rect()
        highscore_text_rect.center = (
            Settings.window_width // 2, Settings.window_height // 2 + 100)

        self.screen.blit(highscore_text, highscore_text_rect)

        font = pygame.font.SysFont(
            Settings.font_restart[0],
            Settings.font_restart[1])
        restart_text = font.render(
            "RESTART", True, (0, 0, 0))
        restart_text_rect = restart_text.get_rect()
        restart_text_rect.center = (
            Settings.window_width // 2, Settings.window_height // 2 + 250)

        self.screen.blit(self.restart_surface, self.restart_surface_rect)
        self.screen.blit(restart_text, restart_text_rect)

    def click_restart_btn_handler(self, mouse_position) -> None:
        """
        Click handler for restart button in game over screen
        """

        if self.restart_surface_rect.collidepoint(mouse_position):
            self.reset()

    def reset(self) -> None:
        """
        Resetting the game
        """

        self.points = 0
        self.bubbles.empty()
        self.bubble_speed = Settings.bubble_speed
        self.game_over = False
        self.pause = False

    def draw_points(self) -> None:
        """
        Draw a point counter onto the screen
        """

        font = pygame.font.SysFont(
            Settings.font_points[0],
            Settings.font_points[1])
        points_text = font.render(
            Settings.title_points.replace(
                '%s', str(
                    self.points)), True, (255, 255, 255))
        points_text_rect = points_text.get_rect()
        points_text_rect.top = Settings.window_height - 50
        points_text_rect.left = 25

        self.screen.blit(points_text, points_text_rect)


if __name__ == '__main__':
    game = Game()
    game.run()
