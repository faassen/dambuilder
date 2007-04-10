import random

import ode

import pygame
from pygame.locals import *

from dambuilder import waterlevel
from dambuilder import fonts
from dambuilder.load import load, main_path
from dambuilder.dam import DamSentinel, Dam
from dambuilder.beaver import Beaver
from dambuilder.fish import Fish, DangerFish
from dambuilder.bird import Bird
from dambuilder.item import random_item
from dambuilder.material import SECTION_HEIGHT
from dambuilder.physbody import (ode_world, ode_space, contactgroup,
                                 Ball, Immovable)
from dambuilder.view import coord, conv, player_view
from dambuilder.constants import (WATER_COLOR, DISPLAY_COLOR, TEXT_COLOR,
                                  MAX_X, MAX_ITEMS, MAX_LIVINGS, GRAVITY,)

class WorldError(Exception):
    pass

class World(object):
    
    def __init__(self):
        # the dams in the world
        self._dams = []
        # items
        self._items = []
        # livings
        self._livings = []

        # maintain list for ode world cleanup
        self._ode_objects = []
      
        # part of the world that manages water levels
        self._water_world = waterlevel.World()
 
        # the initial water level of the whole world
        start_level = self._water_world.add_level('start', 0)

        # start dam sentinel
        self._start_dam = DamSentinel(start_level)

        # start off with 1 animal
        self._last_difficulty = -1
        
    def setup(self):
        # set gravity
        ode_world.setGravity((0, GRAVITY, 0))
        
        # floor at the bottom
        floor = ode.GeomPlane(ode_space, (0, 1, 0), 0)
        self._ode_objects.append(floor)
        
        # the leftmost end of the game
        leftmost = ode.GeomPlane(ode_space, (1, 0, 0), 0)
        self._ode_objects.append(leftmost)
        
        # immovable geom at the right end
        # XXX make it vastly huge so we can't go over it...
        self.rightmost_geom = Immovable(
            MAX_X, 50000.,
            1., 100000.)
        self.rightmost_geom.rightmost = True
        self._ode_objects.append(self.rightmost_geom)
        
        # a physical dam object in ode
        dam_geom = Immovable(
            6., 4 * SECTION_HEIGHT,
            1., 8 * SECTION_HEIGHT)
        # a dam
        self.dam = dam = self.add_dam('sea', dam_geom)

        # water input
        water_world = self._water_world
        sea = water_world.get_level('sea')
        sea.level = 1.
        icecaps = water_world.add_source('icecaps')
        water_world.connect('warming', icecaps, sea, 0.07)

        # beaver
        beaver_geom = Ball(1.2, 0.5, 0.5, 0.5)
        b = Beaver(beaver_geom)
        self.add_living(b)

    def clear_ode(self):
        for dam in self._dams:
            dam.clear_ode()
        for obj in self._ode_objects:
            ode_space.remove(obj)
        for item in self._items:
            ode_space.remove(item.geom)
        for living in self._livings:
            ode_space.remove(living.geom)
            
    def step(self, stepsize):
        """Update world.
        """
        if ode_world is not None:
            ode_space.collide((ode_world, contactgroup),
                              collision_callback)
            ode_world.step(stepsize)
            contactgroup.empty()

        self.step_water(stepsize)

        self.step_erosion(stepsize)
        
        self.step_items(stepsize)
        
        for item in self._items:
            item.step(stepsize, self)
            item.clear_collisions()

        for living in self._livings:            
            living.step(stepsize, self)
            living.clear_collisions()

        # potentially increase difficulty
        self.increase_difficulty()
        
    def step_water(self, stepsize):
        for dam in self._dams:
            dam.update(self)
        self._water_world.step(stepsize)

    def step_erosion(self, stepsize):
        # erode dams
        for dam in self._dams:
            dam.step_erosion(stepsize, self)
            
    def step_items(self, stepsize):
        """Add new items to the world.
        """
        # don't add any items beyond MAX_ITEMS
        if len(self._items) > MAX_ITEMS:
            return
        sea_level = self._water_world.get_level('sea').level
        item_chance = sea_level / 100
        if item_chance < 0.1:
            item_chance = 0.1
        if item_chance > 1.:
            item_chance = 1.0
        item_chance *= stepsize * 10
        if random.random() < item_chance:
            y = random.random() * sea_level + 0.5
            item_class = random_item()
            item = item_class(MAX_X + player_view.width / 2., y)
            item.geom.getBody().addForce((-20, 0, 0))
            self.add_item(item)

    def increase_difficulty(self):
        """Increases difficulty as water level gets higher.
        """
        if len(self._livings) > MAX_LIVINGS:
            return
        height = self._water_world.get_level('sea').level
        difficulty = int(height / 3)
        if self._last_difficulty == difficulty:
            return
        if random.random() < 0.5:
            self.add_fish(height)
        else:
            self.add_bird(height)
        self._last_difficulty = difficulty

    def is_game_over(self):
        height = self._water_world.get_level('start').level
        return height > 10.

    def add_bird(self, height):
        dummy, y, dummy = self._livings[0].geom.getPosition()
        bird_geom = Ball(0.2, 0.5, 3, y + player_view.height)
        bird = Bird(bird_geom)
        self.add_living(bird)

    def add_fish(self, height):
        if height > 28.:
            fish_class = DangerFish
        else:
            fish_class = Fish
        dam = self._dams[0]
        x, y, dummy = self._livings[0].geom.getPosition()
        fish_geom = Ball(0.4, 0.5, dam.start_x + 14, dam.height / 2.)
        fish = fish_class(fish_geom)
        self.add_living(fish)
    
    def add_dam(self, id, geom):
        """Build a dam for geom.
        """
        x, dummy, dummy = geom.getPosition()
        prev_dam = self.get_dam(x)
        if prev_dam is None:
            prev_dam = self._start_dam
        level = self._water_world.add_level(id, prev_dam.level.level)
        next_dam = prev_dam.next_dam
        dam = Dam(id, geom, level, prev_dam, next_dam)
        prev_dam.next_dam = dam        
        if next_dam is not None:
            next_dam.prev_dam = dam
        self._dams.append(dam)
        return dam

    def add_item(self, item):
        self._items.append(item)

    def remove_item(self, item):
        item.geom.obj = None # XXX break cycles
        ode_space.remove(item.geom)
        i = self._items.index(item)
        # means we cannot call this while looping through items, such
        # as in item.step
        del self._items[i]
        
    def add_living(self, living):
        self._livings.append(living)

    def remove_living(self, living):
        living.geom.obj = None # break cycles
        ode_space.remove(living.geom)
        i = self._livings.index(living)
        # means we cannot call this while looping through livings, such
        # as inside living update
        del self._livings[i]
        
    def get_water_world(self):
        return self._water_world
    
    def get_dam(self, x):
        for dam in self._dams:
            if dam.in_area(x):
                return dam
        return None
    
    def get_height(self, x):
        """Get the height of the world in location x.
        """
        for dam in self._dams:
            if dam.in_area(x):
                return dam.height
        return 0.0

    def get_waterlevel(self, x):
        """Get the water level of the world in location x.
        """
        for dam in self._dams:
            if dam.in_area(x):
                if dam.is_flooded():
                    return dam.get_highest_level()
                else:
                    return waterlevel.Waterlevel('none', 0.0)
            if dam.in_water_area(x):
                return dam.level
        return self._start_dam.level
      
    def render_info(self, screen):        
        # render info area
        screen.fill(DISPLAY_COLOR, Rect(0, 550, 800, 600))

        font = fonts.get_display_font()

        # XXX hacky way to get the beaver
        beaver = self._livings[0]
        beaver.render_info(screen, font)

        water_world = self._water_world
        surface = font.render('LAND', True, TEXT_COLOR, DISPLAY_COLOR)
        screen.blit(surface, (220, 555))
        surface = font.render('%.2f' % water_world.get_level('start').level,
                              True, TEXT_COLOR, DISPLAY_COLOR)
        screen.blit(surface, (260, 555))
        surface = font.render('DAM', True, TEXT_COLOR, DISPLAY_COLOR)
        screen.blit(surface, (220, 565))
        # XXX hack to get the only dam in the world
        dam = self._dams[0]
        surface = font.render('%.2f' % dam.height, True,
                              TEXT_COLOR, DISPLAY_COLOR)
        screen.blit(surface, (260, 565))
        surface = font.render('SEA', True, TEXT_COLOR, DISPLAY_COLOR)
        screen.blit(surface, (220, 575))
        surface = font.render('%.2f' % water_world.get_level('sea').level,
                              True, TEXT_COLOR, DISPLAY_COLOR)
        screen.blit(surface, (260, 575))
        
    def render(self, screen):
        # render start water level
        if self._dams:
            xs = self._dams[0].geom.getAABB()[0]
        else:
            xs = 0.0
        start_level = self._start_dam.level
        # XXX why do I have to add 1 to make things fit?
        screen.fill(WATER_COLOR,
                    Rect(coord(0, start_level.level),
                         (conv(xs), conv(start_level.level) + 1)))
        
        # render dams and associated water
        for dam in self._dams:
            dam.render(screen)

        # render charging gadget
        screen.blit(load('gadget2.png'), coord(0, 3.45))
        
        # render items
        for item in self._items:
            item.render(screen)
            
        # render livings
        for living in self._livings:
            living.render(screen, self)

        self.render_info(screen)
        
def collision_callback(args, geom1, geom2):
    """Callback function for the collide() method.

    This function checks if the given geoms do collide and
    creates contact joints if they do.
    """
    # don't collide rightmost object with anything that's not the beaver
    if getattr(geom1, 'rightmost', None) or getattr(geom2, 'rightmost', None):
        obj1 = getattr(geom1, 'obj', None)
        obj2 = getattr(geom2, 'obj', None)
        if not (isinstance(obj1, Beaver) or
                isinstance(obj2, Beaver)):
            return
        
    # check if the objects do collide
    contacts = ode.collide(geom1, geom2)

    if contacts:
        obj1 = getattr(geom1, 'obj', None)
        obj2 = getattr(geom2, 'obj', None)
        if obj1 is not None and obj2 is not None:
            obj1.add_collision(obj2)
            obj2.add_collision(obj1)
                
    # create contact joints
    ode_world, contactgroup = args
    for c in contacts:
        c.setBounce(0.)
        c.setMu(0)
        j = ode.ContactJoint(ode_world, contactgroup, c)
        j.attach(geom1.getBody(), geom2.getBody())
    
