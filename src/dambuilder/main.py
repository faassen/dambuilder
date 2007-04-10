import sys

import pygame
from pygame.locals import *

from dambuilder.load import load
from dambuilder.menu import menuloop

def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Dam Builder")
    pygame.display.set_icon(load('icon.png'))
    
    if len(sys.argv) > 1 and sys.argv[1] == '-p':
        # profiling run
        import hotshot, hotshot.stats
        prof = hotshot.Profile('dambuilder.prof')
        benchtime = prof.runcall(menuloop, screen)
        prof.close()
        stats = hotshot.stats.load('dambuilder.prof')
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        stats.print_stats(20)
    else:
        menuloop(screen)
