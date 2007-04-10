import random

import pygame

from dambuilder import living, anim
from dambuilder.beaver import Beaver
from dambuilder.view import coord, conv, visible
from dambuilder.living import ILLEGAL, WALKING, WADING, SWIMMING, FLYING

BIRD_FLEE_WATER = 10

class Bird(living.Living):

    def __init__(self, geom):
        super(Bird, self).__init__(geom, 1, 10)
        self.geom.getBody().setGravityMode(False)

        self.fly_timeout = living.Timeout(500)
        self.change_animation(anim.BirdFlying)
        
    def behavior(self, stepsize, world):
        x, y, dummy = self.geom.getPosition()
        #w, h = self.anim.get_size()

        body = self.geom.getBody()

        dam = self.near_dam(world)
        state = self.get_state(world)

        if state is SWIMMING:
            # fly up out of the water
            body.addForce((0, 50., 0))
            
        if self._collisions:
            for obj in self._collisions:
                if isinstance(obj, Beaver):
                    self.escape(obj, dam, 25)
        
        if dam is not None:
            if x < dam.start_x:
                self._rightleft = 1
            else:
                self._rightleft = -1
            self.change_animation(anim.BirdPecking)
            erode_amount = 0.015 * stepsize
            xv, yv, dummy = body.getLinearVel()
            # try to sit still
            body.addForce((-xv, -yv, 0))
            # if vertical momentum low enough, nibble
            if -0.01 < yv < 0.01:
                # XXX add 0.3 to go up to beak
                dam.nibble_at(world, y + 0.3, 0.2, erode_amount)
            return
        else:
            self.change_animation(anim.BirdFlying)


        # XXX ugly hack to get to the dam, won't work with multiple dams
        dam = world._dams[0]
        
        if x > dam.end_x + 6.:
            # fly back to dam if too far off
            r = 1
        elif y > dam.height + 4:
            # fly down to dam if too high
            r = 3
        else:
            # random flight
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
        #self.change_animation(anim.BirdFlying)
        self.render_anim(screen)
