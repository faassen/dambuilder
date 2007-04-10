import random

import pygame
from pygame.locals import *

from dambuilder import waterfall
from dambuilder.leak import Leak
from dambuilder.view import coord, conv, player_view
from dambuilder.material import (SECTION_HEIGHT, render_material)
from dambuilder.physbody import Immovable, ode_world, ode_space
from dambuilder.constants import (WATER_COLOR, FLOOD_RATE,
                                  MAX_X, INITIAL_LEAK_RATE,
                                  WOOD,
                                  MATERIAL_ANIMAL_EROSION,
                                  NEW_LEAK_CHANCE)

leak_connection_id = 0

class DamSentinel(object):
    """A dam that isn't really there, but is a sentinel for the dam
    doubly-linked list.
    """
    def __init__(self, level):
        self.id = 'start'
        self.level = level
        self.prev_dam = None
        self.next_dam = None

class Dam(object):
    def __init__(self, id, geom, level, prev_dam, next_dam):
        self.id = id
        
        self.geom = geom

        x, y, dummy = geom.getPosition()

        width, height, z = geom.getLengths()        
        self.start_x = x - width / 2.
        self.end_x = x + width / 2.
        self.height = height
        
        self.level = level
        self.prev_dam = prev_dam
        self.next_dam = next_dam
        self._leaks = []

        # this requires us to only make dams that are multiple of
        # SECTION_HEIGHT high

        self._materials = [WOOD] * int(height / SECTION_HEIGHT)

        self._waterfall = waterfall.Waterfall(
            0., 0., 0.1,
            self.start_x, self.end_x, height)

    def clear_ode(self):
        ode_space.remove(self.geom)
        self._waterfall.clear_ode()
        for leak in self._leaks:
            leak.clear_ode()
        
    # MANIPULATORS

    def add_leak(self, world, height, rate):
        global leak_connection_id
        xs, xe = self.geom.getAABB()[:2]
        leak = Leak(xs, xe, height, rate, leak_connection_id)
        self._leaks.append(leak)
        leak_connection_id += 1
            
    def fix_leaks_at(self, world, y, check_size, amount, material):
        """Returns True when material could actually be used and leak is
        fixed.
        """
        water_world = world._water_world
        for leak in self.get_leaks_at(y, check_size):
            leak.rate -= amount
            if leak.rate < 0.:
                leak.clear_ode()
                self._leaks.remove(leak)
                if water_world.have_connection(leak.connection_id):
                    water_world.disconnect(leak.connection_id)
                # replace material at spot with active material
                self._materials[int(leak.height / SECTION_HEIGHT)] = material
                return True
        return False

    def nibble_at(self, world, y, check_size, amount):
        """Nibble/peck at the dam, damaging it.
        """
        if y >= self.height:
            return
        water_world = world._water_world
        leaks = self.get_leaks_at(y, check_size)
        if leaks:
            material = self.get_material(y)
            for leak in leaks:
                leak.rate += amount * MATERIAL_ANIMAL_EROSION[material]
        else:
            self.add_leak(world, y, INITIAL_LEAK_RATE)

    def build_up(self, material):
        self._materials.append(material)
        h = len(self._materials) * SECTION_HEIGHT
        self.height = h
        # adjust waterfall too, ugly
        self._waterfall.y = h
        
        # adjust geom
        x, y, dummy = self.geom.getPosition()
        w, dummy, dummy = self.geom.getLengths()
        if ode_space is not None:
            ode_space.remove(self.geom)
            geom = Immovable(x, h / 2., w, h)
        else:
            # XXX argh
            from dambuilder.tests import MockGeomBox
            geom = MockGeomBox(x, h/2., w, h)
        self.geom = geom

    def step_erosion(self, stepsize, world):
        """Erode leaks that already have been created.
        """
        dam_height = self.height

        # the more leaks, the more will be eroding at the same time
        erode_attempts = int(len(self._leaks) / 10.) + 1
        if erode_attempts > 10:
            erode_attempts = 10

        if self._leaks:
            for i in range(erode_attempts):
                leak = random.choice(self._leaks)
                leak.step_erosion(stepsize, self)

    def update_flooded(self, world):
        water_world = world._water_world
        prev_level = self.get_prev_level()
        flood_id = 'flood_%s' % self.id
        
        if self.is_flooded():
            # dam is flooded
            self._waterfall.update_flow(FLOOD_RATE, self.level, prev_level)
            
            if not water_world.have_connection(flood_id):
                water_world.connect(flood_id,
                                    self.level, prev_level,
                                    FLOOD_RATE)
        else:
            # dam is not flooding anymore
            if water_world.have_connection(flood_id):
                water_world.disconnect(flood_id)
                self._waterfall.cut_flow()

    def update_leaks(self, world):
        """Create connections for all active leaks, and close those
        for those leaks above water.
        """
        water_world = world._water_world
        prev_level = self.get_prev_level()
        highest_level = self.get_highest_level()
        
        for leak in self._leaks:
            if leak.between(0, highest_level.level):
                leak.activate(water_world, self.level, prev_level)
            else:
                leak.deactivate(water_world)
            leak.update()

    def update(self, world):
        self.update_flooded(world)
        self.update_leaks(world)
        if ode_world is not None:
            self._waterfall.update()

    # ACCESSORS
    
    def in_area(self, x):
        return self.start_x <= x < self.end_x

    def in_water_area(self, x):
        if self.next_dam is None:
            return self.end_x <= x
        return self.end_x <= x < self.next_dam.start_x

    def is_flooded(self):
        if self.level.level > self.height:
            return True
        return self.get_prev_level().level > self.height
    
    def get_prev_level(self):
        return self.prev_dam.level
    
    def get_leaks_at(self, y, check_size):
        start_y = y - check_size / 2.
        end_y = y + check_size / 2.
        return self.get_leaks_between(start_y, end_y)

    def get_leaks_between(self, start_y, end_y):
        result = []
        for leak in self._leaks:
            if leak.between(start_y, end_y):
                result.append(leak)
        return result

    def get_highest_level(self):
        level = self.level
        prev_level = self.get_prev_level()
        if level.level > prev_level.level:
            return level
        else:
            return prev_level

    def get_material(self, y):
        if y > self.height:
            return None
        i = y / SECTION_HEIGHT
        return self._materials[int(i)]
    
    def render_dam(self, screen, x):
        # start height at which we're drawing sections
        hs = player_view.origin_y
        # end height at which we're drawing sections
        he = hs + player_view.height
        s = int(hs / SECTION_HEIGHT)
        e = int(he / SECTION_HEIGHT)
        if s > 0:
            s -= 1
        e += 1
        materials = self._materials[s:e]
    
        i = s
        for material in materials:
            y = SECTION_HEIGHT + SECTION_HEIGHT * i
            render_material(screen, x, y, material)
            i += 1
                
    def render(self, screen):
        xs, xe, ys, ye, zs, ze = self.geom.getAABB()
        # dam itself
        self.render_dam(screen, xs)
        
        # any flooding
        if self.is_flooded():
            highest_level = self.get_highest_level().level
            screen.fill(WATER_COLOR,
                        Rect(coord(xs, highest_level),
                             (conv(xe - xs), conv(highest_level - ye) + 1)))
        # associated water
        if self.next_dam is not None:
            nxs, nxe, nys, nye, nzs, nze = next_dam.geom.getAABB()
        else:
            nxs = MAX_X + player_view.width
        screen.fill(WATER_COLOR,
                    Rect(coord(xe, self.level.level),
                         (conv(nxs - xe), conv(self.level.level) + 1)))
        # draw leaks
        for leak in self._leaks:
            leak.render(screen, self)

        # flooding waterfall
        self._waterfall.render(screen)
