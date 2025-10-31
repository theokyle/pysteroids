import pygame
import sys
from constants import *
from game_objects.player import Player
from game_objects.asteroid import Asteroid
from game_objects.asteroidfield import AsteroidField
from game_objects.shot import Shot

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroids")

        # Fonts and Clock
        self.font = pygame.font.SysFont(None, 36)
        self.big_font = pygame.font.SysFont(None, 72)
        self.clock = pygame.time.Clock()

        #Game State
        self.score = 0
        self.lives = 3
        self.running = True
        self.game_over = False
        self.dt = 0

        self.setup_round()

    def setup_round(self):
        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()

        Player.containers = (self.updatable, self.drawable)
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        AsteroidField.containers = self.updatable
        Shot.containers = (self.shots, self.updatable, self.drawable)

        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.asteroid_field = AsteroidField()
        self.game_over = False
    
    def handle_collision(self):
        for asteroid in self.asteroids:
            # Player hit asteroid → lose life
            if asteroid.collides_with(self.player):
                self.lives -= 1
                self.game_over = True

            # Shots hit asteroid → destroy both
            for shot in self.shots:
                if asteroid.collides_with(shot):
                    self.score += 1
                    asteroid.split()
                    shot.kill()

    def draw_hud(self):
        # Draw score and lives
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_text = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, lives_text.get_rect(topright=(SCREEN_WIDTH - 10, 10)))

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.setup_round()

    def lose_life(self):
        text = self.big_font.render("You Lost a Life", True, (255, 200, 0))
        rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.wait(1500)
    
    def end_game(self):
        waiting = True
        while waiting:
            self.screen.fill("black")

            # Draw texts
            text = self.big_font.render("Game Over", True, (255, 0, 0))
            rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            sub_text = self.font.render("Press Q to Quit or R to Restart", True, (200, 200, 200))
            sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60))

            self.screen.blit(text, rect)
            self.screen.blit(sub_text, sub_rect)
            pygame.display.flip()

            # Event handling loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False
                        waiting = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        waiting = False

            self.clock.tick(30)

    def run_round(self):
        # Play one round until player dies or quits.
        self.setup_round()

        while not self.game_over and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

            self.screen.fill("black")
            self.updatable.update(self.dt)
            self.handle_collision()

            # Draw everything
            for obj in self.drawable:
                obj.draw(self.screen)
            self.draw_hud()

            pygame.display.flip()
            self.dt = self.clock.tick(60) / 1000

    def run(self):
        # Main game loop: handles multiple rounds and restarts.
        while self.running:
            # Run the current round
            self.run_round()

            if not self.running:
                break

            if self.lives > 0:
                self.lose_life()
            else:
                self.end_game()

        pygame.quit()
        sys.exit()