import pygame
from pygame.locals import *

from dambuilder import waterfall
from dambuilder.view import coord, conv
from dambuilder.load import load, load_colorkey
from dambuilder.physbody import ode_world, ode_space
from dambuilder.material import SECTION_HEIGHT
from dambuilder.constants import (WATER_COLOR, SKY_COLOR, 
                                  MATERIAL_EROSION_DRY,
                                  MATERIAL_EROSION_WET)
class Leak(object):
    def __init__(self, xs, xe, height, rate, connection_id):
        self.xs = xs
        self.xe = xe
        self.height = height
        self.connection_id = connection_id
        self.rate = rate
        self._waterfall = None

        self._waterfall = waterfall.Waterfall(
            0., 0., 0.1,
            xs, xe, height)

    def clear_ode(self):
        self._waterfall.clear_ode()
        
    def between(self, start_y, end_y):
        return start_y <= self.height < end_y

    def activate(self, water_world, level, prev_level):
        self._waterfall.update_flow(self.rate, level, prev_level)
    
        if water_world.have_connection(self.connection_id):
            return
        
        water_world.connect(self.connection_id,
                            level, prev_level,
                            self.rate,
                            self.height)

    def deactivate(self, water_world):
        if not water_world.have_connection(self.connection_id):
            return
        
        water_world.disconnect(self.connection_id)
        self._waterfall.cut_flow()

    def step_erosion(self, stepsize, dam):
        water_height = dam.get_highest_level().level
        material = dam.get_material(self.height)
        
        if self.height > water_height:
            self.rate += MATERIAL_EROSION_DRY[material] * stepsize
        else:
            self.rate += MATERIAL_EROSION_WET[material] * stepsize
    
    def update(self):
        if ode_world is not None:
            self._waterfall.update()

    def create_background(self, dam):
        water_height = dam.get_highest_level().level
        half_section_height = SECTION_HEIGHT / 2.

        background = pygame.Surface((64, 20))
        background.fill(SKY_COLOR)
            
        if water_height > self.height - half_section_height:
            background_water_height = water_height - (
                self.height - half_section_height)
            if background_water_height > SECTION_HEIGHT:
                background.fill(WATER_COLOR, Rect(0, 0, 64, 20))
            else:
                # XXX contains evil hack to fix 1 pixel offness...
                background.fill(WATER_COLOR, Rect(
                    0, 19 - conv(background_water_height), 64, 20))
        return background
    
    def render(self, screen, dam):
        white = (255, 255, 255)
        black = (0, 0, 0)
        
        background = self.create_background(dam)
        
        if self.rate < 0.04:
            image = load_colorkey(
                white,
                'leaks', 'leak_01.png')
        elif self.rate < 0.07:
            image = load_colorkey(
                white,
                'leaks', 'leak_02.png')
        elif self.rate < 0.10:
            image = load_colorkey(
                white,
                'leaks', 'leak_03.png')
        elif self.rate < 0.13:
            image = load_colorkey(
                white,
                'leaks', 'leak_04.png')
        else:
            image = load_colorkey(
                white,
                'leaks', 'leak_05.png')
        background.blit(image, (0, 0))
        background.set_colorkey(black)
        
        screen.blit(background,
                    coord(self.xs, self.height + SECTION_HEIGHT / 2.))
        
        self._waterfall.render(screen)
