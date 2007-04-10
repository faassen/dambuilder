import pygame

from dambuilder import living, anim
from dambuilder.input import player_input
from dambuilder.view import coord, conv, set_view
from dambuilder.item import Item
from dambuilder.living import ILLEGAL, WALKING, WADING, SWIMMING, FLYING
from dambuilder.material import SECTION_HEIGHT
from dambuilder.constants import (JUMP_FORCE, CLIMB_Y_FORCE, SWIM_Y_FORCE,
                                  WALK_FORCE,
                                  FIX_SIZE, FIX_AMOUNT, CYCLE_TIMEOUT,
                                  BUILD_TIMEOUT, BUY_TIMEOUT, DISPLAY_COLOR,
                                  TEXT_COLOR, SELECTED_COLOR,
                                  MATERIAL_COST)
from dambuilder.constants import WOOD, STONE, BRICK, METAL, MATERIALS
from dambuilder.load import load_sound

class Beaver(living.Living):

    def __init__(self, geom):
        super(Beaver, self).__init__(geom, 1, 1.5)
        
        self._selected_material = WOOD
        self._worth = 25
        self._materials = {
            WOOD : 10,
            STONE: 1,
            BRICK: 1,
            METAL: 1,
            }
        
        self._cycle_timeout = living.Timeout(CYCLE_TIMEOUT)
        self._build_timeout = living.Timeout(BUILD_TIMEOUT)
        self._buy_timeout = living.Timeout(BUY_TIMEOUT)
        self._beep_timeout = living.Timeout(300)
        self._nano_timeout = living.Timeout(6000)
        
    def behavior(self, stepsize, world):
        if self._collisions:
            for obj in self._collisions:
                if isinstance(obj, Item):
                    snd = load_sound('25880_acclivity_FingerPlop4.wav')
                    snd.play()
                    self._worth += obj.worth
                    world.remove_item(obj)
                    
        # cycle material choice
        if player_input.action3:
            self.cycle_material()

        body = self.geom.getBody()
        state = self.get_state(world)
        
        # go left or right
        if player_input.x_direction is not None:
            self._rightleft = player_input.x_direction
            body.addForce((player_input.x_direction * WALK_FORCE, 0, 0))

        # jump (if possible)
        if player_input.action2:
            if state in (WALKING, WADING):
                body.addForce((0, JUMP_FORCE, 0))
 
        # if we're near a dam
        dam = self.near_dam(world)
        if dam is not None:
            self.behavior_near_dam(stepsize, world, state, dam)
        else:
            self.behavior_away_dam(state)

        dam = self.on_dam(world)
        if dam is not None and player_input.action1:
            self.build_dam(dam)

        # update position of view port
        x, y, z = self.geom.getPosition()

        # charging area
        if x >= 0 and x < 1.5 and y >= 0 and y < 1:
            if player_input.action1 and not self._buy_timeout.active():
                cost = MATERIAL_COST[self._selected_material]
                if self._worth >= cost:
                    self._worth -= cost
                    self._materials[self._selected_material] += 1
                    self._buy_timeout.start()
                    if not self._nano_timeout.active():
                        sound = load_sound('33326_laya_rez_fx.wav')
                        sound.play()
                        self._nano_timeout.start()
                else:
                    self.no_material()
        set_view(x, y)        

    def behavior_near_dam(self, stepsize, world, state, dam):
        """Special behavior possible while near the dam.
        """
        body = self.geom.getBody()
        
        # while clinging to the dam we're not subject to gravity
        body.setGravityMode(False)

        # fixing the dam if we have selected material available
        if player_input.action1:
            if self._materials[self._selected_material] > 0:
                dummy, y, dummy = self.geom.getPosition()
                # if we are near the dam, we fix leaks
                fixed = dam.fix_leaks_at(world, y, FIX_SIZE, FIX_AMOUNT * stepsize,
                                         self._selected_material)
                # if we fixed it this round, we will use up the material
                if fixed:
                    self._materials[self._selected_material] -= 1
            else:
                self.no_material()
    
        # if the player wants to go up or down, let's do that
        if player_input.y_direction is not None:
            self._updown = player_input.y_direction
            body.addForce((0, player_input.y_direction * CLIMB_Y_FORCE, 0))
        if state is not FLYING:
            self._updown = 1

    def no_material(self):
        if not self._beep_timeout.active():
            sound = load_sound('25882_acclivity_Beep1000.wav')
            sound.play()
            self._beep_timeout.start()
            
    def behavior_away_dam(self, state):
        """Special behavior when we're away from the dam.
        """
        self._updown = 1
        body = self.geom.getBody()

        # if we are swimming, we can go up and down extra fast
        if player_input.y_direction is not None:
            if state is SWIMMING:
                body.addForce((0, player_input.y_direction * SWIM_Y_FORCE, 0))

        # we want gravity to apply unless we're flying
        body.setGravityMode(state in (WALKING, WADING, FLYING))

    def build_dam(self, dam):
        """Build up the dam.
        """
        if self._build_timeout.active():
            return
        # we can only build up if we have the selected material
        if self._materials[self._selected_material] == 0:
            self.no_material()
            return
        sound = load_sound('construction.wav')
        sound.play()
        
        # use up material
        self._materials[self._selected_material] -= 1
        # build up dam
        dam.build_up(self._selected_material)
        # move beaver higher
        x, y, z = self.geom.getPosition()
        self.geom.setPosition((x, y + SECTION_HEIGHT, z))
        self._build_timeout.start()
        
    def cycle_material(self):
        if self._cycle_timeout.active():
            return
        i = MATERIALS.index(self._selected_material)
        i += 1
        if i >= len(MATERIALS):
            i = 0
        self._selected_material = MATERIALS[i]
        self._cycle_timeout.start()

    def render_info(self, screen, font):
        y = 555
        for material in MATERIALS:
            if material is self._selected_material:
                color = TEXT_COLOR
            else:
                color = (100, 100, 100)
            surface = font.render(material.upper(), True,
                                  color,
                                  DISPLAY_COLOR)
            screen.blit(surface, (20, y))
            surface = font.render(str(self._materials[material]),
                                  True,
                                  color,
                                  DISPLAY_COLOR)
            screen.blit(surface, (80, y))
            y += 10
        surface = font.render('TRASH', True,
                              TEXT_COLOR, DISPLAY_COLOR)
        screen.blit(surface, (120, 555))
        surface = font.render(str(self._worth), True,
                              TEXT_COLOR, DISPLAY_COLOR)
        screen.blit(surface, (180, 555))

    def render(self, screen, world):
        state = self.get_state(world)

        if state == WALKING or state == WADING:
            if player_input.x_direction is not None:
                self.change_animation(anim.BeaverWalking)
            else:
                self.change_animation(anim.BeaverStanding)
        elif state == SWIMMING:
            self.change_animation(anim.BeaverSwimming)
        elif state == FLYING:
            dam = self.near_dam(world)
            if dam is not None:
                if player_input.y_direction is not None:
                    self.change_animation(anim.BeaverClimbing)
                else:
                    self.change_animation(anim.BeaverClinging)
            else:
                # if swimming, continue 'jump' animation, otherwise switch
                # to walking
                self._updown = 1
                if type(self.anim) is not anim.BeaverSwimming:
                    self.change_animation(anim.BeaverWalking)
        else:
            self.change_animation(anim.BeaverWalking)

        self.render_anim(screen)
