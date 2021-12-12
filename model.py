import numpy as np
import tensorflow as tf
import time
from ball import Ball
from copy import deepcopy
from pygame.locals import *


class User:

    def __init__(self, paddle_side):
        self.paddle_side = paddle_side

    def get_move(self, k, ball, paddle):
        if self.paddle_side == "L":
            if k[K_w]:
                return -1
            if k[K_s]:
                return 1
            return 0
        elif self.paddle_side == "R":
            if k[K_UP]:
                return -1
            if k[K_DOWN]:
                return 1
            return 0

    def train(self, *args, **kwargs):
        time.sleep(1)

    def create_data_point(self, *args):
        return (0, 0)


class Predictor:

    def __init__(self, paddle_x, paddle_side, surface_width, surface_height):
        self.paddle_x = paddle_x
        self.paddle_side = paddle_side
        self.width = surface_width
        self.height = surface_height

    def get_intersect_pos(self, original_ball):
        ball = deepcopy(original_ball)
        if self.paddle_side == "L":
            while ball.pos[0] > self.paddle_x:
                ball.update_pos()
                ball.bound(self.width, self.height)
        elif self.paddle_side == "R":
            while ball.pos[0] < self.paddle_x:
                ball.update_pos()
                ball.bound(self.width, self.height)
        return ball.pos[1]


class DeepPredictor:

    @staticmethod
    def generate_model(splits):
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Dense(4, activation='relu'))
        model.add(tf.keras.layers.Dense(16, activation='relu'))
        model.add(tf.keras.layers.Dropout(0.2))
        model.add(tf.keras.layers.Dense(32, activation='relu'))
        model.add(tf.keras.layers.Dropout(0.2))
        model.add(tf.keras.layers.Dense(splits + 1, activation='softmax'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    def __init__(self, dimensions, ppos, pside, splits=40):
        assert pside == "L" or pside == "R", "Invalid Paddle Side"
        self.window_dim = dimensions
        self.ppos = ppos
        self.pside = pside
        self.splits = splits
        self.model = DeepPredictor.generate_model(self.splits)

    def generate_data(self, simulations, stride=8):
        xs, ys = [], []
        pred = Predictor(self.ppos, self.pside, *self.window_dim)
        for _ in range(simulations):
            rng = 200
            if self.pside == "L":
                x1, x2 = self.ppos, self.ppos + rng
            else:
                x1, x2 = self.ppos - rng, self.ppos
            for i in range(x1, x2, stride):
                for j in range(0, self.window_dim[1], stride):
                    ball = Ball(i, j, None)
                    ball.randomize_velocity()
                    y = np.zeros((self.splits + 1,))
                    y[int(pred.get_intersect_pos(ball) * self.splits / self.window_dim[1])] = 1
                    xs.append(np.array([
                        ball.pos[0] / self.window_dim[0],
                        ball.pos[1] / self.window_dim[1],
                        ball.vel[0] / Ball.MAX_SPEED,
                        ball.vel[1] / Ball.MAX_SPEED
                    ]))
                    ys.append(y)
        p = np.random.permutation(len(xs))
        return np.array(xs)[p], np.array(ys)[p]

    def train(self, simulations=1, stride=8, data=None):
        if data is None:
            train_x, train_y = self.generate_data(simulations, stride=stride)
        else:
            train_x, train_y = data
        self.model.fit(np.array(train_x), np.array(train_y), epochs=10, batch_size=20)

    def get_move(self, k, ball, paddle):
        x = np.array([[
            ball.pos[0] / self.window_dim[0],
            ball.pos[1] / self.window_dim[1],
            ball.vel[0] / Ball.MAX_SPEED,
            ball.vel[1] / Ball.MAX_SPEED
        ]])
        y = np.argmax(self.model.predict(x)) * self.window_dim[1] / self.splits
        if y < paddle.pos[1] + paddle.height / 2:
            return -1
        if y > paddle.pos[1] + paddle.height / 2:
            return 1
        return 0

    def create_data_point(self, ball):
        pred = Predictor(self.ppos, self.pside, *self.window_dim)
        y = np.zeros((self.splits + 1,))
        y[int(pred.get_intersect_pos(ball) * self.splits / self.window_dim[1])] = 1
        x = np.array([
            ball.pos[0] / self.window_dim[0],
            ball.pos[1] / self.window_dim[1],
            ball.vel[0] / Ball.MAX_SPEED,
            ball.vel[1] / Ball.MAX_SPEED
        ])
        return x, y
