import pygame
import sys
from player_class import *
from enemy_class import *
from Serial import Joystick
import time
import win32com.client as wincl
import speech_recognition as sr
import os

r = sr.Recognizer()

# Fix screen position
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x_screen, y_screen)

pygame.init()
vec = pygame.math.Vector2


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'
        self.cell_width = MAZE_WIDTH // COLS
        self.cell_height = MAZE_HEIGHT // ROWS
        self.walls = []
        self.coins = []
        self.enemies = []
        self.enemy_pos = []
        self.player_pos = None
        self.load()
        self.player = Player(self, vec(self.player_pos))
        self.make_enemies()
        self.joystick = Joystick()
        self.button = False
        self.saved_time = 0

    def run(self):
        while self.running:
            if self.state == 'start':
                self.start_draw()
                self.start_events()
            elif self.state == 'playing':
                self.joystick.update_port()
                self.button = self.button_pressed()
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            elif self.state == 'game over':
                self.game_over_draw()
                self.game_over_events()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    #------------------------------- HELPING FUNCTIONS ---------------------------------

    def draw_text(self, words, screen, pos, size, colour, font_name, centered=False):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        # If centered = True, use the centre of the text as position instead of top left corner
        if centered:
            pos[0] = pos[0] - text_size[0] // 2
            pos[1] = pos[1] - text_size[1] // 2
        screen.blit(text, pos)

    def load(self):
        self.background = pygame.image.load('maze.png')
        self.background = pygame.transform.scale(self.background, (MAZE_WIDTH, MAZE_HEIGHT))
        # Define positions of the walls, player, enemies and coins
        with open("walls.txt", 'r') as file:
            for y_index, line in enumerate(file):
                for x_index, char in enumerate(line):
                    if char == "1":
                        self.walls.append(vec(x_index, y_index))
                    elif char == "C":
                        self.coins.append(vec(x_index, y_index))
                    elif char == "P":
                        self.player_pos = [x_index, y_index]
                    elif char in ["2", "3", "4", "5"]:
                        self.enemy_pos.append([x_index, y_index])
                    elif char == "B":
                        pygame.draw.rect(self.background, BLACK, (x_index * self.cell_width, y_index * self.cell_height,
                                                                  self.cell_width, self.cell_height))

    def make_enemies(self):
        for idx, pos in enumerate(self.enemy_pos):
            self.enemies.append(Enemy(self, vec(pos), idx))

    # Only used for help when self.draw_grid() in playing_draw is enabled
    def draw_grid(self):
        for x in range(WIDTH // self.cell_width):
            pygame.draw.line(self.background, GREY, (x * self.cell_width, 0),
                             (x * self.cell_width, HEIGHT))
        for x in range(HEIGHT // self.cell_height):
            pygame.draw.line(self.background, GREY, (0, x * self.cell_height),
                             (WIDTH, x * self.cell_height))

    def reset(self):
        self.player.lives = 3
        self.player.current_score = 0
        self.player.grid_pos = vec(self.player.starting_pos)
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for enemy in self.enemies:
            enemy.grid_pos = vec(enemy.starting_pos)
            enemy.pix_pos = enemy.get_pix_pos()
            enemy.direction *= 0

        self.coins = []
        with open("walls.txt", 'r') as file:
            for y_index, line in enumerate(file):
                for x_index, char in enumerate(line):
                    if char == 'C':
                        self.coins.append(vec(x_index, y_index))
        self.state = "playing"

   #---------------------------- INTRO FUNCTIONS --------------------------------

    # Listen if the player says 'start' or 'stop'
    def start_events(self):
        running = True
        with sr.Microphone() as source:
            while running:
                try:
                    audio = r.listen(source, timeout=1)
                    try:
                        result = r.recognize_google(audio)
                        if result == 'start':
                            print('start')
                            self.state = 'playing'
                            running = False
                        elif result == 'stop':
                            print('stop')
                            self.running = False
                            running = False
                    except sr.UnknownValueError:
                        print('No input')

                except:
                    print('TimeOut')

    def start_draw(self):
        self.screen.fill(BACKGROUNDMENU)
        self.draw_text('SAY START', self.screen, [
            WIDTH // 2, HEIGHT // 2 - 50], START_TEXT_SIZE, SALMON, START_FONT, centered=True)
        self.draw_text('1 PLAYER ONLY', self.screen, [
            WIDTH // 2, HEIGHT // 2 + 50], B_TEXT_SIZE, SILVER, START_FONT, centered=True)
        self.draw_text('Use the joystick to control pacman', self.screen, [
            WIDTH // 2, HEIGHT // 2 + 120], B_TEXT_SIZE, SILVER, START_FONT, centered=True)
        self.draw_text('Press the joystick to stop the enemies', self.screen, [
            WIDTH // 2, HEIGHT // 2 + 150], B_TEXT_SIZE, SILVER, START_FONT, centered=True)
        self.draw_text('Say stop to QUIT', self.screen, [
            WIDTH // 2, HEIGHT // 2 + 220], B_TEXT_SIZE, SILVER, START_FONT, centered=True)
        pygame.display.update()

   #--------------------------------- PLAY FUNCTIONS -----------------------------

    def playing_events(self):

        if self.joystick.output.startswith("LEFT"):
            self.player.move(vec(-1, 0))
        if self.joystick.output.startswith("RIGHT"):
            self.player.move(vec(1, 0))
        if self.joystick.output.startswith("UP"):
            self.player.move(vec(0, -1))
        if self.joystick.output.startswith("DOWN"):
            self.player.move(vec(0, 1))

    def playing_update(self):
        self.player.update()
        # After the button has been pressed, let the enemies freeze for 2 seconds
        if self.saved_time + 2 <= time.time():
            for enemy in self.enemies:
                enemy.update()

        for enemy in self.enemies:
            if enemy.grid_pos == self.player.grid_pos:
                self.remove_life()

    def button_pressed(self):
        if self.joystick.output.startswith("Button"):
            self.saved_time = time.time()
            return True

    def playing_draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (TOP_BOTTOM_BUFFER // 2, TOP_BOTTOM_BUFFER // 2))
        self.draw_coins()
        #self.draw_grid()
        self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score),
                       self.screen, [25, 5], 28, WHITE, START_FONT)
        self.draw_text(('LIVES'), self.screen, [25, HEIGHT-25], 28, WHITE, START_FONT)
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        pygame.display.update()

    def remove_life(self):
        self.player.lives -= 1
        if self.player.lives == 0:
            self.state = "game over"
        else:
            self.player.grid_pos = vec(self.player.starting_pos)
            self.player.pix_pos = self.player.get_pix_pos()
            self.player.direction *= 0
            for enemy in self.enemies:
                enemy.grid_pos = vec(enemy.starting_pos)
                enemy.pix_pos = enemy.get_pix_pos()
                enemy.direction *= 0

    def draw_coins(self):
        for coin in self.coins:
            pygame.draw.circle(self.screen, (124, 123, 7),
                               (int(coin.x * self.cell_width) + self.cell_width // 2 + TOP_BOTTOM_BUFFER // 2,
                                int(coin.y * self.cell_height) + self.cell_height // 2 + TOP_BOTTOM_BUFFER // 2), 5)

   #------------------------------GAME OVER FUNCTIONS-----------------------------

    def game_over_events(self):
        # Tell the player he is game over, tell his score and ask to play again by voice
        game_over_text = 'Game Over. Your score is' + str(self.player.current_score)
        please_play_again_text = "Please play again"
        speak = wincl.Dispatch("SAPI.SpVoice")
        speak.Speak(game_over_text)
        speak.Speak(please_play_again_text)

        # Listen if the player says 'start' or 'stop'
        running = True
        with sr.Microphone() as source:
            while running:

                try:
                    audio = r.listen(source, timeout=1)
                    try:
                        result = r.recognize_google(audio)
                        if result == 'start':
                            print('start')
                            self.reset()
                            running = False
                        elif result == 'stop':
                            print('stop')
                            self.running = False
                            running = False
                    except sr.UnknownValueError:
                        print('No input')

                except:
                    print('TimeOut')

    def game_over_draw(self):
        self.screen.fill(BACKGROUNDMENU)
        quit_text = "Say stop to QUIT"
        again_text = "Say start to PLAY AGAIN"
        self.draw_text("GAME OVER", self.screen, [WIDTH // 2, 100], START_TEXT_SIZE, SALMON, "fixedsys", centered=True)
        self.draw_text(again_text, self.screen, [
            WIDTH // 2, HEIGHT // 2], B_TEXT_SIZE, SILVER, "fixedsys", centered=True)
        self.draw_text(quit_text, self.screen, [
            WIDTH // 2, HEIGHT // 1.5], B_TEXT_SIZE, SILVER, "fixedsys", centered=True)
        pygame.display.update()
