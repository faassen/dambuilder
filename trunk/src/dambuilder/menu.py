from datetime import datetime
import pygame
from pygame.locals import *

from dambuilder.game import mainloop
from dambuilder.load import load
from dambuilder.input import player_input
from dambuilder.high import get_high_scores, ScoreEntry
from dambuilder.living import Timeout
from dambuilder import fonts

MAX_CHARACTERS = 16

class Button(object):
    def __init__(self, normal_img, selected_img, x, y, f):
        self.normal_img = normal_img
        self.selected_img = selected_img
        self.xs = x
        self.ys = y
        w, h = self.normal_img.get_size()
        self.xe = x + w
        self.ye = y + h
        self.f = f

    def click(self, screen):
        return self.f(screen)

def menuloop(screen):
    player_input.clear()
    
    image = load('opening_screen.png')

    start_game_button = Button(load('start_game01.png'),
                               load('start_game02.png'),
                               420, 78, start_game)
    high_scores_button = Button(load('high_scores01.png'),
                                load('high_scores02.png'),
                                420, 192, high_scores)
    instructions_button = Button(load('instructions01.png'),
                                 load('instructions02.png'),
                                 420, 307, instructions)
    full_screen_button = Button(load('full_screen01.png'),
                                load('full_screen02.png'),
                                16, 556, full_screen)
    quit_button = Button(load('quit01.png'),
                         load('quit02.png'),
                         420, 421, quit)

    buttons = [start_game_button, high_scores_button,
               instructions_button, full_screen_button, quit_button]
    
    pygame.mouse.set_visible(True)
    
    screen.blit(image, (0, 0))
    pygame.display.flip()

    last_selected = None

    timeout = Timeout(300)
    
    while True:
        player_input.handle_events()
        
        x, y = pygame.mouse.get_pos()
        button = on_button(x, y, buttons)
        if button is not None:
            screen.blit(button.selected_img,
                        (button.xs, button.ys))
            last_selected = button
            pygame.display.flip()
        else:
            if last_selected is not None:
                screen.blit(last_selected.normal_img,
                            (last_selected.xs, last_selected.ys))
                last_selected = None
                pygame.display.flip()
            
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and button is not None and not timeout.active():
            if button.click(screen):
                # quit the game
                break
            else:
                # redraw
                screen.blit(image, (0, 0))
                pygame.display.flip()
                timeout.start()
                
def high_scores_loop(screen):
    player_input.clear()

    image = load('water_scene.png')

    pygame.mouse.set_visible(True)
    
    screen.blit(image, (0, 0))
    
    scores = get_high_scores()
    scores.render(screen)

    pygame.display.flip()
    
    wait_for_continue()

def wait_for_continue():
    timeout = Timeout(300)
    timeout.start()

    while True:
        player_input.handle_events()

        if player_input.quit_request and not timeout.active():
            break
        
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and not timeout.active():
            # away from this screen
            break

def render_name_entry(screen, score):
    image = load('water_scene.png')
    screen.blit(image, (0, 0))

    big_font = fonts.get_large_font()
    surface = big_font.render('High Score! (%.3f)' % score,
                              True, (255, 255, 255))
    screen.blit(surface, (150, 100))

    small_font = fonts.get_small_font()
    
    surface = small_font.render('Please enter your name and press enter',
                                True, (250, 250, 250))
    screen.blit(surface, (200, 200))

def render_game_over(screen):
    big_font = fonts.get_large_font()
    surface = big_font.render("Game over!", True, (0, 0, 0))
    screen.blit(surface, (230, 200))

    small_font = fonts.get_small_font()
    surface = small_font.render('Press mouse button or escape to continue',
                                True, (0, 0, 0))
    screen.blit(surface, (215, 300))

    pygame.display.flip()
    wait_for_continue()
    
def name_entry_loop(screen, score):
    pygame.mouse.set_visible(False)

    render_name_entry(screen, score)

    big_font = fonts.get_large_font()
    
    pygame.display.flip()

    name = ''
    while True:
        e = pygame.event.wait()
        
        if e.type == KEYDOWN:
            if e.key == K_RETURN:
                break
            elif e.key == K_BACKSPACE:
                name = name[:-1]
                render_name_entry(screen, score)
            else:
                if legal_char(e.unicode) and len(name) < MAX_CHARACTERS:
                    name += e.unicode

        surface = big_font.render(name, True, (255, 255, 255))
        screen.blit(surface, (100, 300))
        pygame.display.flip()

    pygame.event.clear()
    
    if not name:
        return 'Unknown'
    return name

def legal_char(c):
    return (c in '!@#$%^&*()_+-={}[]\/.,<>:;~| ') or c.isalnum()

def instructions_screen(screen, text):
    player_input.clear()

    image = load('water_scene.png')

    screen.blit(image, (0, 0))
    
    pygame.mouse.set_visible(True)

    lines = text.split('\n')

    y = 80
    font = fonts.get_medium_font()
    
    for line in lines:
        line = line.strip()
        surface = font.render(line, True, (250, 250, 250))
        screen.blit(surface, (40, y))
        y += 30

    small_font = fonts.get_small_font()
       
    surface = small_font.render('Press mouse button or escape to continue',
                                True, (250, 250, 250))
    screen.blit(surface, (250, 570))

    pygame.display.flip()
    
    wait_for_continue()

def instructions1(screen):    
    text = """\
It is the future and the world is in trouble. The
sea level is rising. Trash is everywhere.
Genetically engineered animals have gone on a
rampage.

Finally, Dutch genetic engineers have created a
special animal to limit the damage. This animal
is intended to be a hero: you.
"""

def instructions2(screen):
    text = """\


You are a beaver. Your mission: to build a dam
and protect the land from the rising sea as
long as possible, so that people can be safely
evacuated! Clean up the sea while you're at it.

Gather trash in the sea. Go to the
nano-assembler charging device, and charge up
on building materials. 

Protect your dam! Animals damage your dam
and create leaks. Chase them off and fix
any leaks!
"""
    instructions_screen(screen, text)

def instructions3(screen):
    text = """\



left: go left
right: go right
up: climb the dam, swim up
down: climb the dam, swim down
spacebar, on top of the dam: build up the dam
spacebar, near a leak: repair leaks
spacebar, at device: charge up
alt: jump
enter: change material selection
"""
    instructions_screen(screen, text)

def instructions4(screen):
    text = """\
TIPS


Recharging takes time. Keep your spacebar
pressed to recharge

Some leaks are very big. Stay close to them and
keep your spacebar pressed to repair them

Build up vertical speed to make it to the top of
the dam!
"""
    instructions_screen(screen, text)
    
def instructions5(screen):
    text = """\

Eventually your dam must succumb to the
rising sea. Your mission is to hold out as
long as possible. You lose the game when the
water level on the land reaches above 10.

Your final score is determined by the sea level
at the end of the game.

Good luck!

Programming: Martijn Faassen
Graphics: Felicia Wong
Made as part of the PyWeek #4 competition
Theme: The only way is up
"""
    instructions_screen(screen, text)
    
def start_game(screen):
    # play game, get score
    score = mainloop(screen)
    # display game over
    render_game_over(screen)
    
    high_scores = get_high_scores()

    is_high, dummy = high_scores.is_high_score(score)
    if is_high:
        # get a name
        name = name_entry_loop(screen, score)
        # max letters for name
        name = name[:MAX_CHARACTERS]
        # add to high scores
        high_scores.add_potential_high_score(
            ScoreEntry(name, score, datetime.now()))
    
    high_scores_loop(screen)
    return False

def high_scores(screen):
    high_scores_loop(screen)
    return False

def instructions(screen):
    instructions1(screen)
    instructions2(screen)
    instructions3(screen)
    instructions4(screen)
    instructions5(screen)
    return False

_fullscreen = False

def full_screen(screen):
    global _fullscreen
    if _fullscreen:
        pygame.display.set_mode((800, 600))
        _fullscreen = False
    else:
        pygame.display.set_mode((800, 600), FULLSCREEN)
        _fullscreen = True

def quit(screen):
    return True

def on_button(x, y, buttons):
    for button in buttons:
        if (button.xs <= x <= button.xe and
            button.ys <= y <= button.ye):
            return button
    return None
