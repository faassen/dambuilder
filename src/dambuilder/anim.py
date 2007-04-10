import pygame
from pygame.locals import *

from dambuilder.load import load

class Animation(object):
    def __init__(self, images, t, x_offset, y_offset, facing, updown=1):
        """Animate list of images. Complete animation in t milliseconds.

        x_offset is offset in pixels to the right. When facing the
        other direction, offset is reversed.

        y_offset is offset in pixels upwards.
        
        facing is facing direction. +1 for right, -1 for left.

        updown is up/down direction. +1 for up, -1 for down.

        Images are assumed to start out facing right.
        """
        if facing < 0:
            # XXX doing a flip while the game is running each time
            # the character turns may not be very efficient...
            images = [pygame.transform.flip(image, True, False) for
                      image in images]
            x_offset = -x_offset
        if updown < 0:
            images = [pygame.transform.flip(image, False, True) for
                      image in images]
            y_offset = -y_offset
        self.images = images
        self.t = t
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.frame_length = t / len(images)
        self._start = None
        self.facing = facing
        self.updown = updown
        
    def start(self):
        self._start = pygame.time.get_ticks()

    def show(self, surface, coordinates):
        """Show animation on surface at coordinates.
        """
        current = pygame.time.get_ticks() - self._start
        current = current % self.t
        image = self.images[int(current / self.frame_length)]
        x, y = coordinates
        x += self.x_offset
        y += self.y_offset
        surface.blit(image, (x, y))

    def get_size(self):
        return self.images[0].get_size()

class BeaverStanding(Animation):
    def __init__(self, facing, updown):
        super(BeaverStanding, self).__init__(
            [load('beaverWalk02.png')],
            1000., 0, 4, facing, updown)

class BeaverWalking(Animation):
    def __init__(self, facing, updown):
        super(BeaverWalking, self).__init__(
            [load('beaverWalk01.png'),
             load('beaverWalk02.png'),
             load('beaverWalk03.png')],
            250., 0, 4, facing, updown)

class BeaverSwimming(Animation):
    def __init__(self, facing, updown):
        super(BeaverSwimming, self).__init__(
            [load('beaverSwim01.png'),
             load('beaverSwim02.png'),
             load('beaverSwim03.png'),
             ],
            500., 0, 0, facing, updown)

class BeaverClinging(Animation):
    def __init__(self, facing, updown):
        super(BeaverClinging, self).__init__(
            [load('beaverClimb02.png')],
            500, 8, 0, facing, updown)
        
class BeaverClimbing(Animation):
    def __init__(self, facing, updown):
        super(BeaverClimbing, self).__init__(
            [load('beaverClimb01.png'),
             load('beaverClimb02.png'),
             ],
            500., 8, 0, facing, updown)

class BirdFlying(Animation):
    def __init__(self, facing, updown):
        super(BirdFlying, self).__init__(
            [load('woodpecker_flying01.png'),
             load('woodpecker_flying02.png'),
             load('woodpecker_flying03.png')],
            500., 0, 0, facing, updown)

class BirdPecking(Animation):
    def __init__(self, facing, updown):
        super(BirdPecking, self).__init__(
            [load('woodpecker_01.png'),
             load('woodpecker_02.png'),
             load('woodpecker_03.png'),
             load('woodpecker_04.png')],
            200., 18, 0, facing, updown)

class FishBlueSwimming(Animation):
    def __init__(self, facing, updown):
        super(FishBlueSwimming, self).__init__(
            [load('fish_blue_01.png'),
             load('fish_blue_02.png')],
            200., 0, 0, facing, updown)

class FishBlueNibbling(Animation):
    def __init__(self, facing, updown):
        super(FishBlueNibbling, self).__init__(
            [load('fish_blue_01.png'),
             load('fish_blue_02.png')],
            100., 0, 0, facing, updown)
        
class FishGoldSwimming(Animation):
    def __init__(self, facing, updown):
        super(FishGoldSwimming, self).__init__(
        [load('fish2_01.png'),
         load('fish2_02.png'),
         load('fish2_03.png'),],
         400., 0, 0, facing,updown)
    
class FishGoldNibbling(Animation):
    def __init__(self, facing, updown):
        super(FishGoldNibbling, self).__init__(
        [load('fish2_01.png'),
         load('fish2_02.png'),
         load('fish2_03.png'),],
         200., 0, 0, facing,updown)

        
