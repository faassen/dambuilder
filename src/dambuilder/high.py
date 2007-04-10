import pickle

import pygame
from pygame.locals import *

from dambuilder import fonts
from dambuilder.load import main_path

def get_high_scores():
    filename = main_path('highscores')
    try:
        f = open(filename, 'rb')
        result = pickle.load(f)
        f.close()
    except IOError:
        result = HighScores()
    return result

class HighScores(object):
    def __init__(self):
        self._entries = [ScoreEntry('-', 0., None)] * 10

    def add_potential_high_score(self, entry):
        is_high, lowest_entry = self.is_high_score(entry.score)
        if not is_high:
            return
        # remove previous lowest score
        if lowest_entry is not None:
            self._entries.remove(lowest_entry)
        # add new high
        self._entries.append(entry)
        # save
        self.save()
    
    def get_sorted_entries(self):
        return list(reversed(
            sorted(self._entries, key=lambda entry: entry.score)))
        
    def is_high_score(self, score):
        entries = self.get_sorted_entries()
        if not entries:
            return True, None
        lowest_entry = entries[-1]
        return score > lowest_entry.score, lowest_entry  
    
    def save(self):
        filename = main_path('highscores')
        f = open(filename, 'wb')
        pickle.dump(self, f)
        f.close()

    def render(self, screen):
        font = fonts.get_medium_font()

        y = 70
        for entry in self.get_sorted_entries():
            surface = font.render(entry.name, True, (255, 255, 255))
            screen.blit(surface, (60, y))
            surface = font.render('%.3f' % entry.score, True, (255, 255, 255))
            w, h = surface.get_size()
            screen.blit(surface, (480 - w, y))
            if entry.datestamp is not None:
                ds = entry.datestamp.strftime('%Y-%m-%d %H:%M')
                surface = font.render(ds, True, (255, 255, 255))
                screen.blit(surface, (510, y))
            y += 50

        font = fonts.get_small_font()
        surface = font.render('Press mouse button or escape to continue',
                              True, (250, 250, 250))
        screen.blit(surface, (250, 570))
        
class ScoreEntry(object):
    def __init__(self, name, score, datestamp):
        self.name = name
        self.score = score
        self.datestamp = datestamp


