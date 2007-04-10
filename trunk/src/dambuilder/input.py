import sys

import pygame
from pygame.locals import *

class Input(object):
    def __init__(self):
        self.clear()

    def clear(self):
        self.x_direction = None
        self.y_direction = None
        self.action1 = False
        self.action2 = False
        self.action3 = False
        self.quit_request = False
        
    def handle_events(self):
        events = pygame.event.get()
        for e in events:
            if e.type == QUIT:
                sys.exit()
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.quit_request = True
                elif e.key == K_RIGHT:
                    self.x_direction = 1
                elif e.key == K_LEFT:
                    self.x_direction = -1
                elif e.key == K_DOWN:
                    self.y_direction = -1
                elif e.key == K_UP:
                    self.y_direction = 1
                elif e.key == K_SPACE:
                    self.action1 = True
                elif e.key == K_RALT or e.key == K_LALT:
                    self.action2 = True
                elif e.key == K_RETURN:
                    self.action3 = True
            elif e.type == KEYUP:
                if e.key == K_ESCAPE:
                    self.quit_request = False
                elif e.key == K_RIGHT:
                    self.x_direction = None
                elif e.key == K_LEFT:
                    self.x_direction = None
                elif e.key == K_UP:
                    self.y_direction = None
                elif e.key == K_DOWN:
                    self.y_direction = None
                elif e.key == K_SPACE:
                    self.action1 = False
                elif e.key == K_RALT or e.key == K_LALT:
                    self.action2 = False
                elif e.key == K_RETURN:
                    self.action3 = False

player_input = Input()
