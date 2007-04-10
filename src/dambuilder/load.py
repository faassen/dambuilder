import os, sys

import pygame
from pygame.locals import *

def main_is_frozen():
    return hasattr(sys, 'frozen')

def main_path(*paths):
    if main_is_frozen():
        # py2exe, resource directory next to it
        path = os.path.dirname(sys.executable)
    else:
        # run_game.py in project dir
        path = os.path.dirname(sys.argv[0])
        project_path, name = os.path.split(path)
        # buildout bin directory
        if name == 'bin':
            path = project_path
    return os.path.join(path, *paths)
    
class Images(object):
    def __init__(self):
        self._images = {}

    def load(self, *resource_names):
        colorkey = (0, 255, 0)
        image = self._images.get((colorkey, resource_names))
        if image is not None:
            return image
        image = pygame.image.load(main_path('data', *resource_names))
        image.convert()
        image.set_colorkey(colorkey) # RLACCEL)
        self._images[(colorkey, resource_names)] = image
        return image

    def load_colorkey(self, colorkey, *resource_names):
        image = self._images.get((colorkey, resource_names))
        if image is not None:
            return image
        image = pygame.image.load(main_path('data', *resource_names))
        image.convert()
        image.set_colorkey(colorkey) # RLACCEL)
        self._images[(colorkey, resource_names)] = image
        return image

images = Images()

load = images.load
load_colorkey = images.load_colorkey

class Sounds(object):
    def __init__(self):
        self._sounds = {}

    def load(self, *resource_names):
        sound = self._sounds.get(resource_names)
        if sound is not None:
            return sound
        f = open(main_path('data', *resource_names), 'rb')
        snd = pygame.mixer.Sound(f)
        f.close()
        self._sounds[resource_names] = snd
        return snd

sounds = Sounds()

load_sound = sounds.load
