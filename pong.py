# native modules
import time

# intalled modules
import numpy as np
import pygame
from pygame.locals import *

# custom modules
from ball import Ball
from model import DeepPredictor, User
from paddle import Paddle


# graphics functions and classes
def text_objects(text, font, color):
    surface = font.render(text, True, color)
    return surface, surface.get_rect(), surface.get_width(), surface.get_height()


def display_text(surface, text, x, y, color, size):
    outline = pygame.font.Font('freesansbold.ttf', size)
    textSurf, textRect, textW, textH = text_objects(text, outline, color)
    textRect.center = (x, y)
    surface.blit(textSurf, textRect)
    return textW, textH


class Button:

    def __init__(self, text, pos, off_color, on_color, action, size):
        self.text = text
        self.pos = pos
        self.color = off_color
        self.off_color = off_color
        self.on_color = on_color
        self.action = action
        self.size = size

    def update_color(self, mx, my):
        if mx > self.pos[0] - self.width / 2 and mx < self.pos[0] + self.width / 2 and my > self.pos[1] - self.height / 2 and my < self.pos[1] + self.height / 2:
            self.color = self.on_color
        else:
            self.color = self.off_color

    def render(self, surface):
        self.width, self.height = display_text(surface, self.text, self.pos[0], self.pos[1], self.color, self.size)
        self.width = int(self.width * 1.15)
        self.height = int(self.height * 1.15)
        rect_pos = [self.pos[0] - self.width / 2, self.pos[1] - self.height / 2, self.width, self.height]
        pygame.draw.rect(surface, self.color, rect_pos, 4)


# misc functions
def reflect(paddle, ball, paddle_side, theta=8):
    if paddle_side == "L":
        paddle_x = paddle.pos[0] + paddle.width / 2
    elif paddle_side == "R":
        paddle_x = paddle.pos[0] - paddle.width / 2
    future_pos = ball.pos + ball.vel
    if (future_pos[0] >= paddle_x and ball.pos[0] < paddle_x) or (future_pos[0] <= paddle_x and ball.pos[0] > paddle_x):
        slope = future_pos - ball.pos
        slope *= abs((ball.pos[0] - paddle_x) / slope[0])
        future_pos = ball.pos + slope
        if future_pos[1] >= paddle.pos[1] and future_pos[1] <= paddle.pos[1] + paddle.height:
            # reflecting the ball
            vy = (ball.pos[1] - paddle.pos[1] - paddle.height / 2) / theta
            vx = -ball.vel[0]
            v = np.sqrt(vx ** 2 + vy ** 2)
            ball.vel = np.array([vx, vy]) * (np.linalg.norm(ball.vel) / v)
            ball.pos[0] = paddle_x


# pygame functions
def main(window_dimensions):
    pygame.init()
    DS = pygame.display.set_mode(window_dimensions)
    pygame.display.set_caption("PYTHON PONG")
    color_dict = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "blue": (0, 0, 255)
    }
    player1 = User("L")
    player2 = User("R")

    # creating buttons
    W, H = window_dimensions
    HW, HH = int(W / 2), int(H / 2)
    FONT_SIZE = 30
    PADDLE_OFFSET = 30
    buttons = []

    def start(player1, player2):
        pong(player1, player2, window_dimensions, PADDLE_OFFSET)
        return player1, player2
    b = Button("Start the Game", (HW, HH - 2 * FONT_SIZE), color_dict["blue"], color_dict["white"], start, FONT_SIZE)
    buttons.append(b)

    def change_player1(player1, player2):
        if type(player1) == User:
            player1 = DeepPredictor(window_dimensions, HW, player1.paddle_side, splits=40)
        else:
            player1 = User(player1.pside)
        return player1, player2
    b = Button("Change Player 1", (HW, HH), color_dict["blue"], color_dict["white"], change_player1, FONT_SIZE)
    buttons.append(b)

    def change_player2(player1, player2):
        if type(player2) == User:
            player2 = DeepPredictor(window_dimensions, HW, player2.paddle_side, splits=40)
        else:
            player2 = User(player2.pside)
        return player1, player2
    b = Button("Change Player 2", (HW, HH + 2 * FONT_SIZE), color_dict["blue"], color_dict["white"], change_player2, FONT_SIZE)
    buttons.append(b)

    # main loop
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    if button.color == button.on_color:
                        player1, player2 = button.action(player1, player2)
            mx, my = pygame.mouse.get_pos()
            DS.fill((0, 0, 0))
            display_text(DS, "Player 1: {}".format(type(player1).__name__), HW * 0.5, 50, color_dict["blue"], 30)
            display_text(DS, "Player 2: {}".format(type(player2).__name__), HW * 1.5, 50, color_dict["blue"], 30)

            for button in buttons:
                button.render(DS)
                button.update_color(mx, my)
            pygame.display.update()


def pong(player1, player2, window_dimensions, poffset):

    # setup
    W, H = window_dimensions
    HW, HH = int(W / 2), int(H / 2)
    DS = pygame.display.set_mode((W, H))
    pygame.display.set_caption("PYTHON PONG")
    clock = pygame.time.Clock()

    # variables
    FPS = 60
    color_dict = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "blue": (0, 0, 255)
    }
    ball = Ball(HW, HH, color_dict["red"])
    ball.randomize_velocity(low=15.0, high=30.0)
    pl = Paddle(poffset, HH, color_dict["blue"])
    pl.pos[1] -= pl.height / 2
    pr = Paddle(W - poffset, HH, color_dict["blue"])
    pr.pos[1] -= pr.height / 2
    paddle_speed = 10

    # game play variables
    MAX_SCORE = 2
    pl_score = 0
    pr_score = 0
    rnd = 1
    MAX_RND = 10

    # players
    player1_x, player1_y = [], []
    player2_x, player2_y = [], []
    rng = 200

    # main loop
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if rnd > MAX_RND:
            time.sleep(2)
            break

        if pr_score == -1 and pl_score == -1:
            player1.train(stride=6)
            player1.train(data=(player1_x, player1_y))
            player2.train(stride=6)
            player2.train(data=(player2_x, player2_y))
            pr_score = 0
            pl_score = 0
            player1_x, player1_y = [], []
            player2_x, player2_y = [], []

        # paddle movement
        k = pygame.key.get_pressed()
        pl.pos[1] += player1.get_move(k, ball, pl) * paddle_speed
        pr.pos[1] += player2.get_move(k, ball, pr) * paddle_speed

        # data collection (for DeepPredictor players)
        if ball.pos[0] < rng:
            x, y = player1.create_data_point(ball)
            player1_x.append(x)
            player1_y.append(y)
        elif ball.pos[0] > W - rng:
            x, y = player2.create_data_point(ball)
            player2_x.append(x)
            player2_y.append(y)

        # collison detection
        reflect(pl, ball, "L")
        reflect(pr, ball, "R")

        # game objects
        ball.update_pos()
        ball.bound(W, H)

        if ball.pos[0] <= 0:
            pr_score += 1
            ball.pos[0] = HW
            ball.pos[1] = HH
            ball.randomize_velocity(low=15.0, high=30.0)
            pl.pos[1] = HH - pl.height / 2
            pr.pos[1] = HH - pr.height / 2
            time.sleep(1)
        elif ball.pos[0] >= W:
            pl_score += 1
            ball.pos[0] = HW
            ball.pos[1] = HH
            ball.randomize_velocity(low=15.0, high=30.0)
            pl.pos[1] = HH - pr.height / 2
            pr.pos[1] = HH - pr.height / 2
            time.sleep(1)

        pl.bound(H, 0)
        pr.bound(H, 0)

        # graphics
        DS.fill(color_dict["black"])
        ball.render(DS)
        pl.render(DS)
        pr.render(DS)

        display_text(DS, "Player 1: {}".format(pl_score), 60, 15, color_dict["white"], 20)
        display_text(DS, "Player 2: {}".format(pr_score), W - 60, 15, color_dict["white"], 20)

        if pr_score == MAX_SCORE or pl_score == MAX_SCORE:
            rnd += 1
            DS.fill(color_dict["black"])
            if rnd > MAX_RND:
                display_text(DS, "Round Limit Reached", HW, HH, color_dict["white"], 40)
            else:
                if pr_score == MAX_SCORE:
                    display_text(DS, "Player 2 Wins", HW, HH - 25, color_dict["white"], 40)
                elif pl_score == MAX_SCORE:
                    display_text(DS, "Player 1 Wins", HW, HH - 25, color_dict["white"], 40)
                display_text(DS, "Prepare for Round {}".format(rnd), HW, HH + 25, color_dict["white"], 40)
                pr_score = -1
                pl_score = -1

        pygame.display.update()
        clock.tick(FPS)




# main program
if __name__ == "__main__":
    dimensions = (1000, 600)
    main(dimensions)
