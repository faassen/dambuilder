import sys

import pygame
from pygame.locals import *

from dambuilder.world import World
from dambuilder.load import load
from dambuilder.input import player_input
from dambuilder.constants import SKY_COLOR

def mainloop(screen):
    pygame.mouse.set_visible(False)

    world = World()
    world.setup()
    
    clk = pygame.time.Clock()
    fps = 50
    dt = 1.0 / fps
 
    while True:
        player_input.handle_events()
        if player_input.quit_request:
            break
        screen.fill(SKY_COLOR)
    
        world.render(screen)
                    
        pygame.display.flip()

        world.step(dt)

        if world.is_game_over():
            break

        clk.tick(fps)
        #print "fps: %2.1f  dt:%d rawdt:%d"%(clk.get_fps(), clk.get_time(), clk.get_rawtime())

    score = world.get_water_world().get_level('sea').level
                                              
    # clean out all ODE objects
    world.clear_ode()
    # clear keyboard state
    player_input.clear()
    # clear event queue
    pygame.event.clear()
    return score
