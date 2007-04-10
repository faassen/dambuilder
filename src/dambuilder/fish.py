import random

import pygame

from dambuilder import living, anim
from dambuilder.beaver import Beaver
from dambuilder.view import coord, conv, visible
from dambuilder.living import ILLEGAL, WALKING, WADING, SWIMMING, FLYING

BIRD_FLEE_WATER = 10

class Fish(living.Living):

    escape_force = 20
    swim_force = 25
    erode_rate = 0.010
    dam_distance = 10
    timeout = 700
    
    swimming_anim = anim.FishBlueSwimming
    nibbling_anim = anim.FishBlueNibbling
    x_friction = 1
    y_friction = 10
    
    def __init__(self, geom):
        super(Fish, self).__init__(geom, self.x_friction, self.y_friction)
        self.geom.getBody().setGravityMode(False)

        self.fly_timeout = living.Timeout(self.timeout)
        self.change_animation(self.swimming_anim)
        
    def behavior(self, stepsize, world):
        x, y, dummy = self.geom.getPosition()
        #w, h = self.anim.get_size()

        body = self.geom.getBody()

        dam = self.near_dam(world)
        
        if self._collisions:
            for obj in self._collisions:
                if isinstance(obj, Beaver):
                    self.escape(obj, dam, self.escape_force)

        state = self.get_state(world)

        if state is FLYING or state is WALKING or state is WADING:
            body.setGravityMode(True)
        else:
            body.setGravityMode(False)

        # flop around
        if state is WALKING or state is WADING:
            body.addForce(
                ((random.random() * stepsize * stepsize) - (5 * stepsize),
                 self.swim_force * stepsize, 0))

        if dam is not None:
            if x < dam.start_x:
                self._rightleft = 1
            else:
                self._rightleft = -1
            self.change_animation(self.nibbling_anim)
            erode_amount = self.erode_rate * stepsize
            # try to sit still
            xv, yv, dummy = body.getLinearVel()
            body.addForce((-xv, -yv, 0))
            # if vertical momentum low enough, nibble
            if -0.01 < yv < 0.01:
                dam.nibble_at(world, y, 0.2, erode_amount)
            return
        else:
            self.change_animation(self.swimming_anim)
            
        # XXX ugly hack to get to the dam, won't work with multiple dams
        dam = world._dams[0]
          
        if x > dam.end_x + self.dam_distance:
            # swim back to dam if too far off
            r = 1
        elif y > dam.height:
            # swim down to dam if too high
            r = 3
        else:
            # random swimming
            r = random.randint(0, 3)
    
        if r == 0:
            if not self.fly_timeout.active():
                body.addForce((20, 0, 0))
                self._rightleft = 1
                self.fly_timeout.start()
        elif r == 1:
            if not self.fly_timeout.active():
                body.addForce((-20, 0, 0))
                self._rightleft = -1
                self.fly_timeout.start()
        elif r == 2:
            if not self.fly_timeout.active():
                body.addForce((0, 20, 0))
                self.fly_timeout.start()
        else:
            if not self.fly_timeout.active():
                body.addForce((0, -20, 0))
                self.fly_timeout.start()
    
        
    def render(self, screen, world):
        self.render_anim(screen)

class DangerFish(Fish):
    escape_force = 10
    swim_force = 30
    dam_distance = 5
    swimming_anim = anim.FishGoldSwimming
    nibbling_anim = anim.FishGoldNibbling
    timeout = 800
    x_friction = 4
    

