import pygame
from pygame.locals import *

from dambuilder.physbody import CollisionBase
from dambuilder.view import coord, conv
from dambuilder.physbody import Ball
from dambuilder.load import load

import random

class Item(CollisionBase):
    """Collectible item.
    """

    worth = 1
    radius = 0.5
    density = 1
    
    def __init__(self, x, y):
        geom = Ball(self.density, self.radius, x, y)
        super(Item, self).__init__(geom)
        
    def step(self, stepsize, world):
        body = self.geom.getBody()
        # some friction
        xv, yv, zv = body.getLinearVel()
        body.addForce(((-xv / 2.) * stepsize,
                       (-yv / 2.) * stepsize,
                       0))
        in_water = self.in_water(world)
        # only gravity when not in water
        body.setGravityMode(not in_water)
        if in_water:
            xf = random.random() * -0.2 * stepsize
            yf = (random.random() - 0.5) * 10. * stepsize
            # drift towards the left
            body.addForce((xf, yf, 0))

        # make sure we restrict to z coord
        x, y, dummy = self.geom.getPosition()
        self.geom.setPosition((x, y, 0))
        
    def in_water(self, world):
        x, y, z = self.geom.getPosition()
        size = self.geom.getRadius() * 2
        height = world.get_height(x)
        water_height = world.get_waterlevel(x).level
        if y < water_height:
            return True
        else:
            return False

    def render(self, screen):
        x, y, dummy = self.geom.getPosition()
        image = load(self.image)
        w, h = image.get_size()
        x, y = coord(x, y)
        x = int(x - w / 2.)
        y = int(y - h / 2.)
        screen.blit(image, (x, y))

def random_item():
    if random.random() < 0.99:
        return random.choice([Bottle, Can, OldBoot, Tyre])
    else:
        return Bicycle
    
class Bottle(Item):
    image = 'bottle.png'
    worth = 1
    
class Can(Item):
    image = 'can.png'
    worth = 2
    
class OldBoot(Item):
    image = 'oldboot.png'
    worth = 4

class Tyre(Item):
    image = 'tyre.png'
    density = 1.2
    worth = 5

class Bicycle(Item):
    image = 'bicycle.png'
    radius = 0.75
    worth = 50

