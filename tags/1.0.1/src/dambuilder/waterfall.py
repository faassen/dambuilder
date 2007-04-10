import ode

import pygame
from pygame.locals import *

from dambuilder import physbody
from dambuilder.physbody import ode_world, ode_space
from dambuilder.view import coord, conv
from dambuilder.constants import WATERFALL_COLOR, WATERFALL_DROPLET_FORCE

class Waterfall(object):
    def __init__(self, amount, disappear_height,
                 disappear_always_height, xs, xe, y):
        self.amount = amount
        self.disappear_height = disappear_height
        self.disappear_always_height = disappear_always_height
        self.xs = xs
        self.xe = xe
        self.x = xs
        self.dir = -1
        self.y = y
        self._droplets = []

    def clear_ode(self):
        for droplet in self._droplets:
            ode_space.remove(droplet.geom)

    def cleanup(self):
        """Remove any objects below disappearing height.
        """
        new_droplets = []
        h = self.disappear_height
        for droplet in self._droplets:
            geom = droplet.geom
            x, y, z = geom.getPosition()
            if y > h and y > self.disappear_always_height:
                new_droplets.append(droplet)
            else:
                ode_space.remove(geom)
        self._droplets = new_droplets

    def add(self):
        """Add new object at starting point if necessary.
        """
        if self.y < self.disappear_height:
            return

        if len(self._droplets) >= self.amount or len(self._droplets) > 20:
            return

        geom = physbody.Ball(0.2, 0.06, self.x, self.y)
        droplet = Droplet(geom)
        geom.getBody().setForce((WATERFALL_DROPLET_FORCE * self.dir, 0, 0))
        self._droplets.append(droplet)

    def update_flow(self, rate, level, prev_level):
        self.amount = int(rate * 200)
        if prev_level.level > level.level:
            self.disappear_height = level.level
            self.direction = 1
            self.x = self.xe
        else:
            self.disappear_height = prev_level.level
            self.direction = -1
            self.x = self.xs
            
    def cut_flow(self):
        self.amount = 0
        
    def update(self):
        self.cleanup()
        self.add()

    def render(self, screen):
        for droplet in self._droplets:
            droplet.render(screen)

class Droplet(object):
    def __init__(self, geom):
        self.geom = geom

    def render(self, screen):
        x, y, dummy = self.geom.getPosition()
        r = self.geom.getRadius()
        pygame.draw.circle(screen, WATERFALL_COLOR, coord(x, y),
                           conv(r * 4), 0)
