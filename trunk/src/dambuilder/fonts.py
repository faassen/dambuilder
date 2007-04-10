import pygame
from pygame.locals import *

from dambuilder.load import main_path

def get_display_font():
    return pygame.font.Font(
        main_path('data', 'ttf-bitstream-vera', 'Vera.ttf'),
        10)

#pygame.font.SysFont('bitstream', 12)

def get_small_font():
    return pygame.font.Font(
        main_path('data', 'ttf-bitstream-vera', 'Vera.ttf'),
        16)

#return pygame.font.SysFont('bitstream', 20)

def get_medium_font():
    return pygame.font.Font(
        main_path('data', 'ttf-bitstream-vera', 'Vera.ttf'),
        30)

    #return pygame.font.SysFont('bitstream', 40)

def get_large_font():
    return pygame.font.Font(
        main_path('data', 'ttf-bitstream-vera', 'Vera.ttf'),
        50)
    
    #return pygame.font.SysFont('bitstream', 80)

