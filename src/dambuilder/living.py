import pygame
from pygame.locals import *

from dambuilder.input import player_input
from dambuilder.view import coord, conv
from dambuilder import anim
from dambuilder.physbody import CollisionBase
from dambuilder.constants import NEGLIBLE_WATER_LEVEL_FACTOR, NEAR_DAM_SLACK

ILLEGAL = 'illegal'
WALKING = 'walking'
WADING = 'wading'
SWIMMING = 'swimming'
FLYING = 'flying'

class Living(CollisionBase):
    def __init__(self, geom, x_friction_factor=1., y_friction_factor=10.):
        super(Living, self).__init__(geom)
        # initial facing directions
        self._rightleft = 1
        self._updown = 1        
        # animation
        self.anim = None
        
        self.x_friction_factor = x_friction_factor
        self.y_friction_factor = y_friction_factor
        
    def step(self, stepsize, world):
        self.friction(stepsize)
        self.behavior(stepsize, world)
        # make sure to constrain body to z dimension
        x, y, dummy = self.geom.getPosition()
        self.geom.setPosition((x, y, 0))
        
    def friction(self, stepsize):
        body = self.geom.getBody()
        # friction in direction of motion
        xv, yv, zv = body.getLinearVel()
        body.addForce((-xv / self.x_friction_factor,
                       -yv / (self.y_friction_factor),
                       0))

    def change_animation(self, animation_class):
        if (type(self.anim) is animation_class and
            self.anim.facing == self._rightleft and
            self.anim.updown == self._updown):
            return
        self.anim = animation_class(self._rightleft, self._updown)
        self.anim.start()

    def escape(self, obj, dam, escape_force):
        """Try to escape from obj.

        obj - object to try to escape from
        dam - is dam we may be near to, or None
        escape_force - is force with which we escape
        """
        x, y, dummy = self.geom.getPosition()
        obj_x, obj_y, dummy = obj.geom.getPosition()
        # if we are near the dam, get away from it
        if dam is not None:
            if x < dam.start_x:
                xf = -escape_force
                yf = 0
            else:
                xf = escape_force
                yf = 0
        else:
            if x < obj_x:
                xf = -escape_force
            else:
                xf = escape_force
            if y < obj_y:
                yf = -escape_force
            else:
                yf = escape_force
        if xf < 0:
            self._rightleft = -1
        else:
            self._rightleft = 1
            
        self.geom.getBody().addForce((xf, yf, 0))
    
    def behavior(self, stepsize, world):
        pass
    
    def get_state(self, world):
        x, y, z = self.geom.getPosition()
        size = self.geom.getRadius() * 2
        height = world.get_height(x)
        water_height = world.get_waterlevel(x).level
        # if we are below ground
        if y < height:
            return ILLEGAL
        # if we are on the ground
        if (y < height + size):
            water_size = water_height - height
            # if waterlevel is very low or zil, we walk
            if water_size < size / NEGLIBLE_WATER_LEVEL_FACTOR:
                return WALKING
            # if waterlevel is smaller than us, we wade
            if water_size < size:
                return WADING
            # if the waterlevel is higher than us, we swim
            return SWIMMING
        # we are above the ground
        if y < water_height:
            return SWIMMING
        else:
            return FLYING

    def near_dam(self, world):
        """Returns dam if near a dam, None if not near a dam.
        """
        x, y, dummy = self.geom.getPosition()
        r = self.geom.getRadius() + NEAR_DAM_SLACK
        xs = x - r
        xe = x + r
        dam = world.get_dam(xs)
        if dam is not None:
            if y > dam.height:
                return None
            return dam
        dam = world.get_dam(xe)
        if dam is not None:
            if y > dam.height:
                return None
            return dam
        return None

    def on_dam(self, world):
        """Return dam is on a dam.
        """
        x, y, dummy = self.geom.getPosition()
        r = self.geom.getRadius()
        xs = x - r
        xe = x + r
        dam = world.get_dam(xs)
        if dam is not None:
            if y > dam.height and y < (dam.height + r + NEAR_DAM_SLACK):
                return dam
        dam = world.get_dam(xe)
        if dam is not None:
            if y > dam.height and y < (dam.height + r + NEAR_DAM_SLACK):
                return dam
        return None
    
    def render(self, screen):
        raise NotImplementedError

    def render_anim(self, screen):
        x, y, dummy = self.geom.getPosition()
        w, h = self.anim.get_size()
        x, y = coord(x, y)
        x = int(x - w/2.)
        y = int(y - h/2.)
        self.anim.show(screen, (x, y))

class Timeout(object):
    def __init__(self, amount):
        self.amount = amount
        self._end = 0
        
    def start(self):
        self._end = pygame.time.get_ticks() + self.amount

    def active(self):
        return pygame.time.get_ticks() < self._end 
